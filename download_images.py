import csv
import json
import os
import urllib.request
from urllib.parse import urlparse
import time

# Read the CSV file
csv_path = 'static/directory.csv'
static_dir = 'static'
base_domain = 'https://adgsenpai.github.io/leagueoflegendsstaticapi/'

# Create static directory if it doesn't exist
os.makedirs(static_dir, exist_ok=True)

# Store the mapping
image_data = []

print("Starting image downloads...")

with open(csv_path, 'r', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    
    for row in reader:
        image_id = row['id']
        description = row['description']
        url = row['url']
        
        # Extract the filename from URL
        parsed_url = urlparse(url)
        original_filename = os.path.basename(parsed_url.path)
        
        # Create a new filename with ID prefix
        extension = os.path.splitext(original_filename)[1]
        new_filename = f"lol_meme_{image_id}{extension}"
        
        # Full path to save the image
        save_path = os.path.join(static_dir, new_filename)
        
        try:
            # Download the image with proper headers
            print(f"Downloading {description} from {url}...")
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            
            with urllib.request.urlopen(req) as response, open(save_path, 'wb') as out_file:
                out_file.write(response.read())
            
            print(f"  ✓ Saved as: {new_filename}")
            
            # Add to mapping
            image_data.append({
                "id": int(image_id),
                "description": description,
                "filename": new_filename,
                "url": f"{base_domain}static/{new_filename}",
                "original_url": url
            })
            
            # Add delay to avoid rate limiting
            time.sleep(1)
            
        except Exception as e:
            print(f"  ✗ Error downloading {url}: {e}")

# Save the JSON file
json_path = 'static/directory.json'
with open(json_path, 'w', encoding='utf-8') as jsonfile:
    json.dump({
        "base_url": base_domain,
        "total_images": len(image_data),
        "images": image_data
    }, jsonfile, indent=2)

print(f"\n✅ Download complete!")
print(f"📁 Downloaded {len(image_data)} images to '{static_dir}' folder")
print(f"📄 Created mapping file: {json_path}")
