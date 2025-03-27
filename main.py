import os
import pprint
import time
import datetime
import random
import asyncio
import aiohttp
from dotenv import load_dotenv

from DB_processing import store_db
from info import set_novel_info
from store import store_info, store_info_end

#https://api.joara.com/v1/book/list.joa?api_key=mw_8ba234e7801ba288554ca07ae44c7&ver=3.6&device=mw&deviceuid=*&devicetoken=mw&store=&orderby=redate&offset=20&page=1&class=
#최신작품 전체

headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G975N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.210 Mobile Safari/537.36"
}

#최신
#url = f"https://api.joara.com/v1/book/list.joa?api_key=mw_8ba234e7801ba288554ca07ae44c7&ver=3.6&device=mw&deviceuid=*&devicetoken=mw&store=&orderby=redate&offset=20&page={num}&class="
#완결
#url = f"https://api.joara.com/v1/book/list.joa?api_key=mw_8ba234e7801ba288554ca07ae44c7&ver=3.6&device=mw&deviceuid=*&devicetoken=mw&store=finish&orderby=redate&offset=20&page={num}"

#검색 api
#url = f"https://api.joara.com/v2/search/query?api_key=mw_8ba234e7801ba288554ca07ae44c7&ver=3.2.0&device=mw&deviceuid=*&devicetoken=mw&query=%22%22&page=1&offset=100&store=all&target=all&orderby=redate

#전체
#https://api.joara.com/v2/book/total_book?api_key=mw_8ba234e7801ba288554ca07ae44c7&ver=3.2.0&device=mw&deviceuid=8ca8d6ba6cba29fffd0be4f18cb0df2a9626fd3c4a772b46d0fe79d3dd0ba7fc&devicetoken=mw&gnb_idx=2&category=1%2C2%2C3%2C25%2C4%2C12%2C21%2C19%2C7%2C8&age_constrict=all&store=all&orderby=redate&page=2&offset=20


MAX_CONCURRENT_REQUESTS = 10


async def fetch_novel(session, url, novel_list, sem, end_event):
    if end_event.is_set():
        return
    async with sem:
        if end_event.is_set():
            return
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
                    if not page:
                        print("더이상 books 가 존재 하지 않습니다.")
                        end_event.set()  # 페이지가 비어있으면 종료 이벤트 설정
                    else:
                        for i in page:
                            url = f"https://www.joara.com/book/{i['book_code']}"
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
                                                        locate=url,
                                                        adult=i['is_adult'])
                            novel_list.append(novel_info)
                    print(f"페이지 순회 완료 {url}")
        except aiohttp.ClientError as e:
            print(f"{url}에서 데이터를 가져오는 중 오류 발생: {e}")

async def fetch_novel_end(session, url, novel_list, sem, end_event):
    if end_event.is_set():
        return
    async with sem:
        if end_event.is_set():
            return
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
                    page = page['data']['list']
                    if not page:
                        print("더이상 list 가 존재 하지 않습니다.")
                        end_event.set()  # 페이지가 비어있으면 종료 이벤트 설정
                    else:
                        for i in page:
                            url = f"https://www.joara.com/book/{i['book_code']}"
                            novel_info = set_novel_info(platform="Joara",
                                                        title=i['subject'],
                                                        info=i['intro'].replace("\n", "").replace("\r", ""),
                                                        author_id="not_ready_author_id",
                                                        author=i['member_name'],
                                                        tag=i['category_name'],
                                                        keyword=i['keyword'],
                                                        chapter=i['total_chapter_count'],
                                                        view=i['page_read'],
                                                        like=i['recommend_count'],
                                                        favorite=i['favorite_count'],
                                                        thumbnail=i['cover'],
                                                        finish_state=i['chkfinish'],
                                                        is_finish="not_ready_is_finish",
                                                        createdDate=i['first_regist_datetime'],
                                                        updatedDate=i['last_regist_datetime'],
                                                        id=i['book_code'],
                                                        locate=url,
                                                        adult=i['chkadult'])
                            novel_list.append(novel_info)
                    print(f"페이지 순회 완료 {url}")
        except aiohttp.ClientError as e:
            print(f"{url}에서 데이터를 가져오는 중 오류 발생: {e}")

