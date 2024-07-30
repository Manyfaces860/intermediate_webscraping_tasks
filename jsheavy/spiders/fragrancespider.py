import scrapy
from scrapy_playwright.page import PageMethod
import random

USER_AGENT_LIST = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:91.0) Gecko/20100101 Firefox/91.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.64',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 OPR/77.0.4054.172',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 10; SM-G973U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Mobile Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; AS; rv:11.0) like Gecko'
]

class FragrancespiderSpider(scrapy.Spider):
    name = "fragrancespider"

    custom_settings = {
        'DOWNLOAD_DELAY': 6,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'PLAYWRIGHT_LAUNCH_OPTIONS': {
            'headless': True,  # You may want to run in non-headless mode to see the browser interactions
            'args': ['--disable-blink-features=AutomationControlled'],  # Mimic human interaction
        }
    }

    def start_requests(self):

        yield scrapy.Request('https://www.fragrancex.com/shopping/type/cologne?currentPage=6' , meta={
            'playwright' : True,
            'current_page': 6,
        } , callback=self.get_links)

    def get_links(self, response):
        product_cell = response.css("div.product-grid-cell")

        links = []

        for product in product_cell:
            p_link = product.css("div.product-img a::attr(href)").get()
            print(p_link)
            links.append(p_link)

        if len(links) != 0:
            for link in links:
                yield scrapy.Request(f"https://www.fragrancex.com{link}" , meta={
            'playwright' : True,
        } , callback=self.parse)

        current_page = response.meta['current_page']

        if current_page <= 48:
            yield scrapy.Request(f'https://www.fragrancex.com/shopping/type/cologne?currentPage={current_page+1}' , meta={
            'playwright' : True,
            'current_page': current_page + 1,
        } , callback=self.get_links)

    def parse(self, response):
        container = response.css("div.products-container")
        disc = container.css("div.faq-description p::text").getall()
        pro_disc = {}
        if len(disc) != 0:
            pro_disc['about'] = (disc[0] if len(disc) > 0 else "") + (disc[1] if len(disc) > 1 else "")
            pro_disc['fragrance_family'] = disc[2] if len(disc) > 2 else ""
            pro_disc['scent_type'] = disc[3] if len(disc) > 3 else ""
            pro_disc['notes'] = disc[4] if len(disc) > 4 else ""
            pro_disc['suggested_use'] = disc[5] if len(disc) > 5 else ""

        yield {
            'name': container.css("span.perfume-name::text").get(),
            'brand': container.css("span.brand-name a.link-1::text").get(),
            'review_count': container.css("div.review-count a::text").get(),
            'usage': container.css("div.select_size_text span::text").get(),
            'price': container.css("span.sale-price-val::text").get(),
            'product_description': pro_disc,
            'additional_info': container.css("div.faq-info p")
        }

