from contact_extract.contact_extract.spiders.email_extract import EmailExtractSpider
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor
import logging

class RunSpider():
    def execute_crawling(a,keyword, url, taskid):
        runner = CrawlerRunner()
        
        # To run email scraping spider
        if keyword == 'email':
            print("Running email scraping spider")
            d = runner.crawl(EmailExtractSpider, url=url, taskid=taskid)
            d.addBoth(lambda _: reactor.stop())
            reactor.run() 

