import json
import pprint

def store_info(info_list):
    with open("Joara_novel_info.json", "w", encoding="utf-8") as f:
        novel_data = []
        for info in info_list:
            novel_dict = {
                "platform": info.platform,
                "title": info.title,
                "info": info.info,
                "author_id": info.author_id,
                "author": info.author,
                "tag": info.tag,
                "keyword": info.keyword,
                "chapter": info.chapter,
                "view": info.view,
                "like": info.like,
                "favorite": info.favorite,
                "thumbnail": info.thumbnail,
                "finish_state": info.finish_state,
                "is_finish": info.is_finish,
                "createdDate": info.createdDate,
                "updatedDate": info.updatedDate,
                "id": info.id,
                "adult": info.adult
            }
            novel_data.append(novel_dict)
        json.dump(novel_data, f, ensure_ascii=False, indent=4)
        count = len(info_list)
        print(f"총 {count}개의 데이터를 저장하였습니다.")
        print("store is done!")