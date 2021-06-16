from newsapi import NewsApiClient


class News:
    APIKEY = '4263d99c28304105ac95ed7c4514299e'

    def __init__(self):
        self.newsapi = NewsApiClient(News.APIKEY)

    def get_news(self):
        top_headlines = self.newsapi.get_top_headlines(q='', sources='bbc-news,the-verge')
        head = top_headlines['articles']
        headlines = []
        count = 0

        for i in head:
            if count > 4:
                break
            headlines.append(i)
            count += 1

        return headlines


n = News()
print(n.get_news())
