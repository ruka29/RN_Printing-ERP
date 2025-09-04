import json
import os

def load_coco_annotations(json_path, images_dir):
    with open(json_path, "r") as f:
        coco = json.load(f)

    # Map image id to image info
    id2img = {img["id"]: img for img in coco["images"]}

    samples = []
    for ann in coco["annotations"]:
        image_info = id2img[ann["image_id"]]
        samples.append({
            "image": os.path.join(images_dir, os.path.basename(image_info["file_name"])),  # key "image" for loader
            "bbox": ann["bbox"],  # [x, y, w, h]
            "category_id": ann["category_id"]
        })
    return samples