import scrapy

"""
    2 Different ProductItems in case we want to scrape from 2
    different websites and add different items.
"""
class SaintLaurentProductItem(scrapy.Item):
    """
        Item class for storing product data scraped from Saint Laurent's website.

        Fields:
            product_id: Unique identifier for the product.
            title: Name or title of the product.
            brand: Brand name of the product.
            description: Detailed description of the product.
            current_price: Current selling price of the product.
            original_price: Original price of the product before any discounts.
            availability: Stock status of the product.
            image_urls: List of URLs pointing to images of the product.
            colors: Available colors of the product.
            sizes: Available sizes of the product.
            category_path: Hierarchical category to which the product belongs.
            url: URL to the product page.
    """
    product_id = scrapy.Field()
    title = scrapy.Field()
    brand = scrapy.Field()
    description = scrapy.Field()
    current_price = scrapy.Field()
    original_price = scrapy.Field()
    availability = scrapy.Field()
    image_urls = scrapy.Field()
    colors = scrapy.Field()
    sizes = scrapy.Field()
    category_path = scrapy.Field()
    url = scrapy.Field()

class PumaProductItem(scrapy.Item):
    """
        Item class for storing product data scraped from Puma's website.

        Fields:
            product_id: Unique identifier for the product.
            title: Name or title of the product.
            brand: Brand name of the product.
            description: Detailed description of the product.
            current_price: Current selling price of the product.
            original_price: Original price of the product before any discounts.
            availability: Stock status of the product.
            image_urls: List of URLs pointing to images of the product.
            colors: Available colors of the product.
            sizes: Available sizes of the product.
            category_path: Hierarchical category to which the product belongs.
            url: URL to the product page.
    """
    product_id = scrapy.Field()
    title = scrapy.Field()
    brand = scrapy.Field()
    description = scrapy.Field()
    current_price = scrapy.Field()
    original_price = scrapy.Field()
    availability = scrapy.Field()
    image_urls = scrapy.Field()
    colors = scrapy.Field()
    sizes = scrapy.Field()
    category_path = scrapy.Field()
    url = scrapy.Field()