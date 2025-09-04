print("Starting script...")

import json

def convert_bounding_box(x, y, width, height, image_width, image_height):
    """Convert percentage coords into absolute coordinates."""
    x1 = int(x / 100 * image_width)
    y1 = int(y / 100 * image_height)
    x2 = int((x + width) / 100 * image_width)
    y2 = int((y + height) / 100 * image_height)
    return [x1, y1, x2, y2]

with open("training_dataset.json") as f:
    dataset = json.load(f)

output = []

for annotated_image in dataset:
    data = {}
    ann_list = []

    if "ocr" not in annotated_image or "bbox" not in annotated_image:
        continue

    # filename
    v = annotated_image["ocr"].split("8080/")[-1]
    data["file_name"] = f"../data/images/{v}"

    width = annotated_image["bbox"][0]["original_width"]
    height = annotated_image["bbox"][0]["original_height"]
    data["width"] = width
    data["height"] = height

    # Combine bbox and field info
    for i, bb in enumerate(annotated_image["bbox"]):
        # Find matching field by coordinates
        field_label = -1
        for field in annotated_image.get("field", []) + annotated_image.get("table_field", []):
            if (
                abs(field["x"] - bb["x"]) < 0.01 and
                abs(field["y"] - bb["y"]) < 0.01 and
                abs(field["width"] - bb["width"]) < 0.01 and
                abs(field["height"] - bb["height"]) < 0.01
            ):
                field_label = field["rectanglelabels"][-1] if field["rectanglelabels"] else -1
                break

        ann_dict = {
            "box": convert_bounding_box(bb["x"], bb["y"], bb["width"], bb["height"], width, height),
            "text": annotated_image.get("transcription", [])[i] if i < len(annotated_image.get("transcription", [])) else "",
            "label": field_label
        }
        ann_list.append(ann_dict)

    data["annotations"] = ann_list
    output.append(data)

with open("converted_layoutLMV3_dataset.json", "w") as f:
    json.dump(output, f, indent=4)