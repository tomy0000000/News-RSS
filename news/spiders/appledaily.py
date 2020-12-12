import scrapy


class AppleDailySpider(scrapy.Spider):
    name = "appledaily"
    allowed_domains = ["tw.appledaily.com"]
    start_urls = ["https://tw.appledaily.com/archive/20201203/"]

    def parse(self, response, **kwargs):

        news_links = response.xpath("//*[@id='section-body']/div/a")
        # print(news_links)
        yield from response.follow_all(news_links, self.parse_news)

        # page = response.url.split("/")[-2]
        # filename = f"entry-list-{page}.html"
        # with open(filename, "wb") as f:
        #     f.write(response.body)
        # self.log(f"Saved file {filename}")

    def parse_news(self, response):
        # TODO: only fetch first paragraph
        # TODO: Ensure ASCII false on JSON
        yield {
            "title": response.xpath(
                "//*[@id='article-header']/header/div/h1/span/text()"
            ).get(),
            "subtitle": response.xpath(
                "//*[@id='article-header']/header/p/span/text()"
            ).get(),
            "timestamp": response.xpath(
                "//*[@id='article-header']/div/div/text()"
            ).get(),
            "context": response.xpath(
                "//*[@id='articleBody']/section[2]/p/text()"
            ).get(),
        }
