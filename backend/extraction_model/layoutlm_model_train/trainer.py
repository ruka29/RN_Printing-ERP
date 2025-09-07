import torch
from torch.utils.data import DataLoader
from transformers import (
    LayoutLMv3ForTokenClassification,
    LayoutLMv3FeatureExtractor,
    LayoutLMv3TokenizerFast,
    LayoutLMv3Processor,
    AdamW
)
from loader import COCODataset
from utils import load_coco_annotations
from engine import train_fn, eval_fn
import numpy as np
import os

def run_training(coco_json, images_dir, ocr_json_path, label2id, device="cpu", epochs=5, batch_size=2):
    # Load processor
    feature_extractor = LayoutLMv3FeatureExtractor(apply_ocr=False)
    tokenizer = LayoutLMv3TokenizerFast.from_pretrained("../models/layoutlmv3-base")
    processor = LayoutLMv3Processor(tokenizer=tokenizer, feature_extractor=feature_extractor)

    # Load data
    samples = load_coco_annotations(coco_json, images_dir, ocr_json_path)
    dataset = COCODataset(samples, processor, label2id)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    # Pre-compute BIO label mappings
    bio_labels = {"O": 0}
    for i, cat in enumerate(label2id.keys(), 1):
        bio_labels[f"B-{cat}"] = 2 * i - 1
        bio_labels[f"I-{cat}"] = 2 * i
    id2label = {v: k for k, v in bio_labels.items()}
    label2id_bio = {k: v for k, v in bio_labels.items()}

    # Model
    model = LayoutLMv3ForTokenClassification.from_pretrained(
        "../models/layoutlmv3-base",
        num_labels=len(bio_labels),  # Total number of BIO labels
        id2label=id2label,
        label2id=label2id_bio
    ).to(device)

    optimizer = AdamW(model.parameters(), lr=5e-5)

    best_loss = float("inf")
    patience, counter = 3, 0

    train_losses = []
    eval_losses = []

    os.makedirs("../models", exist_ok=True)

    for epoch in range(epochs):
        print(f"\n===== Epoch {epoch+1}/{epochs} =====")
        train_loss = train_fn(dataloader, model, optimizer, device)
        eval_loss = eval_fn(dataloader, model, device)

        print(f"Epoch {epoch+1} - Train loss: {train_loss:.4f}, Eval loss: {eval_loss:.4f}")

        train_losses.append(train_loss)
        eval_losses.append(eval_loss)

        np.save("../models/train_losses.npy", np.array(train_losses))
        np.save("../models/eval_losses.npy", np.array(eval_losses))

        if eval_loss < best_loss:
            hf_model_dir = "../models/final_model"
            os.makedirs(hf_model_dir, exist_ok=True)
            model.save_pretrained(hf_model_dir)
            processor.save_pretrained(hf_model_dir)
            best_loss = eval_loss
            counter = 0
        else:
            counter += 1
            if counter >= patience:
                print("Early stopping triggered.")
                break

    print("\nTraining complete. Loss curves and best model saved.")