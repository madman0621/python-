class Article(object):
    def __init__(self, id, title, url, updateTime):
        self.id = id
        self.title = title
        self.url = url
        self.updateTime = updateTime


art = Article(1, 'title', 'https://xxx', 12222222)
print(art.__dict__)

