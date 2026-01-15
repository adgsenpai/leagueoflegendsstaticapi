import json
import os
import urllib.request
import time

# Configuration
static_dir = 'static'
base_domain = 'https://adgsenpai.github.io/leagueoflegendsstaticapi/'
api_url = 'https://nekos.best/api/v2/neko'
target_count = 50

# Create static directory if it doesn't exist
os.makedirs(static_dir, exist_ok=True)

# Store the mapping
image_data = []

print("Starting neko image downloads from nekos.best API...")
print(f"Target: {target_count} images\n")

for i in range(1, target_count + 1):
    try:
        # Fetch image info from API
        print(f"[{i}/{target_count}] Fetching image from API...")
        
        req = urllib.request.Request(api_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
        
        # Extract image info
        result = data['results'][0]
        image_url = result['url']
        artist_name = result.get('artist_name', 'Unknown')
        artist_href = result.get('artist_href', '')
        source_url = result.get('source_url', '')
        
        # Extract filename and create new one
        original_filename = os.path.basename(image_url.split('?')[0])
        extension = os.path.splitext(original_filename)[1]
        new_filename = f"neko_{i:03d}{extension}"
        
        # Download the image
        save_path = os.path.join(static_dir, new_filename)
        
        print(f"  Downloading: {image_url}")
        img_req = urllib.request.Request(image_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        with urllib.request.urlopen(img_req) as img_response, open(save_path, 'wb') as out_file:
            out_file.write(img_response.read())
        
        print(f"  ✓ Saved as: {new_filename}")
        print(f"  Artist: {artist_name}\n")
        
        # Add to mapping
        image_data.append({
            "id": i,
            "filename": new_filename,
            "url": f"{base_domain}static/{new_filename}",
            "artist_name": artist_name,
            "artist_href": artist_href,
            "source_url": source_url,
            "original_url": image_url
        })
        
        # Small delay to be respectful to the API
        time.sleep(0.5)
        
    except Exception as e:
        print(f"  ✗ Error: {e}\n")
        # Wait a bit longer on error
        time.sleep(2)

# Save the JSON file
json_path = 'static/directory.json'
json_output = {
    "api_source": "nekos.best",
    "base_url": base_domain,
    "total_images": len(image_data),
    "images": image_data
}

with open(json_path, 'w', encoding='utf-8') as jsonfile:
    json.dump(json_output, jsonfile, indent=2, ensure_ascii=False)

# Also create CSV for compatibility
csv_path = 'static/directory.csv'
with open(csv_path, 'w', encoding='utf-8') as csvfile:
    csvfile.write('id,filename,url,artist_name,artist_href,source_url\n')
    for img in image_data:
        csvfile.write(f"{img['id']},{img['filename']},{img['url']},{img['artist_name']},{img['artist_href']},{img['source_url']}\n")

print("\n" + "="*60)
print("✅ Download complete!")
print(f"📁 Downloaded {len(image_data)} images to '{static_dir}' folder")
print(f"📄 Created JSON mapping: {json_path}")
print(f"📄 Created CSV file: {csv_path}")
print("="*60)
