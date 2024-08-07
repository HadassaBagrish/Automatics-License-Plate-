import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import cv2
import urllib3
from urllib.parse import urlencode
from sklearn.cluster import KMeans  # ייבוא KMeans מ scikit-learn
import numpy as np
import webcolors
from datetime import datetime  # Importing datetime class directly


def closest_color(rgb_color):
    css3_hex_to_names = {webcolors.hex_to_rgb(hex_code): name for name, hex_code in webcolors.CSS3_NAMES_TO_HEX.items()}
    min_dist = float('inf')
    closest_name = None
    for color, name in css3_hex_to_names.items():
        dist = np.linalg.norm(np.array(color) - np.array(rgb_color))
        if dist < min_dist:
            min_dist = dist
            closest_name = name
    return closest_name


def get_dominant_color(image, k=4):
    # Reshape the image to have two dimensions
    image_flat = image.reshape((-1, 3))

    # Apply KMeans clustering
    kmeans = KMeans(n_clusters=k)
    kmeans.fit(image_flat)

    # Get the dominant colors
    dominant_colors = kmeans.cluster_centers_

    # Convert dominant color to integer
    dominant_colors = dominant_colors.astype(int)
    return dominant_colors[0]  # Return the most dominant color



def get_dominant_color1(image, k=1):

    pixels = image.reshape((-1, 3))

    # שימוש KMeans כדי למצוא את הצבע הדומיננטי
    kmeans = KMeans(n_clusters=k)
    kmeans.fit(pixels)

    # קבללת ערכי RGB של הצבע הדומיננטי
    dominant_colors = kmeans.cluster_centers_.astype(int)
    return dominant_colors[0] if k == 1 else dominant_colors

def convert_rgb_to_name(rgb_color):
    requested_color = rgb_color
    min_colors = {}
    for name, hex_value in webcolors.css3_names_to_hex.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(hex_value)
        rd = (r_c - requested_color[0]) ** 2
        gd = (g_c - requested_color[1]) ** 2
        bd = (b_c - requested_color[2]) ** 2
        min_colors[(rd + gd + bd)] = name
    print(min_colors[min(min_colors.keys())])

    r, g, b = rgb_color
    if 122 <= r <= 135 and 122 <= g <= 135 and 112 <= b <= 136:
        return 'קפה מטאלי' ,"אפור","שנהב לבן" ,"כסף מטלי"
    elif 100 <= r <= 105 and 100 <= g <= 105 and 100 <= b <= 105:
        return 'כחול כהה',"שנהב לבן","שחור מטלי"
    elif 104 <= r <= 160 and 100 <= g <= 160 and 100 <= g <= 160:
        return 'שנהב לבן', 'כסף', 'כחול', "כסף מטלי", "כסוף כהה מטלי" ,"כחול מטל" ,"רב גווני" ,"תכלת מטאלי" ,"בז" ,"כסף כחלחל מטלי"
    elif 70 <= r <= 105 and 70 <= g <= 105 and 70 <= b <= 115:
        return 'כסוף מטלי', "שחור מטלי", "אפור כהה" ,"שחור","כסף","כסף מטאלי"
    elif 150 <= r <= 180 and 150 <= g <= 180 and 150 <= b <= 200:
        return 'שנהב לבן',"רב גווני"
    elif 0 <= r <= 50 and 200 <= g <= 255 and 0 <= b <= 50:
        return 'ירוק'
    elif 0 <= b <= 70 and 0 <= g <= 70 and 0 <= r <= 70:
        return 'כחול פנינה'
    elif 200 <= r <= 255 and 200 <= g <= 255 and 0 <= b <= 50:
        return 'צהוב'
    elif 0 <= r <= 50 and 200 <= g <= 255 and 200 <= b <= 255:
        return 'טורקיז'
    elif 200 <= r <= 255 and 0 <= g <= 50 and 200 <= b <= 255:
        return 'מגנטה'
    elif 0 <= r <= 50 and 0 <= g <= 50 and 0 <= b <= 50:
        return 'שחור'
    elif 200 <= r <= 255 and 200 <= g <= 255 and 200 <= b <= 255:
        return 'לבן'
    # elif 100 <= r <= 150 and 100 <= g <= 150 and 100 <= b <= 150:
    #     return 'אפור'

    elif 180 <= r <= 200 and 180 <= g <= 200 and 180 <= b <= 200:
        return 'כהה'
    elif 180 <= b <= 255 and 180 <= g <= 220 and 140 <= r <= 200:
        return 'בז מטאלי'
    elif 160 <= r <= 185 and 200 <= g <= 225 and 220 <= b <= 240:
        return 'תכלת מטאלי'
    elif 69 <= r <= 100 and 60 <= g <= 100 and 60 <= b <= 105:
        return 'כסף'
    elif 30 <= r <= 50 and 30 <= g <= 50 and 30 <= b <= 50:
        return 'אפור כהה'
    elif 50 <= b <= 80 and 80 <= g <= 120 and 110 <= r <= 150:
        return 'אפור כהה מטלי'
    elif 160 <= r <= 185 and 200 <= g <= 225 and 220 <= b <= 240:
        return 'כחול בהיר'
    elif 0 <= r <= 20 and 110 <= g <= 140 and 0 <= b <= 20:
        return 'ירוק כהה'
    elif 100 <= b <= 150 and 100 <= g <= 150 and 100 <= r <= 150:
        return 'אפור'
    elif 150 <= b <= 200 and 130 <= g <= 160 and 90 <= r <= 120:
        return 'קרם'

    elif 100 <= r <= 150 and 0 <= g <= 30 and 0 <= b <= 30:
        return 'בורדו מטלי'
    elif 60 <= r <= 80 and 90 <= g <= 120 and 120 <= b <= 150:
        return 'אפור פלדה'
    elif 100 <= b <= 150 and 90 <= g <= 140 and 100 <= r <= 120:
        return 'אפור בהיר מטלי'
    elif 20 <= r <= 40 and 20 <= g <= 40 and 20 <= b <= 40:
        return 'שחור מטלי'
    elif 240 <= r <= 255 and 190 <= g <= 220 and 0 <= b <= 30:
        return 'זהב'
    else:
        return 'צבע לא מוגדר'

