# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsItem(scrapy.Item):
    url = scrapy.Field()  # link, guid
    title = scrapy.Field()  # title
    summary = scrapy.Field()  # description
    context = scrapy.Field()  # description (complete raw text)
    rich_context = scrapy.Field()  # description (complete HTML)
    author = scrapy.Field()  # author
    image = scrapy.Field()  # enclosure
    category = scrapy.Field()  # category
    id = scrapy.Field()
    timestamp = scrapy.Field()  # pubDate
    third_party = scrapy.Field()  # source
    subtitle = scrapy.Field()
