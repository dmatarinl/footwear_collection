# Footwear_Collection

A Python project that scrapes and provides an API for managing footwear data from various brands. Using Flask and Scrapy as main frameworks.

This project features a system of two spiders designed to collect data from the Saint Laurent and Puma websites, extracting the following information for each product:

- `product_id`
- `title`
- `brand`
- `description`
- `current_price`
- `original_price`
- `availability`
- `image_urls`
- `colors`
- `sizes`
- `category_path`
- `url`

The first spider scrapes the Saint Laurent website, generating a `products.csv` file with at least 27 products.

The second spider, created with more Scrapy experience, targets the Puma website. It can gather data for up to 1,233 products, but the pagination is managed using a count limiter to minimize pages. Currently, it scrapes only one page, resulting in 36 products, to promptly provide initial results. 

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
    - `/products`: Get all products (GET)
    - `/products/search`: Search products using various filters and sorting options (GET)
    - `/products/summary`: Get summary of products per category (GET)
    - `/products/create`: Create a new product (POST)
    - `/products/<product_id>`: Update or delete a product (PUT, DELETE)
    - `/products/visualization`: Generate a visualization of products per category (GET)

Within the api.py you will find each method documented appropriately. Tested using VsCode extension ThunderClient.

**Examples API Search Calls**

```bash
http://127.0.0.1:5000/products/search?sizes=42,43&colors=blue,red

http://127.0.0.1:5000/products/search?title=sneaker

http://127.0.0.1:5000/products/search?description=running&sort_by=current_price&sort_order=desc

http://127.0.0.1:5000/products/search?title=sneaker&colors=red,blue&sizes=42,43,45&sort_by=title&sort_order=asc
```

## Room for Improvement

1. **Handling Pagination**: I plan to change the way pagination is handled to improve efficiency and compliance, moving away from ignoring robots.txt. Instead, I aim to incorporate tools like Splash or Selenium to handle JavaScript-rendered pages effectively.

2. **Testing Enhancements**: I'll focus on adding more comprehensive tests and improving the current testing setup using pytest. The existing tests will be uploaded in the next iterations to maintain a consistent testing environment.

3. **Saint Laurent Spider Enhancements**: The current Saint Laurent spider scrapes all possible sizes instead of only available sizes. I plan to refine this spider's behavior to ensure accurate data collection, similar to how the Puma spider currently works.

These improvements will enhance the quality, maintainability, and ethical compliance of the project.


## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate. 
(Tests will be uploaded in the next iterations)

## License

[MIT](https://choosealicense.com/licenses/mit/)