async def get_novel_list(session, novel_list, end_num, end_event):
    sem = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    tasks = []
    for num in range(1, end_num):
        if end_event.is_set():  # 종료 이벤트가 설정되면 루프 종료
            break
        url = f"https://api.joara.com/v2/search/query?api_key=mw_8ba234e7801ba288554ca07ae44c7&ver=3.2.0&device=mw&deviceuid=*&devicetoken=mw&query=%22%22&page={num}&offset=100&store=all&target=all&orderby=redate"
        tasks.append(fetch_novel(session, url, novel_list, sem, end_event))

    await asyncio.gather(*tasks)

async def main_async():
    start = time.time()
    end_num = 1000000
    novel_list = []
    end_event = asyncio.Event()  # 종료 이벤트를 나타내는 Event 객체 생성

    async with aiohttp.ClientSession() as session:
        await get_novel_list(session, novel_list, end_num, end_event)

    # 종료 이벤트를 확인하여 작업이 완료되었음을 판단할 수 있음
    store_info(novel_list)
    end = time.time()
    sec = (end - start)
    result = datetime.timedelta(seconds=sec)
    if end_event.is_set():
        print("데이터 수집 완료")

    print(f"총 크롤링 개수: {len(novel_list)}")
    print(f"크롤러 동작 시간 : {result}")

async def main_async_end():
    start = time.time()
    end_num = 10000
    novel_list = []
    end_event = asyncio.Event()  # 종료 이벤트를 나타내는 Event 객체 생성

    async with aiohttp.ClientSession() as session:
        await get_novel_list_end(session, novel_list, end_num, end_event)

    # 종료 이벤트를 확인하여 작업이 완료되었음을 판단할 수 있음
    store_info_end(novel_list)
    end = time.time()
    sec = (end - start)
    result = datetime.timedelta(seconds=sec)
    if end_event.is_set():
        print("데이터 수집 완료")

    print(f"총 크롤링 개수: {len(novel_list)}")
    print(f"크롤러 동작 시간 : {result}")

async def get_novel_list_end(session, novel_list, end_num, end_event):
    sem = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    tasks = []
    for num in range(1, end_num):
        if end_event.is_set():  # 종료 이벤트가 설정되면 루프 종료
            break
        url = f"https://api.joara.com/v2/book/finish_book?api_key=mw_8ba234e7801ba288554ca07ae44c7&ver=3.2.0&device=mw&deviceuid=*&devicetoken=mw&token=*&category=0&store=all&orderby=redate&offset=100&page={num}"
        url = f"{url}&token={token}" if token else url
        tasks.append(fetch_novel_end(session, url, novel_list, sem, end_event))

    await asyncio.gather(*tasks)


