
---

## Setup and Installation

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/SafeCityAI.git
cd SafeCityAI
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Clone YOLOv5
```bash
git clone https://github.com/ultralytics/yolov5
cd yolov5
pip install -r requirements.txt
```

### 4. Download model weights
Download best.pt from the Releases section and place it in the project root folder.

### 5. Run the app
```bash
streamlit run app.py
```

---

## API Usage

Start the Flask API:
```bash
python server.py
```

Test with curl:
```bash
curl -X POST -F "image=@test.jpg" http://localhost:5000/detect
```

Sample API response:
```json
{
  "total_detections": 2,
  "violations_found": 1,
  "alert": true,
  "detections": [
    {
      "class": "without_helmet",
      "confidence": 0.88,
      "box": {"x1": 100, "y1": 120, "x2": 200, "y2": 280},
      "violation": true
    }
  ]
}
```

---

## Tech Stack
- Model: YOLOv5s with Transfer Learning from COCO
- Framework: PyTorch
- UI: Streamlit
- Video Processing: OpenCV
- API: Flask
- Dataset: Roboflow (3,341 images)

---

## Use Cases
- Traffic law enforcement automation
- Smart city surveillance
- Construction site safety monitoring
- Two-wheeler safety compliance

---

## Dataset
Dataset sourced from Roboflow Universe.
Classes: with_helmet, without_helmet
License: CC BY 4.0

---

## Author
Built as part of SafeCityAI - AI-powered traffic safety system.
