# Footwear_Collection

A Python project that scrapes and provides an API for managing footwear data from various brands. 

Using Flask and Scrapy as main frameworks.

## Features

- Scrapes data from Puma and Saint Laurent websites.
- Provides a REST API for managing the scraped data.
- Generates a visualization of the collected data.

## Technologies Used

- Python
- Scrapy
- Flask
- Pandas
- Matplotlib
- Seaborn

## Installation

1. **Clone the Repository**
    ```bash
    git clone https://github.com/dmatarinl/footwear-collection.git
    cd footwear-collection
    ```

2. **Create a Virtual Environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/macOS
    venv\Scripts\activate  # Windows
    ```

3. **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```
## Usage Notes ⚠️IMPORTANT⚠️

This project is my first time using Scrapy, a powerful web scraping framework in Python, to collect data from various footwear brand websites. 

To handle pagination within the spiders, and due to my inexperience using Scrapy, I chose to disable the robots.txt compliance in settings.py:
```
# Obey robots.txt rules
ROBOTSTXT_OBEY = False
```
**Important Information:** While this approach allows unfettered access to web pages, it poses certain risks and challenges:

**Ignoring robots.txt:** This setting means spiders can disregard the website's robots.txt file, which usually details the rules for web scraping:

**1 - Legal Risks:** Disobeying robots.txt or a website's terms of service can potentially lead to legal issues.

**2 - Blocking:** Websites may detect scraping activity and block IP addresses or user accounts if they suspect policy violations.

**3 - Ethical Considerations:** Excessive requests can burden the server infrastructure, affecting site performance.

I acknowledge these challenges and will explore ways to manage pagination responsibly in future iterations, possibly leveraging tools like Splash (for JavaScript-rendered pages) or Selenium.

## Running Spiders

**Run Both Spiders Consecutively**

The included script will run the Saint Laurent spider first, creating a products.csv file in the data folder, followed by the Puma spider, which will create products.json. 

This approach allowed me to test different strategies by customizing pipelines and settings.

```bash
python run_spiders.py
```
In case of individual run:

```bash
scrapy crawl puma
# scrapy crawl saint_laurent 
```

## API Usage

1. **Run the API Server**
    ```bash
    python api.py products.csv  # or products.json in case of PUMA spider
    ```
It will run on port :5000

2. **API Endpoints**
    - `/products`: Get all products
    - `/products/search`: Search products using various filters and sorting options
    - `/products/summary`: Get summary of products per category
    - `/products/create`: Create a new product (POST)
    - `/products/<product_id>`: Update or delete a product (PUT, DELETE)
    - `/products/visualization`: Generate a visualization of products per category

Within the api.py you will find each method documented appropriately. Tested using VsCode extension ThunderClient.

**Examples API Search Calls**

```bash
http://127.0.0.1:5000/products/search?sizes=42,43&colors=blue,red

http://127.0.0.1:5000/products/search?title=sneaker

http://127.0.0.1:5000/products/search?description=running&sort_by=current_price&sort_order=desc

http://127.0.0.1:5000/products/search?title=sneaker&colors=red,blue&sizes=42,43,45&sort_by=title&sort_order=asc
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate. 
(Tests will be uploaded in the next iterations)

## License

[MIT](https://choosealicense.com/licenses/mit/)
