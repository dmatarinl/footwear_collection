from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from data_collection_project.spiders.puma import PumaSpider
from data_collection_project.spiders.saintlaurent import SaintLaurentSpider

def run_spiders():
    process = CrawlerProcess(get_project_settings())
    process.crawl(PumaSpider)
    process.crawl(SaintLaurentSpider)
    process.start()

if __name__ == '__main__':
    run_spiders()
