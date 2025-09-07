# import numpy as np
# if not hasattr(np, 'int'):
#     np.int = int
# if not hasattr(np, 'float'):
#     np.float = float

# import torch
# from transformers import AutoProcessor, LayoutLMv3ForTokenClassification
# from PIL import Image
# import json
# import re
# from paddleocr import PaddleOCR

# # ==== SETTINGS ====
# DEVICE = "cpu"
# MODEL_DIR = "./models/final_model"
# OUTPUT_JSON = "./extracted_po.json"

# label2id = {
#     "O": 0,
#     "PO_NUMBER": 1,
#     "CURRENCY": 2,
#     "TOTAL_VALUE": 3,
#     "CUSTOMER": 4,
#     "INVOICE_ADDRESS": 5,
#     "DELIVERY_ADDRESS": 6,
#     "ITEM_NAME": 7,
#     "UNIT_PRICE": 8,
#     "QUANTITY": 9
# }
# id2label = {v: k for k, v in label2id.items()}

# # ==== LOAD MODEL ====
# processor = AutoProcessor.from_pretrained(MODEL_DIR, apply_ocr=False)
# model = LayoutLMv3ForTokenClassification.from_pretrained(MODEL_DIR)
# model.to(DEVICE)
# model.eval()


# # ==== HELPERS ====
# def normalize_box(box, width, height):
#     return [
#         int(1000 * box[0] / width),
#         int(1000 * box[1] / height),
#         int(1000 * box[2] / width),
#         int(1000 * box[3] / height)
#     ]

# ocr = PaddleOCR(use_angle_cls=True, lang="en")

# def ocr_image(image_path):
#     image = Image.open(image_path).convert("RGB")
#     ocr_result = ocr.ocr(image_path, cls=True)

#     words, boxes = [], []
#     width, height = image.size

#     print("\n🔎 OCR Extracted Values:")
#     print("=" * 50)

#     for line in ocr_result[0]:
#         text, conf = line[1]
#         (x_min, y_min), (x_max, y_max) = line[0][0], line[0][2]
#         words.append(text)
#         boxes.append(normalize_box([x_min, y_min, x_max, y_max], width, height))

#         # Print each OCR result
#         print(f"Word: {text}, Confidence: {conf:.2f}, "
#               f"Box: {normalize_box([x_min, y_min, x_max, y_max], width, height)}")

#     print("=" * 50 + "\n")
#     return image, words, boxes


# # ==== PREDICTION ====
# def predict(image_path):
#     image, words, boxes = ocr_image(image_path)

#     encoding = processor(
#         image,
#         words,
#         boxes=boxes,
#         return_tensors="pt",
#         truncation=True,
#         padding="max_length"
#     )
#     for k, v in encoding.items():
#         encoding[k] = v.to(DEVICE)

#     with torch.no_grad():
#         outputs = model(**encoding)
#         predictions = outputs.logits.argmax(-1).squeeze().tolist()

#     # Collect predictions by label
#     results = {}
#     for word, pred_id in zip(words, predictions):
#         label = id2label[pred_id]
#         if label != "O" and word.strip():
#             results.setdefault(label, []).append(word)

#     # Post-process into structured JSON
#     structured = {
#         "PO_NUMBER": None,
#         "CURRENCY": None,
#         "TOTAL_VALUE": None,
#         "CUSTOMER": None,
#         "INVOICE_ADDRESS": None,
#         "DELIVERY_ADDRESS": None,
#         "ITEMS": []
#     }

#     if "PO_NUMBER" in results:
#         match = re.search(r"[A-Z0-9-]+", " ".join(results["PO_NUMBER"]))
#         structured["PO_NUMBER"] = match.group(0) if match else " ".join(results["PO_NUMBER"])

#     if "CURRENCY" in results:
#         structured["CURRENCY"] = " ".join(results["CURRENCY"])

#     if "TOTAL_VALUE" in results:
#         match = re.search(r"([A-Z]{2,3}\s*\d+[,.]?\d*)", " ".join(results["TOTAL_VALUE"]))
#         structured["TOTAL_VALUE"] = match.group(1) if match else " ".join(results["TOTAL_VALUE"])

#     if "CUSTOMER" in results:
#         structured["CUSTOMER"] = " ".join(results["CUSTOMER"])

#     if "INVOICE_ADDRESS" in results:
#         structured["INVOICE_ADDRESS"] = " ".join(results["INVOICE_ADDRESS"])

#     if "DELIVERY_ADDRESS" in results:
#         structured["DELIVERY_ADDRESS"] = " ".join(results["DELIVERY_ADDRESS"])

#     # Items (align ITEM_NAME, UNIT_PRICE, QUANTITY)
#     item_names = results.get("ITEM_NAME", [])
#     unit_prices = results.get("UNIT_PRICE", [])
#     quantities = results.get("QUANTITY", [])

#     max_len = max(len(item_names), len(unit_prices), len(quantities))
#     for i in range(max_len):
#         structured["ITEMS"].append({
#             "ITEM_NAME": item_names[i] if i < len(item_names) else None,
#             "UNIT_PRICE": unit_prices[i] if i < len(unit_prices) else None,
#             "QUANTITY": quantities[i] if i < len(quantities) else None
#         })

#     return structured


# # ==== RUN ====
# if __name__ == "__main__":
#     po_image = "./data/images/PDF_01_page1.png"
#     output = predict(po_image)

#     with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
#         json.dump(output, f, indent=2, ensure_ascii=False)

#     print(f"✅ Extracted PO data saved to {OUTPUT_JSON}")
#     print(json.dumps(output, indent=2, ensure_ascii=False))




