import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

def bge_rerank(query, documents):
    tokenizer = AutoTokenizer.from_pretrained('BAAI/bge-reranker-v2-m3')
    model = AutoModelForSequenceClassification.from_pretrained('BAAI/bge-reranker-v2-m3')
    model.eval()

    pairs = [[query, d] for d in documents]
    with torch.no_grad():
        inputs = tokenizer(pairs, padding=True, truncation=True, return_tensors='pt', max_length=1024)
        scores = model(**inputs, return_dict=True).logits.view(-1, ).float()
        return scores.tolist()