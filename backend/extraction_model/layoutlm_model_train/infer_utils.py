import torch
import json
from transformers import LayoutLMv3FeatureExtractor, LayoutLMv3TokenizerFast, LayoutLMv3Processor, LayoutLMv3ForTokenClassification
from utils import dataSetFormat
from collections import defaultdict
from PIL import Image

# label mapping (must match training)
id2label = {
    0: "PO Number",
    1: "Customer",
    2: "Invoice Address",
    3: "Delivery Address",
    4: "Currency",
    5: "PO Value",
    6: "Item Description",
    7: "Quantity",
    8: "Unit Price",
    9: "Ignore"
}
label2id = {v: k for k, v in id2label.items()}


def load_model(model_path="../models/best_model.bin"):
    feature_extractor = LayoutLMv3FeatureExtractor(apply_ocr=False)
    tokenizer = LayoutLMv3TokenizerFast.from_pretrained("../models/layoutlmv3-base")
    processor = LayoutLMv3Processor(tokenizer=tokenizer, feature_extractor=feature_extractor)

    model = LayoutLMv3ForTokenClassification.from_pretrained(
        "../models/layoutlmv3-base",
        num_labels=len(id2label),
        id2label=id2label,
        label2id=label2id
    )
    model.load_state_dict(torch.load(model_path, map_location="cpu"))
    model.eval()

    return model, processor


def predict(model, processor, image_path):
    # Run OCR + formatting
    img = Image.open(image_path).convert("RGB")
    ocr_result, width, height = dataSetFormat(img)

    words = ocr_result["tokens"]
    boxes = ocr_result["bboxes"]

    # Encode into LayoutLMv3 format
    encoding = processor(
        images=img,
        words=[words],
        boxes=[boxes],
        max_length=512,
        padding="max_length",
        truncation=True,
        return_tensors="pt"
    )

    with torch.no_grad():
        outputs = model(**encoding)
        predictions = torch.argmax(outputs.logits, dim=-1).squeeze().tolist()

    labels = [id2label[p] for p in predictions]

    results = []
    for word, box, label in zip(words, boxes, labels):
        if label != "Ignore":
            results.append({"word": word, "bbox": box, "label": label})

    return results


def postprocess(results):
    structured_output = defaultdict(list)
    for r in results:
        structured_output[r["label"]].append(r["word"])

    # join tokens into full values
    for k in structured_output:
        structured_output[k] = " ".join(structured_output[k])

    return dict(structured_output)