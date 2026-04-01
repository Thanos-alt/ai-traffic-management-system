"""Move yolo26n model to models directory"""

import shutil
from pathlib import Path

# Create models directory
models_dir = Path('models')
models_dir.mkdir(exist_ok=True)

# Find the downloaded model
src = Path('yolo26n.pt')
if src.exists():
    dst = models_dir / 'yolo26n.pt'
    shutil.copy2(src, dst)
    src.unlink()  # Delete from root
    print(f'✓ Moved model to {dst}')
    print(f'  Size: {dst.stat().st_size / (1024*1024):.2f} MB')
else:
    # Check in home/.ultralytics
    home_model = Path.home() / '.ultralytics' / 'models' / 'yolo26n.pt'
    if home_model.exists():
        dst = models_dir / 'yolo26n.pt'
        shutil.copy2(home_model, dst)
        print(f'✓ Copied model from {home_model}')
        print(f'  Size: {dst.stat().st_size / (1024*1024):.2f} MB')

# Delete old yolov11n if exists
old_model = models_dir / 'yolov11n.pt'
if old_model.exists():
    old_model.unlink()
    print('✓ Deleted old yolov11n.pt')

# List models directory
print('\nModels in directory:')
for model in models_dir.glob('*.pt'):
    size = model.stat().st_size / (1024*1024)
    print(f'  - {model.name}: {size:.2f} MB')
