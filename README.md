# langchain-job-opportunities-api

LangChain tools for [Job Opportunities API](https://jobopportunitiesapi.org): live job postings taken straight from employers' own career pages, their ATS feeds and official government feeds.

> **Disclosure:** I am the founder of Job Opportunities API. There is a paid tier. This package is MIT and free to use.

## Why

Job data is a common agent need, and it is usually wired up by scraping job boards. That breaks constantly and sits in a grey legal area. JOA is a licensed, maintained source: every posting comes from the employer, and each row reports where its fields came from.

A free key is 1,000 records a month with no card, and the statistics endpoints are keyless, so you can evaluate this before committing.

## Install

```bash
pip install langchain-job-opportunities-api
```

## Setup

Get a free key at https://jobopportunitiesapi.org/login and set it:

```bash
export JOA_API_KEY=...
```

## Usage

```python
from langchain_job_opportunities_api import job_opportunities_api_tools

tools = job_opportunities_api_tools()

# hand them to any LangChain agent
agent = create_tool_calling_agent(llm, tools, prompt)
```

## The four tools

| Tool | What it does |
|---|---|
| `job_search` | Free-text search over live postings, optional ISO country filter |
| `job_get` | One full posting by id, with provenance for every field |
| `company_hiring` | An employer's open roles and hiring signal |
| `job_changes` | The change feed since a timestamp, for keeping a local copy in sync |

## API contract

- Base URL: `https://api.jobopportunitiesapi.org`
- Auth: `Authorization: Bearer <key>`. A key with no card is fine.
- `401` when the key is missing, `402` when the monthly records are used up.

The tools map both error codes to readable output rather than raising, so an agent can recover without a stack trace.

## Honest limits

- Coverage is employer-direct, so it is not every job on the internet. It is the ones we can trace to a source.
- Salary fields are null when the employer did not publish a number. We never infer one.

## Licence

MIT for this code. The data behind the API has its own terms: https://jobopportunitiesapi.org/terms
