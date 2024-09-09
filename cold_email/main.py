import os
import streamlit as st

from dotenv import load_dotenv
from scrapper import AppleJobScrapper
from llm import LLM
from agent import get_job, get_email, Email

load_dotenv()

model = os.getenv("API_MODEL")
llm_generator = LLM(model=model)

EMAIL_TEMPLATE = """
**SUBJECT: {email_subject}**

{email_content}

Portifolio:
{portfolio_links}
"""


def format_email(email: Email) -> str:
    email_subject = email.subject
    email_content = email.content
    portfolio_links = "\n".join(
        [f"* [{link.name}]({link.link})" for link in email.portfolio_links]
    )
    return EMAIL_TEMPLATE.format(
        email_subject=email_subject,
        email_content=email_content,
        portfolio_links=portfolio_links,
    )


st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")

st.title("📧 Cold Mail Generator")
col1, col2 = st.columns(2)
with col1:
    company_input = st.text_input("Company", value="BARON IA")
with col2:
    person_input = st.text_input("Person", value="Rodrigo")

url_input = st.text_input(
    "Enter a URL:",
    value="https://jobs.apple.com/en-us/details/200503445/aiml-machine-learning-engineer-scientist-siri-information-intelligence",
)
submit_button = st.button("Submit")

if submit_button:
    try:
        job_info = get_job(url_input, llm_generator, AppleJobScrapper())
        email = get_email(
            job_info,
            llm_generator,
            {"person": person_input, "company": company_input},
            [{"name": "Rodrigo", "link": "https://rodrigobaron.com"}],
        )
        st.markdown(format_email(email))

    except Exception as e:
        st.error(f"An Error Occurred: {e}")
        raise e
