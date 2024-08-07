from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import main
import add_missing_data
import validation
import util
import pandas as pd
import os
import csv
from datetime import datetime

app = Flask(__name__)
CORS(app)



async def main_routine():

    frame_queue = await main.process_video()
    frame_queue = await add_missing_data.interpolated_data(frame_queue)
    frame_queue = await add_missing_data.merge_rows(frame_queue)
    frame_queue = await validation.validation(frame_queue)
    output_path = '/final_Project/temp/details_cars.csv'
    util.write_csv(frame_queue, output_path)



@app.route('/upload_video/<video>', methods=['POST'])
def upload_video(video):
    if 'video' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['video']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        file.save(os.path.join('/final_Project/temp', 'video.mp4'))
        # הפעלת הפונקציה האסינכרונית לאחר טעינת הסרטון
        asyncio.run(main_routine())
        return jsonify({"message": "Video uploaded successfully"}), 200


@app.route('/find_by_number/<int:number>', methods=['GET'])
def find_by_number(number):
    if not number:
        return jsonify({"error": "No number provided"}), 400

    try:
        data = pd.read_csv('/final_Project/temp/details_cars.csv', encoding='ISO-8859-8')

        # המרת עמודת התאריך לפורמט datetime
        data['date'] = pd.to_datetime(data['date'], dayfirst=True, errors='coerce')

        # הסרת השניות מהתאריכים
        # data['date'] = data['date'].dt.floor('min')

    except FileNotFoundError:
        return jsonify({"error": "Data file not found"}), 404
    except ValueError:
        return jsonify({"error": "Error parsing date in the data file"}), 400

    # חיפוש לפי מספר רישוי
    result = data[data['license_plate'] == number]
    if result.empty:
        return jsonify({"": "רכב זה לא קיים באגר"})

    return result.to_json(orient='records')


@app.route('/display_by_date/<string:date>', methods=['GET'])
def display_by_date(date):
    if date == 'T':
        return jsonify({"error": "No date provided"}), 400

    try:
        date = datetime.strptime(date, '%Y-%m-%d').strftime('%Y-%d-%m')

        data = pd.read_csv('/final_Project/temp/details_cars.csv', encoding='ISO-8859-8')

        # המרת עמודת התאריך לפורמט datetime
        data['date'] = pd.to_datetime(data['date'])

        # הסרת השניות מהתאריכים
        data['date'] = data['date'].dt.floor('H')


        # התאריך הרצוי
        target_date = pd.to_datetime(date)

        # סינון השורות עם התאריך הרצוי
        filtered_df = data[data['date'] == target_date]

    except FileNotFoundError:
        return jsonify({"error": "Data file not found"}), 404
    except ValueError:
        return jsonify({"error": "Invalid date format provided"}), 400

    if filtered_df.empty:
        return jsonify({"": "אין פירוט על רכבים בתאריך ו/או בשעה זה/ו"})

    return jsonify(filtered_df.to_dict(orient='records'))



@app.route(f'/add_car_waring/<string:number>', methods=['GET'])
def add_car_waring(number):
    # קרא את הנתונים הקיימים מהקובץ
    data = pd.read_excel('/final_Project/temp/carWaring.xlsx', header=None)
    print(number)
    if number !='undefined' and (len(number) == 7 or len(number) == 8):
        try:
            # המרת המספר למספר שלם והוספתו לרשימה הקיימת
            number = int(number)
            new_data = pd.DataFrame([number])  # צור DataFrame חדש עבור המספר החדש
            data = pd.concat([data, new_data], ignore_index=True)  # הוסף את המספר לקובץ ה-Excel הקיים
            print(data)
            data.to_excel('/final_Project/temp/carWaring.xlsx', index=False, header=False)

            # שמירת הנתונים המעודכנים חזרה לקובץ
        except Exception as e:
            return str(e), 500

    data_fixed = []
    for i in range(0, len(data)):
        if i < len(data):
            entry = {str(i + 1): int(data.iloc[i, 0])}
            data_fixed.append(entry)
    return jsonify(data_fixed)

