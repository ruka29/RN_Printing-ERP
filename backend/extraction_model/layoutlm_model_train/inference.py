import argparse
import json
from infer_utils import load_model, predict, postprocess

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True, help="Path to input image")
    parser.add_argument("--output", required=False, help="Path to save output JSON")
    args = parser.parse_args()

    model, processor = load_model()

    results = predict(model, processor, args.image)
    structured = postprocess(results)

    print("\n✅ Extracted Fields:\n", json.dumps(structured, indent=2))

    if args.output:
        with open(args.output, "w") as f:
            json.dump(structured, f, indent=2)

if __name__ == "__main__":
    main()