import pytest
from pydantic import ValidationError
from agent import JobInfo, PortifolioLink, Email, get_email, get_job
from unittest.mock import MagicMock


job_content = """Software Engineer (Remote)
We seek for a software engineer with 2-3 years of experience:
Skills:
- Python
- Django
- SQL
"""

email_content = """ Write an cold email using 
portfolio: [{"name": "Rodrigo", "role": "Web Developer", "link": "https://example.com/rodrigo-portfolio"}]
"""
portfolio_links = ["https://example.com/rodrigo-portfolio"]


def test_job_info_valid():
    job_info_dict = dict(
        title="Software Engineer",
        description="We are looking for a skilled software engineer...",
        role="Software Engineer",
        experience="2-3 years",
        skills=["Python", "Django", "SQL"],
    )
    job_info = JobInfo.model_validate(
        job_info_dict, context={"text_chunk": job_content}
    )

    assert job_info.title == "Software Engineer"
    assert job_info.role == "Software Engineer"
    assert job_info.experience == "2-3 years"
    assert job_info.skills == ["Python", "Django", "SQL"]


def test_job_info_invalid_role():
    with pytest.raises(ValueError):
        job_info_dict = dict(
            title="Software Engineer",
            description="We are looking for a skilled software engineer...",
            role="Developer",
            experience="2-3 years",
            skills=["Python", "Django", "SQL"],
        )
        JobInfo.model_validate(job_info_dict, context={"text_chunk": job_content})


def test_job_info_invalid_experience():
    with pytest.raises(ValueError):
        job_info_dict = dict(
            title="Software Engineer",
            description="We are looking for a skilled software engineer...",
            role="Software Engineer",
            experience="No Experience",
            skills=["Python", "Django", "SQL"],
        )
        JobInfo.model_validate(job_info_dict, context={"text_chunk": job_content})


def test_job_info_invalid_skill():
    with pytest.raises(ValueError):
        job_info_dict = dict(
            title="Software Engineer",
            description="We are looking for a skilled software engineer...",
            role="Software Engineer",
            experience="2-3 years",
            skills=["Python", "Django", "C++"],
        )
        JobInfo.model_validate(job_info_dict, context={"text_chunk": job_content})


def test_portfolio_link_valid():
    link_dict = PortifolioLink(
        name="Rodrigo",
        role="Web Developer",
        link="https://example.com/rodrigo-portfolio",
    )

    email_dict = dict(
        subject="Job Application",
        content="I am interested in applying for the software engineer position...",
        portfolio_links=[link_dict],
        best_regards="Best regards, Rodrigo Baron",
    )
    email = Email.model_validate(email_dict, context={"links": portfolio_links})
    link = email.portfolio_links[0]
    assert link.name == "Rodrigo"
    assert link.role == "Web Developer"
    assert link.link == "https://example.com/rodrigo-portfolio"


def test_email_valid():
    email_dict = dict(
        subject="Job Application",
        content="I am interested in applying for the software engineer position...",
        portfolio_links=[
            dict(
                name="Rodrigo",
                role="Web Developer",
                link="https://example.com/rodrigo-portfolio",
            )
        ],
        best_regards="Best regards, Rodrigo",
    )
    email = Email.model_validate(email_dict, context={"links": portfolio_links})

    assert email.subject == "Job Application"
    assert email.content.startswith("I am interested")
    assert len(email.portfolio_links) == 1
    assert email.best_regards == "Best regards, Rodrigo"


def test_email_invalid_link():
    link_dict = PortifolioLink(
        name="Rodrigo",
        role="Web Developer",
        link="https://example.com/invalid-portfolio",
    )

    email_dict = dict(
        subject="Job Application",
        content="I am interested in applying for the software engineer position...",
        portfolio_links=[link_dict],
        best_regards="Best regards, Rodrigo Baron",
    )
    with pytest.raises(ValueError):
        Email.model_validate(email_dict, context={"links": portfolio_links})


def test_get_email_valid(mocker):
    llm_mock = mocker.patch("llm.LLM", return_value=MagicMock())
    llm_mock.structured_complete.return_value = MagicMock()

    job_info = JobInfo(
        title="Software Engineer",
        description="We are looking for a skilled software engineer...",
        role="Software Engineer",
        experience="2-3 years",
        skills=["Python", "Django", "SQL"],
    )
    user_info = {"person": "Rodrigo", "company": "Baron"}
    link_list = [
        {
            "name": "Rodrigo",
            "role": "Web Developer",
            "link": "https://example.com/rodrigo-portfolio",
        }
    ]

    _ = get_email(job_info, llm_mock, user_info, link_list)
    llm_mock.structured_complete.assert_called_once()


def test_get_job_valid(mocker):
    llm_mock = mocker.patch("llm.LLM", return_value=MagicMock())
    llm_mock.structured_complete.return_value = MagicMock()

    scrapper_mock = mocker.patch("scrapper.BaseJobScrapper", return_value=MagicMock())
    scrapper_mock.extract.return_value = MagicMock(), MagicMock()

    url = "https://example.com/job-posting"
    _ = get_job(url, llm_mock, scrapper_mock)

    scrapper_mock.extract.assert_called_once()
    llm_mock.structured_complete.assert_called_once()