@app.route('/car_warning', methods=['GET'])
def car_warning():
    # קריאת הנתונים מקובץ ה-Excel
    car_warning_data = pd.read_excel('/final_Project/temp/carWaring.xlsx', header=None)
    car_warning_numbers = car_warning_data[0].tolist()
    # קריאת הנתונים מקובץ ה-CSV
    details_cars_data = pd.read_csv('/final_Project/temp/details_cars.csv', encoding='ISO-8859-8')

    license_plate_numbers = details_cars_data['license_plate'].tolist()
    # חיפוש התאמות בין שני הקבצים
    matched_cars = details_cars_data[details_cars_data['license_plate'].isin(car_warning_numbers)]
    # בדיקת האם יש רכבים בעמודת details_cars_data שמכילים את הערך FALSE
    false_entries = details_cars_data[details_cars_data['color_verified'] == False]

    # החזרת התאמות
    if not matched_cars.empty or not false_entries.empty:
        return jsonify({
            "message": "Matching license plates found",
            "matched_cars": matched_cars.to_dict(orient='records'),
            "false_entries_exist": false_entries.to_dict(orient='records')
        }), 200
    else:
        return jsonify({
            "message": "No matching license plates found",
            "false_entries_exist": not false_entries.empty
        }), 404


@app.route('/check_license_plates', methods=['POST'])
def check_license_plates():
    license_plates = request.json.get('list')
    if not license_plates:
        return jsonify({"error": "No license plates provided"}), 400

    result = {}
    for plate in license_plates:
        # Validate that plate is numeric and has 7-8 digits

        if plate.isdigit() and len(plate) in [7, 8]:
            try:
                data = pd.read_csv('/final_Project/temp/details_cars.csv', encoding='ISO-8859-8')
            except FileNotFoundError:
                return jsonify({"error": "Data file not found"}), 404
            except ValueError:
                return jsonify({"error": "Error reading the data file"}), 400

            exists = not data[data['license_plate'] == int(plate)].empty
            result[plate] = exists
        else:
            result[plate] = False  # If plate format is invalid

    return jsonify(result), 200



if __name__ == "__main__":
    # asyncio.run(main_routine())
    app.run(debug=False)

    # output_path = 'details_cars.csv'
    # data = pd.read_excel('/final_Project/temp/details_cars.xlsx', header=None)
    # fieldnames = ['license_plate', 'frame_number', 'color_verified', 'date', 'data']
    # with open(output_path, 'a', newline='') as csvfile:
    #     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    #     writer.writerows(frame_queue)

        # writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    # for item in frame_queue:
    #     util.write_csv(item, output_path)

        # data = pd.concat([item, new_data], ignore_index=True)  # הוסף את המספר לקובץ ה-Excel הקיים
        # data.to_excel('/final_Project/temp/details_cars.xlsx', index=False, header=False)

        # item.to
        # util.write_csv(item, output_path)


# util.write_csv(frame_queue, './data.csv')


            # return "Number added successfully", 200
# @app.route('/get_by_date/<date>', methods=['get'])
# def get_by_date(date):


# @app.route('/check_license_plates', methods=['POST'])
# def check_license_plates():
#     license_plates = request.json.get('list')
#     if not license_plates:
#         return jsonify({"error": "No license plates provided"}), 400
#
#     try:
#         data = pd.read_csv('/final_Project/temp/details_cars.csv', encoding='ISO-8859-8')
#     except FileNotFoundError:
#         return jsonify({"error": "Data file not found"}), 404
#     except ValueError:
#         return jsonify({"error": "Error reading the data file"}), 400
#
#     result = {}
#     for plate in license_plates:
#         exists = not data[data['license_plate'] == int(plate)].empty
#         result[plate] = exists
#
#     return jsonify(result), 200
