import json
import os
from woocommerce import API

# --- CONFIGURATION ---
# Replace these with your actual credentials or set them as environment variables
WC_URL = os.getenv("WC_URL", "https://your-website.com")
WC_KEY = os.getenv("WC_KEY", "ck_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
WC_SECRET = os.getenv("WC_SECRET", "cs_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

wcapi = API(
    url=WC_URL,
    consumer_key=WC_KEY,
    consumer_secret=WC_SECRET,
    version="wc/v3",
    timeout=30
)

def get_or_create_category(name):
    # Search for category
    categories = wcapi.get("products/categories", params={"search": name}).json()
    for cat in categories:
        if cat['name'].lower() == name.lower():
            return cat['id']

    # Create if not found
    data = {"name": name}
    new_cat = wcapi.post("products/categories", data).json()
    return new_cat.get('id')

def import_products():
    with open("products.json", "r", encoding="utf-8") as f:
        products = json.load(f)

    for product in products:
        print(f"Importing: {product['title']}...")

        # Prepare Categories
        cat_ids = []
        for cat_name in product['categories']:
            cat_id = get_or_create_category(cat_name)
            if cat_id:
                cat_ids.append({"id": cat_id})

        # Prepare Attributes
        # Map Maat -> Size, Kleur -> Color, Merk -> Brand
        mapped_attributes = []

        attr_source = product.get('attributes', {})

        # Size
        size_val = attr_source.get('Maten')
        if size_val:
            # We need to ensure the options match what variations will use.
            # In the variations, 's' and 'm' are used.
            # Let's map 's' -> 'Maat 36 – 39' and 'm' -> 'Maat 40 – 43' if they exist in size_val
            options = [o.strip() for o in size_val.split(',')]
            mapped_attributes.append({
                "name": "Size",
                "visible": True,
                "variation": True,
                "options": options
            })

        # Color
        color_val = attr_source.get('Kleur')
        if color_val:
            options = [o.strip() for o in color_val.split(',')]
            mapped_attributes.append({
                "name": "Color",
                "visible": True,
                "variation": True,
                "options": options
            })

        # Brand
        brand_val = attr_source.get('Merk')
        if brand_val:
            mapped_attributes.append({
                "name": "Brand",
                "visible": True,
                "variation": False, # Usually brands don't vary
                "options": [brand_val]
            })

        # Images
        images = []
        for i, img_url in enumerate(product['images']):
            images.append({"src": img_url})

        # Main Product Data
        data = {
            "name": product['title'],
            "type": "variable" if product['variations'] else "simple",
            "description": product['description'],
            "short_description": product['short_description'],
            "categories": cat_ids,
            "images": images,
            "attributes": mapped_attributes
        }

        if not product['variations']:
            # Simple product price
            price = product['price'].replace('€', '').replace(',', '.').strip()
            data["regular_price"] = price

        # Create Product
        res = wcapi.post("products", data).json()
        if 'id' not in res:
            print(f"Error creating product {product['title']}: {res}")
            continue

        product_id = res['id']
        print(f"Product created with ID: {product_id}")

        # Create Variations
        if product['variations']:
            # Get size mapping for this product
            size_val = attr_source.get('Maten', '')
            options = [o.strip() for o in size_val.split(',')]

            for var in product['variations']:
                # Extract variation attributes and map them
                var_attributes = []
                for attr_key, attr_val in var.get('attributes', {}).items():
                    name = ""
                    option = attr_val
                    if "maat" in attr_key:
                        name = "Size"
                        # Try to map 's', 'm', 'l' to full option names
                        if attr_val == 's':
                            match = [o for o in options if '36' in o or '38' in o]
                            if match: option = match[0]
                        elif attr_val == 'm':
                            match = [o for o in options if '39' in o or '40' in o or '42' in o]
                            if match: option = match[0]
                        elif attr_val == 'l':
                            match = [o for o in options if '43' in o or '45' in o]
                            if match: option = match[0]
                    elif "kleur" in attr_key:
                        name = "Color"
                        # Map slug back to color name from global attributes if possible
                        color_name = attr_source.get('Kleur', attr_val.capitalize())
                        option = color_name

                    if name:
                        var_attributes.append({
                            "name": name,
                            "option": option
                        })

                var_data = {
                    "regular_price": str(var.get('display_price', '')),
                    "sku": var.get('sku', ''),
                    "image": {"src": var.get('image', {}).get('url', '')} if var.get('image', {}).get('url') else None,
                    "attributes": var_attributes,
                    "manage_stock": False,
                    "stock_status": "instock" if var.get('is_in_stock') else "outofstock"
                }

                var_res = wcapi.post(f"products/{product_id}/variations", var_data).json()
                if 'id' in var_res:
                    print(f"  Variation created: {var_res['id']}")
                else:
                    print(f"  Error creating variation: {var_res}")

if __name__ == "__main__":
    if WC_KEY == "ck_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx":
        print("Please configure your WooCommerce API credentials in importer.py or environment variables.")
    else:
        import_products()
