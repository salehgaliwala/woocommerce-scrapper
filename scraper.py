import requests
from bs4 import BeautifulSoup
import json
import re
import time

BASE_URL = "https://happyhippieyoga.nl/yoga-pilates-sokken/"
TARGET_COUNT = 24

def get_product_links(page_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(page_url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    links = []
    # Find all product links in the list
    products = soup.select("ul.products li.product a.woocommerce-LoopProduct-link")
    for a in products:
        links.append(a['href'])
    return links

def scrape_product(url):
    print(f"Scraping: {url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

    soup = BeautifulSoup(response.content, "html.parser")

    product_data = {
        "url": url,
        "title": "",
        "price": "",
        "short_description": "",
        "description": "",
        "categories": [],
        "specifications": {},
        "attributes": {},
        "variations": [],
        "images": []
    }

    # Title
    title_tag = soup.select_one("h1.product_title")
    if title_tag:
        product_data["title"] = title_tag.get_text(strip=True)

    # Price
    price_tag = soup.select_one("p.price")
    if price_tag:
        product_data["price"] = price_tag.get_text(strip=True)

    # Short Description
    short_desc_tag = soup.select_one(".woocommerce-product-details__short-description")
    if short_desc_tag:
        product_data["short_description"] = short_desc_tag.get_text(strip=True)

    # Content / Long Description (Preserve HTML)
    desc_tag = soup.select_one("#tab-description")
    if desc_tag:
        # Using decode_contents to get inner HTML
        product_data["description"] = desc_tag.decode_contents().strip()

    # Categories
    cat_tags = soup.select(".posted_in a")
    if cat_tags:
        product_data["categories"] = [cat.get_text(strip=True) for cat in cat_tags]

    # Try finding categories in product class as well
    product_div = soup.select_one("div.product")
    if product_div:
        for cls in product_div.get('class', []):
            if cls.startswith("product_cat-"):
                cat_name = cls.replace("product_cat-", "").replace("-", " ").title()
                if cat_name not in product_data["categories"]:
                    product_data["categories"].append(cat_name)

    if not product_data["categories"]:
        # Fallback to breadcrumbs
        breadcrumb_items = soup.select(".ast-breadcrumbs .trail-item a")
        found_producten = False
        for item in breadcrumb_items:
            text = item.get_text(strip=True)
            if found_producten:
                if text not in product_data["categories"]:
                    product_data["categories"].append(text)
            if text.lower() == "producten":
                found_producten = True

    # Specifications & Attributes
    spec_table = soup.select_one(".woocommerce-product-attributes")
    if spec_table:
        rows = spec_table.select(".woocommerce-product-attributes-item")
        for row in rows:
            label = row.select_one(".woocommerce-product-attributes-item__label").get_text(strip=True)
            value = row.select_one(".woocommerce-product-attributes-item__value").get_text(strip=True)
            product_data["specifications"][label] = value
            # Attributes are often the same as specifications in WooCommerce
            product_data["attributes"][label] = value

    # Variations
    form_variation = soup.select_one("form.variations_form")
    if form_variation and 'data-product_variations' in form_variation.attrs:
        try:
            variations_json = form_variation['data-product_variations']
            product_data["variations"] = json.loads(variations_json)
        except Exception as e:
            print(f"Error parsing variations for {url}: {e}")

    # Images
    image_tags = soup.select(".woocommerce-product-gallery__image img")
    for img in image_tags:
        img_url = img.get('data-src') or img.get('src')
        if img_url and img_url not in product_data["images"]:
            product_data["images"].append(img_url)

    return product_data

def main():
    all_products = []
    page = 1

    while len(all_products) < TARGET_COUNT:
        if page == 1:
            current_url = BASE_URL
        else:
            current_url = f"{BASE_URL}page/{page}/"

        print(f"Fetching products from page {page}...")
        links = get_product_links(current_url)

        if not links:
            print("No more products found.")
            break

        for link in links:
            if len(all_products) >= TARGET_COUNT:
                break

            product = scrape_product(link)
            if product:
                all_products.append(product)

            time.sleep(1) # Be respectful

        page += 1

    with open("products.json", "w", encoding="utf-8") as f:
        json.dump(all_products, f, ensure_ascii=False, indent=4)

    print(f"Successfully scraped {len(all_products)} products.")

if __name__ == "__main__":
    main()