async def crawl_latest_works_use_cursor(novel_list, end_num, max_retries, initial_delay):
    cursor_point = None
    previous_cursor = None
    count = 0
    all_works = []

    base_url = (
        "https://api.joara.com/v2/book/latest_book?"
        "api_key=mw_8ba234e7801ba288554ca07ae44c7&ver=3.2.0&device=mw"
        "&deviceuid=*&devicetoken=mw&category=0&store=all&orderby=redate"
        "&offset=100&page=1&use_cursor_pagination=y"
    )

    async with aiohttp.ClientSession() as session:
        for i in range(0, end_num):
            # 커서가 있으면 URL에 추가
            url = f"{base_url}&cursor_point={cursor_point}" if cursor_point else base_url
            url = f"{url}&token={token}" if token else url

            # 재시도 로직 구현
            retries = 0
            success = False
            while retries <= max_retries and not success:
                try:
                    # 첫 번째 시도가 아니면 지수 백오프로 대기
                    if retries > 0:
                        delay = initial_delay * (2 ** (retries - 1))
                        print(f"재시도 {retries}/{max_retries} - {delay}초 후 재시도합니다...")
                        await asyncio.sleep(delay)

                    async with session.get(url, timeout=30) as response:
                        if response.status == 200:
                            res = await response.json()

                            # 응답에 cursor_point가 있고 비어있지 않은지 확인
                            if 'cursor_point' not in res or not res['cursor_point']:
                                print(f"응답에 cursor_point가 없거나 비어 있습니다 - 재시도 {retries + 1}/{max_retries}")
                                retries += 1
                                if retries > max_retries:
                                    raise Exception(f"최대 재시도 횟수 초과 (cursor_point 오류)")
                                await asyncio.sleep(3 * (retries))  # 서버 부하 문제일 수 있으므로 대기 시간 추가
                                continue

                            # 필수 데이터가 있는지 확인
                            if 'data' not in res or 'list' not in res['data']:
                                print(f"응답에 필수 데이터가 없습니다 - 재시도 {retries + 1}/{max_retries}")
                                retries += 1
                                if retries > max_retries:
                                    raise Exception(f"최대 재시도 횟수 초과 (응답 데이터 오류)")
                                await asyncio.sleep(3 * (retries))
                                continue

                            success = True

                        elif response.status == 429:  # Too Many Requests
                            print(f"Rate limit 발생 (429) - 재시도 {retries + 1}/{max_retries}")
                            retries += 1
                            if retries > max_retries:
                                raise Exception(f"최대 재시도 횟수 초과 (429 에러)")
                            await asyncio.sleep(5 * (retries))
                            continue
                        else:
                            print(f"HTTP 오류: {response.status} - 재시도 {retries + 1}/{max_retries}")
                            retries += 1
                            if retries > max_retries:
                                raise Exception(f"최대 재시도 횟수 초과 (HTTP {response.status})")
                except (aiohttp.ClientError, asyncio.TimeoutError, KeyError, ValueError) as e:
                    print(f"오류 발생: {e} - 재시도 {retries + 1}/{max_retries}")
                    retries += 1
                    if retries > max_retries:
                        raise Exception(f"최대 재시도 횟수 초과: {e}")

            # 재시도 최대치를 초과하여 실패한 경우
            if not success:
                print(f"페이지 {count}에서 데이터를 가져오는데 실패했습니다. 크롤링을 중단합니다.")
                break

            # 성공적으로 데이터를 가져온 경우
            works = res['data']['list']
            all_works.extend(works)

            # 다음 커서 갱신 (이미 유효성 검사를 통과함)
            new_cursor = res['cursor_point']

            for work in works:
                url = f"https://www.joara.com/book/{work['book_code']}"
                novel_info = set_novel_info(platform="Joara",
                                            title=work['subject'],
                                            info=work['intro'].replace("\n", "").replace("\r", ""),
                                            author_id="not_ready_author_id",
                                            author=work['member_name'],
                                            tag=work['category_name'],
                                            keyword=work['keyword'],
                                            chapter=work['total_chapter_count'],
                                            view=work['page_read'],
                                            like=work['recommend_count'],
                                            favorite=work['favorite_count'],
                                            thumbnail=work['cover'],
                                            finish_state=work['chkfinish'],
                                            is_finish="not_ready_is_finish",
                                            createdDate=work['first_regist_datetime'],
                                            updatedDate=work['last_regist_datetime'],
                                            id=work['book_code'],
                                            locate=url,
                                            adult=work['chkadult'])
                novel_list.append(novel_info)

            pprint.pprint(f"다음 커서: {new_cursor}")
            pprint.pprint(f"현재까지 크롤링한 작품 수: {len(all_works)}")
            pprint.pprint(f"총 작품수: {res['total_cnt']}")
            pprint.pprint(f"페이지 순회 {count}")
            count += 1

            # 종료 조건: 커서가 없거나 작품 목록이 비어 있거나, 커서가 반복되면 중단
            if not new_cursor or not works or (new_cursor == previous_cursor):
                break

            previous_cursor = cursor_point
            cursor_point = new_cursor

    time.sleep(30)
    return all_works


async def main():
    end_num = 3000
    novel_list = []
    pprint.pprint("크롤링 시작")
    try:
        works = await crawl_latest_works_use_cursor(novel_list, end_num, max_retries=10, initial_delay=2)
        print(f"총 {len(works)}개의 작품을 크롤링했습니다.")
    except Exception as e:
        print(f"크롤링 중 오류 발생: {e}")

    store_info(novel_list)


if __name__ == "__main__":
    load_dotenv()
    token = os.environ.get("TOKEN")
    if token is None:
        print("토큰이 없습니다. 프로그램을 종료합니다.")
        exit(1)
    pprint.pprint("토큰 확인 완료")
    start = time.time()
    asyncio.run(main())
    asyncio.run(main_async_end())
    store_db()
    # 미사용 asyncio.run(main_async())
    end = time.time()
    pprint.pprint(f"총 소요 시간: {end - start:.2f}초")