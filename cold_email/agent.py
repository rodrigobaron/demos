from pydantic import BaseModel, Field, model_validator, FieldValidationInfo
from pydantic import ValidationInfo, BaseModel, field_validator

from prompt import JOBS_PROMPT, EMAIL_PROMPT
from typing import List


class JobInfo(BaseModel):
    title: str = Field(..., description="Short text to for job title, ", required=True)
    description: str = Field(..., description="Detailed job description", required=True)
    role: str
    experience: str
    skills: List[str]

    @field_validator("role")
    @classmethod
    def role_exists(cls, v: str, info: ValidationInfo):
        context = info.context
        if context:
            context = context.get("text_chunk").lower()
            if v.lower() not in context:
                raise ValueError(f"Role `{v}` not found in text")
        return v

    @field_validator("experience")
    @classmethod
    def experience_exists(cls, v: str, info: ValidationInfo):
        context = info.context
        if context:
            context = context.get("text_chunk").lower()
            if v.lower() not in context:
                raise ValueError(f"Experience `{v}` not found in text")
        return v

    @field_validator("skills")
    @classmethod
    def skills_exists(cls, v: List[str], info: ValidationInfo):
        context = info.context
        if context:
            context = context.get("text_chunk").lower()
            for skill in v:
                if skill.lower() not in context:
                    raise ValueError(f"Skill `{skill}` not found in text")
        return v


class PortfolioLink(BaseModel):
    name: str = Field(..., description="Person name", required=True)
    role: str = Field(..., description="Person role", required=True)
    link: str = Field(..., description="Person portfolio link", required=True)


class Email(BaseModel):
    subject: str = Field(..., description="Email subject", required=True)
    content: str = Field(
        ...,
        description="Mail content without the ending regards, and links",
        required=True,
    )
    portfolio_links: List[PortfolioLink]
    best_regards: str

    @field_validator("portfolio_links")
    @classmethod
    def portfolio_links_exists(cls, v: List[PortfolioLink], info: ValidationInfo):
        context = info.context
        if context:
            context_links = context.get("links")
            for link in v:
                if link.link not in context_links:
                    raise ValueError(
                        f"Link `{link.link}` not found in the reference links."
                    )
        return v


def get_email(job_info, llm, user_info, link_list):
    sales_person = user_info["person"]
    company_name = user_info["company"]
    email_prompt = EMAIL_PROMPT.format(
        job_description=job_info.description,
        sales_person=sales_person,
        company_name=company_name,
        link_list=link_list,
    )

    response = llm.structured_complete(
        prompt=email_prompt,
        response_model=Email,
        validation_context={"links": [link["link"] for link in link_list]},
        max_retries=2,
        temperature=0.1,
    )
    return response


def get_job(url, llm, scrapper):
    page_title, page_content = scrapper.extract(url)
    jobs_prompt = JOBS_PROMPT.format(page_title=page_title, page_content=page_content)

    response = llm.structured_complete(
        prompt=jobs_prompt,
        response_model=JobInfo,
        validation_context={"text_chunk": page_content},
        max_retries=2,
        temperature=0.1,
    )

    return response
