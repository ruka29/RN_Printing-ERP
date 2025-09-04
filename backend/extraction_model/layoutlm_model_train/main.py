import torch
from trainer import run_training

if __name__ == "__main__":
    label2id = {
        "Currency": 0,
        "Customer": 1,
        "Delivery Address": 2,
        "Ignore": 3,
        "Invoice Address": 4,
        "Item Description": 5,
        "PO Number": 6,
        "PO Value": 7,
        "Quantity": 8,
        "Unit Price": 9
    }

    device = "cuda" if torch.cuda.is_available() else "cpu"

    run_training(
        coco_json="dataset/result.json",
        images_dir="../data/images",
        label2id=label2id,
        device=device,
        epochs=20,
        batch_size=2
    )