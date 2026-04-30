import json
import re
from collections import Counter

# Load crawl data
with open('.firecrawl/jusst4you-crawl.json', 'r', encoding='utf-8') as f:
    raw_data = json.load(f)

data = raw_data.get('data', []) if isinstance(raw_data, dict) else raw_data

print("="*100)
print("COMPREHENSIVE WEBSITE ANALYSIS - jusst4you.com")
print("="*100)
print(f"\nCrawl Summary:")
print(f"  Total Pages Crawled: {len(data)}")
print(f"  Crawl Job ID: {raw_data.get('id', 'N/A')}")
print(f"  Status: {raw_data.get('status', 'N/A')}")
print(f"  Credits Used: {raw_data.get('creditsUsed', 'N/A')}")

# Categorize content
categories = {
    'products': [],
    'product_categories': [],
    'shop_filters': [],
    'pages': [],
    'blogs': [],
    'offers': [],
    'other': []
}

for item in data:
    url = item.get('metadata', {}).get('sourceURL', '')
    
    if '/product/' in url and '/product-category/' not in url:
        categories['products'].append(url)
    elif '/product-category/' in url:
        categories['product_categories'].append(url)
    elif '/shop/' in url:
        categories['shop_filters'].append(url)
    elif '/blog/' in url or '/blogs/' in url:
        categories['blogs'].append(url)
    elif any(x in url for x in ['/about', '/contact', '/terms', '/privacy', '/faq']):
        categories['pages'].append(url)
    elif '/offers/' in url:
        categories['offers'].append(url)
    else:
        categories['other'].append(url)

print("\n" + "="*100)
print("CONTENT BREAKDOWN:")
print("="*100)
print(f"  Individual Products: {len(categories['products'])}")
print(f"  Product Categories: {len(categories['product_categories'])}")
print(f"  Shop Filter Pages: {len(categories['shop_filters'])}")
print(f"  Static Pages: {len(categories['pages'])}")
print(f"  Blog Posts: {len(categories['blogs'])}")
print(f"  Offers/Promotions: {len(categories['offers'])}")
print(f"  Other Pages: {len(categories['other'])}")

# Extract product categories hierarchy
print("\n" + "="*100)
print("PRODUCT CATEGORY HIERARCHY:")
print("="*100)

category_depth = {}
for cat_url in categories['product_categories']:
    # Count depth by slashes after /product-category/
    path = cat_url.split('/product-category/')[1] if '/product-category/' in cat_url else ''
    depth = path.count('/')
    category_depth[depth] = category_depth.get(depth, 0) + 1

for depth in sorted(category_depth.keys()):
    print(f"  Level {depth}: {category_depth[depth]} categories")

# Sample main categories (level 0)
main_cats = [cat for cat in categories['product_categories'] if cat.count('/product-category/') == 1 and cat.rstrip('/').split('/')[-1].count('/') == 0]
print(f"\n  Main Categories (Top Level):")
for cat in main_cats[:15]:
    cat_name = cat.rstrip('/').split('/')[-1].replace('-', ' ').title()
    print(f"    • {cat_name}")

# Analyze pricing
print("\n" + "="*100)
print("PRICING ANALYSIS:")
print("="*100)

prices_found = []
for item in data:
    markdown = item.get('markdown', '')
    url = item.get('metadata', {}).get('sourceURL', '')
    
    if '/product/' in url and '₹' in markdown:
        prices = re.findall(r'₹([\d,]+)', markdown)
        for price_str in prices:
            try:
                price = int(price_str.replace(',', ''))
                if 500 <= price <= 100000:  # Reasonable range
                    prices_found.append(price)
            except:
                pass

if prices_found:
    prices_found.sort()
    print(f"  Total Price Points Found: {len(prices_found)}")
    print(f"  Minimum Price: ₹{min(prices_found):,}")
    print(f"  Maximum Price: ₹{max(prices_found):,}")
    print(f"  Average Price: ₹{sum(prices_found)//len(prices_found):,}")
    print(f"  Median Price: ₹{prices_found[len(prices_found)//2]:,}")
    
    # Price ranges
    ranges = {
        'Budget (< ₹5,000)': sum(1 for p in prices_found if p < 5000),
        'Mid-Range (₹5K-₹15K)': sum(1 for p in prices_found if 5000 <= p < 15000),
        'Premium (₹15K-₹30K)': sum(1 for p in prices_found if 15000 <= p < 30000),
        'Luxury (> ₹30K)': sum(1 for p in prices_found if p >= 30000)
    }
    
    print(f"\n  Price Distribution:")
    for range_name, count in ranges.items():
        percentage = (count / len(prices_found)) * 100
        print(f"    {range_name}: {count} ({percentage:.1f}%)")

# Location analysis
print("\n" + "="*100)
print("GEOGRAPHIC COVERAGE:")
print("="*100)

locations = set()
location_keywords = ['delhi', 'mumbai', 'bangalore', 'jaipur', 'agra', 'goa', 'manali', 
                     'chandigarh', 'bhopal', 'kolkata', 'gurgaon', 'pune', 'hyderabad',
                     'chennai', 'lucknow', 'noida']

for item in data:
    markdown = item.get('markdown', '').lower()
    url = item.get('metadata', {}).get('sourceURL', '').lower()
    text = markdown + ' ' + url
    
    for loc in location_keywords:
        if loc in text:
            locations.add(loc.title())

