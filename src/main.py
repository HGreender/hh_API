from datetime import datetime
from typing import List, Optional

import re
import httpx
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

MAX_PAGES = 100
TIMEOUT = httpx.Timeout(15.0)
GRADE_KEYWORDS = {
    r'\b(junior|джуниор|младший)\b': 'Junior',
    r'\b(middle|мидл|средний)\b': 'Middle',
    r'\b(senior|сеньор|старший)\b': 'Senior',
    r'\b(lead|ведущий|лид)\b': 'Lead',
    r'\b(principal|главный|эксперт)\b': 'Expert',
    r'\b(стажер|intern|практикант|trainee)\b': 'Intern'
}


class VacancyResponse(BaseModel):
    name: str
    grade: Optional[str]
    url: str
    publish_date: str


class VacanciesResponse(BaseModel):
    vacancies_name_grade_url_date: List[VacancyResponse]


@app.get("/hh_vacancies/{job_name}", response_model=VacanciesResponse)
async def get_hh_vacancies(job_name: str, pages: int = 20):
    pages = min(pages, MAX_PAGES)

    headers = {"User-Agent": "Mozilla/5.0"}
    url = f"https://api.hh.ru/vacancies" \
          f"?text={job_name}" \
          f"&search_field=name" \
          f"&per_page={pages}"
    try:
        vacancies_data = await fetch_vacancies(url=url, headers=headers)
        name_grade_url_date = extract_name_grade_url_date(vacancies_data)

        return {"vacancies_name_grade_url_date": name_grade_url_date}
    except httpx.RequestError as e:
        return {"error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


def extract_name_grade_url_date(data):
    name_and_link = [
        {
            "name": item.get("name", ""),
            "grade": extract_grade(item.get("name", "")),
            "url": item.get("alternate_url", ""),
            "publish_date": '.'.join(item.get("published_at", "").strip().split('T')[0].split('-')[::-1])
        }
        for item in data.get("items", [])
    ]

    return sorted(name_and_link, key=parse_date, reverse=True)


async def fetch_vacancies(url, headers):
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(url, headers=headers)

        return response.json()


def parse_date(item):
    return datetime.strptime(item["publish_date"], "%d.%m.%Y")


def extract_grade(name: str) -> Optional[str]:
    name_lower = name.lower()
    for pattern, grade in GRADE_KEYWORDS.items():
        if re.search(pattern, name_lower, re.IGNORECASE):
            return grade
    return None

