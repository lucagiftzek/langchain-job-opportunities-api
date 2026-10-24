"""Job Opportunities API toolkit for LangChain.

Live job postings taken from employers' own career pages, their ATS feeds and
official government feeds. No job boards, no agencies, no reposts.

Get a free key (1,000 records a month, no card) at
https://jobopportunitiesapi.org/login and set JOA_API_KEY.

API docs: https://jobopportunitiesapi.org/api
"""

from __future__ import annotations

import os
from typing import Optional, Type

import requests
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool

API_BASE = "https://api.jobopportunitiesapi.org"


class JobSearchInput(BaseModel):
    """Input for searching live job postings."""

    query: str = Field(..., description="Free-text search over job titles and descriptions.")
    country: Optional[str] = Field(
        None, description="ISO 3166-1 alpha-2 country code, for example DE, GB, US."
    )
    limit: int = Field(10, description="How many postings to return, max 100.")


class JobGetInput(BaseModel):
    """Input for fetching one posting by id."""

    job_id: str = Field(..., description="The job_id returned by a previous search.")


class CompanyHiringInput(BaseModel):
    """Input for reading an employer current hiring signal."""

    slug: str = Field(..., description="The employer slug from a posting employer field.")


class ChangesInput(BaseModel):
    """Input for reading the posting change feed."""

    since: str = Field(
        ...,
        description="ISO 8601 timestamp to read changes from, for example 2026-10-24T00:00:00Z.",
    )


class _JOATool(BaseTool):
    api_key: str = ""

    def _get(self, path: str, params: dict | None = None) -> dict:
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        response = requests.get(f"{API_BASE}{path}", headers=headers, params=params, timeout=30)
        if response.status_code == 402:
            return {
                "error": "quota_exhausted",
                "message": "This key has used its monthly records. Details: "
                "https://jobopportunitiesapi.org/pricing",
            }
        if response.status_code == 401:
            return {
                "error": "unauthorized",
                "message": "Set JOA_API_KEY to a free key from "
                "https://jobopportunitiesapi.org/login",
            }
        response.raise_for_status()
        return response.json()


class JobSearchTool(_JOATool):
    """Search live job postings from employer career pages, ATS feeds and government feeds."""

    name: str = "job_search"
    description: str = (
        "Search JOA live job postings. Every row comes from an employer own career page, "
        "its ATS or an official government feed, never from job boards or agencies. "
        "Use country to narrow to one market. Results carry apply_url (the employer own "
        "apply page) and salary_published (true only when the employer printed a salary)."
    )
    args_schema: Type[BaseModel] = JobSearchInput

    def _run(self, query: str, country: Optional[str] = None, limit: int = 10) -> dict:
        params: dict = {"q": query, "limit": min(limit, 100)}
        if country:
            params["country"] = country.upper()
        return self._get("/v1/jobs", params)


class JobGetTool(_JOATool):
    """Fetch one full job posting by its job_id."""

    name: str = "job_get"
    description: str = (
        "Fetch one complete job posting by job_id, including full description, published "
        "salary fields and where each field came from."
    )
    args_schema: Type[BaseModel] = JobGetInput

    def _run(self, job_id: str) -> dict:
        return self._get(f"/v1/jobs/{job_id}")


class CompanyHiringTool(_JOATool):
    """Read one employer current hiring signal and open role count."""

    name: str = "company_hiring"
    description: str = (
        "Read an employer hiring signal: open roles, industries and recent movement. "
        "Useful for market research and for deciding which companies are actively hiring."
    )
    args_schema: Type[BaseModel] = CompanyHiringInput

    def _run(self, slug: str) -> dict:
        return self._get(f"/v1/companies/{slug}")


class ChangesTool(_JOATool):
    """Read the change feed: postings added, closed or updated since a timestamp."""

    name: str = "job_changes"
    description: str = (
        "Read JOA change feed since a given ISO 8601 timestamp: new postings, closed "
        "postings and field updates. This is how you keep a local copy in sync."
    )
    args_schema: Type[BaseModel] = ChangesInput

    def _run(self, since: str) -> dict:
        return self._get("/v1/changes", {"since": since})


def job_opportunities_api_tools(api_key: str | None = None) -> list[_JOATool]:
    """Build the JOA toolset. Reads JOA_API_KEY when no key is passed."""
    key = api_key or os.environ.get("JOA_API_KEY", "")
    return [
        JobSearchTool(api_key=key),
        JobGetTool(api_key=key),
        CompanyHiringTool(api_key=key),
        ChangesTool(api_key=key),
    ]
