import scrapy
from scrapy import Request
from scrapy_playwright.page import PageMethod

class InfiscrollspiderSpider(scrapy.Spider):
    name = "infiscrollspider"

    def start_requests(self):
        yield scrapy.Request("https://quotes.toscrape.com/scroll" , meta={
            'playwright' : True,
            'playwright_page_methods': [
                PageMethod('evaluate', 'for (let i = 0; i < 8; i++) setTimeout(() => window.scrollTo(0, document.body.scrollHeight), i * 3000);'),
                PageMethod("wait_for_timeout", 15000)
            ]
        })


    async def parse(self, response):
        quotes = response.css("div.quotes div.quote")

        for quote in quotes:
            yield {
                'quote': quote.css("span.text::text").get(),
                'author': quote.css("small.author::text").get(),
                'tags': [quotee for quotee in quote.css("div.tags a.tag::text").getall()]
            }

