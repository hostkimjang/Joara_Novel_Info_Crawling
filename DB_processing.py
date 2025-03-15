import sqlite3
import json
import os
import time
from datetime import datetime
from pprint import pprint


def load_novel_data():
    # JSON 파일 이름을 실제 파일명으로 변경하세요.
    with open('joara_novel_info.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        pprint(f"총 {len(data)}개 데이터 로드 완료")
        return data


def change_log(result):
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    log_directory = 'DB_Processing_Log'
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    log_file_path = os.path.join(log_directory, f'{timestamp}-log.json')

    def datetime_convert(obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        raise TypeError(f'Type {type(obj)} not supported.')

    with open(log_file_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4, default=datetime_convert)


def store_db():
    novel_list = load_novel_data()
    conn = sqlite3.connect('joara_novel.db')
    cur = conn.cursor()

    # JSON 구조에 맞춘 테이블 생성 (필요한 필드가 있으면 추가)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS novel (
            id INTEGER PRIMARY KEY,
            platform TEXT,
            title TEXT,
            info TEXT,
            author TEXT,
            author_id TEXT,
            tag TEXT,
            keyword TEXT,
            chapter INTEGER,
            view INTEGER,
            like INTEGER,
            favorite INTEGER,
            thumbnail TEXT,
            finish_state TEXT,
            is_finish TEXT,
            createdDate DATETIME,
            updatedDate DATETIME,
            adult TEXT,
            crawl_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    count = 1
    total = []
    start_time = time.time()
    dt = datetime.now()

    for novel in novel_list:
        if novel is None:
            print("데이터가 없습니다 또는 삭제, 작업이 정상으로 완료되지 않음.")
            continue

        # "createdDate"와 "updatedDate"를 datetime 객체로 변환한 후, 지정 포맷의 문자열로 변환
        try:
            novel["createdDate"] = datetime.strptime(novel["createdDate"], "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            print(f"Error converting createdDate for novel {novel.get('id')}: {e}")
            novel["createdDate"] = novel.get("createdDate")  # 변환 실패 시 원본 사용

        try:
            novel["updatedDate"] = datetime.strptime(novel["updatedDate"], "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            print(f"Error converting updatedDate for novel {novel.get('id')}: {e}")
            novel["updatedDate"] = novel.get("updatedDate")  # 변환 실패 시 원본 사용

        # id를 정수형으로 변환 (만약 id가 숫자로 되어 있다면)
        try:
            novel_id = int(novel["id"])
        except ValueError:
            novel_id = novel["id"]

        # 현재 크롤링 시간을 추가합니다.
        novel["crawl_timestamp"] = dt

        # keyword가 리스트인 경우, 콤마로 구분된 문자열로 변환
        if isinstance(novel.get("keyword"), list):
            novel["keyword"] = ", ".join(novel["keyword"])

        # 기존 레코드 확인 (id를 기준으로)
        existing_record = cur.execute("SELECT * FROM novel WHERE id=?", (novel_id,)).fetchone()

        if existing_record:
            print(f"{novel_id}는 이미 존재합니다. 레코드를 업데이트하거나 무시합니다.")
            changes = {}
            # 테이블 컬럼 순서는 아래와 같습니다:
            # 0: id, 1: platform, 2: title, 3: info, 4: author, 5: author_id, 6: tag,
            # 7: keyword, 8: chapter, 9: view, 10: like, 11: favorite, 12: thumbnail,
            # 13: finish_state, 14: is_finish, 15: createdDate, 16: updatedDate, 17: adult,
            # 18: crawl_timestamp
            fields = [
                ("platform", 1), ("title", 2), ("info", 3), ("author", 4), ("author_id", 5),
                ("tag", 6), ("keyword", 7), ("chapter", 8), ("view", 9), ("like", 10),
                ("favorite", 11), ("thumbnail", 12), ("finish_state", 13), ("is_finish", 14),
                ("createdDate", 15), ("updatedDate", 16), ("adult", 17)
            ]
            for field, index in fields:
                # 문자열 비교를 위해 str()로 변환합니다.
                if str(existing_record[index]) != str(novel.get(field, "")):
                    changes[field] = {"before": existing_record[index], "after": novel.get(field, "")}

            if changes:
                print(f"변경된 사항: {changes}")
                total.append({"ID": novel_id, "Changes": changes})
                cur.execute("""
                    UPDATE novel
                    SET platform=?, title=?, info=?, author=?, author_id=?, tag=?, keyword=?,
                        chapter=?, view=?, like=?, favorite=?, thumbnail=?, finish_state=?,
                        is_finish=?, createdDate=?, updatedDate=?, adult=?, crawl_timestamp=?
                    WHERE id=?
                """, (
                    novel.get("platform"), novel.get("title"), novel.get("info"), novel.get("author"),
                    novel.get("author_id"), novel.get("tag"), novel.get("keyword"),
                    novel.get("chapter"), novel.get("view"), novel.get("like"), novel.get("favorite"),
                    novel.get("thumbnail"), novel.get("finish_state"), novel.get("is_finish"),
                    novel.get("createdDate"), novel.get("updatedDate"), novel.get("adult"),
                    novel.get("crawl_timestamp"), novel_id
                ))
        else:
            print(f"ID:{novel_id}는 존재하지 않습니다. 새 레코드를 삽입합니다.")
            cur.execute("""
                INSERT INTO novel 
                (id, platform, title, info, author, author_id, tag, keyword, chapter, view, like, favorite,
                 thumbnail, finish_state, is_finish, createdDate, updatedDate, adult, crawl_timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                novel_id, novel.get("platform"), novel.get("title"), novel.get("info"), novel.get("author"),
                novel.get("author_id"), novel.get("tag"), novel.get("keyword"), novel.get("chapter"),
                novel.get("view"), novel.get("like"), novel.get("favorite"), novel.get("thumbnail"),
                novel.get("finish_state"), novel.get("is_finish"), novel.get("createdDate"),
                novel.get("updatedDate"), novel.get("adult"), novel.get("crawl_timestamp")
            ))

        print(f"{count}/{len(novel_list)}번째 데이터 저장 완료")
        count += 1

    end_time = time.time()
    print(f"총 {end_time - start_time:.2f}초 소요")
    print("데이터 저장 완료")

    conn.commit()
    conn.close()

    if total:
        change_log(total)


if __name__ == '__main__':
    store_db()
