# 🚦 SafeCityAI

SafeCityAI is a computer vision–based system that detects helmet usage by motorbike riders using a YOLOv5 model in real time.

---

## 🚀 Features
- Helmet / No-Helmet detection  
- Image & video processing  
- Backend API support  
- Sample test images  

---

## 🛠️ Tech Stack
- Python  
- YOLOv5  
- OpenCV  
- Flask  
- Streamlit  

---

## ⚙️ Setup and Installation

### 1. Clone the repository
git clone https://github.com/priyakirdak1535/SafeCityAI.git  
cd SafeCityAI  

### 2. Install dependencies
pip install -r requirements.txt  

### 3. Clone YOLOv5
git clone https://github.com/ultralytics/yolov5  
cd yolov5  
pip install -r requirements.txt  

### 4. Add model
Place your trained `best.pt` file in the project root folder.

---

## ▶️ Run the App
streamlit run app.py  

---

## 🔌 API Usage

Start server:
python server.py  

Test:
curl -X POST -F "image=@test.jpg" http://localhost:5000/detect  

---

## 📊 Use Cases
- Traffic law enforcement  
- Smart city surveillance  
- Helmet safety monitoring  

---

## 📜 License
MIT License
