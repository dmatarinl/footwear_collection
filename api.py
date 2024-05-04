import sys
import os
import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
from flask import Flask, jsonify, request, send_file, Response

# Initialize the Flask app
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# Directory to store the data files
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

# Sub-directory for storing visualization images
VISUALIZATION_DIR = os.path.join(DATA_DIR, 'product_per_category')
os.makedirs(VISUALIZATION_DIR, exist_ok=True)

def normalize_sizes(size_str):
    """
    Replace underscores with dots in the sizes string.
    Args:
        size_str (str): Size string containing underscores.
    Returns:
        str: Size string with underscores replaced by dots.
    """
    return size_str.replace('_', '.')

def load_data(file_name):
    """
    Load data from a file and normalize sizes.

    Args:
        file_name (str): Name of the file to load.

    Returns:
        pd.DataFrame: DataFrame with normalized sizes.

    Raises:
        ValueError: If the file format is unsupported.
    """
    file_path = os.path.join(DATA_DIR, file_name)
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    elif file_path.endswith('.json'):
        df = pd.read_json(file_path, orient='records')
    else:
        raise ValueError("Unsupported file format")
    
    # Normalize the 'sizes' column immediately after loading
    df['sizes'] = df['sizes'].apply(normalize_sizes)
    return df

# Check if the file name argument is provided
if len(sys.argv) != 2:
    print("Error: Please specify the data file as an argument.")
    print("Usage: python api.py <datafile>")
    sys.exit(1)

data_file = sys.argv[1]
data_path = os.path.join(DATA_DIR, data_file)

# Check if the file exists in the data directory
if not os.path.exists(data_path):
    print(f"Error: File {data_path} not found.")
    sys.exit(1)

try:
    df = load_data(data_file)
except Exception as e:
    print(f"Error loading data: {e}")
    sys.exit(1)

@app.route('/products', methods=['GET'])
def get_products():
    """
    Retrieve all products and total count.

    Returns:
        flask.Response: JSON response containing total product count and products.
    """
    products_json = df.to_dict(orient='records')
    total_products = len(products_json)
    response_data = {
        "total_products": total_products,
        "products": products_json
    }
    response_str = json.dumps(response_data, indent=4)
    return Response(response_str, mimetype='application/json')

@app.route('/products/search', methods=['GET'])
def search_products():
    """
    Search products using various filters and sorting options.

    Query Parameters:
        title (str): Search string for matching product titles (case insensitive).
        description (str): Search string for matching product descriptions (case insensitive).
        product_id (str): Filter by product ID (case insensitive).
        min_price (float): Minimum price of the product.
        max_price (float): Maximum price of the product.
        colors (str): Comma-separated list of colors to filter products by.
        sizes (str): Comma-separated list of sizes to filter products by.
        sort_by (str): Field to sort results by (default is 'title').
        sort_order (str): Sorting order ('asc' or 'desc', default is 'asc').

    Returns:
        flask.Response: JSON response containing the filtered products or an error message.
    """
    query_params = request.args
    filtered_df = df.copy()

    # Text search on Title or Description
    title_query = query_params.get('title')
    description_query = query_params.get('description')
    product_id_query = query_params.get('product_id')
    if title_query:
        filtered_df = filtered_df[filtered_df['title'].str.contains(title_query, case=False, na=False)]
    if description_query:
        filtered_df = filtered_df[filtered_df['description'].str.contains(description_query, case=False, na=False)]
    if product_id_query:
        filtered_df = filtered_df[filtered_df['product_id'].str.contains(product_id_query, case=False, na=False)]

    # Range filters for price
    min_price = query_params.get('min_price', type=float)
    max_price = query_params.get('max_price', type=float)
    if min_price is not None:
        filtered_df = filtered_df[filtered_df['current_price'] >= min_price]
    if max_price is not None:
        filtered_df = filtered_df[filtered_df['current_price'] <= max_price]

    # Multiple values filtering for Colors and Sizes both of them expected to be comma-separated
    colors = query_params.get('colors')
    sizes = query_params.get('sizes')
    filtered_df['sizes'] = filtered_df['sizes'].apply(normalize_sizes)

    if colors:
        color_list = [color.strip().lower() for color in colors.split(',')]
        filtered_df = filtered_df[filtered_df['colors'].str.lower().apply(lambda x: any(color in x for color in color_list))]
    if sizes:
        size_list = [size.strip() for size in sizes.split(',')]
        filtered_df = filtered_df[filtered_df['sizes'].apply(lambda x: any(size in x.split(', ') for size in size_list))]

    # Sort handling
    sort_by = query_params.get('sort_by', 'title')  # Default sort by title
    sort_order = query_params.get('sort_order', 'asc') == 'asc'
    filtered_df = filtered_df.sort_values(by=sort_by, ascending=sort_order)

    if filtered_df.empty:
        return jsonify({'error': 'No products found matching the criteria'}), 404

    products_json = filtered_df.to_dict(orient='records')
    return jsonify({"products": products_json})

