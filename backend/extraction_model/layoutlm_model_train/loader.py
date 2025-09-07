import torch
from torch.utils.data import Dataset
from transformers import LayoutLMv3Processor
from PIL import Image
from utils import compute_iou  # Add this function from earlier responses if not present

def compute_iou(box_a, box_b):
    xA = max(box_a[0], box_b[0])
    yA = max(box_a[1], box_b[1])
    xB = min(box_a[0] + box_a[2], box_b[0] + box_b[2])
    yB = min(box_a[1] + box_b[3], box_b[1] + box_b[3])
    inter_area = max(0, xB - xA) * max(0, yB - yA)
    box_a_area = box_a[2] * box_a[3]
    box_b_area = box_b[2] * box_b[3]
    return inter_area / (box_a_area + box_b_area - inter_area)

class COCODataset(Dataset):
    def __init__(self, samples, processor: LayoutLMv3Processor, label2id, max_length=512):
        self.samples = samples
        self.processor = processor
        self.label2id = label2id
        self.max_length = max_length
        self.bio_label2id = {"O": 0}
        for i, cat in enumerate(["Currency", "Customer", "Delivery Address", "Ignore", "Invoice Address",
                                "Item Description", "PO Number", "PO Value", "Quantity", "Unit Price"], 1):
            self.bio_label2id[f"B-{cat}"] = 2 * i - 1
            self.bio_label2id[f"I-{cat}"] = 2 * i

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        sample = self.samples[idx]
        image = Image.open(sample["image"]).convert("RGB")
        ocr_results = sample["ocr"]
        words = [item["text"] for item in ocr_results]
        ocr_boxes = [item["bbox"] for item in ocr_results]

        # Normalize boxes to 0-1000
        width, height = image.size
        boxes = [[int(b * 1000 / width) if i % 2 == 0 else int(b * 1000 / height) 
                  for i, b in enumerate([x, y, w, h])] for x, y, w, h in ocr_boxes]

        # Assign BIO labels based on entity bbox overlap
        entity_bbox = sample["bbox"]
        labels = [0] * len(words)  # Default "O"
        for i, word_box in enumerate(ocr_boxes):
            if compute_iou(word_box, entity_bbox) > 0.5:
                cat_id = sample["category_id"]
                cat_name = ["Currency", "Customer", "Delivery Address", "Ignore", "Invoice Address",
                            "Item Description", "PO Number", "PO Value", "Quantity", "Unit Price"][cat_id]
                labels[i] = self.bio_label2id[f"B-{cat_name}"] if i == 0 else self.bio_label2id[f"I-{cat_name}"]

        # Pad labels
        label_ids = labels + [self.bio_label2id["O"]] * (self.max_length - len(labels))

        encoding = self.processor(
            images=image,
            text=words,
            boxes=boxes,
            word_labels=label_ids[:self.max_length],
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )

        return {k: v.squeeze() for k, v in encoding.items()}