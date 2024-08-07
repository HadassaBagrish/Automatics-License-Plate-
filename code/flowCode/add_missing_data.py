import csv
import numpy as np
from scipy.interpolate import interp1d
import pandas as pd


async def interpolated_data(queue):
    # אסוף את כל הנתונים מהתור לרשימה
    data = []
    while queue:
        data.append(queue.popleft())

    # בצע אינטרפולציה על הנתונים
    interpolated_data = await interpolate_bounding_boxes(data)

    # הכנס את הנתונים החדשים חזרה לתור
    for item in interpolated_data:
        queue.append(item)

    return queue


async def interpolate_bounding_boxes(data):

    # Extract necessary data columns from input data
    frame_numbers = np.array([int(row['frame_nmr']) for row in data])
    car_ids = np.array([int(float(row['car_id'])) for row in data])
    # car_bboxes = np.array([list(map(float, row['car_bbox'][1:-1].split())) for row in data])
    car_bboxes = np.array([list(map(float, row['car']['bbox'])) for row in data])
    # license_plate_bboxes = np.array([list(map(float, row['license_plate_bbox'][1:-1].split())) for row in data])
    license_plate_bboxes = np.array([list(map(float, row['license_plate']['bbox'])) for row in data])
    interpolated_data = []
    unique_car_ids = np.unique(car_ids)
    for car_id in unique_car_ids:

        frame_numbers_ = [p['frame_nmr'] for p in data if int(float(p['car_id'])) == int(float(car_id))]
        print(frame_numbers_, car_id)

        # Filter data for a specific car ID
        car_mask = car_ids == car_id
        car_frame_numbers = frame_numbers[car_mask]
        car_bboxes_interpolated = []
        license_plate_bboxes_interpolated = []

        first_frame_number = car_frame_numbers[0]
        last_frame_number = car_frame_numbers[-1]

        for i in range(len(car_bboxes[car_mask])):
            frame_number = car_frame_numbers[i]
            car_bbox = car_bboxes[car_mask][i] # ליצירת מערך דו מימדי יחד עם מערך prev_car_bbox (המכלים קואורדינטות של תיבת הרכב התוחמת)
            license_plate_bbox = license_plate_bboxes[car_mask][i]# ליצירת מערך דו מימדי יחד עם מערך prev_license_plate_bbox (המכלים קואורדינטות של תיבת הרכב התוחמת)

            if i > 0:   #קטע הקוד הנל מבצע אינטרפולציה ליניארית כדי להעריך תיבות תוחמות עבור מכונית ולוחית הרישוי שלה בין שתי פריימים בסרטון
                prev_frame_number = car_frame_numbers[i-1]
                prev_car_bbox = car_bboxes_interpolated[-1]
                prev_license_plate_bbox = license_plate_bboxes_interpolated[-1]

                if frame_number - prev_frame_number > 1:   # וידוא סדר הפריימים
                    # Interpolate missing frames' bounding boxes
                    frames_gap = frame_number - prev_frame_number # הפרש חלקי השניות בין הפריימים של הרכב
                    x = np.array([prev_frame_number, frame_number]) # מערך המכיל את האלמנטים הנתונים, המציין את הנקודות שבהן יש להעריך את האינטרפולציה
                    x_new = np.linspace(prev_frame_number, frame_number, num=frames_gap, endpoint=False)#יוצר numערכים ברווח שווה בין startלבין stop
                    interp_func = interp1d(x, np.vstack((prev_car_bbox, car_bbox)), axis=0, kind='linear')# סוג האינטרפולציה שיש לבצע לרכב היא לינארית
                    interpolated_car_bboxes = interp_func(x_new)# מכיל את תיבות התוחמות המשולבות עבור המכונית על פני הפריימים שצוינו
                    interp_func = interp1d(x, np.vstack((prev_license_plate_bbox, license_plate_bbox)), axis=0, kind='linear')#בדומה לאינטרפולציה של הרכב
                    interpolated_license_plate_bboxes = interp_func(x_new)

                    car_bboxes_interpolated.extend(interpolated_car_bboxes[1:])
                    license_plate_bboxes_interpolated.extend(interpolated_license_plate_bboxes[1:])

            car_bboxes_interpolated.append(car_bbox)
            license_plate_bboxes_interpolated.append(license_plate_bbox)
        for i in range(len(car_bboxes_interpolated)):
            frame_number = first_frame_number + i
            row = {}
            row['frame_nmr'] = str(frame_number)
            row['car_id'] = str(car_id)
            row['car_bbox'] = ' '.join(map(str, car_bboxes_interpolated[i]))
            row['license_plate_bbox'] = ' '.join(map(str, license_plate_bboxes_interpolated[i]))

            if frame_number in frame_numbers_:
                # Original row, retrieve values from the input data if available
                original_row = [p for p in data if int(p['frame_nmr']) == frame_number and int(float(p['car_id'])) == int(float(car_id))][0]
                row['license_plate_bbox_score'] = original_row['license_plate']['bbox_score'] if 'bbox_score' in original_row['license_plate'] else '0'
                row['license_number'] = original_row['license_plate']['text'] if 'text' in original_row['license_plate'] else '0'
                row['license_number_score'] = original_row['license_plate']['text_score'] if 'text_score' in original_row['license_plate'] else '0'

                # row['license_plate_bbox_score'] = original_row['license_plate_bbox_score'] if 'license_plate_bbox_score' in original_row else '0'
                # row['license_number'] = original_row['license_number'] if 'license_number' in original_row else '0'
                # row['license_number_score'] = original_row['license_number_score'] if 'license_number_score' in original_row else '0'
            else:
                # Imputed row, set the following fields to '0'
                row['license_plate_bbox_score'] = '0'
                row['license_number'] = '0'
                row['license_number_score'] = '0'

            interpolated_data.append(row)

    return interpolated_data


async def merge_rows(queue):
    data = []
    while queue:
        data.append(queue.popleft())
    # המרת רשימת מילונים ל-DataFrame של pandas
    results_df = pd.DataFrame(data)
    # לוודא שהעמודות הרלוונטיות הן מסוג מספרי
    results_df['car_id'] = results_df['car_id'].astype(int)
    results_df['license_number_score'] = results_df['license_number_score'].astype(float)

    # יצירת מבני נתונים לאחסון התוצאות
    license_plate = {}
    validation = {}

    for car_id in np.unique(results_df['car_id']):
        car_results = results_df[results_df['car_id'] == car_id]
        max_score_row = car_results.loc[car_results['license_number_score'].idxmax()]
        max_score = max_score_row['license_number_score']

        license_plate[car_id] = {
            'license_crop': None,
            'license_plate_number': max_score_row['license_number']
        }
        validation[car_id] = {
            'frame_nmr': max_score_row['frame_nmr'],
            'car_bbox': max_score_row['car_bbox'],
            'license_number': max_score_row['license_number']
        }
        # הוסף לתור את התוצאות
        queue.append ({
            'car_id': car_id,
            'license_plate': license_plate[car_id],
            'validation': validation[car_id]
        })
    return queue

