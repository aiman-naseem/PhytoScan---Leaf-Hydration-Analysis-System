import cv2
import numpy as np

def analyze_plant_health(image_path):
    img = cv2.imread(image_path)
    # 1. Convert to HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # 2. Define range for "Green"
    lower_green = np.array([35, 40, 40])
    upper_green = np.array([85, 255, 255])
    
    # 3. Create Mask and Extract Green Pixels
    mask = cv2.inRange(hsv, lower_green, upper_green)
    green_pixels = hsv[mask > 0]
    
    if len(green_pixels) == 0:
        return "No Plant Detected", 0
    
    # 4. Calculate Average Saturation and Value
    avg_sat = np.mean(green_pixels[:, 1])
    avg_val = np.mean(green_pixels[:, 2])
    
    # 5. Logic: High Saturation (>100) is usually healthy
    health_score = (avg_sat / 255) * 100
    
    status = "Healthy" if health_score > 40 else "Water Stress Detected"
    return status, round(health_score, 2)