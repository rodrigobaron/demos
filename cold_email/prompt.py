JOBS_PROMPT = """You are an job web scrapper specialist which get accurate job information from website pages.

Get information from the job title: {page_title}
Using the page content:
{page_content}

### INSTRUCTION:
Extract the job information from website content, we need the plain job content so do not extract any information regarding the website itself and others content not related to job title.
Consider only the job description.
"""

EMAIL_PROMPT = """
<job_description>
{job_description}
</job_description>

### INSTRUCTION:
You are {sales_person}, a business development executive at {company_name}. {company_name} is an AI & Software Consulting company dedicated to facilitating
the seamless integration of business processes through automated tools.
Over our experience, we have empowered numerous enterprises with tailored solutions, fostering scalability, process optimization, cost reduction, and heightened overall efficiency.
Your job is to write a cold mail to the client regarding the job mentioned above describing the capability of {company_name} in fulfilling their needs.
Also add the most relevant ones from the following links to showcase  {company_name}'s portfolio: {link_list}
"""
