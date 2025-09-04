import torch
from torch.utils.data import Dataset
from transformers import LayoutLMv3Processor
from PIL import Image
from transformers import LayoutLMv3ImageProcessor

class COCODataset(Dataset):
    def __init__(self, samples, processor: LayoutLMv3ImageProcessor, label2id, max_length=512):
        self.samples = samples
        self.processor = processor
        self.label2id = label2id
        self.max_length = max_length

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        sample = self.samples[idx]
        image_path = sample["image"]
        image = Image.open(image_path).convert("RGB")

        x, y, w, h = sample["bbox"]
        boxes = [[x, y, x + w, y + h]]
        text = [""]  # dummy text for LayoutLMv3
        labels = [sample["category_id"]]

        encoding = self.processor(
            images=image,
            text=text,          # use text instead of words
            boxes=boxes,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )

        # map labels to ids, pad to max length
        label_ids = labels + [self.label2id["Ignore"]] * (self.max_length - len(labels))
        encoding["labels"] = torch.tensor(label_ids[:self.max_length])

        return {k: v.squeeze() for k, v in encoding.items()}