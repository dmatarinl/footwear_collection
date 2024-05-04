import scrapy
import json
from data_collection_project.items import PumaProductItem

class PumaSpider(scrapy.Spider):
    """
        Spider for crawling Puma's website specifically targeting men's shoes.

        This spider is customized to handle data from Puma's product listings,
        focusing on extracting detailed information about each product, such as 
        product ID, title, price, and available sizes, etc.

        Attributes:
            name (str): Identifier for the spider.
            allowed_domains (list of str): Domains that this spider is allowed to crawl.
            start_urls (list of str): Initial URLs to kick-off the crawling process.
            custom_settings (dict): Defines settings specific to this spider, overriding 
                                    global settings defined in settings.py to try different
                                    pipelines for each spider.
    """
    name = "puma"
    allowed_domains = ["eu.puma.com"]
    start_urls = ["https://eu.puma.com/de/en/men/shoes"]

    custom_settings = {
        'ITEM_PIPELINES': {
            'data_collection_project.pipelines.JsonPipeline': 300
        }
    }
    
    def __init__(self, *args, **kwargs):
        """
            Initialize the spider with default page count.

        """
        super().__init__(*args, **kwargs)
        self.page_count = 0

    def parse(self, response):
        """
            Process each page loaded by the spider.

            This method extracts product data from the response and generates requests to 
            individual product pages for further data extraction. The extracted data includes 
            product ID, title, current price, image URLs, brand, original price, availability, 
            colors, category path, and URL.

            The extracted data is stored in a `PumaProductItem` instance, which is then passed 
            to the `parse_product_details` method via the `meta` attribute of the Scrapy request.

            After processing all products on the current page, the method calls the 
            `handle_pagination` method to handle pagination, different approach than
            saint_laurent's spider.

            Args:
                response (scrapy.http.Response): The response object to be processed. 
                It contains the HTML content of a product listing page.

            Yields:
                scrapy.Request: A request to a product page, with the partially filled item 
                passed in the `meta` attribute.
        """
        # Extract product data and URLs
        products = response.css('div.grid-tile')
        for product in products:
            item = PumaProductItem()
            data = product.css('::attr(data-puma-analytics)').get()
            if data:
                data = json.loads(data)
                item['product_id'] = data['products'][0].get('productID', '')
                item['title'] = data['products'][0].get('localName', 'No title')
                item['current_price'] = data['products'][0].get('price', '0')
                item['image_urls'] = data['products'][0].get('imageURL', [])
                item['original_price'] = data['products'][0].get('listPrice', '0')
                item['availability'] = data['products'][0].get('inStock', False)
                item['colors'] = data['products'][0].get('colorName', 'Unknown')
                item['category_path'] = f"{data['products'][0].get('productCategory', '')} > {data['products'][0].get('category', '')}"
                item['url'] = response.urljoin(product.css('a.product-tile-image-link::attr(href)').get())

                request = scrapy.Request(item['url'], callback=self.parse_product_details)
                request.meta['item'] = item
                yield request

        # Call the pagination handler
        yield from self.handle_pagination(response)

    def parse_product_details(self, response):
        """
            Parse the product details from the response.

            This method extracts the product description and available sizes from the 
            response. The description is extracted directly from the response using CSS 
            selectors. The sizes are extracted from JSON strings in the response using 
            the `extract_sizes_from_json` helper method.

            The extracted data is stored in the `item` dictionary, which is then yielded 
            to be processed by Scrapy's item pipelines.

            Args:
                response (scrapy.http.Response): The response object to be processed. 

            Yields:
                dict: A dictionary containing the product description and available sizes.
        """
        item = response.meta['item']
        item['description'] = response.css('div[itemprop="description"] p:first-of-type::text').get(default='').strip()
        json_strs = response.css('div.attributes-container ::attr(data-component-options)').getall()
        item['sizes'] = self.extract_sizes_from_json(json_strs)

        # Extracting brand from JSON-LD structured data
        json_ld_string = response.xpath('//script[@type="application/ld+json"]/text()').get()
        if json_ld_string:
            try:
                json_ld_data = json.loads(json_ld_string)
                item['brand'] = json_ld_data.get('brand', 'Brand not found')
            except json.JSONDecodeError:
                self.logger.error('Failed to decode JSON-LD data')
                
        yield item

    def extract_sizes_from_json(self, json_strings):
        """
            Extract sizes from the JSON strings.

            This method iterates over a list of JSON strings, each representing a product 
            variant. It attempts to load each string as a JSON object and extract the 
            'label' value from each 'swatch' in the 'swatches' list, if the 'available' 
            key is not present or its value is not 0. 

            The extracted sizes are then joined into a single string separated by commas.

            Args:
                json_strings (list): List of JSON strings to extract sizes from.

            Returns:
                str: A string of sizes separated by commas. If no sizes could be extracted, 
                an empty string is returned.
        """
        sizes = []
        for json_str in json_strings:
            try:
                json_data = json.loads(json_str)
                if 'swatches' in json_data:
                    for swatch in json_data['swatches']:
                        if 'label' in swatch and swatch.get('available', 1):
                            sizes.append(swatch['label'])
            except json.JSONDecodeError:
                continue
        return ', '.join(sizes)

    def handle_pagination(self, response):
        """
            Handle pagination for the spider.
            The objective of the limitation is to obtain less products, and show
            as soon as possible the results of the scrapping.
            Current pages crawled are limited to 1.
            Total products per page = 36.
            If you want to obtain the full list of products, remove the limitation.

            Args:
                response (scrapy.http.Response): The response object to be processed.
        """
        self.page_count += 1
        if self.page_count <= 0:  # Only proceed if the page count is within the limit of 1 page
            next_page_url = response.css('p.loading-bar[data-js-load-more]::attr(data-url)').get()
            if next_page_url:
                yield scrapy.Request(url=next_page_url, callback=self.parse)
            else:
                self.logger.info("No more pages to load.")