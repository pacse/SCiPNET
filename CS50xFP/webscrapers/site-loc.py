'''
Script to find the location of a site, based on it's left & top positions on
the large map here: https://scp-wiki.wikidot.com/secure-facilities-locations

Created by me, with teaching from ChatGPT
(chat: https://chatgpt.com/share/689bea0a-bc40-8004-a5ce-512f5339c913)
'''
from time import perf_counter as pf_ctr

prg_srt = pf_ctr() # program start time

def print_done(s) -> None:
    print(f"Done (took {(pf_ctr()-s):.5f} s)\n")


print("Initializing numpy . . .")
s = pf_ctr()

import numpy as np

print_done(s)

print("Initalizing and validating calibration points . . .")
s = pf_ctr()

# data from ChatGPT to calibrate when we find cords
calibration_points = [
	# site name, left %, top %, long (est), lat (est)
    {"site": 7,     "left_pf_ctrt": 13.0, "top_pf_ctrt": 11.0, "lat": 64.5000,  "lon": -165.0000},  # Norton Sound (~80 km offshore)
    {"site": "6-3", "left_pf_ctrt": 48.7, "top_pf_ctrt": 19.8, "lat": 48.6900,  "lon":   6.1800},   # Lorraine (Nancy approx)
    {"site": 11,    "left_pf_ctrt": 26.6, "top_pf_ctrt": 23.2, "lat": 42.7325,  "lon": -84.5555},   # Lansing, MI
    {"site": 12,    "left_pf_ctrt": 46.6, "top_pf_ctrt": 18.6, "lat": 50.7200,  "lon":  -3.5000},   # Devon (Exeter approx)
    {"site": 14,    "left_pf_ctrt": 16.5, "top_pf_ctrt": 26.3, "lat": 38.5816,  "lon": -121.4944},  # Sacramento, CA
    {"site": 28,    "left_pf_ctrt": 28.6, "top_pf_ctrt": 24.9, "lat": 40.7240,  "lon": -74.0000},   # SoHo, NYC
    {"site": 36,    "left_pf_ctrt": 66.9, "top_pf_ctrt": 32.8, "lat": 24.1710,  "lon":  72.4380},   # Banaskantha (Palanpur approx)
    {"site": 50,    "left_pf_ctrt": 83.5, "top_pf_ctrt": 28.0, "lat": 35.6938,  "lon": 139.7534},   # Chiyoda City, Tokyo
    {"site": 54,    "left_pf_ctrt": 50.3, "top_pf_ctrt": 18.2, "lat": 51.3397,  "lon":  12.3731},   # Leipzig
    {"site": 80,    "left_pf_ctrt": 51.0, "top_pf_ctrt": 13.8, "lat": 58.6500,  "lon":  14.6000},   # Tiveden National Park
    {"site": 95,    "left_pf_ctrt": 84.8, "top_pf_ctrt": 76.5, "lat": -42.8821, "lon": 147.3272},   # Hobart, Tasmania
    {"site": 120,   "left_pf_ctrt": 52.3, "top_pf_ctrt": 18.5, "lat": 50.8100,  "lon":  19.1200},   # Częstochowa
]

# sanity check
for site in calibration_points:
    assert site["lat"] < 90 and site["lat"] > -90, f"Error with site: Latitude Invalid\nSite Data:\n{site}"
    assert site["lon"] < 180 and site["lat"] > -180, f"Error with site: Longitude Invalid\nSite Data:\n{site}"

print_done(s)

print("Building raw data arrays . . .")
s = pf_ctr()

left_pf_ctrt = np.array([site["left_pf_ctrt"] for site in calibration_points], dtype=float) # all left %'s
top_pf_ctrt = np.array([site["top_pf_ctrt"] for site in calibration_points], dtype=float)   # all top %'s
true_lat = np.array([site["lat"] for site in calibration_points], dtype=float) # all latitudes
true_lon = np.array([site["lon"] for site in calibration_points], dtype=float) # all longitudes

print_done(s)

print("Normalizing & Building design matrix A . . .")
s = pf_ctr()

# get percentages to be decimals
x = left_pf_ctrt / 100.0
y = top_pf_ctrt  / 100.0

# build design matrix (magic)
A = np.column_stack([
    np.ones_like(x),
    x,
    y,
    x**2,
    x*y,
    y**2
])

print_done(s)

print("Fitting latitide & longitude coefficients . . .") # magic
s = pf_ctr()

lat_coeffs, *_ = np.linalg.lstsq(A, true_lat, rcond=None)
#print(lat_coeffs)

lon_coeffs, *_ = np.linalg.lstsq(A, true_lat, rcond=None)
#print(lat_coeffs)

print_done(s)

# predict control points for RMSE in degrees (magic)
print("Computing accuracy . . .")
s = pf_ctr()

pred_lat = A @ lat_coeffs
pred_lon = A @ lon_coeffs

res_lat = pred_lat - true_lat
res_lon = pred_lon - true_lon

lat_rmse = np.sqrt(np.mean(res_lat ** 2))
lon_rmse = np.sqrt(np.mean(res_lat ** 2))
combined_rmse = np.sqrt(np.mean((res_lat ** 2 + res_lon ** 2)))

print(f"{lat_rmse:.5f}\n{lon_rmse:.5f}\n{combined_rmse:.5f}")

print_done(s)

print(f"Program end - Total time: {(pf_ctr()-prg_srt):.5f} s")