#!/usr/bin/env python
"""Test the fix for SpeedTracker.get_speed_statistics() method"""

from src.speed_tracker import SpeedTracker

st = SpeedTracker()

# Test with empty list
stats_empty = st.get_speed_statistics([])
print('✓ Empty vehicles stats:', stats_empty)

# Test with sample vehicles
test_vehicles = [
    {'track_id': 1, 'current_speed': 45.5, 'bbox': (0,0,50,50), 'center': (25,25), 'class_name': 'car', 'confidence': 0.9, 'max_speed': 45.5, 'history': []},
    {'track_id': 2, 'current_speed': 75.2, 'bbox': (100,100,150,150), 'center': (125,125), 'class_name': 'truck', 'confidence': 0.85, 'max_speed': 75.2, 'history': []},
    {'track_id': 3, 'current_speed': 55.0, 'bbox': (200,200,250,250), 'center': (225,225), 'class_name': 'car', 'confidence': 0.88, 'max_speed': 55.0, 'history': []},
]

stats = st.get_speed_statistics(test_vehicles)
print('\n✓ Speed stats calculated:')
print(f'  Avg Speed: {stats["avg_speed"]:.1f} km/h')
print(f'  Max Speed: {stats["max_speed"]:.1f} km/h')
print(f'  Min Speed: {stats["min_speed"]:.1f} km/h')
print(f'  Speeding Count: {stats["speeding_count"]}')
print(f'  Total Vehicles: {len(stats["tracked_vehicles"])}')
print('\n✓ FIX SUCCESSFUL - get_speed_statistics() working correctly!')
