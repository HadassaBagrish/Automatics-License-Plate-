import string
import easyocr
import os
import csv
import json
from sklearn.cluster import KMeans

reader = easyocr.Reader(['ang','en'], gpu=False)

dict_char_to_int_UK = {'O': '0',
                    'I': '1',
                    'J': '3',
                    'A': '4',
                    'G': '6',
                    'S': '5'}
dict_int_to_char_UK = {v: k for k, v in dict_char_to_int_UK.items()}



dict_char_to_int_IL = {'0': 0,
                    '1': 1,
                    '2': 2,
                    '3': 3,
                    '4': 4,
                    '5': 5,
                    '6': 6,
                    '7': 7,
                    '8': 8,
                    '9': 9}

dict_int_to_char_IL = {v: k for k, v in dict_char_to_int_IL.items()}

def write_csv(frame_queue, output_path):

    # בדיקה אם הקובץ קיים ואם יש צורך לכתוב כותרות
    write_header = not os.path.exists(output_path)

    with open(output_path, 'a', newline='') as csvfile:
        fieldnames = ['license_plate', 'frame_number', 'color_verified', 'data', 'date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if write_header:
            writer.writeheader()
        for frame in frame_queue:
            writer.writerow(frame)


def license_complies_format(text):

    if len(text)< 7:
        return None
    if len(text) == 7:
        if (text[0] in dict_char_to_int_IL.keys()) and \
                (text[1] in dict_char_to_int_IL.keys()) and \
                (text[2] in dict_char_to_int_IL.keys()) and \
                (text[3] in dict_char_to_int_IL.keys()) and \
                (text[4] in dict_char_to_int_IL.keys()) and \
                (text[5] in dict_char_to_int_IL.keys()) and \
                (text[6] in dict_char_to_int_IL.keys()):
            return True

    if len(text) == 8:
        if (text[0] in dict_char_to_int_IL.keys()) and \
                (text[1] in dict_char_to_int_IL.keys()) and \
                (text[2] in dict_char_to_int_IL.keys()) and \
                (text[3] in dict_char_to_int_IL.keys()) and \
                (text[4] in dict_char_to_int_IL.keys()) and \
                (text[5] in dict_char_to_int_IL.keys()) and \
                (text[6] in dict_char_to_int_IL.keys()) and \
                (text[7] in dict_char_to_int_IL.keys()):
            return True


    else:
        return False




def read_license_plate(license_plate_crop):

    import string
    detections = reader.readtext(license_plate_crop)
    score = 0
    for detection in detections:
        bbox, text, score = detection


        text = text.upper().replace(' ', '')
        translator = str.maketrans("", "", string.punctuation)
        text = text.translate(translator)

        if license_complies_format(text):
            return text, score
            # return format_license(text), score

    return None, None


def get_car(license_plate, vehicle_track_ids):

    x1, y1, x2, y2, score, class_id = license_plate

    foundIt = False
    for j in range(len(vehicle_track_ids)):
        xcar1, ycar1, xcar2, ycar2, car_id = vehicle_track_ids[j]

        if x1 > xcar1 and y1 > ycar1 and x2 < xcar2 and y2 < ycar2:
            car_indx = j
            foundIt = True
            break

    if foundIt:
        return vehicle_track_ids[car_indx]

    return -1, -1, -1, -1, -1







        # writer.writerows(frame_queue)


# def write_csv(frame_queue, output_path):
#     # בדיקה אם הקובץ קיים ואם יש צורך לכתוב כותרות
#     write_header = not os.path.exists(output_path)
#
#     with open(output_path, 'a', newline='') as csvfile:
#         fieldnames = ['license_plate', 'frame_number', 'color_verified', 'data', 'date']
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#
#         if write_header:
#             writer.writeheader()
#



# def write_csv(record, output_path):
#
#     # בדיקה אם הקובץ קיים ואם יש צורך לכתוב כותרות
#     write_header = not os.path.exists(output_path)
#
#     with open(output_path, 'w', newline='') as csvfile:
#         # בדיקה אם הקובץ קיים ואם יש צורך לכתוב כותרות
#         write_header = not os.path.exists(output_path)
#
#         with open(output_path, 'w', newline='') as csvfile:
#             fieldnames = ['license_plate', 'frame_number', 'color_verified', 'data']
#             writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#
#             if write_header:
#                 writer.writeheader()
#
#             # בדיקה אם record הוא רשימה או מחרוזת ולכתיבה לקובץ
#             for row in record:
#                 if isinstance(row, dict):
#                     writer.writerow(row)
#                 elif isinstance(row, str):
#                     try:
#                         # Try to parse the string as JSON
#                         row_dict = json.loads(row)
#                     except json.JSONDecodeError:
#                         # If the string is not in JSON format, assume it is comma-separated and convert it to a dictionary
#                         row_list = row.split(',')
#                         if len(row_list) == len(fieldnames):
#                             row_dict = dict(zip(fieldnames, row_list))
#                         else:
#                             print(f"Skipping invalid row: {row}")
#                             continue
#                     writer.writerow(row_dict)
#                 else:
#                     print(f"Skipping invalid row: {row}")