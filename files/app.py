from flask import Flask, request, jsonify, render_template
from PIL import Image
import torch
from transformers import AutoModelForImageClassification, AutoProcessor
import requests
import io

app = Flask(__name__, template_folder="templates")

# Load the model and processor
MODEL_NAME = "umm-maybe/AI-image-detector"
model = AutoModelForImageClassification.from_pretrained(MODEL_NAME)
processor = AutoProcessor.from_pretrained(MODEL_NAME)

@app.route("/")
def home():
    """Serve the HTML form for uploading images or URLs."""
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    """Handle image analysis requests."""
    img = None

    # Handle file upload
    if "file" in request.files and request.files["file"].filename != "":
        img_file = request.files["file"]
        img = Image.open(img_file).convert("RGB")
    elif "url" in request.form and request.form["url"].strip() != "":
        img_url = request.form["url"].strip()
        try:
            response = requests.get(img_url)
            response.raise_for_status()
            img = Image.open(io.BytesIO(response.content)).convert("RGB")
        except Exception as e:
            return jsonify({"error": f"Failed to fetch image from URL: {str(e)}"}), 400
    else:
        return jsonify({"error": "No valid image file or URL provided"}), 400

    # Preprocess the image
    inputs = processor(images=img, return_tensors="pt")

    # Run inference
    with torch.no_grad():
        outputs = model(**inputs)

    # Extract logits and analyze confidence
    logits = outputs.logits
    probabilities = torch.nn.functional.softmax(logits, dim=-1)

    # Assuming binary classification with class 1 = "AI-generated"
    is_ai_generated = probabilities[0][0].item() > 0.5
    confidence = probabilities[0][1].item() if is_ai_generated else probabilities[0][0].item()

    return jsonify({
        "is_ai_generated": is_ai_generated,
        "confidence": confidence
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
