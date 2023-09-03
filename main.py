import pprint
import aiohttp
import random
import asyncio
from info import set_novel_info
from store import store_info
import re
import json

#https://api.joara.com/v1/book/list.joa?api_key=mw_8ba234e7801ba288554ca07ae44c7&ver=2.6.3&device=mw&deviceuid=*&devicetoken=mw&store=&orderby=redate&offset=20&page=1&class=
#최신작품 전체

headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G975N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.210 Mobile Safari/537.36"

}

#최신
#url = f"https://api.joara.com/v1/book/list.joa?api_key=mw_8ba234e7801ba288554ca07ae44c7&ver=2.6.3&device=mw&deviceuid=*&devicetoken=mw&store=&orderby=redate&offset=20&page={num}&class="
#완결
#url = f"https://api.joara.com/v1/book/list.joa?api_key=mw_8ba234e7801ba288554ca07ae44c7&ver=2.6.3&device=mw&deviceuid=*&devicetoken=mw&store=finish&orderby=redate&offset=20&page={num}"

MAX_CONCURRENT_REQUESTS = 5

async def fetch_novel(session, url, novel_list, sem):
    async with sem:
        try:
            async with session.get(url) as res:
                if res.status == 429:
                    wait_time = random.randint(5, 10)
                    print(f"HTTP 오류 429: 대기 후 재시도 ({wait_time}초 대기)")
                    await asyncio.sleep(wait_time)
                elif res.status == 403:
                    wait_time = random.randint(5, 10)
                    print(f"HTTP 오류 403: 대기 후 재시도 ({wait_time}초 대기)")
                    await asyncio.sleep(wait_time)
                elif res.status != 200:
                    print(f"HTTP 오류: {res.status}")
                else:
                    print(f"페이지 순회 {url}")
                    page = await res.json()
                    page = page['books']
                    for i in page:
                        novel_info = set_novel_info(platform="Joara",
                                                    title=i['subject'],
                                                    info=i['intro'].replace("\n", "").replace("\r", ""),
                                                    author_id=i['writer_id'],
                                                    author=i['writer_name'],
                                                    tag=i['category_ko_name'],
                                                    keyword=i['keyword'],
                                                    chapter=i['cnt_chapter'],
                                                    view=i['cnt_page_read'],
                                                    like=i['cnt_recom'],
                                                    favorite=i['cnt_favorite'],
                                                    thumbnail=i['book_img'],
                                                    finish_state=i['chk_finish'],
                                                    is_finish=i['is_finish'],
                                                    createdDate=i['created'],
                                                    updatedDate=i['updated'],
                                                    id=i['book_code'],
                                                    adult=i['is_adult'])
                        novel_list.append(novel_info)
                    print(f"페이지 순회 완료 {url}")
        except aiohttp.ClientError as e:
            print(f"{url}에서 데이터를 가져오는 중 오류 발생: {e}")


async def get_novel_list(session, novel_list, end_num):
    sem = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    tasks = []
    count = 1
    for num in range(1, end_num):
        url = f"https://api.joara.com/v1/book/list.joa?api_key=mw_8ba234e7801ba288554ca07ae44c7&ver=2.6.3&device=mw&deviceuid=*&devicetoken=mw&store=&orderby=redate&offset=20&page={num}&class="
        tasks.append(fetch_novel(session, url, novel_list, sem))

    await asyncio.gather(*tasks)


async def main_async():
    end_num = 1000
    novel_list = []

    async with aiohttp.ClientSession() as session:
        await get_novel_list(session, novel_list, end_num)

    # 이후 novel_list를 저장하거나 처리할 수 있음
    store_info(novel_list)

asyncio.run(main_async())