from datetime import datetime
from typing import Optional, List

import uvicorn
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from chrome import find_link_last_visit_time, open_chrome_with_profile


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class BrowserInfo(BaseModel):
    profile_dir: str
    username: str
    default_name: str
    email: str


class LinkInfo(BaseModel):
    id: int
    url: str
    title: str
    visit_count: int
    last_visit_time: datetime
    last_visit_day_since_now: float


class Data(BaseModel):
    browser: BrowserInfo
    links: List[LinkInfo]


@app.get('/open/{profile_name}')
async def open(profile_name: str, url: str = Query()):
    return open_chrome_with_profile(profile_name, url)


@app.get('/')
async def root(qs: str = Query()) -> List[Data]:
    data = []

    for item in find_link_last_visit_time(qs):
        data.append(Data(browser=item['browser'], links=item['links']))

    return data


if __name__ == '__main__':
    uvicorn.run('app:app', reload=True)
