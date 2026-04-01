"""Download YOLOv26n model"""

import requests
from pathlib import Path
import sys

# Download yolo26n model
url = 'https://github.com/ultralytics/assets/releases/download/v0.0.0/yolo26n.pt'
model_dir = Path('models')
model_dir.mkdir(exist_ok=True)

# Delete old yolov11n if exists
old_model = model_dir / 'yolov11n.pt'
if old_model.exists():
    old_model.unlink()
    print('✓ Deleted old yolov11n.pt')

model_path = model_dir / 'yolo26n.pt'

print('Downloading yolo26n model...')
print(f'URL: {url}')
print('This may take 2-5 minutes...\n')

try:
    response = requests.get(url, allow_redirects=True, timeout=120, stream=True)
    response.raise_for_status()
    
    total_size = int(response.headers.get('content-length', 0))
    print(f'Expected size: {total_size/(1024*1024):.2f} MB')
    
    downloaded = 0
    with open(model_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if downloaded % (1024*1024*5) == 0:
                    print(f'  Downloaded: {downloaded/(1024*1024):.1f} MB...')
    
    actual_size = model_path.stat().st_size
    if actual_size > 100000:
        print(f'\n✓ Model downloaded successfully!')
        print(f'  Location: {model_path}')
        print(f'  Size: {actual_size/(1024*1024):.2f} MB')
    else:
        print(f'✗ Downloaded file too small')
        
except Exception as e:
    print(f'✗ Error: {e}')
    sys.exit(1)