async def validation(queue):
    http = urllib3.PoolManager()
    results = []
    # Load the video
    video_path = '/final_Project/temp/video.mp4'

    while queue:
        item = queue.popleft()
        result = item['license_plate']['license_plate_number']
        if result:
            print("Extracted text:")
            print(result)
            # Base URL of the API endpoint
            base_url = 'https://data.gov.il/api/3/action/datastore_search'
            # Resource ID for the specific dataset
            resource_id = '053cea08-09bc-40ec-8f7a-156f0677aff3'
            mispar_rechev = str(result)

            # Create a dictionary of query parameters
            query_params = {
                'resource_id': resource_id,
                'q': mispar_rechev  # Example query parameter
            }

            full_url = f"{base_url}?{urlencode(query_params)}"

            response = http.request('GET', full_url)

            response_data = response.data.decode('utf-8')

            # Find the position of the word "fields"
            end = response_data.find('fields')
            start = response_data.find('"records"')
            filtered_data = response_data[start:end] if end != -1 and start != -1 else response_data


            # print(filtered_data)
            color_start = filtered_data.find('"tzeva_rechev":') + len('"tzeva_rechev":')
            color_end = filtered_data.find(',', color_start)
            nameColorCar = filtered_data[color_start:color_end].strip().strip('"')
            frame_number = int(item['validation']['frame_nmr'])

            if (nameColorCar == ''):
                results.append({
                    'license_plate': result,
                    'frame_number': frame_number,
                    'color_verified': True,
                    'data': filtered_data,
                    'date': datetime.now().strftime("%Y-%m-%d")
                })
                continue




            car_bbox = item['validation']['car_bbox']  # Assuming it's in a form like '[x, y, w, h]'

            cap = cv2.VideoCapture(video_path)
            # Set the video to the specific frame number
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = cap.read()

            if not ret:
                print(f"Failed to extract frame {frame_number} from the video.")
                continue

            # Extract the car's bounding box from the frame
            car_bbox = car_bbox.split()
            car_bbox = [float(item) for item in car_bbox]
            x, y, w, h = car_bbox
            car_image = frame[int(y):int(y + h), int(x):int(x + w)]
            # print("Shape of car_image:", car_image.shape)

            # Get the dominant color of the car image
            dominant_color = get_dominant_color1(car_image)
            # dominant_color = get_dominant_color(car_image)
            car_color_name = convert_rgb_to_name(dominant_color)
            # print("Detected car color:", car_color_name,"API" ,nameColorCar)
            print(dominant_color)

            if nameColorCar in car_color_name:
                print(f"Color match for license number {result}: {car_color_name}")
            else:
                print(
                    f"Color mismatch for license number {result}: API color - {nameColorCar}, Detected color - {car_color_name}")
            color_match = nameColorCar in car_color_name
            results.append({
                'license_plate': result,
                'frame_number': frame_number,
                'color_verified': color_match,
                'data': filtered_data,
                'date': datetime.now().strftime("%Y-%m-%d")
            })

            cap.release()
        else:
            print("Failed to extract text from the image.")
    return results

