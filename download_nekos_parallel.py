import json
import os
import urllib.request
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
static_dir = 'static'
base_domain = 'https://adgsenpai.github.io/leagueoflegendsstaticapi/'
api_url = 'https://nekos.best/api/v2/neko'
target_count = 50
max_workers = 10  # Number of parallel downloads

# Create static directory if it doesn't exist
os.makedirs(static_dir, exist_ok=True)

# Thread-safe list for storing results
image_data = []
data_lock = threading.Lock()

def download_image(index):
    """Download a single image from the API"""
    try:
        # Fetch image info from API
        print(f"[{index}/{target_count}] Fetching image from API...")
        
        req = urllib.request.Request(api_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        with urllib.request.urlopen(req, timeout=30) as response:
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
        new_filename = f"neko_{index:03d}{extension}"
        
        # Download the image
        save_path = os.path.join(static_dir, new_filename)
        
        print(f"  [{index}] Downloading: {new_filename}")
        img_req = urllib.request.Request(image_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        with urllib.request.urlopen(img_req, timeout=30) as img_response, open(save_path, 'wb') as out_file:
            out_file.write(img_response.read())
        
        print(f"  ✓ [{index}] Saved: {new_filename} (Artist: {artist_name})")
        
        # Create image data entry
        image_entry = {
            "id": index,
            "filename": new_filename,
            "url": f"{base_domain}static/{new_filename}",
            "artist_name": artist_name,
            "artist_href": artist_href,
            "source_url": source_url,
            "original_url": image_url
        }
        
        # Thread-safe append
        with data_lock:
            image_data.append(image_entry)
        
        return True, index, None
        
    except Exception as e:
        print(f"  ✗ [{index}] Error: {e}")
        return False, index, str(e)

def save_files():
    """Save JSON and CSV files"""
    # Sort by ID
    sorted_data = sorted(image_data, key=lambda x: x['id'])
    
    # Save JSON
    json_path = 'static/directory.json'
    json_output = {
        "api_source": "nekos.best",
        "api_url": "https://nekos.best/api/v2/neko",
        "base_url": base_domain,
        "total_images": len(sorted_data),
        "images": sorted_data
    }
    
    with open(json_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(json_output, jsonfile, indent=2, ensure_ascii=False)
    
    # Save CSV
    csv_path = 'static/directory.csv'
    with open(csv_path, 'w', encoding='utf-8') as csvfile:
        csvfile.write('id,filename,url,artist_name,artist_href,source_url\n')
        for img in sorted_data:
            # Escape commas in artist names
            artist_name = img['artist_name'].replace(',', ';')
            csvfile.write(f"{img['id']},{img['filename']},{img['url']},{artist_name},{img['artist_href']},{img['source_url']}\n")
    
    return json_path, csv_path

# Main execution
print("="*70)
print(f"Starting parallel neko image downloads from nekos.best API")
print(f"Target: {target_count} images | Workers: {max_workers}")
print("="*70 + "\n")

start_time = time.time()
success_count = 0
fail_count = 0

# Use ThreadPoolExecutor for parallel downloads
with ThreadPoolExecutor(max_workers=max_workers) as executor:
    # Submit all download tasks
    future_to_index = {executor.submit(download_image, i): i for i in range(1, target_count + 1)}
    
    # Process completed tasks
    for future in as_completed(future_to_index):
        success, index, error = future.result()
        if success:
            success_count += 1
        else:
            fail_count += 1
        
        # Save files periodically (every 10 images)
        if (success_count + fail_count) % 10 == 0:
            print(f"\n📊 Progress: {success_count} success, {fail_count} failed")
            save_files()
            print("💾 Files updated!\n")

# Final save
json_path, csv_path = save_files()

end_time = time.time()
elapsed = end_time - start_time

# Summary
print("\n" + "="*70)
print("✅ Download complete!")
print(f"⏱️  Time elapsed: {elapsed:.2f} seconds")
print(f"✓ Successfully downloaded: {success_count} images")
print(f"✗ Failed: {fail_count} images")
print(f"📁 Images saved in: {static_dir}/")
print(f"📄 JSON mapping: {json_path}")
print(f"📄 CSV file: {csv_path}")
print("="*70)