import numpy as np
if not hasattr(np, 'int'):
    np.int = int
if not hasattr(np, 'float'):
    np.float = float

import torch
from transformers import AutoProcessor, LayoutLMv3ForTokenClassification
from PIL import Image
import json
import re
from paddleocr import PaddleOCR

# ==== SETTINGS ====
DEVICE = "cpu"
MODEL_DIR = "./models/final_model"
OUTPUT_JSON = "./extracted_po.json"

label2id = {
    "O": 0,
    "PO_NUMBER": 1,
    "CURRENCY": 2,
    "TOTAL_VALUE": 3,
    "CUSTOMER": 4,
    "INVOICE_ADDRESS": 5,
    "DELIVERY_ADDRESS": 6,
    "ITEM_NAME": 7,
    "UNIT_PRICE": 8,
    "QUANTITY": 9
}
id2label = {v: k for k, v in label2id.items()}

# ==== LOAD MODEL ====
processor = AutoProcessor.from_pretrained(MODEL_DIR, apply_ocr=False)
model = LayoutLMv3ForTokenClassification.from_pretrained(MODEL_DIR)
model.to(DEVICE)
model.eval()

# ==== HELPERS ====
def normalize_box(box, width, height):
    return [
        int(1000 * box[0] / width),
        int(1000 * box[1] / height),
        int(1000 * box[2] / width),
        int(1000 * box[3] / height)
    ]

ocr = PaddleOCR(use_angle_cls=True, lang="en")

def ocr_image(image_path):
    image = Image.open(image_path).convert("RGB")
    ocr_result = ocr.ocr(image_path, cls=True)

    words, boxes = [], []
    width, height = image.size

    print("\n🔎 OCR Extracted Values:")
    print("=" * 50)

    for line in ocr_result[0]:
        text, conf = line[1]
        (x_min, y_min), (x_max, y_max) = line[0][0], line[0][2]
        words.append(text)
        boxes.append(normalize_box([x_min, y_min, x_max, y_max], width, height))

        # Print each OCR result
        print(f"Word: {text}, Confidence: {conf:.2f}, "
              f"Box: {normalize_box([x_min, y_min, x_max, y_max], width, height)}")

    print("=" * 50 + "\n")
    return image, words, boxes

# ==== PREDICTION ====
def predict(image_path):
    image, words, boxes = ocr_image(image_path)

    encoding = processor(
        image,
        words,
        boxes=boxes,
        return_tensors="pt",
        truncation=True,
        padding="max_length"
    )
    for k, v in encoding.items():
        encoding[k] = v.to(DEVICE)

    with torch.no_grad():
        outputs = model(**encoding)
        predictions = outputs.logits.argmax(-1).squeeze().tolist()

    # Print all model-labeled values
    print("\n📝 Model Predictions:")
    print("=" * 50)
    for word, pred_id in zip(words, predictions):
        label = id2label[pred_id]
        print(f"Word: {word} | Label: {label}")
    print("=" * 50 + "\n")

    # Collect predictions by label
    results = {}
    for word, pred_id in zip(words, predictions):
        label = id2label[pred_id]
        if label != "O" and word.strip():
            results.setdefault(label, []).append(word)

    # Post-process into structured JSON
    structured = {
        "PO_NUMBER": None,
        "CURRENCY": None,
        "TOTAL_VALUE": None,
        "CUSTOMER": None,
        "INVOICE_ADDRESS": None,
        "DELIVERY_ADDRESS": None,
        "ITEMS": []
    }

    if "PO_NUMBER" in results:
        match = re.search(r"[A-Z0-9-]+", " ".join(results["PO_NUMBER"]))
        structured["PO_NUMBER"] = match.group(0) if match else " ".join(results["PO_NUMBER"])

    if "CURRENCY" in results:
        structured["CURRENCY"] = " ".join(results["CURRENCY"])

    if "TOTAL_VALUE" in results:
        match = re.search(r"([A-Z]{2,3}\s*\d+[,.]?\d*)", " ".join(results["TOTAL_VALUE"]))
        structured["TOTAL_VALUE"] = match.group(1) if match else " ".join(results["TOTAL_VALUE"])

    if "CUSTOMER" in results:
        structured["CUSTOMER"] = " ".join(results["CUSTOMER"])

    if "INVOICE_ADDRESS" in results:
        structured["INVOICE_ADDRESS"] = " ".join(results["INVOICE_ADDRESS"])

    if "DELIVERY_ADDRESS" in results:
        structured["DELIVERY_ADDRESS"] = " ".join(results["DELIVERY_ADDRESS"])

    # Items (align ITEM_NAME, UNIT_PRICE, QUANTITY)
    item_names = results.get("ITEM_NAME", [])
    unit_prices = results.get("UNIT_PRICE", [])
    quantities = results.get("QUANTITY", [])

    max_len = max(len(item_names), len(unit_prices), len(quantities))
    for i in range(max_len):
        structured["ITEMS"].append({
            "ITEM_NAME": item_names[i] if i < len(item_names) else None,
            "UNIT_PRICE": unit_prices[i] if i < len(unit_prices) else None,
            "QUANTITY": quantities[i] if i < len(quantities) else None
        })

    return structured

# ==== RUN ====
if __name__ == "__main__":
    po_image = "./data/images/PDF_04_page1.png"
    output = predict(po_image)

    # Save to JSON file
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"✅ Extracted PO data saved to {OUTPUT_JSON}")
    print(json.dumps(output, indent=2, ensure_ascii=False))