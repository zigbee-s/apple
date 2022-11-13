from ast import keyword
from cProfile import run
from symbol import parameters
import requests
import json
import multiprocessing
import asyncio
import aiohttp

url = 'http://localhost:7071/api/HttpScrapper?keyword={}&url={}&taskid={}'

def get_tasks(session):
    tasks = []
    with open("tasks.txt", "r") as tasksfile:
        for task in tasksfile.readlines():
            arr = task.split(',')
            tasks.append(session.get(url.format(arr[0], arr[1], arr[2]), ssl=False))
    return tasks

async def run_tasks():
    async with aiohttp.ClientSession() as session:
        tasks = get_tasks(session)
        responses = await asyncio.gather(*tasks)

asyncio.run(run_tasks())
