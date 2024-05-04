import csv
import json
import os

# Create the data directory if it doesn't already exist
data_dir = os.path.join(os.path.dirname(__file__), '../data')
os.makedirs(data_dir, exist_ok=True)

class CsvPipeline:
    """
        Pipeline for exporting item data to a CSV file.

        This pipeline opens a CSV file at the start of the spider and writes item data in CSV format. 
        It ensures that each item is written as a row in the CSV file when processed.
    """
    def open_spider(self, spider):
        """
            Open a CSV file in the data directory and prepare it to write item data.
        """
        csv_path = os.path.join(data_dir, 'products.csv')
        self.file = open(csv_path, 'w', newline='', encoding='utf8')
        self.writer = csv.writer(self.file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        self.writer.writerow(['product_id', 'title', 'brand', 'description', 'current_price', 'original_price',
                              'availability', 'image_urls', 'colors', 'sizes', 'category_path', 'url'])

    def close_spider(self, spider):
        """
            Close the CSV file when the spider closes.
        """
        self.file.close()

    def process_item(self, item, spider):
        """
            Write an item to the CSV file.

            Args:
                item: The item scraped.
                spider: The spider that scraped the item.

            Returns:
                The item, after processing.
        """
        self.writer.writerow([
            item['product_id'], item['title'], item['brand'], item['description'],
            item['current_price'], item['original_price'], item['availability'],
            '; '.join(item['image_urls']), item['colors'], ', '.join(item['sizes']),
            ' > '.join([item['category_path']]),
            item['url']
        ])
        return item

class JsonPipeline:
    """
        Pipeline for exporting item data to a JSON file.

        This pipeline opens a JSON file at the start of the spider and writes items in JSON format.
        It ensures the JSON format is maintained by adding appropriate commas and new lines.
    """
    def open_spider(self, spider):
        """
            Open a JSON file in the data directory and prepare it to write item data.
        """
        json_path = os.path.join(data_dir, 'products.json')
        self.file = open(json_path, 'w')
        self.file.write('[')
        self.first_item = True

    def close_spider(self, spider):
        """
            Properly close the JSON file by appending a closing bracket.
        """
        self.file.write(']')
        self.file.close()

    def process_item(self, item, spider):
        """
            Write an item to the JSON file, formatted properly.

            Args:
                item: The item scraped.
                spider: The spider that scraped the item.

            Returns:
                The item, after processing.
        """
        line = json.dumps(dict(item), indent=4)
        if not self.first_item:
            self.file.write(',\n' + line)
        else:
            self.file.write(line)
            self.first_item = False
        return item
