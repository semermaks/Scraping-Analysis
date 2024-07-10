import scrapy
from scrapy.http import Response
from selenium import webdriver
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
import os

load_dotenv()
technologies = os.getenv("TECHNOLOGIES").split(",")


class JobsSpider(scrapy.Spider):
    name = "jobs"
    allowed_domains = ["www.work.ua"]
    start_urls = ["https://www.work.ua/jobs-python/", "https://www.work.ua/jobs-python-програміст/"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.driver = webdriver.Chrome()

    def close(self, reason):
        self.driver.close()

    def _parse_jobs_details(self, url: str, **kwargs):
        self.driver.get(url)
        try:
            job_description = self.driver.find_element(By.ID, "job-description")
            return job_description.text
        except Exception as e:
            self.logger.error(f"Error extracting job description from {url}: {e}")
            return ""

    def parse(self, response: Response, **kwargs):
        for job in response.css('.my-0>a'):
            job_url = response.urljoin(job.css('::attr(href)').get())
            description = self._parse_jobs_details(job_url).lower()

            tech_found = {}
            for tech in technologies:
                tech_found[tech] = description.find(tech.lower()) != -1

            yield {
                "title": job.css('::attr(title)').get(),
                **tech_found
            }
        next_page = response.css(".pagination>li")[-1].css("a::attr(href)").get()
        print(next_page)
        if next_page is not None:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, callback=self.parse, dont_filter=True)


