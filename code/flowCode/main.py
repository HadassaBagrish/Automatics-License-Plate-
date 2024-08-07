from ultralytics import YOLO
import cv2
import numpy as np
from sort.sort import *
from util import get_car, read_license_plate, write_csv
import easyocr
from collections import deque



async def process_video():
    # Initialize SORT tracker
    mot_tracker = Sort()
    # Load YOLO models
    coco_model = YOLO('/final_Project/models/yolov8n.pt')
    license_plate_detector = YOLO('/final_Project/models/best1.pt')
    # Load video
    cap = cv2.VideoCapture('/final_Project/temp/video.mp4')

    vehicles = [2, 3, 5, 6, 7, 8]  # Define vehicle classes to detect
    fps = cap.get(cv2.CAP_PROP_FPS)
    frames_per_second = 5
    interval = int(fps / frames_per_second)
    results = {}

    # global frame_queue
    frame_queue = deque()  # Change the maxlen to control the queue size maxlen=100

    # Process video frames
    frame_nmr = -1
    ret = True
    while ret:
        frame_nmr += 1
        ret, frame = cap.read()
        if ret and frame_nmr % interval == 0:
            detections_by_id = {}  # Create a new dictionary for the current frame's detections by car ID
            frame_results = {}
            frame_results[frame_nmr] = {}
            results[frame_nmr] = {}
            # Detect vehicles
            detections = coco_model(frame)[0]
            detections_ = []
            for detection in detections.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = detection
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                if int(class_id) in vehicles:
                    x1, y1, x2, y2 = max(0, x1), max(0, y1), max(0, x2), max(0, y2)
                    x1, y1, x2, y2 = min(frame.shape[1], x1), min(frame.shape[0], y1), min(frame.shape[1], x2), min(
                        frame.shape[0], y2)
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                    detections_.append([x1, y1, x2, y2, score])
            # cv2.imwrite(f'frame_{frame_nmr}.jpg', frame)

            # Track vehicles
            track_ids = mot_tracker.update(np.asarray(detections_))

            # Detect license plates
            license_plates = license_plate_detector(frame)[0]
            for license_plate in license_plates.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = license_plate


                # Assign license plate to a car
                # xcar1, ycar1, xcar2, ycar2, car_id = get_car(license_plate, track_ids)
                x1, y1, x2, y2 = max(0, x1), max(0, y1), max(0, x2), max(0, y2)
                x1, y1, x2, y2 = min(frame.shape[1], x1), min(frame.shape[0], y1), min(frame.shape[1], x2), min(
                    frame.shape[0], y2)

                xcar1, ycar1, xcar2, ycar2, car_id = get_car(license_plate, track_ids)
                xcar1, ycar1, xcar2, ycar2 = max(0, xcar1), max(0, ycar1), max(0, xcar2), max(0, ycar2)
                xcar1, ycar1, xcar2, ycar2 = min(frame.shape[1], xcar1), min(frame.shape[0], ycar1), min(frame.shape[1],
                                                                                                         xcar2), min(
                    frame.shape[0], ycar2)

                if car_id != -1:
                    # Crop license plate
                    license_plate_crop = frame[int(y1):int(y2), int(x1):int(x2), :]

                    # Read license plate number
                    license_plate_text, license_plate_text_score = read_license_plate(license_plate_crop)

                    if license_plate_text is not None:
                        # Store or update detection if it has a higher text_score

                        if car_id not in detections_by_id or detections_by_id[car_id]['license_plate'][
 'text_score'] < license_plate_text_score:
                            detections_by_id[car_id] = {'frame_nmr': frame_nmr,
                                                        'car_id': car_id,
                                                        'car': {'bbox': [xcar1, ycar1, xcar2, ycar2]},
                                                        'license_plate': {'bbox': [x1, y1, x2, y2],
                                                                          'text': license_plate_text,
                                                                          'bbox_score': score,
                                                                          'text_score': license_plate_text_score}}


                        # Add frame and associated data to queue
            for detection in detections_by_id.values():
                frame_queue.append(detection)
    cap.release()
    return frame_queue






