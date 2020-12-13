# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsItem(scrapy.Item):
    url = scrapy.Field()  # link
    title = scrapy.Field()  # title
    context = scrapy.Field()  # description
    author = scrapy.Field()  # author
    category = scrapy.Field()  # category
    id = scrapy.Field()  # guid
    timestamp = scrapy.Field()  # pubDate
    third_party = scrapy.Field()  # source
    subtitle = scrapy.Field()
