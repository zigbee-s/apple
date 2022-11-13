import logging
import re
import os
import urllib
from tld import get_tld
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor



class EmailExtractSpider(CrawlSpider):
    name = 'email_extract'
    domain_regex = '/([a-z0-9|-]+\.)*[a-z0-9|-]+\.[a-z]+/'
    skip_domains = [
        "behance.net",
        "adobe.com",
        "stackoverflow.com",
        "linkedin.com",
        "github.com",
        "pinterest.com",
        "medium.com",
        "twitter.com",
        "tumblr.com",
        "wikipedia.org",
        "instagram.com",
        "facebook.com",
        "google.com",
        "amazon.com",
        "yahoo.com",
        "tiktok.com",
    ]

    yielded_emails = []
    filename = ""

    rules = (
        Rule(
            LinkExtractor(
                allow=([domain_regex, ".*contact*", ".*about*"]),
                deny_domains=(skip_domains)),
            callback='parse_page',
            process_links='exclude_links',
            follow=False
        ),
    )

    # constuctor
    def __init__(self, url, taskid, **kwargs):
        self.allowed_domains = [f'{url}']
        self.start_urls = [f'https://{url}']
        self.filename = taskid
        super().__init__(**kwargs)


    def exclude_links(self, links):
        for link in links:
            for skip_domain in self.skip_domains:
                if skip_domain in link.url:
                    continue
                yield link

    def parse_page_test(self, response):
        yield {
            'emails': '',
            'link': response.url,
        }

    def parse_page(self, response):
        emails = []
        email_regex = re.compile(
            r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
        )

        try:
            html = response.body.decode('utf-8')
            html_text = response.text
        except UnicodeDecodeError:
            return
        # Find mailto's
        mailtos = response.xpath(
            "//a[starts-with(@href, 'mailto')]/@href").getall()
        emails = [urllib.parse.unquote(
            mail.replace('mailto:', '')) for mail in mailtos]
        body_emails = email_regex.findall(html)
        emails += [urllib.parse.unquote(email) for email in body_emails if
                   get_tld('https://' + email.split('@')[-1], fail_silently=True)]

        self.yielded_emails = self.yielded_emails + emails
        yield {
            'emails': list(set(emails)),
        }

    def closed(self, reason):
        logging.info("Writing to file")
        pathToFile = os.path.join(os.path.dirname(
            __file__), "../../../" + self.filename + ".txt")
        with open(pathToFile, "w") as file:
            for email in list(set(self.yielded_emails)):
                file.write(email)
                file.write("\n")