@app.route('/products/summary', methods=['GET'])
def products_summary():
    """
    Generate a summary of product counts, average prices, and availability per category.

    Returns:
        flask.Response: JSON response containing a summary of products grouped by category.
    """
    # Convert 'current_price' to float to ensure calculations work properly
    df['current_price'] = pd.to_numeric(df['current_price'], errors='coerce')

    # Now calculate the category counts, average price, and availability counts
    category_counts = df['category_path'].value_counts().to_dict()
    price_average = df.groupby('category_path')['current_price'].mean().round(2).to_dict()
    availability_count = df.groupby('category_path')['availability'].value_counts().unstack(fill_value=0).to_dict(orient='index')

    summary_data = []
    for category in category_counts.keys():
        summary_entry = {
            "category_path": category,
            "product_count": category_counts[category],
            "average_price": price_average.get(category, 0),
            "availability": availability_count.get(category, {})
        }
        summary_data.append(summary_entry)

    return jsonify(summary_data)

@app.route('/products/create', methods=['POST'])
def add_product():
    """
    Add a new product to the dataset.

    This function expects a JSON payload with the necessary product information. 
    It verifies the required fields, ensures there are no duplicates, 
    and then appends the new product to the dataset.

    Expected JSON Payload:
        - product_id (str): Unique identifier for the product.
        - title (str): Title or name of the product.
        - brand (str): Product brand.
        - description (str): Product description.
        - current_price (float): Current selling price.
        - original_price (float): Original price before discount (can be NaN).
        - availability (str): Availability status (e.g., 'In stock', 'Out of stock').
        - image_urls (str): URLs pointing to the product images (comma-separated).
        - colors (str): Available colors (comma-separated).
        - sizes (str): Available sizes (comma-separated).
        - category_path (str): Path showing product category hierarchy.
        - url (str): Direct URL to the product page.

    Returns:
        flask.Response: JSON response with the new product information or an error message.
    """
    if not request.json:
        return jsonify({'error': 'No JSON payload provided.'}), 400

    required_fields = ["product_id", "title", "brand", "description", "current_price",
                       "original_price", "availability", "image_urls", "colors", "sizes", "category_path", "url"]

    missing_fields = [field for field in required_fields if field not in request.json]
    if missing_fields:
        return jsonify({'error': 'Missing required fields', 'missing': missing_fields}), 400

    new_product = {k: str(v).strip() if isinstance(v, str) else str(v) for k, v in request.json.items()}
    new_product['original_price'] = pd.to_numeric(new_product['original_price'], errors='coerce')  # Convert to numeric, NaN if invalid
    new_product_df = pd.DataFrame([new_product])

    global df  # Global df variable to update dataframe loaded at start

    try:
        # Ensure all data used for comparison or manipulation as strings are indeed strings
        df['product_id'] = df['product_id'].astype(str)
        new_product['product_id'] = str(new_product['product_id'])

        # Check for duplicate entries based on 'product_id'
        if df['product_id'].str.lower().str.strip().isin([new_product['product_id'].lower().strip()]).any():
            return jsonify({'error': 'Duplicate entry: Product with this ID already exists.'}), 409

        # Add new product to dataframe
        df = pd.concat([df, new_product_df], ignore_index=True)

        # Write updated dataframe back to file
        if data_file.endswith('.csv'):
            df.to_csv(data_file, index=False)
        elif data_file.endswith('.json'):
            df.to_json(data_file, orient='records')
        else:
            raise ValueError("Unsupported file format")

    except Exception as e:
        return jsonify({'error': 'Failed to add product.', 'exception': str(e)}), 500

    return jsonify(new_product), 201

