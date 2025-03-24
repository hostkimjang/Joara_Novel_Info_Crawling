class NovelInfo:
    def __init__(self, platform, title, info, author_id, author, tag, keyword, chapter, view, like, favorite, thumbnail, finish_state, is_finish, createdDate, updatedDate, id, locate, adult):
        self.platform = platform
        self.title = title
        self.info = info
        self.author_id = author_id
        self.author = author
        self.tag = tag
        self.keyword = keyword
        self.chapter = chapter
        self.view = view
        self.like = like
        self.favorite = favorite
        self.thumbnail = thumbnail
        self.finish_state = finish_state
        self.is_finish = is_finish
        self.createdDate = createdDate
        self.updatedDate = updatedDate
        self.id = id
        self.locate = locate
        self.adult = adult

    def __str__(self):
        return f"platform: {self.platform}, " \
               f"title: {self.title}, " \
               f"info: {self.info}, " \
               f"author_id: {self.author_id}, " \
               f"author: {self.author}, " \
               f"tag: {self.tag}, " \
               f"keyword: {self.keyword}, " \
               f"chapter: {self.chapter}, " \
               f"view: {self.view}, " \
               f"like: {self.like}, " \
               f"favorite: {self.favorite}, " \
               f"thumbnail: {self.thumbnail}, " \
               f"finish_state: {self.finish_state}, " \
               f"is_finish: {self.is_finish}, " \
               f"createdDate: {self.createdDate}, " \
               f"updatedDate: {self.updatedDate}, " \
               f"id: {self.id}, " \
               f"locate: {self.locate}, " \
               f"adult: {self.adult}"

    def to_dict(self):
        return {
            "platform": self.platform,
            "title": self.title,
            "info": self.info,
            "author_id": self.author_id,
            "author": self.author,
            "tag": self.tag,
            "keyword": self.keyword,
            "chapter": self.chapter,
            "view": self.view,
            "like": self.like,
            "favorite": self.favorite,
            "thumbnail": self.thumbnail,
            "finish_state": self.finish_state,
            "is_finish": self.is_finish,
            "createdDate": self.createdDate,
            "updatedDate": self.updatedDate,
            "id": self.id,
            "locate": self.locate,
            "adult": self.adult
        }

def set_novel_info(platform, title, info, author_id, author, tag, keyword, chapter, view, like, favorite, thumbnail, finish_state, is_finish, createdDate, updatedDate, id, locate, adult):
    # print("-" * 100)
    # print(f"platform: {platform}")
    # print(f"title: {title}")
    # print(f"info: {info}")
    # print(f"author_id: {author_id}")
    # print(f"author: {author}")
    # print(f"tag: {tag}")
    # print(f"keyword: {keyword}")
    # print(f"chapter: {chapter}")
    # print(f"view: {view}")
    # print(f"like: {like}")
    # print(f"favorite: {favorite}")
    # print(f"thumbnail: {thumbnail}")
    # print(f"finish_state: {finish_state}")
    # print(f"is_finish: {is_finish}")
    # print(f"createdDate: {createdDate}")
    # print(f"updatedDate: {updatedDate}")
    # print(f"id: {id}")
    # print(f"locate: {locate}")
    # print(f"adult: {adult}")
    # print("-" * 100)
    return NovelInfo(platform, title, info, author_id, author, tag, keyword, chapter, view, like, favorite, thumbnail, finish_state, is_finish, createdDate, updatedDate, id, locate, adult)
