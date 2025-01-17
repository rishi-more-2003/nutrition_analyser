import os
import cv2
import easyocr
import torch

yolo_path = '..\label_localization\yolov5_label_localization_runs'
best_weights = os.path.join(yolo_path, 'weights', 'best.pt')
localization_model = torch.hub.load('ultralytics/yolov5', 'custom', best_weights, force_reload=True)

reader = easyocr.Reader(['en'], gpu=False)


def nutrients_classifier(nutrition_dict):
    """
    Function to classify the amount of nutrients as healthy or not
    """

    class_dict = {
        'Calories': [], 'Fats': [],
        'Carbohydrates': [], 'Sugars': [],
        'Cholesterol': []
    }
    total_fat, saturated_fat, sugar = 0, 0, 0

    for nutrient in nutrition_dict.keys():
        try:
            val = nutrition_dict[nutrient]
            if not val:
                nutrition_dict[nutrient] = 0.0

            elif val:
                if val.endswith('g') or val.endswith('9'):
                    val = val[:-1]

                    if val.endswith('m'):
                        val = val[:-1]
                        if val == 'o' or val == 'O':
                            val = 0.0
                        else:
                            val = float(val)

                    else:
                        if val == 'o' or val == 'O':
                            val = 0.0
                        else:
                            val = float(val)

                try:
                    val = float(val)
                except ValueError:
                    continue

                if nutrient == 'calories':
                    val = val / 9
                    if val > 100:
                        val = 100
                    class_dict['Calories'] = val

                elif nutrient == 'total_fat':
                    total_fat = val

                elif nutrient == 'total_carbs':
                    class_dict['Carbohydrates'] = val

                elif nutrient == 'fiber':
                    try:
                        class_dict['Carbohydrates'] -= val
                    except TypeError:
                        pass
                elif nutrient == 'saturated_fat':
                    saturated_fat = val

                elif nutrient == 'trans_fat':
                    continue

                elif nutrient == 'total_sugar':
                    sugar = val

                elif nutrient == 'protein':
                    try:
                        class_dict['Carbohydrates'] -= val
                    except TypeError:
                        pass
                elif nutrient == 'sodium':
                    val = val / 3
                    if val > 120:
                        val = 100
                    class_dict['Sodium'] = val

                elif nutrient == 'potassium':
                    val = val / 5
                    if val > 100:
                        val = 100
                    class_dict['Potassium'] = val

                elif nutrient == 'cholesterol':
                    val = val / 300
                    if val > 100:
                        val = 100
                    class_dict['Cholesterol'] = val
            else:
                continue

        except ValueError and TypeError:
            continue

    carbs = class_dict['Carbohydrates']

    try:
        carbs = (carbs / 45) * 100
        total_fat = (total_fat - 3.0) * 8
        saturated_fat = ((saturated_fat - 1.5) * 1000) / 350
        sugar = ((sugar - 5) * 1000) / 175

        if carbs > 100:
            carbs = 100

        if sugar > 100:
            sugar = 100

        if total_fat > 100:
            total_fat = 100

        if saturated_fat > 100:
            saturated_fat = 100
    except TypeError:
        pass

    class_dict['Sugars'] = sugar
    class_dict['Fats'] = (total_fat + saturated_fat) / 2
    class_dict['Carbohydrates'] = carbs

    return class_dict


def extract_nutrients(text):
    """
    Function to extract the nutrients from text while iterating through it
    """

    nutrition_dict = {
        'calories': [], 'total_fat': [],
        'total_carbs': [], 'protein': [],
        'total_sugar': [], 'cholesterol': [], 'fiber': [],
        'saturated_fat': [], 'trans_fat': [],
        'sodium': [], 'potassium': []
    }

    text = text.lower()
    text = text.split()

    for j, i in enumerate(text):

        if i == 'calories':
            nutrition_dict['calories'] = text[text.index(i) + 1]

        elif i == 'total':
            if text[j + 1] == 'fat':
                nutrition_dict['total_fat'] = text[j + 2]

            elif text[j + 1] == 'carbohydrate' or text[j + 1] == 'carbohydrates':
                nutrition_dict['total_carbs'] = text[j + 2]

            elif text[j + 1] == 'fiber':
                nutrition_dict['fiber'] = text[j + 2]

            elif text[j + 1] == 'sugars' or text[j + 1] == 'sugar':
                nutrition_dict['total_sugar'] = text[j + 2]

            elif text[j + 1] == 'cholesterol':
                nutrition_dict['total_cholestrol'] = text[j + 2]

        elif i == 'cholesterol':
            nutrition_dict['cholesterol'] = text[j + 1]

        elif i == 'saturated':
            nutrition_dict['saturated_fat'] = text[j + 2]

        elif i == 'trans':
            nutrition_dict['trans_fat'] = text[j + 2]

        elif i == 'sodium':
            nutrition_dict['sodium'] = text[j + 1]

        elif i == 'potassium':
            nutrition_dict['potassium'] = text[j + 1]

        elif i == 'dietary':
            nutrition_dict['fiber'] = text[j + 2]

        elif i == 'fiber':
            nutrition_dict['fiber'] = text[j + 1]

        elif i == 'protein':
            nutrition_dict['protein'] = text[j + 1]

        elif i == 'sugars' or i == 'sugar':
            if not nutrition_dict['total_sugar']:
                nutrition_dict['total_sugar'] = text[j + 1]

    return nutrients_classifier(nutrition_dict)


def nutrients_recognition(img, method='easyocr'):
    """
    Function to recognize the text in the image and extract the nutrition facts
    """

    if method == 'easyocr':
        detections = reader.readtext(img)

        text = ""
        for i in detections:
            text += i[1] + " "

        return extract_nutrients(text)

    elif method == 'pytesseract':
        return extract_nutrients(pytesseract.image_to_string(img))


def get_nutrition(img, confidence_threshold=0.1, ocr='easyocr'):
    """
    Function to localize the labels in the image and extract nutrition facts
    """

    nutrients_list = []
    output = localization_model(img)
    output_df = output.pandas().xyxy[0]
    output_df = output_df[output_df['confidence'] > confidence_threshold]
    number_of_boxes = output_df.shape[0]

    for i in range(number_of_boxes):
        bb = output_df.loc[i]
        x1, x2, y1, y2 = int(bb['xmin']), int(bb['xmax']), int(bb['ymin']), int(bb['ymax'])
        cropped_image = img[y1:y2, x1:x2]

        label_info = nutrients_recognition(cropped_image, method=ocr)
        nutrients_list.append(label_info)

    return nutrients_list


if __name__ == '__main__':
    img = cv2.imread(r'food_viser\static\images\label_examples\nutrition-facts-label-download-image1.jpg')
    nutrients_list = get_nutrition(img, ocr='easyocr')
    print(nutrients_list)
