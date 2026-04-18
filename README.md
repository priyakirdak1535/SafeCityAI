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
=======
# 🚦 SafeCityAI

SafeCityAI is an AI-powered traffic safety system that uses a custom-trained **YOLOv5** model to detect helmet usage by motorbike riders in real-time.

---

## ✨ Features
- **Real-time Detection:** High-speed helmet/no-helmet identification.
- **Dual Interface:** Interactive UI via Streamlit and a robust Backend API via Flask.
- **Visual Feedback:** Bounding boxes with confidence scores and automated violation alerts.
- **Edge-Ready:** Optimized for smart city surveillance and law enforcement automation.

---

## 🛠️ Tech Stack
- **Model:** YOLOv5s (Transfer Learning from COCO)
- **Frameworks:** PyTorch, Flask
- **UI:** Streamlit
- **Processing:** OpenCV
- **Dataset:** Roboflow (3,341 images, CC BY 4.0)

---

## ⚙️ Setup and Installation

### 1. Clone the repository
```bash
git clone [https://github.com/priyakirdak1535/SafeCityAI.git](https://github.com/priyakirdak1535/SafeCityAI.git)
cd SafeCityAI
>>>>>>> 94fc1a08f96a0a9940b606d8b997d39a1cb1264c
