from datetime import datetime, timedelta

import scrapy
from pytz import timezone

TIMEZONE = "Asia/Taipei"
CATEGORIES = {
    "headline": "要聞",
    "entertainment": "娛樂",
    "international": "國際",
    "finance": "財經",
    "lifestyle": "副刊",
    "sports": "體育",
    "property": "地產",
    "forum": "論壇",
}


class AppleDailySpider(scrapy.Spider):
    name = "appledaily"
    allowed_domains = ["tw.appledaily.com"]
    metadata = {  # Custom, used in pipeline
        "category": "News",
        "copyright": "© 2020 APPLE ONLINE All rights reserved. 蘋果新聞網 版權所有 不得轉載",
        "description": "提供全面新聞資訊、即時分析，全天候報道本地及全球新聞。",
        "image": "https://img.appledaily.com.tw/appledaily/images/fbshare/appledaily_fb_600x315.png",
        "language": "zh-tw",
        "link": "https://tw.appledaily.com",
        "title": "蘋果新聞網",
    }

    def __init__(self, date=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if date is None:
            self.start_urls = ["https://tw.appledaily.com/archive/"]
            self.crawl_one_more_page = True
            self.file_name = "appledaily"
        else:
            self.start_urls = [f"https://tw.appledaily.com/archive/{date}/"]
            self.crawl_one_more_page = False
            self.file_name = f"appledaily_{date}"  # Custom, used in pipeline

    def parse(self, response, **kwargs):
        news_links = response.xpath("//*[@id='section-body']/div/a")
        yield from response.follow_all(news_links, self.parse_news)
        if self.crawl_one_more_page:
            one_day_before = (
                datetime.strptime(
                    response.xpath(
                        "//*[@id='section-body']/div[2]/div[2]/span/text()"
                    ).get(),
                    "%Y.%m.%d",
                )
                - timedelta(days=1)
            )
            self.crawl_one_more_page = False
            yield scrapy.Request(
                f"https://tw.appledaily.com/archive/{one_day_before.strftime('%Y%m%d')}/"
            )

    def parse_news(self, response):
        url = response.url
        context_selector = response.xpath("//*[@id='articleBody']/section[2]/p")
        for sel in context_selector:
            self.logger.info(
                "".join(sel.xpath("descendant-or-self::*/text()").getall())
            )
        yield {
            "url": url,
            "title": response.xpath(
                "//*[@id='article-header']/header/div/h1/span/text()"
            ).get(),
            "context": "\n".join(
                [
                    "".join(sel.xpath("descendant-or-self::*/text()").getall())
                    for sel in context_selector
                ]
            ),
            "author": context_selector.re_first(r"【(.*)】"),
            "category": CATEGORIES.get(url.split("/")[-4]),
            "id": url.split("/")[-2],
            "timestamp": datetime.strptime(
                response.xpath("//*[@id='article-header']/div/div/text()").getall()[1],
                "%Y/%m/%d %H:%M",
            ).astimezone(timezone(TIMEZONE)),
            "third_party": context_selector.re_first(r"本文由(.*)提供"),
            "subtitle": response.xpath(
                "//*[@id='article-header']/header/p/span/text()"
            ).get(),
        }
