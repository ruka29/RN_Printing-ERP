import json
import os
from paddleocr import PaddleOCR
from PIL import Image

def compute_iou(box_a, box_b):
    """Compute Intersection over Union (IoU) between two bounding boxes [x, y, w, h]."""
    xA = max(box_a[0], box_b[0])
    yA = max(box_a[1], box_b[1])
    xB = min(box_a[0] + box_a[2], box_b[0] + box_b[2])
    yB = min(box_a[1] + box_a[3], box_b[1] + box_b[3])
    inter_area = max(0, xB - xA) * max(0, yB - yA)
    box_a_area = box_a[2] * box_a[3]
    box_b_area = box_b[2] * box_b[3]
    return inter_area / (box_a_area + box_b_area - inter_area) if (box_a_area + box_b_area - inter_area) > 0 else 0

def load_coco_annotations(json_path, images_dir, ocr_json_path):
    with open(json_path, "r") as f:
        coco = json.load(f)

    # Map image id to image info and filename
    id2img = {img["id"]: img for img in coco["images"]}
    filename2id = {os.path.basename(img["file_name"]): img["id"] for img in coco["images"]}

    # Load Label Studio OCR data
    with open(ocr_json_path, "r") as f:
        ocr_data = json.load(f)

    # Map OCR results to COCO image IDs based on filename in ocr URL
    ocr_map = {}
    for item in ocr_data:
        ocr_url = item["data"]["ocr"]
        filename = os.path.basename(ocr_url)  # Extract filename like "PDF_01_page1.png"
        img_id = filename2id.get(filename)
        if img_id is not None:
            ocr_results = []
            predictions = item.get("predictions", [])
            for pred in predictions:
                results = pred.get("result", [])
                for result in results:
                    if result.get("from_name") == "transcription":  # Check if key exists
                        value = result["value"]
                        text = value.get("text", [""])[0]  # Default to empty string if text missing
                        x = value.get("x", 0)
                        y = value.get("y", 0)
                        width = value.get("width", 0)
                        height = value.get("height", 0)
                        # Convert percentage coordinates to absolute
                        image_info = id2img[img_id]
                        img_path = os.path.join(images_dir, filename)
                        with Image.open(img_path) as img:
                            img_width, img_height = img.size
                        x_abs = x * img_width / 100
                        y_abs = y * img_height / 100
                        w_abs = width * img_width / 100
                        h_abs = height * img_height / 100
                        ocr_results.append({
                            "text": text,
                            "bbox": [x_abs, y_abs, w_abs, h_abs]
                        })
            ocr_map[img_id] = ocr_results

    samples = []
    ocr_model = PaddleOCR(use_angle_cls=True, lang="en")
    for ann in coco["annotations"]:
        image_info = id2img[ann["image_id"]]
        img_path = os.path.join(images_dir, os.path.basename(image_info["file_name"]))
        # Use precomputed OCR if available, otherwise fallback to live OCR
        ocr_result = ocr_map.get(ann["image_id"], [])
        if not ocr_result:  # Fallback to OCR if no precomputed data
            result = ocr_model.ocr(img_path, cls=True)
            ocr_result = [{"text": line[1][0], "bbox": [min(p[0] for p in line[0]), min(p[1] for p in line[0]), 
                                                       max(p[0] for p in line[0]) - min(p[0] for p in line[0]), 
                                                       max(p[1] for p in line[0]) - min(p[1] for p in line[0])]} 
                          for line in result if result]

        samples.append({
            "image": img_path,
            "bbox": ann["bbox"],  # [x, y, w, h]
            "category_id": ann["category_id"],
            "ocr": ocr_result  # List of {"text": str, "bbox": [x0, y0, x1, y1]}
        })
    return samples