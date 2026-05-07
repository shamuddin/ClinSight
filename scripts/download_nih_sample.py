"""Download 6 representative NIH Chest X-ray14 images for demo cases.

Uses HuggingFace datasets to stream the NIH-Chest-Xray-14 dataset.
Maps each demo case to an image with matching pathology labels.
"""

import json
from pathlib import Path
from PIL import Image
import io

try:
    from datasets import load_dataset
except ImportError as e:
    raise ImportError("Please install datasets: pip install datasets") from e

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_IMG_DIR = PROJECT_ROOT / "backend" / "data" / "images"
FRONTEND_IMG_DIR = PROJECT_ROOT / "frontend" / "react-app" / "public" / "demo-images"
CASES_JSON = PROJECT_ROOT / "backend" / "data" / "demo_cases.json"

BACKEND_IMG_DIR.mkdir(parents=True, exist_ok=True)
FRONTEND_IMG_DIR.mkdir(parents=True, exist_ok=True)

# Case-to-pathology mapping
# We want images whose labels contain these keywords
CASE_MAP = {
    "CS-2024-001": ["Cardiomegaly", "Effusion"],          # Chest pain
    "CS-2024-002": ["Pneumothorax", "Infiltration"],      # Head trauma
    "CS-2024-003": ["Pneumonia", "Infiltration"],         # Pediatric fever
    "CS-2024-004": ["Pneumonia", "Edema", "Infiltration"], # Sepsis/AMS
    "CS-2024-005": ["No Finding"],                         # Headache (normal)
    "CS-2024-006": ["No Finding", "Pneumothorax"],        # Abdominal pain
}


def label_matches(target_keywords, label_text):
    """Check if any target keyword appears in the label text."""
    label_lower = label_text.lower()
    for kw in target_keywords:
        if kw.lower() in label_lower:
            return True
    return False


def download_images():
    print("Loading NIH Chest X-ray14 dataset from HuggingFace...")
    # Stream the dataset to avoid downloading everything
    ds = load_dataset("BahaaEldin0/NIH-Chest-Xray-14", split="train", streaming=True)

    found = {case_id: False for case_id in CASE_MAP}
    counts = {case_id: 0 for case_id in CASE_MAP}
    max_per_case = 3  # Save a few options

    for item in ds:
        # item has keys like: 'image', 'label', ' findings', etc.
        # Different HF repos use slightly different column names
        img = item.get("image")
        label = item.get("label") or item.get("findings") or item.get("Finding Labels") or ""

        if img is None:
            continue

        # label might be a string like "Cardiomegaly|Infiltration"
        label_str = str(label) if label else ""

        for case_id, keywords in CASE_MAP.items():
            if found[case_id]:
                continue
            if label_matches(keywords, label_str):
                counts[case_id] += 1
                suffix = f"_{counts[case_id]}" if counts[case_id] > 1 else ""
                filename = f"{case_id}{suffix}.png"

                # Save image
                if isinstance(img, Image.Image):
                    pil_img = img
                else:
                    # Some datasets return bytes or other formats
                    pil_img = Image.open(io.BytesIO(img))

                # Convert to RGB if needed
                if pil_img.mode != "RGB":
                    pil_img = pil_img.convert("RGB")

                backend_path = BACKEND_IMG_DIR / filename
                frontend_path = FRONTEND_IMG_DIR / filename

                pil_img.save(backend_path, "PNG")
                pil_img.save(frontend_path, "PNG")

                print(f"  Saved {case_id}: {filename} (labels: {label_str})")

                if counts[case_id] >= max_per_case:
                    found[case_id] = True

        if all(found.values()):
            break

    # Report
    print("\nDownload summary:")
    for case_id in CASE_MAP:
        if counts[case_id] == 0:
            print(f"  {case_id}: NOT FOUND (tried keywords: {CASE_MAP[case_id]})")
        else:
            print(f"  {case_id}: {counts[case_id]} image(s) saved")

    # Update demo_cases.json with the first image for each case
    if CASES_JSON.exists():
        cases = json.loads(CASES_JSON.read_text())
        for case in cases:
            case_id = case["case_id"]
            first_img = BACKEND_IMG_DIR / f"{case_id}.png"
            if first_img.exists():
                case["image_path"] = str(first_img.relative_to(PROJECT_ROOT)).replace("\\", "/")
                print(f"  Updated {case_id} image_path -> {case['image_path']}")
            else:
                # Try with _1 suffix
                alt = BACKEND_IMG_DIR / f"{case_id}_1.png"
                if alt.exists():
                    case["image_path"] = str(alt.relative_to(PROJECT_ROOT)).replace("\\", "/")
                    print(f"  Updated {case_id} image_path -> {case['image_path']}")

        CASES_JSON.write_text(json.dumps(cases, indent=2))
        print(f"\nUpdated {CASES_JSON}")


if __name__ == "__main__":
    download_images()
