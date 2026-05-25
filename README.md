# Product Scraper & WooCommerce Importer

This project contains two scripts:
1. `scraper.py`: Scrapes 24 products from happyhippieyoga.nl.
2. `importer.py`: Imports the scraped data into a WordPress WooCommerce store.

## Prerequisites

- Python 3.x
- Required libraries: `requests`, `beautifulsoup4`, `woocommerce`

Install dependencies:
```bash
pip install requests beautifulsoup4 woocommerce
```

## How to use the Scraper

Run the scraper to generate `products.json`:
```bash
python scraper.py
```
This will fetch 24 products with all details (attributes, variations, images, etc.).

## How to use the Importer

### 1. Setup WooCommerce API
1. Go to your WordPress Dashboard.
2. Navigate to **WooCommerce > Settings > Advanced > REST API**.
3. Click **Add Key**.
4. Description: "Product Importer".
5. Permissions: **Read/Write**.
6. Copy the **Consumer Key** and **Consumer Secret**.

### 2. Configure Credentials
Open `importer.py` and update the following variables at the top of the file:
- `WC_URL`: Your website URL (e.g., `https://example.com`).
- `WC_KEY`: Your Consumer Key.
- `WC_SECRET`: Your Consumer Secret.

Alternatively, you can set them as environment variables:
```bash
export WC_URL="https://example.com"
export WC_KEY="ck_..."
export WC_SECRET="cs_..."
```

### 3. Run the Importer
Ensure `products.json` is in the same directory, then run:
```bash
python importer.py
```

## Data Mapping Notes
- **Maten (Maat)**: Mapped to WooCommerce attribute **Size**.
- **Kleur**: Mapped to WooCommerce attribute **Color**.
- **Merk**: Mapped to WooCommerce attribute **Brand**.
- **Images**: The first image is set as the featured image, and subsequent images are added to the gallery.
- **Variations**: Variable products are created with all scraped variations (price, SKU, stock status, and mapped attributes).
