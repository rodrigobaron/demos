import pandas as pd
import chromadb
import sentence_transformers

import uuid


class VectorStore:
    def __init__(self, persistent_path, collection_name, embedding_model) -> None:
        chroma_client = chromadb.PersistentClient(persistent_path)
        self.collection = chroma_client.get_or_create_collection(name=collection_name)
        self.model = sentence_transformers.SentenceTransformer(embedding_model)

    def load_documents(self, file_path):
        data = pd.read_csv(file_path)
        for _, row in data.iterrows():
            embeddings = self.model.encode(row["Skills"]).tolist()
            self.collection.add(
                documents=row["Skills"],
                embeddings=embeddings,
                metadatas={"role": row["Role"], "link": row["Link"]},
                ids=[str(uuid.uuid4())],
            )

    def query_document(self, skills, n_results=1):
        query_embedding = self.model.encode(skills).tolist()
        return self.collection.query(
            query_embeddings=[query_embedding], n_results=n_results
        ).get("metadatas", [])

    def count(self):
        return self.collection.count()
