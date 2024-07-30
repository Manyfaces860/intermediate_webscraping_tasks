
import scrapy
from scrapy import Request
from scrapy_playwright.page import PageMethod

class HeavyspiderSpider(scrapy.Spider):
    name = "heavyspider"

    def start_requests(self):

        yield scrapy.Request('https://quotes.toscrape.com/js-delayed/', meta={
            'playwright' : True,
            'playwright_page_methods': [
                PageMethod('wait_for_selector', 'div.quote')
            ]
        })


    async def parse(self, response):
        quotes = response.css("div#quotesPlaceholder div.quote")

        for quote in quotes:
            yield {
                'quote': quote.css("span.text::text").get(),
                'author': quote.css("small.author::text").get(),
                'tags' : [quotee for quotee in quote.css("div.tags a.tag::text").getall()]
            }

        next_page = response.css("li.next a::attr(href)").get()

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse, meta={
            'playwright' : True,
            'playwright_page_methods': [
                PageMethod('wait_for_selector', 'div.quote')
            ]
        })