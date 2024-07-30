import scrapy
from scrapy.utils.log import configure_logging
import random
import string
class CompanyrevSpider(scrapy.Spider):
    name = "companyrev"

    log_file = ''.join(random.choices(string.ascii_letters, k=5))

    def __init__(self, job=None, output=None ,*args, **kwargs):
        super(CompanyrevSpider, self).__init__(*args, **kwargs)
        self.job = job
        self.output = output

        with open(f'C:/Users/agbli/Desktop/webscraping/scrapy_scrapper/jsheavy/jsheavy/jobs/{self.job}', 'w', encoding='utf-8') as file:
            file.write("output file: " + self.output)
            file.write("\nlog file: " + self.log_file)

    custom_settings = {
        'DOWNLOAD_DELAY': 3,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'PLAYWRIGHT_BROWSER_TYPE': 'firefox',
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; AS; rv:11.0) like Gecko',
        'PLAYWRIGHT_LAUNCH_OPTIONS': {
            'headless': True,
            'args': ['--disable-blink-features=AutomationControlled'],
        },
        'LOG_LEVEL': 'DEBUG',
        'LOG_FILE': f"C:/Users/agbli/Desktop/webscraping/scrapy_scrapper/jsheavy/jsheavy/logs/{log_file}.txt",  # Ensure absolute path
        'LOG_FORMAT': '%(levelname)s: %(message)s',
        'LOG_STDOUT': True
    }



    def start_requests(self):
        print("starting requests...")
        yield scrapy.Request('https://www.ambitionbox.com/list-of-companies', meta={
            'playwright' : True,
            'playwright_page_methods': {
                # PageMethod('wait_for_selector', 'div.companyCardWrapper__tertiaryInformation'),
                # PageMethod('click', 'div.companyCardWrapper__tertiaryInformation > a:first-child'),
                # PageMethod("wait_for_timeout", 1500),
            }
        }, callback=self.follow_links)

    def follow_links(self, response):
        print("following links...")
        links = response.css("div.companyCardWrapper__tertiaryInformation > a:first-child::attr(href)").getall()
        company_names = response.css("h2.companyCardWrapper__companyName::text")

        for index , link in enumerate([links[0]]):
            yield scrapy.Request(link , meta={
            'playwright' : True,
            'company' : str(company_names[index]).strip()
        }, callback=self.parse)



    def parse(self, response):
        print("parsing html...")
        reviews = response.css("div#reviews-section")
        r_list = reviews.css("div.ab_comp_review_card")

        def resolve_ratings(ratings):
            data = {}

            if ratings is not None:
                for rating in ratings:
                    key = rating.css("p.rating-name::text").get() if (rating.css("p.rating-name::text").get() is not None) else ""
                    if key != "":
                        da = rating.css("p.rating-val::text").get()
                        data[key] = str(da).strip() if (da is not None) else ""
            return data


        # for card in r_list:
        #     yield {
        #         'company name' : response.meta['company'],
        #         'post' : card.css("div.reviewer-info h2::text").get(),
        #         'job type' : card.css("p.jobTypeBox::text").get(),
        #         'department': str(card.css("p.jobTypeBox-p::text").get()).strip(),
        #         'place': card.xpath('//span[@itemprop="author"]').xpath('meta[last()]/@content').get(),
        #         'average rating' : card.css("span.avg-rating::text").get(),
        #         'ratings' : resolve_ratings(card.css("div.avg_review_wrap div.avg_review_item")),
        #         'review' : card.css('div.review-body *::text').getall()
        #     }

        next_page = response.css("a.page-nav-btn::attr(href)").getall()
        print(next_page , 'this is the next page')
        if next_page[-1]:
            yield scrapy.Request(f"https://www.ambitionbox.com{next_page[-1]}" , meta={
                'playwright' : True,
                'company': response.meta['company']
            }, callback=self.parse)



