# 📹 Camera Settings & Video Quality Guide

## ✅ Fixed Issues

Your camera system is now optimized for **natural, clear video capture** with:
- ✅ Fixed excessive brightness
- ✅ Better auto-exposure control
- ✅ Proper FPS handling (30 FPS stable)
- ✅ Improved contrast and clarity
- ✅ Better performance on all lighting conditions

---

## 🎥 Current Camera Configuration

All settings are now in [config/config.py](config/config.py) and are **fully customizable**:

```python
# Frame quality
FPS = 30
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

# Image properties (for natural appearance)
CAMERA_BRIGHTNESS = 0          # Range: -64 to 64
CAMERA_CONTRAST = 50           # Range: 0 to 100
CAMERA_SATURATION = 64         # Range: 0 to 128
CAMERA_GAIN = 0                # Range: 0 to 100
CAMERA_EXPOSURE = -5           # Range: -13 to -1 (lower = darker)
CAMERA_AUTO_EXPOSURE = True    # Enable smart exposure
CAMERA_WHITE_BALANCE = True    # Enable auto white balance
CAMERA_BUFFER_SIZE = 1         # Keep latest frame only
CAMERA_ENHANCE_CONTRAST = False # CLAHE enhancement (if very dark)
```

---

## 🎛️ Parameter Explanations & How to Adjust

### **CAMERA_BRIGHTNESS** (Default: 0)
```
Range: -64 to 64
- Negative (-64 to -1): Darker image
- 0: Normal brightness
- Positive (1 to 64): Brighter image

Example adjustments:
  Video too bright? → Set to -20 or -30
  Video too dark? → Set to 10 or 20
```

### **CAMERA_CONTRAST** (Default: 50)
```
Range: 0 to 100
- 50: Normal contrast
- 0-40: Low contrast (washed out)
- 51-100: High contrast (more detail)

Example adjustments:
  For clear vehicle detection → 50-70
  For harsh lighting → 40-60
```

### **CAMERA_SATURATION** (Default: 64)
```
Range: 0 to 128
- 64: Normal saturation
- 0-50: Less saturated (more natural colors)
- 65-128: More saturated (vibrant colors)

Example adjustments:
  For traffic analysis → 50-70
  For natural appearance → 60-64
```

### **CAMERA_GAIN** (Default: 0)
```
Range: 0 to 100
- 0: No gain (normal)
- 1-100: Increases sensor sensitivity

Example adjustments:
  Low light conditions → 20-50
  Normal conditions → 0-10
  Well-lit conditions → 0
```

### **CAMERA_EXPOSURE** (Default: -5)
```
Range: -13 to -1
- Lower number (-13): Much darker, more detail preservation
- Higher number (-1): Brighter, less detail

Example adjustments:
  Bright/sunny conditions → -8 to -13 (preserve details)
  Night/low light → -1 to -3 (brighter)
  Overcast → -5 (default, good balance)
```

### **CAMERA_AUTO_EXPOSURE** (Default: True)
```
Options: True or False
- True: Camera automatically adjusts exposure (RECOMMENDED)
- False: Manual exposure mode (use CAMERA_EXPOSURE value)

When to use False:
  - You want consistent exposure despite lighting changes
  - Specific manual tuning needed
```

### **CAMERA_WHITE_BALANCE** (Default: True)
```
Options: True or False
- True: Automatic white balance (RECOMMENDED)
- False: Fixed white balance

When to disable:
  - Specific color consistency needed
  - Under controlled lighting
```

### **CAMERA_ENHANCE_CONTRAST** (Default: False)
```
Options: True or False
- False: Normal processing (RECOMMENDED for performance)
- True: CLAHE enhancement (use only if video is very dark)

When to enable:
  - Video is too dark even after other adjustments
  - Need to enhance local contrast
  - Note: Uses more CPU, may reduce FPS
```

---

## 🚗 Recommended Presets

### **Preset 1: Sunny/Bright Road**
```python
CAMERA_BRIGHTNESS = -20
CAMERA_CONTRAST = 60
CAMERA_EXPOSURE = -10
CAMERA_GAIN = 0
CAMERA_ENHANCE_CONTRAST = False
```