@app.route('/products/visualization', methods=['GET'])
def products_visualization():
    """
    Generate and return a bar chart visualization of the number of products per category.

    This function uses seaborn and matplotlib to generate a bar chart showing the count of products grouped by their category path. The resulting image is saved to the `product_per_category` sub-directory inside the `data` directory.

    Returns:
        flask.Response: Image file as a downloadable PNG file.
    """
    # Initialize the visualization plot
    fig, ax = plt.subplots(figsize=(10, 7))
    sns.countplot(y='category_path', data=df, ax=ax, order=df['category_path'].value_counts().index)
    ax.set_title('Product Count by Category')
    ax.set_xlabel('Product Count')
    ax.set_ylabel('Category Path')

    # Generate a unique filename based on data file name and the current timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    base_filename = os.path.splitext(os.path.basename(data_file))[0]
    image_file_name = f'products_per_category_{base_filename}_{timestamp}.png'
    image_path = os.path.join(VISUALIZATION_DIR, image_file_name)

    # Save the visualization plot as a PNG file and close the plot
    plt.tight_layout()
    plt.savefig(image_path)
    plt.close(fig)

    # Serve the image as a file download
    return send_file(image_path, mimetype='image/png', as_attachment=True)


@app.route('/products/<product_id>', methods=['PUT', 'DELETE'])
def modify_or_delete_product(product_id):
    """
    Modify or delete a product based on its product ID.

    This function handles both updating and deleting a product in the dataset. It first searches for the product by its ID. If found, it will either update its details or delete it, depending on the HTTP request method.

    Args:
        product_id (str): The ID of the product to modify or delete.

    PUT Method:
        - Requires a JSON payload containing fields to update.
        - Skips updating the `product_id` field itself.

    DELETE Method:
        - No request body required.
        - Deletes the product matching the given ID.

    Returns:
        flask.Response: JSON response indicating the success or failure of the operation.
    """
    global df  # Reference the global DataFrame

    try:
        # Reload and ensure 'product_id' is a string
        if data_file.endswith('.csv'):
            df = pd.read_csv(data_file)
        elif data_file.endswith('.json'):
            df = pd.read_json(data_file, orient='records')

        df['product_id'] = df['product_id'].astype(str)  # Ensure `product_id` is treated as a string
        df['original_price'] = pd.to_numeric(df['original_price'], errors='coerce')  # Handle non-numeric gracefully

        # Look for the product idx with case insensitive matching
        product_idx = df[df['product_id'].str.lower() == product_id.lower()].index
        if product_idx.empty:
            return jsonify({'error': 'Product not found'}), 404

        # Update the product information if the method is PUT
        if request.method == 'PUT':
            update_fields = request.json
            update_fields['original_price'] = pd.to_numeric(update_fields.get('original_price'), errors='coerce')
            for key, value in request.json.items():
                if key in df.columns and key != 'product_id':
                    df.at[product_idx.item(), key] = value.strip() if isinstance(value, str) else value

            # Save changes from df back to the file
            if data_file.endswith('.csv'):
                df.to_csv(data_file, index=False)
            elif data_file.endswith('.json'):
                df.to_json(data_file, orient='records', lines=False, force_ascii=False)
            
            return jsonify({'message': 'Product updated successfully'}), 200
        
        # Delete the product if the method is DELETE
        elif request.method == 'DELETE':
            df = df.drop(index=product_idx)
            if data_file.endswith('.csv'):
                df.to_csv(data_file, index=False)
            elif data_file.endswith('.json'):
                df.to_json(data_file, orient='records', lines=False, force_ascii=False)
            
            return jsonify({'message': 'Product deleted successfully'}), 200

    except Exception as e:
        return jsonify({'error': 'Failed to modify or delete product', 'exception': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)  # Run the application
