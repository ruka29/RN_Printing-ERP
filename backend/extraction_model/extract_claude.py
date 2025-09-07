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
from collections import Counter

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
try:
    processor = AutoProcessor.from_pretrained(MODEL_DIR, apply_ocr=False)
    model = LayoutLMv3ForTokenClassification.from_pretrained(MODEL_DIR)
    model.to(DEVICE)
    model.eval()
    print("✅ Model loaded successfully")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    exit()

# ==== CRITICAL DEBUGGING FUNCTIONS ====
def deep_model_analysis():
    """Perform deep analysis of the model"""
    print("\n🔬 DEEP MODEL ANALYSIS")
    print("=" * 60)
    
    # Check model config vs our mapping
    print(f"Model config num_labels: {model.config.num_labels}")
    print(f"Our num_labels: {len(label2id)}")
    
    if hasattr(model.config, 'id2label'):
        print(f"Model config id2label: {model.config.id2label}")
        if model.config.id2label != id2label:
            print("⚠️  CRITICAL: Model was trained with different labels!")
            print("This is likely the main issue!")
            return False
    
    # Check classifier weights
    classifier_weights = model.classifier.weight.data
    print(f"Classifier weights shape: {classifier_weights.shape}")
    print(f"Classifier bias: {model.classifier.bias.data}")
    
    # Check if weights are reasonable
    weight_std = classifier_weights.std().item()
    print(f"Weight standard deviation: {weight_std}")
    
    if weight_std < 0.01:
        print("⚠️  WARNING: Very small weight variation - model might not be trained properly")
    
    return True

def test_with_dummy_input():
    """Test model with simple dummy input"""
    print("\n🧪 TESTING WITH DUMMY INPUT")
    print("=" * 50)
    
    # Create simple test case
    dummy_image = Image.new('RGB', (224, 224), color='white')
    dummy_words = ["PO", "123", "USD", "100.00", "Apple", "Inc"]
    dummy_boxes = [[0, 0, 50, 20], [60, 0, 100, 20], [110, 0, 150, 20], 
                   [160, 0, 220, 20], [0, 30, 80, 50], [90, 30, 150, 50]]
    
    try:
        encoding = processor(
            dummy_image,
            dummy_words,
            boxes=dummy_boxes,
            return_tensors="pt",
            truncation=True,
            padding="max_length"
        )
        
        with torch.no_grad():
            outputs = model(**encoding)
            predictions = outputs.logits.argmax(-1).squeeze().tolist()
            probabilities = torch.softmax(outputs.logits, dim=-1)
        
        print("Dummy test results:")
        for word, pred_id in zip(dummy_words, predictions[:len(dummy_words)]):
            print(f"'{word}' -> {id2label.get(pred_id, 'UNKNOWN')}")
            
        # Check if all predictions are the same
        unique_predictions = set(predictions[:len(dummy_words)])
        if len(unique_predictions) == 1:
            print("⚠️  CRITICAL: All predictions are identical - model is broken!")
            return False
            
    except Exception as e:
        print(f"❌ Error in dummy test: {e}")
        return False
    
    return True

# ==== RULE-BASED EXTRACTION (BACKUP SOLUTION) ====
def extract_with_rules_only(words, boxes=None):
    """Pure rule-based extraction as fallback"""
    results = {
        "PO_NUMBER": None,
        "CURRENCY": None,
        "TOTAL_VALUE": None,
        "CUSTOMER": None,
        "INVOICE_ADDRESS": None,
        "DELIVERY_ADDRESS": None,
        "ITEMS": []
    }
    
    full_text = " ".join(words)
    
    # PO Number - look for patterns like "P.O. No. 1795" or "PO: 1795"
    po_patterns = [
        r"P\.?O\.?\s*(?:No\.?|Number|#)?\s*:?\s*([A-Z0-9-]+)",
        r"Purchase\s*Order\s*(?:No\.?|#)?\s*:?\s*([A-Z0-9-]+)",
        r"(?:^|\s)(\d{4,6})(?=\s|$)"  # Standalone 4-6 digit numbers
    ]
    
    for pattern in po_patterns:
        match = re.search(pattern, full_text, re.IGNORECASE)
        if match:
            results["PO_NUMBER"] = match.group(1)
            break
    
    # Currency - look for currency codes
    currency_match = re.search(r'\b(USD|EUR|GBP|LKR|INR|CAD|AUD)\b', full_text)
    if currency_match:
        results["CURRENCY"] = currency_match.group(1)
    
    # Total Value - look for "Total" followed by amount
    total_patterns = [
        r"Total\s*:?\s*([A-Z]{2,3}?\s*[\d,]+\.?\d*)",
        r"([A-Z]{2,3}\s*[\d,]+\.?\d*)\s*$",  # Amount at end of line
        r"(\d{1,3}(?:,\d{3})*\.?\d{0,2})"   # Large formatted numbers
    ]
    
    for pattern in total_patterns:
        matches = re.finditer(pattern, full_text, re.IGNORECASE)
        amounts = [match.group(1) for match in matches]
        if amounts:
            # Take the largest amount as total
            results["TOTAL_VALUE"] = max(amounts, key=lambda x: float(re.sub(r'[^\d.]', '', x)) if re.search(r'\d', x) else 0)
            break
    
    # Customer - look for company indicators
    customer_patterns = [
        r"([A-Za-z\s]+(?:Ltd|Pvt|Inc|Corp|Company|Tech)(?:\s*\([^)]*\))?)",
        r"Vendor\s*:?\s*([A-Za-z\s&]+)",
        r"([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Za-z]+)*)"  # Capitalized names
    ]
    
    for pattern in customer_patterns:
        match = re.search(pattern, full_text, re.IGNORECASE)
        if match and len(match.group(1).strip()) > 3:
            results["CUSTOMER"] = match.group(1).strip()
            break
    
    # Extract items (simplified)
    # Look for quantity + description + price patterns
    item_pattern = r"(\d{1,4})\s+([A-Za-z][^0-9]{10,50})\s+([\d,]+\.?\d*)"
    item_matches = re.finditer(item_pattern, full_text)
    
    items = []
    for match in item_matches:
        qty, desc, price = match.groups()
        items.append({
            "ITEM_NAME": desc.strip(),
            "UNIT_PRICE": price,
            "QUANTITY": qty
        })
    
    results["ITEMS"] = items
    
    return results

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

    print("\n🔎 OCR Results (first 10):")
    print("=" * 50)

    for i, line in enumerate(ocr_result[0]):
        text, conf = line[1]
        (x_min, y_min), (x_max, y_max) = line[0][0], line[0][2]
        words.append(text)
        boxes.append(normalize_box([x_min, y_min, x_max, y_max], width, height))

        # Print only first 10 for debugging
        if i < 10:
            print(f"Word: '{text}', Confidence: {conf:.2f}")

    print(f"... and {len(words)-10} more words")
    print("=" * 50 + "\n")
    return image, words, boxes

