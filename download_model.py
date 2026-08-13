"""
Download any YOLO model variant

Usage:
  python download_model.py yolov11n  # Download YOLOv11 nano
  python download_model.py yolov10n  # Download YOLOv10 nano
  python download_model.py yolov8n   # Download YOLOv8 nano
"""

import sys
from pathlib import Path

print("=" * 60)
print("YOLO MODEL DOWNLOADER")
print("=" * 60)

# Available YOLO models (as of 2026)
available_models = {
    'yolov11n': 'YOLOv11 Nano (fastest)',
    'yolov11s': 'YOLOv11 Small',
    'yolov11m': 'YOLOv11 Medium',
    'yolov11l': 'YOLOv11 Large',
    'yolov11x': 'YOLOv11 Extra-Large',
    'yolov10n': 'YOLOv10 Nano',
    'yolov10s': 'YOLOv10 Small',
    'yolov10m': 'YOLOv10 Medium',
    'yolov10l': 'YOLOv10 Large',
    'yolov10x': 'YOLOv10 Extra-Large',
    'yolov8n': 'YOLOv8 Nano',
    'yolov8s': 'YOLOv8 Small',
    'yolov8m': 'YOLOv8 Medium',
}

print("\nAvailable Models:")
print("-" * 60)
for model_name, description in available_models.items():
    print(f"  {model_name:<12} - {description}")

print("\n" + "=" * 60)

# Get model from command line or ask user
if len(sys.argv) > 1:
    requested_model = sys.argv[1].lower()
else:
    print("\nNOTE: yolov26n does not exist.")
    print("Latest YOLO versions available: v11, v10, v8")
    print("\nWhich model would you like to download?")
    print("Enter model name (e.g., yolov11n, yolov10n, yolov8n)")
    print("Or press Enter for default (yolov11n):")
    requested_model = input().strip().lower() or 'yolov11n'

if requested_model not in available_models:
    print(f"\n✗ Model '{requested_model}' not found!")
    print(f"\nAvailable models:")
    for model_name in available_models.keys():
        print(f"  - {model_name}")
    sys.exit(1)

print(f"\n📥 Downloading {requested_model}...")
print("This may take 2-5 minutes depending on your internet speed...\n")

try:
    from ultralytics import YOLO
    from pathlib import Path
    import shutil
    
    # Create models directory
    Path('models').mkdir(exist_ok=True)
    
    # Download model (Ultralytics handles this automatically)
    model = YOLO(f'{requested_model}.pt', verbose=True)
    
    # Find where Ultralytics cached the model
    import os
    yolo_home = Path.home() / '.ultralytics'
    
    # Check various locations
    possible_locations = [
        yolo_home / 'models' / f'{requested_model}.pt',
        Path.cwd() / f'{requested_model}.pt',
        yolo_home / f'{requested_model}.pt',
    ]
    
    source_model = None
    for potential_path in possible_locations:
        if potential_path.exists() and potential_path.stat().st_size > 100000:
            source_model = potential_path
            print(f'\n✓ Model found at: {source_model}')
            break
    
    if source_model and source_model.stat().st_size > 100000:
        # Copy to our models directory
        dest_model = Path('models') / f'{requested_model}.pt'
        shutil.copy2(source_model, dest_model)
        size_mb = dest_model.stat().st_size / (1024 * 1024)
        
        print(f'\n✓ Model ready!')
        print(f'  Model: {requested_model}')
        print(f'  Location: {dest_model}')
        print(f'  Size: {size_mb:.2f} MB')
        print(f'  Status: Ready to use')
        
        # Update config to use this model
        print(f'\n📝 Updating config to use {requested_model}...')
        config_file = Path('config/config.py')
        if config_file.exists():
            config_content = config_file.read_text()
            config_content = config_content.replace('MODEL_NAME = "yolov11n"', f'MODEL_NAME = "{requested_model}"')
            config_file.write_text(config_content)
            print(f'  ✓ Config updated')
        
        print(f'\n✓ Setup complete! Ready to run: python main.py')
        sys.exit(0)
    else:
        print(f'✗ Model downloaded but could not locate file')
        sys.exit(1)

except Exception as e:
    print(f'\n✗ Error: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
