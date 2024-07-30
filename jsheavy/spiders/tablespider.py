
import scrapy
from scrapy import Request


class TablespiderSpider(scrapy.Spider):
    name = "tablespider"

    def start_requests(self):
        yield scrapy.Request("https://quotes.toscrape.com/tableful/" , callback=self.parse)

    def parse(self, response):
        trs = response.css("tr")

        for tr in range(1, len(trs), 2):
            yield {
                "quote" : trs[tr].css("td::text").get(),
                "tags" : [quote for quote in trs[tr + 1].css("td a::text").getall()]
            }
