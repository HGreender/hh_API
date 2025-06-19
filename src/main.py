import time

import httpx
import asyncio
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr

TIMEOUT = httpx.Timeout(15.0)

app = FastAPI()


@app.get("/hello")
async def hello(name: str):
    return {"message": f"Hello, {name}!"}


@app.get("/hello/{name}")
async def hello_with_name(name: str):
    return {"message": f"Hi, {name}!"}


@app.get("/slow")
async def slow_endpoint(seconds: int = 10):
    start = time.time()
    await asyncio.sleep(seconds)
    end = time.time()
    return {
        "message": f"Проспал {seconds} секунд",
        "duration": round(end - start, 2)
    }


@app.get("/slow_loop")
async def slow_endpoint(count: int = 500000000):
    await asyncio.get_running_loop().run_in_executor(None, loop_sleep, count)
    return {
        "message": f"прошел {count} "
    }


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


class User(BaseModel):
    name: str
    age: int
    email: EmailStr


@app.post("/create_user")
async def create_user(user: User):
    return {"message": f"{user.name} | {user.age} y.o. | {user.email}, "}


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


def loop_sleep(count):
    for i in range(count):
        pass
