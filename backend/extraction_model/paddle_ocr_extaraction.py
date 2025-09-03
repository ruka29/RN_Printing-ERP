import numpy as np
if not hasattr(np, 'int'):
    np.int = int
if not hasattr(np, 'float'):
    np.float = float

import os
from paddleocr import PaddleOCR
from PIL import Image
import json
from uuid import uuid4
import re

# Initialize PaddleOCR
ocr = PaddleOCR(
    use_angle_cls=False,
    lang='en',
    rec=False,  # disable recognition if only bounding boxes are needed
)

# Your paths
IMAGES_FOLDER_PATH = "data/images"
OUTPUT_JSON_FILE = "data/labels/label-studio_input_file.json"


def create_image_url(filename):
    """
    Label Studio requires image URLs, so this defines the mapping from filesystem to URLs.
    """
    return f"http://localhost:8080/{filename}"


def natural_sort_key(s):
    """
    Sorts strings with embedded numbers in a human way:
    e.g. PDF_2.png < PDF_10.png
    """
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]


def extracted_tables_to_label_studio_json_file_with_paddleOCR(images_folder_path, output_json_file):
    label_studio_task_list = []

    # Natural sort ensures correct numeric ordering
    image_files = sorted(
        [f for f in os.listdir(images_folder_path) if f.endswith(".png")],
        key=natural_sort_key
    )

    for image_file in image_files:
        output_json = {}
        annotation_result = []

        print(f"Processing {image_file}")

        # Map image to URL (matches your target format)
        output_json["data"] = {"ocr": create_image_url(image_file)}

        # Open image
        img_path = os.path.join(images_folder_path, image_file)
        img = Image.open(img_path)
        img = np.asarray(img)
        image_height, image_width = img.shape[:2]

        # Run OCR
        result = ocr.ocr(img, cls=False)

        # Extract annotations
        for output in result:
            for item in output:
                co_ord = item[0]  # bounding box points
                text = item[1][0]  # recognized text

                # Convert polygon to rectangle
                four_co_ord = [
                    co_ord[0][0],
                    co_ord[1][1],
                    co_ord[2][0] - co_ord[0][0],
                    co_ord[2][1] - co_ord[1][1],
                ]

                bbox = {
                    "x": 100 * four_co_ord[0] / image_width,
                    "y": 100 * four_co_ord[1] / image_height,
                    "width": 100 * four_co_ord[2] / image_width,
                    "height": 100 * four_co_ord[3] / image_height,
                    "rotation": 0,
                }

                if not text:
                    continue

                region_id = str(uuid4())[:10]
                score = 0.5

                # Rectangle annotation
                bbox_result = {
                    "id": region_id,
                    "from_name": "bbox",
                    "to_name": "image",
                    "type": "rectangle",
                    "value": bbox,
                }

                # Text annotation
                transcription_result = {
                    "id": region_id,
                    "from_name": "transcription",
                    "to_name": "image",
                    "type": "textarea",
                    "value": dict(text=[text], **bbox),
                    "score": score,
                }

                annotation_result.extend([bbox_result, transcription_result])

        # Wrap results in predictions
        output_json["predictions"] = [{"result": annotation_result, "score": 0.97}]
        label_studio_task_list.append(output_json)

    # Save JSON
    os.makedirs(os.path.dirname(output_json_file), exist_ok=True)
    with open(output_json_file, "w", encoding="utf-8") as f:
        json.dump(label_studio_task_list, f, indent=4)

    print(f"\n✅ JSON saved at {output_json_file}")


# Run the pipeline
extracted_tables_to_label_studio_json_file_with_paddleOCR(IMAGES_FOLDER_PATH, OUTPUT_JSON_FILE)