### **Preset 2: Overcast/Normal Lighting**
```python
CAMERA_BRIGHTNESS = 0
CAMERA_CONTRAST = 50
CAMERA_EXPOSURE = -5
CAMERA_GAIN = 10
CAMERA_ENHANCE_CONTRAST = False
```

### **Preset 3: Night/Low Light**
```python
CAMERA_BRIGHTNESS = 15
CAMERA_CONTRAST = 45
CAMERA_EXPOSURE = -2
CAMERA_GAIN = 40
CAMERA_ENHANCE_CONTRAST = True
```

### **Preset 4: High Contrast (Best for vehicle detection)**
```python
CAMERA_BRIGHTNESS = 0
CAMERA_CONTRAST = 70
CAMERA_EXPOSURE = -6
CAMERA_GAIN = 5
CAMERA_ENHANCE_CONTRAST = False
```

---

## 📊 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| **Video too bright/washed out** | Reduce CAMERA_BRIGHTNESS to -20/-30, or lower CAMERA_EXPOSURE to -10 |
| **Video too dark** | Increase CAMERA_BRIGHTNESS to 10-20, increase CAMERA_GAIN to 20-50 |
| **Poor object detection (cars invisible)** | Increase CAMERA_CONTRAST to 60-70 |
| **Colors look unnatural** | Check CAMERA_SATURATION (64 is normal), enable CAMERA_WHITE_BALANCE |
| **Jerky/choppy video** | Check FPS=30, ensure system has enough CPU. If still slow, reduce FRAME_WIDTH/FRAME_HEIGHT |
| **Blurry video** | Increase CAMERA_CONTRAST, check autofocus is enabled |

---

## 🔧 How to Change Settings

### Step 1: Open config file
```bash
# Edit the camera settings in:
config/config.py
```

### Step 2: Adjust parameters
```python
# Example: Make video less bright and more contrasty
CAMERA_BRIGHTNESS = -15      # Was 0
CAMERA_CONTRAST = 65         # Was 50
CAMERA_EXPOSURE = -8         # Was -5
```

### Step 3: Save and run
```bash
python main.py
```

The new settings take effect **immediately** the next time you start the application.

---

## 📹 Video Quality Targets

Your system is now optimized for:
- ✅ **Resolution**: 1280x720 (HD quality)
- ✅ **FPS**: 30 frames/second (smooth)
- ✅ **Brightness**: Natural, not washed out
- ✅ **Contrast**: Clear vehicle detection
- ✅ **Latency**: Minimal (single frame buffer)
- ✅ **CPU Usage**: Optimized

---

## 🎯 What Changed

### Before (Issues)
- Hardcoded brightness boost: +20 pixels
- Alpha scaling: 1.2x brightness increase
- Results: Washed out video, lost details

### After (Fixed)
- Camera auto-exposure enabled
- Configurable brightness/contrast
- Natural video quality
- Optional CLAHE enhancement for dark videos
- Better vehicle detection

---

## 🚀 Run with Optimized Settings

```bash
# This should now show natural, clear video
python main.py
```

If you need adjustments:
```bash
# Edit config/config.py with presets above
# Then restart the application
```

---

## 💡 Tips

1. **Test different presets** - Try each preset setting to find the best for your specific camera and location
2. **Use AUTO modes** - Leave CAMERA_AUTO_EXPOSURE and CAMERA_WHITE_BALANCE on True (better adaptation)
3. **Stability** - Once you find good settings, they're saved in config.py and consistent across runs
4. **Performance** - If FPS drops, disable CAMERA_ENHANCE_CONTRAST (uses CPU)
5. **Monitor logs** - The app logs which settings are applied at startup

---

## ✅ System Status

- ✅ Camera brightness fixed
- ✅ FPS optimized (30 FPS)
- ✅ Resolution set to 1280x720 (HD)
- ✅ Auto-exposure enabled
- ✅ Configuration fully customizable
- ✅ Ready for production use

**Your system is now ready for clear, natural video analysis!** 📹✨
