import scrapy
import json
from data_collection_project.items import SaintLaurentProductItem
from googletrans import Translator

class SaintLaurentSpider(scrapy.Spider):
    """
        Spider for crawling Saint Laurent's website, specifically targeting men's sneakers.
        This spider gathers detailed product information including product IDs, titles,
        descriptions, prices, and available sizes.

        Attributes:
            name (str): Identifier for the spider.
            allowed_domains (list of str): Domains that this spider is allowed to crawl.
            start_urls (list of str): Initial URLs to kick-off the crawling process.
            custom_settings (dict): Defines settings specific to this spider, overriding
                                    global settings defined in settings.py. This spider
                                    uses a CSV pipeline for item storage.
    """
    name = 'saint_laurent'
    allowed_domains = ['ysl.com']
    start_urls = ['https://www.ysl.com/es-es/comprar-art%C3%ADculos-de-hombre/zapatos/sneakers']

    custom_settings = {
        'ITEM_PIPELINES': {
            'data_collection_project.pipelines.CsvPipeline': 400
        }
    }

    def parse(self, response):
        """
            Process each page loaded by the spider to extract and generate requests to
            individual product detail pages.

            Args:
                response (scrapy.http.Response): The response object to be processed.
            
            Yields:
                scrapy.Request: A request to each product detail page, passing product data via meta.
        """
        # Extract product data and URLs
        products = response.css('article.c-product')
        for product in products:
            product_data = json.loads(product.attrib['data-gtmproduct']) if 'data-gtmproduct' in product.attrib else {}
            product_url = response.urljoin(product.css('a.c-product__link::attr(href)').get())

            request = scrapy.Request(product_url, callback=self.parse_product_page)
            request.meta['product_data'] = product_data
            request.meta['product_url'] = product_url
            yield request

        # Pagination logic
        if products:
            next_start = response.meta.get('start', 0) + 12
            next_page_url = f'https://www.ysl.com/on/demandware.store/Sites-SLP-WEUR-Site/es_ES/Search-UpdateGrid?cgid=sneakers-men&start={next_start}&sz=12'
            yield scrapy.Request(next_page_url, callback=self.parse, meta={'start': next_start})

    def parse_product_page(self, response):
        """
            Extract detailed product information from the product detail page.

            Args:
                response (scrapy.http.Response): The response object containing product details.

            Yields:
                dict: The extracted product details ready to be processed by item pipelines.
        """
        # Extract product data and URL from meta
        product_data = response.meta['product_data']
        product_url = response.meta['product_url']

        # Extract and set image URLs, filtering out placeholders
        image_urls = set(
            response.css('div.c-productcarousel li.c-productcarousel__slide img::attr(src)').getall() +
            response.css('div.c-productcarousel li.c-productcarousel__slide img::attr(data-src)').getall()
        )
        image_urls = {url for url in image_urls if url and 'placeholder' not in url}

        # Extract the full product description and translate it
        description_elements = response.css('p.c-product__longdesc, ul.c-product__detailslist li')
        full_description = ' '.join(description_elements.css('::text').getall())
        full_description = ' '.join(full_description.split())

        # Initialize description translator
        translator = Translator()

        try:
            translated_description = translator.translate(full_description, src='es', dest='en').text
        except Exception as e:
            self.logger.error(f"Translation failed: {e}")
            translated_description = full_description

        # Sizes extraction
        size_elements = response.css('div[data-ref="listbox"] div[role="option"][data-attr-value]:not([data-attr-value="RESET"])')
        sizes = [elem.attrib['data-attr-value'] for elem in size_elements]

        # Handling the 'price' to replace None or null value with 'N/A'
        original_price = product_data.get('price') if product_data.get('price') is not None else 'N/A'

        # Creating a Scrapy Item
        item = SaintLaurentProductItem(
            product_id=product_data.get('id', ''),
            title=product_data.get('name', ''),
            brand=product_data.get('brand', ''),
            description=translated_description,
            current_price=product_data.get('discountPrice', ''),
            original_price=original_price,
            availability=product_data.get('stock', ''),
            image_urls=list(image_urls),
            colors=product_data.get('color', ''),
            sizes=sizes,
            category_path=' > '.join([
                product_data.get('topCategory', ''),
                product_data.get('category', ''),
                product_data.get('subCategory', '')
            ]),
            url=product_url
        )

        yield item
