
from flask import Flask, request, jsonify
import torch
from PIL import Image
import io

app = Flask(__name__)

# Load model once at startup
model = torch.hub.load("ultralytics/yolov5", "custom",
                        path="best.pt", force_reload=False)
model.conf = 0.5

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "running", "model": "YOLOv5 Helmet Detector"})

@app.route("/detect", methods=["POST"])
def detect():
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400

    file = request.files["image"]
    img = Image.open(io.BytesIO(file.read()))
    results = model(img)

    detections = []
    for *box, conf, cls in results.xyxy[0].tolist():
        label = model.names[int(cls)]
        detections.append({
            "class": label,
            "confidence": round(conf, 2),
            "box": {
                "x1": round(box[0]), "y1": round(box[1]),
                "x2": round(box[2]), "y2": round(box[3])
            },
            "violation": label == "without_helmet"
        })

    violations = [d for d in detections if d["violation"]]

    return jsonify({
        "total_detections": len(detections),
        "violations_found": len(violations),
        "alert": len(violations) > 0,
        "detections": detections
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)
