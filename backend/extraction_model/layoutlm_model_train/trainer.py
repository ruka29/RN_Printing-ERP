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


def run_training(coco_json, images_dir, label2id, device="cpu", epochs=10, batch_size=2):
    # load processor
    feature_extractor = LayoutLMv3FeatureExtractor(apply_ocr=False)
    tokenizer = LayoutLMv3TokenizerFast.from_pretrained("../models/layoutlmv3-base")
    processor = LayoutLMv3Processor(tokenizer=tokenizer, feature_extractor=feature_extractor)

    # load data
    samples = load_coco_annotations(coco_json, images_dir)
    dataset = COCODataset(samples, processor, label2id)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    # model
    model = LayoutLMv3ForTokenClassification.from_pretrained(
        "../models/layoutlmv3-base",
        num_labels=len(label2id),
        id2label={v: k for k, v in label2id.items()},
        label2id=label2id
    ).to(device)

    optimizer = AdamW(model.parameters(), lr=5e-5)

    best_loss = float("inf")
    patience, counter = 3, 0

    # track loss
    train_losses = []
    eval_losses = []

    for epoch in range(epochs):
        print(f"\n===== Epoch {epoch+1}/{epochs} =====")

        print("Starting training...")
        train_loss = train_fn(dataloader, model, optimizer, device)
        train_loss = float(train_loss.detach().numpy()) if torch.is_tensor(train_loss) else float(train_loss)

        print("\nStarting evaluation...")
        eval_loss = eval_fn(dataloader, model, device)
        eval_loss = float(eval_loss.detach().numpy()) if torch.is_tensor(eval_loss) else float(eval_loss)

        print(f"Epoch {epoch+1} - Train loss: {train_loss:.4f}, Eval loss: {eval_loss:.4f}")

        train_losses.append(train_loss)
        eval_losses.append(eval_loss)

        # save progress every epoch (safe checkpointing)
        np.save("../models/train_losses.npy", np.array(train_losses))
        np.save("../models/eval_losses.npy", np.array(eval_losses))

        if eval_loss < best_loss:
            torch.save(model.state_dict(), "../models/best_model.bin")
            print("\n>> Saved new best model.")
            best_loss = eval_loss
            counter = 0
        else:
            counter += 1
            print(f"\nNo improvement. Early stopping counter: {counter}/{patience}")
            if counter >= patience:
                print("Early stopping triggered.")
                break

    print("\nTraining complete. Loss curves and best model saved.")