import pytest
from store import VectorStore
import pandas as pd


@pytest.fixture
def pandas_data():
    return pd.DataFrame(
        {
            "Skills": ["Software development, Problem solving"],
            "Role": ["Software Engineer"],
            "Link": ["https://example.com"],
        }
    )


@pytest.fixture
def vector_store(mocker):
    mocker.patch("chromadb.PersistentClient")
    mocker.patch("sentence_transformers.SentenceTransformer")
    return VectorStore("some/path", "test", "model")


def test_load_documents(pandas_data, vector_store, mocker):
    mocker.patch("pandas.read_csv", return_value=pandas_data)
    vector_store.load_documents("some/path.csv")

    vector_store.model.encode.assert_called_once()
    vector_store.collection.add.assert_called_once()


def test_query_document(pandas_data, vector_store, mocker):
    mocker.patch("pandas.read_csv", return_value=pandas_data)
    vector_store.load_documents("some/path.csv")

    mock_query_skills = "Software development, Problem solving"
    vector_store.query_document(mock_query_skills)

    vector_store.model.encode.call_count == 2
    vector_store.collection.query.assert_called_once()


def test_count(pandas_data, vector_store, mocker):
    mocker.patch("pandas.read_csv", return_value=pandas_data)
    vector_store.load_documents("some/path.csv")

    vector_store.count()

    vector_store.collection.count.assert_called_once()
