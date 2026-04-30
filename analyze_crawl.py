import json
import re

# Load crawl data
with open('.firecrawl/jusst4you-crawl.json', 'r', encoding='utf-8') as f:
    raw_data = json.load(f)

# Extract the actual data array
data = raw_data.get('data', []) if isinstance(raw_data, dict) else raw_data

print(f"Total pages crawled: {len(data)}")
print("\n" + "="*80)
print("SAMPLE URLs (First 15):")
print("="*80)
for i, item in enumerate(data[:15], 1):
    url = item.get('metadata', {}).get('sourceURL', 'N/A')
    print(f"{i}. {url}")

print("\n" + "="*80)
print("URL PATTERN ANALYSIS:")
print("="*80)

# Categorize URLs
categories = {
    'products': [],
    'product_categories': [],
    'pages': [],
    'blogs': [],
    'other': []
}

for item in data:
    url = item.get('metadata', {}).get('sourceURL', '')
    if '/product/' in url and '/product-category/' not in url:
        categories['products'].append(url)
    elif '/product-category/' in url:
        categories['product_categories'].append(url)
    elif '/blog/' in url or '/blogs/' in url:
        categories['blogs'].append(url)
    elif any(x in url for x in ['/about', '/contact', '/terms', '/privacy', '/faq']):
        categories['pages'].append(url)
    else:
        categories['other'].append(url)

print(f"\nProducts: {len(categories['products'])}")
print(f"Product Categories: {len(categories['product_categories'])}")
print(f"Blog Posts: {len(categories['blogs'])}")
print(f"Pages: {len(categories['pages'])}")
print(f"Other: {len(categories['other'])}")

print("\n" + "="*80)
print("PRODUCT CATEGORIES FOUND:")
print("="*80)
for cat_url in categories['product_categories'][:20]:
    print(f"  - {cat_url}")

print("\n" + "="*80)
print("EXTRACTING PRICING DATA FROM PRODUCTS:")
print("="*80)

price_count = 0
for item in data[:50]:  # Check first 50 items
    markdown = item.get('markdown', '')
    url = item.get('metadata', {}).get('sourceURL', '')
    if '₹' in markdown and '/product/' in url:
        # Extract price
        prices = re.findall(r'₹[\d,]+', markdown)
        if prices:
            price_count += 1
            product_name = url.split('/')[-1]
            print(f"  Product: {product_name}")
            print(f"  Price(s): {', '.join(prices[:2])}")
            print()

print(f"\nProducts with pricing found: {price_count}/50 sampled")
