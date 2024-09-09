import os
import streamlit as st

from dotenv import load_dotenv
from scrapper import AppleJobScrapper
from llm import LLM
from agent import get_job, get_email, Email
from store import VectorStore
import logfire
import litellm

load_dotenv()

logfire.configure(pydantic_plugin=logfire.PydanticPlugin(record="all"))
litellm.success_callback = ["logfire"]

model = os.getenv("API_MODEL")
embedding_model = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
llm_generator = LLM(model=model)
vector_store = VectorStore("vect_db", "portfolio", embedding_model)

EMAIL_TEMPLATE = """
**SUBJECT: {email_subject}**

{email_content}

Portifolio:
{portfolio_links}

{regards}
"""


def format_email(email: Email) -> str:
    email_subject = email.subject
    email_content = email.content
    regards = email.best_regards
    portfolio_links = "\n".join(
        [
            f"* [{link.name} ({link.role})]({link.link})"
            for link in email.portfolio_links
        ]
    )
    return EMAIL_TEMPLATE.format(
        email_subject=email_subject,
        email_content=email_content,
        portfolio_links=portfolio_links,
        regards=regards,
    )


if not vector_store.count():
    vector_store.load_documents("resources/portfolio.csv")


st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")
st.title("📧 Cold Mail Generator")

col1, col2 = st.columns(2)
with col1:
    company_input = st.text_input("Company:", value="BARON IA")
with col2:
    person_input = st.text_input("Person:", value="Rodrigo")

url_input = st.text_input(
    "Enter a URL:",
    value="https://jobs.apple.com/en-us/details/200503445/aiml-machine-learning-engineer-scientist-siri-information-intelligence",
)
submit_button = st.button("Submit")

if submit_button:
    try:
        job_info = get_job(url_input, llm_generator, AppleJobScrapper())
        documents = vector_store.query_document(", ".join(job_info.skills))
        portfolio = [
            {"name": "Rodrigo", "role": doc["role"], "link": doc["link"]}
            for doc in documents[0]
        ]

        email = get_email(
            job_info,
            llm_generator,
            {"person": person_input, "company": company_input},
            portfolio,
        )
        st.divider()
        st.markdown(format_email(email))

    except Exception as e:
        st.error(f"An Error Occurred: {e}")
        raise e
