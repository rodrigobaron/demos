import pandas as pd
from typing import List, Dict
from sentence_transformers import SentenceTransformer

from pydantic import BaseModel, Field
from dotenv import load_dotenv
from db import get_connection
from llm import client, model, llm
from rerank import bge_rerank

from prompts import KEYWORD_PROMPT


load_dotenv()

# dataset to ingest
file_path = 'dataset/legal_text_classification_first_1000.csv'

# embedding model
emb_model = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')

# fusion ranked query
fusion_sql = """
WITH semantic_search AS (
    SELECT id, case_id, RANK () OVER (ORDER BY embedding <=> %(embedding)s) AS rank
    FROM documents
    ORDER BY embedding <=> %(embedding)s
    LIMIT 20
),
keyword_search AS (
    SELECT id, case_id, RANK () OVER (ORDER BY ts_rank_cd(to_tsvector('english', content), query) DESC)
    FROM documents, plainto_tsquery('english', %(query)s) query
    WHERE to_tsvector('english', content) @@ query
    ORDER BY ts_rank_cd(to_tsvector('english', content), query) DESC
    LIMIT 20
)
SELECT
    COALESCE(semantic_search.id, keyword_search.id) AS id,
    COALESCE(semantic_search.case_id, keyword_search.case_id) AS case_id,
    COALESCE(1.0 / (%(k)s + semantic_search.rank), 0.0) +
    COALESCE(1.0 / (%(k)s + keyword_search.rank), 0.0) AS score
FROM semantic_search
FULL OUTER JOIN keyword_search ON semantic_search.id = keyword_search.id
ORDER BY score DESC
LIMIT 5
"""

search_by_id_sql = """
SELECT case_id text, title text, content text
FROM documents
WHERE case_id in (%(case_id_list)s)
"""

def create_documents_table(conn, lang='english'):
    conn.execute('DROP TABLE IF EXISTS documents')
    conn.execute('CREATE TABLE documents (id bigserial PRIMARY KEY, case_id text, title text, content text, embedding vector(384))')
    conn.execute(f"CREATE INDEX ON documents USING GIN (to_tsvector('{lang}', content))")

def insert_documents(conn, data):
    for document in data:
        case_id = document['case_id']
        title = document['case_title']
        content = document['case_text']
        embedding = document['embedding']
        conn.execute('INSERT INTO documents (case_id, title, content, embedding) VALUES (%s, %s, %s, %s)', (case_id, title, content, embedding))


def get_embeddings(
    df,
    model
) -> List[Dict]:
    result_list = []
    uid_list = []
    title_list = []
    text_list = []

    for _, row in df.iterrows():
        uid_list.append(row['case_id'])
        title_list.append(row['case_title'])
        text_list.append(row['case_text'])
    
    embeddings = model.encode(text_list)
    for uid, title, text, embedding in zip(uid_list, title_list, text_list, embeddings):
        result_list.append({
            'case_id': uid,
            'case_title': title,
            'case_text': text,
            'embedding': embedding,
        })
    
    return result_list

def ingest_data(conn, file_path, emb_model):
    df = pd.read_csv(file_path)
    create_documents_table(conn)
    data = get_embeddings(df, emb_model)
    insert_documents(conn, data)

def fusion_search(conn, query, emb_model, k=60):
    embedding = emb_model.encode(query)
    results = conn.execute(fusion_sql, {'query': query, 'embedding': embedding, 'k': k}).fetchall()
    return [{"case_id": case_id, "rrf_score": float(score)} for _, case_id, score in results]

def search_by_id(conn, case_id_list):
    case_id_list_str = ",".join([f"'{case_id}'" for case_id in case_id_list])
    results = conn.execute(search_by_id_sql % {'case_id_list': case_id_list_str}).fetchall()
    return [{"case_id": case_id, "title": title, "content": content} for case_id, title, content in results]

class QueryKeyword(BaseModel):
    keywords: list[str] = Field(
        ..., title="The list of keyword from query",
    )

def get_keywords(query, model):
    response = client.chat.completions.create(
        model=model,
        temperature=0.1,
        # max_retries=5,
        response_model=QueryKeyword,
        messages=[
            {
                "role": "user",
                "content": KEYWORD_PROMPT.format(query=query),
            }
        ],
    )
    return " & ".join([f"'{k}'" for k in response.keywords])

def get_answer(query: str, document: list[str]):
    stream = llm.stream_complete(f"""Give the context: {document}\n\nAnswer: {query}""")
    for chunk in stream:
        yield chunk.delta
    return

conn = get_connection()
query = "Whats the verdict from Palmer J in Macleay Nominees Pty"

ingest_data(conn, file_path, emb_model)

query_keywords = get_keywords(query, model)
print("query:", query)

fusion_results = fusion_search(conn, query_keywords, emb_model, k=60)
documents_result = search_by_id(conn, [r['case_id'] for r in fusion_results])
rerank_result = bge_rerank(query, [d["content"] for d in documents_result])

final_result = []
for fusion, doc, rr_score in zip(fusion_results, documents_result, rerank_result):
    final_result.append({
        'case_id': doc['case_id'],
        'title': doc['title'],
        'content': doc['content'],
        'rrf_score': fusion['rrf_score'],
        'rerank_score': rr_score
    })

# filter out the negative rerank
final_result = [d for d in final_result if d['rerank_score'] > 0]

# sort by renrank
final_result = sorted(final_result, key=lambda x: x['rerank_score'], reverse=True)
print("final_result:", final_result)

# stream the LLM response
final_response = ""
for chunk in get_answer(query, [d['content'] for d in final_result]):
    final_response = chunk
    print(chunk, end='', flush=True)

