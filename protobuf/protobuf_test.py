from news_pb2 import Article
from datetime import datetime

if __name__ == "__main__":
    a = Article()
    a.id = "An ID"
    a.title = "A Title"
    a.subtitle = "A Subtitle"
    a.publish_ts.FromDatetime(datetime.now())
    print(a)
    print(a.publish_ts.ToDatetime())
