# 🎨 Vehicle Color Coding Guide

Your traffic management system now uses **distinct colors** for different vehicle types for easy visual identification!

## Color Legend

### 👥 Pedestrians & Small Vehicles
| Color | Hex | Objects |
|-------|-----|---------|
| 🟡 Yellow | `(0, 255, 255)` | Person, Human, Pedestrian |
| 🟢 Green | `(0, 255, 0)` | Bicycle, Cycle, Bike |
| 🔷 Cyan | `(255, 255, 0)` | Motorcycle, Scooter |

### 🚗 Regular Vehicles
| Color | Hex | Objects |
|-------|-----|---------|
| 🔵 Blue | `(255, 0, 0)` | Car, Sedan |
| 🔷 Dark Blue | `(255, 100, 0)` | SUV |
| 🔷 Darker Blue | `(255, 50, 0)` | Hatchback |
| 🟠 Gold | `(0, 215, 255)` | VIP Car, Luxury Car |
| 🔷 Cyan | `(200, 200, 0)` | Taxi |

### 🚌 Heavy Vehicles
| Color | Hex | Objects |
|-------|-----|---------|
| 🔴 Red | `(0, 0, 255)` | Bus |
| 🟠 Orange | `(0, 128, 255)` | Truck, Lorry |
| 🟠 Light Orange | `(0, 150, 255)` | Van |
| 🟠 Orange-Light | `(100, 150, 200)` | Auto, Autorickshaw |
| 🟤 Brown | `(180, 100, 50)` | Tractor |
| 🟤 Dark Brown | `(150, 100, 50)` | Cart |

### 🚨 Emergency Vehicles
| Color | Hex | Objects |
|-------|-----|---------|
| 🟣 Magenta/Purple | `(200, 0, 200)` | Ambulance, Emergency |
| 🔷 Light Blue | `(150, 150, 255)` | Police Car |
| 🟠 Bright Orange | `(0, 100, 255)` | Fire Brigade, Fire Engine, Fire Truck |

### 🎖️ Special Vehicles
| Color | Hex | Objects |
|-------|-----|---------|
| 🟢 Dark Green | `(0, 128, 0)` | Military, Army |
| 🟠 Light Orange | `(100, 200, 255)` | Sprinkler, Water Tanker |
| ⚫ Gray | `(100, 100, 100)` | Garbage Truck |
| ⚫ Light Gray | `(150, 150, 150)` | Cement Mixer |
| 🟤 Dark Orange | `(150, 75, 0)` | Crane |

### ⚪ Unknown/Unclassified
| Color | Hex | Objects |
|-------|-----|---------|
| ⚫ Gray | `(128, 128, 128)` | Unknown/Unclassified |

---

## 📊 How It Works

When the YOLO detector identifies objects in the video:

1. ✅ Exact match → Gets specific color
2. ✅ Partial match → Gets corresponding color
3. ✅ Unknown type → Gets gray color (default)

### Examples

```
"Car" → Blue (255, 0, 0)
"Police Car" → Light Blue (150, 150, 255)
"Fire Truck" → Bright Orange (0, 100, 255)
"VIPCar" → Gold (0, 215, 255)
"Ambulance" → Magenta (200, 0, 200)
"Human" → Yellow (0, 255, 255)
"Unknown" → Gray (128, 128, 128)
```

---

## 🎯 Quick Visual Reference

```
PEDESTRIANS & CYCLES
  🟡 Yellow = Person/Human
  🟢 Green  = Bicycle/Cycle
  🔷 Cyan   = Motorcycle/Scooter

REGULAR CARS
  🔵 Blue   = Car/Sedan
  🟠 Gold   = VIP/Luxury

HEAVY VEHICLES
  🔴 Red    = Bus
  🟠 Orange = Truck/Lorry
  🟤 Brown  = Tractor

EMERGENCY
  🟣 Purple = Ambulance
  🔷 LtBlue = Police
  🟠 Bright = Fire Brigade

SPECIAL
  🟢 DkGrn  = Military
  ⚫ Gray   = Unknown
```

---

## 🚀 Usage

Simply run:
```bash
python main.py
```

**The video will show:**
- Bounding boxes around detected objects
- **Different colors** for different vehicle types
- Easy visual identification of traffic composition
- **Speed labels** (if enabled) in the respective colors

---

## 🔧 How to Customize Colors

Edit the `get_box_color()` method in `main.py` (around line 683):

```python
color_map = {
    "your_class": (B, G, R),  # BGR format (OpenCV style)
    ...
}
```

**Note:** OpenCV uses BGR (Blue, Green, Red) format, not RGB!

---

## 📺 What You'll See

Live video feed with:
- ✅ Yellow boxes around pedestrians
- ✅ Green boxes around bicycles
- ✅ Blue boxes around cars
- ✅ Gold boxes around VIP/luxury vehicles
- ✅ Red boxes around buses
- ✅ Orange boxes around trucks
- ✅ Magenta boxes around ambulances
- ✅ Light blue boxes around police cars
- ✅ Bright orange boxes around fire vehicles
- ✅ Gray boxes around unknown objects

**Perfect for quick visual traffic analysis!** 🎨