# ==== MAIN PREDICTION FUNCTION ====
def predict(image_path):
    print("🚀 Starting PO Data Extraction")
    print("=" * 50)
    
    # Step 1: Deep model analysis
    model_ok = deep_model_analysis()
    
    # Step 2: Test with dummy input
    dummy_ok = test_with_dummy_input()
    
    # Step 3: Process actual image
    image, words, boxes = ocr_image(image_path)
    
    # If model seems broken, use rules only
    if not model_ok or not dummy_ok:
        print("\n⚠️  MODEL ISSUES DETECTED - USING RULE-BASED EXTRACTION ONLY")
        return extract_with_rules_only(words, boxes)
    
    # Try model prediction
    try:
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
            logits = outputs.logits
            predictions = outputs.logits.argmax(-1).squeeze().tolist()
            probabilities = torch.softmax(logits, dim=-1)

        # Check prediction quality
        pred_labels = [id2label.get(p, 'UNK') for p in predictions[:len(words)]]
        label_distribution = Counter(pred_labels)
        
        print(f"\n📊 Model Prediction Distribution: {dict(label_distribution)}")
        
        # If model is clearly broken (>80% same label), use rules
        most_common_count = label_distribution.most_common(1)[0][1]
        if most_common_count / len(pred_labels) > 0.8:
            print("⚠️  MODEL PREDICTIONS ARE HEAVILY BIASED - SWITCHING TO RULES")
            return extract_with_rules_only(words, boxes)
        
        # Otherwise, process model results normally
        results = {}
        for word, pred_id in zip(words, predictions):
            if pred_id < len(id2label):
                label = id2label[pred_id]
                if label != "O" and word.strip():
                    results.setdefault(label, []).append(word)
        
        print(f"\n📋 Model extracted categories: {list(results.keys())}")
        
    except Exception as e:
        print(f"❌ Model prediction failed: {e}")
        print("🔄 Falling back to rule-based extraction")
        return extract_with_rules_only(words, boxes)
    
    # Post-process model results (simplified)
    structured = {
        "PO_NUMBER": " ".join(results.get("PO_NUMBER", [])) or None,
        "CURRENCY": " ".join(results.get("CURRENCY", [])) or None,
        "TOTAL_VALUE": " ".join(results.get("TOTAL_VALUE", [])) or None,
        "CUSTOMER": " ".join(results.get("CUSTOMER", [])) or None,
        "INVOICE_ADDRESS": " ".join(results.get("INVOICE_ADDRESS", [])) or None,
        "DELIVERY_ADDRESS": " ".join(results.get("DELIVERY_ADDRESS", [])) or None,
        "ITEMS": []
    }
    
    # If model results are empty/poor, supplement with rules
    rule_results = extract_with_rules_only(words, boxes)
    
    for key in structured:
        if not structured[key] and rule_results[key]:
            structured[key] = rule_results[key]
            print(f"🔄 Used rule-based result for {key}")
    
    return structured

# ==== RUN ====
if __name__ == "__main__":
    po_image = "./data/images/PDF_04_page1.png"
    
    try:
        output = predict(po_image)

        # Save to JSON file
        with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Results saved to {OUTPUT_JSON}")
        print("\n📄 Final Output:")
        print("=" * 40)
        print(json.dumps(output, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"❌ Critical error: {str(e)}")
        import traceback
        traceback.print_exc()