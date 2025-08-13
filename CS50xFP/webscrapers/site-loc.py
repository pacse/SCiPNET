'''
Script to find the location of a site, based on it's left & top positions on
the large map here: https://scp-wiki.wikidot.com/secure-facilities-locations

Created by me, with teaching from ChatGPT
(chat: https://chatgpt.com/share/689bea0a-bc40-8004-a5ce-512f5339c913)
'''

# data from ChatGPT to calibrate when we find cords
calibration_points = [
	# site name, left %, top %, long (est), lat (est)
    {"site": 7,     "left_pct": 13.0, "top_pct": 11.0, "lat": 64.5000,  "lon": -165.0000},  # Norton Sound (~80 km offshore)
    {"site": "6-3", "left_pct": 48.7, "top_pct": 19.8, "lat": 48.6900,  "lon":   6.1800},   # Lorraine (Nancy approx)
    {"site": 11,    "left_pct": 26.6, "top_pct": 23.2, "lat": 42.7325,  "lon": -84.5555},   # Lansing, MI
    {"site": 12,    "left_pct": 46.6, "top_pct": 18.6, "lat": 50.7200,  "lon":  -3.5000},   # Devon (Exeter approx)
    {"site": 14,    "left_pct": 16.5, "top_pct": 26.3, "lat": 38.5816,  "lon": -121.4944},  # Sacramento, CA
    {"site": 28,    "left_pct": 28.6, "top_pct": 24.9, "lat": 40.7240,  "lon": -74.0000},   # SoHo, NYC
    {"site": 36,    "left_pct": 66.9, "top_pct": 32.8, "lat": 24.1710,  "lon":  72.4380},   # Banaskantha (Palanpur approx)
    {"site": 50,    "left_pct": 83.5, "top_pct": 28.0, "lat": 35.6938,  "lon": 139.7534},   # Chiyoda City, Tokyo
    {"site": 54,    "left_pct": 50.3, "top_pct": 18.2, "lat": 51.3397,  "lon":  12.3731},   # Leipzig
    {"site": 80,    "left_pct": 51.0, "top_pct": 13.8, "lat": 58.6500,  "lon":  14.6000},   # Tiveden National Park
    {"site": 95,    "left_pct": 84.8, "top_pct": 76.5, "lat": -42.8821, "lon": 147.3272},   # Hobart, Tasmania
    {"site": 120,   "left_pct": 52.3, "top_pct": 18.5, "lat": 50.8100,  "lon":  19.1200},   # Częstochowa
]