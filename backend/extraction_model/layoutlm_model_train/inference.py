import numpy as np
if not hasattr(np, 'int'):
    np.int = int
if not hasattr(np, 'float'):
    np.float = float

from transformers import LayoutLMv3Processor, LayoutLMv3ForTokenClassification
from PIL import Image
import torch
from paddleocr import PaddleOCR
import os

def extract_data(image_path, model_path="../models/final_model"):
    processor = LayoutLMv3Processor.from_pretrained(model_path)
    model = LayoutLMv3ForTokenClassification.from_pretrained(model_path)

    ocr_model = PaddleOCR(use_angle_cls=True, lang="en")
    result = ocr_model.ocr(image_path, cls=True)
    words = []
    ocr_boxes = []
    for line in result:
        if line and len(line) > 0:  # Ensure line exists and has points
            points = line[0]  # List of [x, y] pairs
            text = line[1][0] if len(line) > 1 else ""  # Ensure text exists
            if points and all(isinstance(point, (list, tuple)) and len(point) >= 2 for point in points):  # Validate points
                x_coords = [point[0] for point in points if isinstance(point[0], (int, float))]
                y_coords = [point[1] for point in points if isinstance(point[1], (int, float))]
                if x_coords and y_coords:  # Ensure we have valid coordinates
                    x_min = min(x_coords)
                    y_min = min(y_coords)
                    x_max = max(x_coords)
                    y_max = max(y_coords)
                    ocr_boxes.append([x_min, y_min, x_max - x_min, y_max - y_min])  # [x, y, width, height]
                    words.append(text)
    image = Image.open(image_path).convert("RGB")
    width, height = image.size
    boxes = [[int(b * 1000 / width) if i % 2 == 0 else int(b * 1000 / height)
              for i, b in enumerate([x, y, w, h])] for x, y, w, h in ocr_boxes if all(isinstance(b, (int, float)) for b in [x, y, w, h])]

    # Ensure words and boxes match in length
    if len(words) != len(boxes):
        min_length = min(len(words), len(boxes))
        words = words[:min_length]
        boxes = boxes[:min_length]

    inputs = processor(images=image, text=words, boxes=boxes, return_tensors="pt", padding=True, truncation=True)
    outputs = model(**inputs)
    predictions = torch.argmax(outputs.logits, dim=2)

    id2label = model.config.id2label
    extracted = {}
    current_entity = None
    current_text = []
    for pred, word in zip(predictions[0].tolist(), words):
        label = id2label[pred]
        if label == "O":
            if current_entity:
                extracted[current_entity] = " ".join(current_text)
                current_entity = None
                current_text = []
        elif label.startswith("B-"):
            if current_entity:
                extracted[current_entity] = " ".join(current_text)
            current_entity = label[2:]
            current_text = [word]
        elif label.startswith("I-") and current_entity == label[2:]:
            current_text.append(word)
    if current_entity:
        extracted[current_entity] = " ".join(current_text)

    return extracted

if __name__ == "__main__":
    image_path = "../data/images/PDF_01_page1.png"
    result = extract_data(image_path)
    print(result)
    # Save to JSON for ERP
    import json
    with open("extracted_data.json", "w") as f:
        json.dump(result, f)
    print("Saved to extracted_data.json")