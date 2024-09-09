from pydantic import BaseModel, Field, model_validator, FieldValidationInfo
from prompt import JOBS_PROMPT, EMAIL_PROMPT
from typing import List


class JobInfo(BaseModel):
    title: str = Field(..., description="Short text to for job title, ", required=True)
    description: str = Field(..., description="Detailed job description", required=True)
    role: str
    experience: str
    skills: List[str]

    @model_validator(mode="after")
    def validate_infos(self, info: FieldValidationInfo) -> "JobInfo":
        if info.context is None:
            print("No context found, skipping validation")
            return self

        context = info.context.get("text_chunk", None).lower()

        if context:
            # Validate Role
            if self.role.lower() not in context:
                raise ValueError(f"Role `{self.role}` not found in text")
            # Validate Role
            if self.experience.lower() not in context:
                raise ValueError(f"Experience `{self.experience}` not found in text")
            # Validate skills
            for skill in self.skills:
                if skill.lower() not in context:
                    raise ValueError(f"Skill `{skill}` not found in text")

        return self


class PortifolioLink(BaseModel):
    name: str
    link: str


class Email(BaseModel):
    subject: str
    content: str
    portfolio_links: list[PortifolioLink]

    @model_validator(mode="after")
    def validate_infos(self, info: FieldValidationInfo) -> "JobInfo":
        if info.context is None:
            print("No context found, skipping validation")
            return self

        context_links = info.context.get("links", None)

        if context_links:
            # Validate links
            for link in self.portfolio_links:
                if link.link not in context_links:
                    raise ValueError(
                        f"Link `{link.link}` not found in the reference links"
                    )
        return self


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