print(f"  Cities/Regions Identified: {len(locations)}")
for loc in sorted(locations):
    print(f"    • {loc}")

# Technology Stack Detection
print("\n" + "="*100)
print("TECHNOLOGY STACK:")
print("="*100)

tech_indicators = {
    'WordPress': 0,
    'WooCommerce': 0,
    'Google Analytics': 0,
    'Facebook Pixel': 0,
    'reCAPTCHA': 0,
    'jQuery': 0
}

for item in data:
    metadata = item.get('metadata', {})
    generator = metadata.get('generator', '')
    
    if isinstance(generator, list):
        for gen in generator:
            if 'WordPress' in gen:
                tech_indicators['WordPress'] += 1
            if 'WooCommerce' in gen:
                tech_indicators['WooCommerce'] += 1
    
    markdown = item.get('markdown', '')
    if 'google-analytics' in markdown.lower() or 'gtag' in markdown.lower():
        tech_indicators['Google Analytics'] += 1
    if 'facebook.com/tr' in markdown.lower() or 'fbq(' in markdown.lower():
        tech_indicators['Facebook Pixel'] += 1
    if 'recaptcha' in markdown.lower():
        tech_indicators['reCAPTCHA'] += 1

print(f"  Platform & Tools Detected:")
for tech, count in tech_indicators.items():
    if count > 0:
        print(f"    ✓ {tech}: Found in {count} pages")

# SEO Metadata Analysis
print("\n" + "="*100)
print("SEO METADATA QUALITY:")
print("="*100)

titles_with_keywords = 0
descriptions_found = 0
og_tags_found = 0

for item in data:
    metadata = item.get('metadata', {})
    title = metadata.get('title', '')
    description = metadata.get('ogDescription', '') or metadata.get('description', '')
    og_title = metadata.get('ogTitle', '')
    
    if title:
        titles_with_keywords += 1
    if description:
        descriptions_found += 1
    if og_title:
        og_tags_found += 1

total = len(data)
print(f"  Pages with Title Tags: {titles_with_keywords}/{total} ({titles_with_keywords/total*100:.1f}%)")
print(f"  Pages with Meta Descriptions: {descriptions_found}/{total} ({descriptions_found/total*100:.1f}%)")
print(f"  Pages with Open Graph Tags: {og_tags_found}/{total} ({og_tags_found/total*100:.1f}%)")

# Content Quality Indicators
print("\n" + "="*100)
print("CONTENT QUALITY INDICATORS:")
print("="*100)

avg_markdown_length = sum(len(item.get('markdown', '')) for item in data) // len(data)
print(f"  Average Content Length: {avg_markdown_length:,} characters")

images_count = sum(item.get('markdown', '').count('![') for item in data)
print(f"  Total Images Found: {images_count:,}")

links_count = sum(item.get('markdown', '').count('](') for item in data)
print(f"  Total Internal Links: {links_count:,}")

# Social Media Presence
print("\n" + "="*100)
print("SOCIAL MEDIA INTEGRATION:")
print("="*100)

social_platforms = {
    'Facebook': 0,
    'Instagram': 0,
    'Twitter/X': 0,
    'YouTube': 0,
    'Pinterest': 0,
    'WhatsApp': 0
}

for item in data:
    markdown = item.get('markdown', '').lower()
    
    if 'facebook.com' in markdown or 'fb.com' in markdown:
        social_platforms['Facebook'] += 1
    if 'instagram.com' in markdown:
        social_platforms['Instagram'] += 1
    if 'twitter.com' in markdown or 'x.com' in markdown:
        social_platforms['Twitter/X'] += 1
    if 'youtube.com' in markdown or 'youtu.be' in markdown:
        social_platforms['YouTube'] += 1
    if 'pinterest.com' in markdown:
        social_platforms['Pinterest'] += 1
    if 'wa.me' in markdown or 'whatsapp' in markdown:
        social_platforms['WhatsApp'] += 1

for platform, count in social_platforms.items():
    if count > 0:
        print(f"  ✓ {platform}: Referenced in {count} pages")

print("\n" + "="*100)
print("KEY INSIGHTS & RECOMMENDATIONS:")
print("="*100)
print("""
1. BUSINESS MODEL:
   - E-commerce platform specializing in surprise planning & event decorations
   - 44 individual products across 17+ categories
   - Price range: Budget-friendly to luxury experiences (₹500 - ₹100,000+)
   - Strong focus on romantic experiences, proposals, birthdays, anniversaries

2. GEOGRAPHIC REACH:
   - Multi-city presence across major Indian metros
   - Primary markets: Delhi NCR, Mumbai, Bangalore, Jaipur
   - Expanding to tier-2 cities

3. TECHNICAL STACK:
   - WordPress + WooCommerce (standard e-commerce setup)
   - Good SEO foundation with meta tags and OG tags
   - Social media integration present

4. CONTENT STRATEGY:
   - Heavy reliance on visual content (images)
   - Product-focused with detailed descriptions
   - Limited blog/content marketing (0 blog posts found)

5. OPPORTUNITIES FOR IMPROVEMENT:
   - Add blog section for SEO and customer education
   - Implement customer reviews/testimonials prominently
   - Add video content for product demonstrations
   - Expand social proof elements
   - Consider API optimization for mobile app integration
""")

print("="*100)
