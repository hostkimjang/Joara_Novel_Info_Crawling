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

async def get_novel_list(session, nove_list):
    end = False
    for num in range(1, end_num):
        url = f"https://api.joara.com/v1/book/list.joa?api_key=mw_8ba234e7801ba288554ca07ae44c7&ver=2.6.3&device=mw&deviceuid=*&devicetoken=mw&store=&orderby=redate&offset=20&page={num}&class="
        try:
            while True:
                async with session.get(url, headers=headers) as res:
                    if res.status == 429:
                        # 대기시간을 무작위로 설정한 후 재시도
                        wait_time = random.randint(5, 10)  # 예: 5~10초 대기
                        print(f"유료 신규베스트 순회{i}회 오류")
                        print(f"HTTP 오류 429: 대기 후 재시도 ({wait_time}초 대기)")
                        await asyncio.sleep(wait_time)
                        continue  # 현재 페이지 재시도
                    elif res.status != 200:
                        print(f"HTTP 오류: {res.status}")
                        break  # 오류가 발생한 경우 현재 페이지를 스킵하고 다음 페이지로 이동
                    print(f"페이지 순회 {num}회")
                    page = await res.json()
                    page = page['books']
                    if not page:
                        print("최대 페이지 도달")
                        end = True
                        return end
                        break
                    else:
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
                            nove_list.append(novel_info)
                        break
        except aiohttp.ClientError as e:
            print(f"{url}에서 데이터를 가져오는 중 오류 발생: {e}")
            print(f"현재 페이지: {num}")


async def main_async():
    async with aiohttp.ClientSession() as session:
        await get_novel_list(session, novel_list)

end_num = 10
novel_list = []
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(main_async())
loop.close()
store_info(novel_list)