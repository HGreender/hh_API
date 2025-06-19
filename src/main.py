import httpx
import asyncio
from fastapi import FastAPI

TIMEOUT = httpx.Timeout(15.0)

app = FastAPI()


@app.get("/hh_vacancies/{job_name}")
async def get_hh_vacancies(job_name, pages: int = 20):
    headers = {"User-Agent": "Mozilla/5.0"}
    url = f"https://api.hh.ru/vacancies" \
          f"?text={job_name}" \
          f"&search_field=name" \
          f"&per_page={pages}"
    try:
        vacancies_data = await fetch_vacancies(url=url, headers=headers)
        links = await extract_vacancies_links(vacancies_data)
        return {"vacancies_title_and_link": links}
    except httpx.RequestError as e:
        return {"error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


async def fetch_vacancies(url, headers):
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(url, headers=headers)
        return response.json()


async def extract_vacancies_links(data):
    name_and_link = [
        [item.get("name", ""), item.get("alternate_url", "")]
        for item in data.get("items", [])
    ]
    return name_and_link
