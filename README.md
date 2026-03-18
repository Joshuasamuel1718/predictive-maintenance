# 🚀 Predictive Maintenance System

## 📌 Overview

This project predicts machine failures using Machine Learning and displays results in an interactive dashboard.

It helps in identifying potential failures early, improving maintenance planning and reducing downtime.

---

## 🛠️ Tech Stack

* **Backend:** Python, Flask
* **Frontend:** React.js
* **Machine Learning:** Scikit-learn
* **Data Processing:** Pandas, NumPy

---

## ⚙️ Features

* Predict machine failure based on sensor data
* Display failure probability using gauge chart
* Interactive dashboard UI
* REST API integration between frontend and backend

---

## 📂 Project Structure

```
predictive-maintenance/
│
├── api.py                 # Flask backend
├── Main.py                # Model training
├── predictive_maintenance.csv
├── README.md
│
├── maintenance-dashboard/  # React frontend
│   ├── src/
│   ├── public/
│   ├── package.json
```

---

## ▶️ How to Run

### 🔹 1. Train Model

```bash
python Main.py
```

### 🔹 2. Start Backend

```bash
python api.py
```

### 🔹 3. Start Frontend

```bash
cd maintenance-dashboard
npm install
npm start
```

---

## 📊 Input Features

* Type (L, M, H)
* Air Temperature
* Process Temperature
* Rotational Speed
* Torque
* Tool Wear

---

## 📈 Output

* Machine Status (Failure / Normal)
* Failure Probability (0–100%)

---

## 🎯 Future Improvements

* Real-time data streaming
* Advanced visualization (charts, alerts)
* Deployment using cloud platforms

---

## 👨‍💻 Author

Joshua Samuel T|

Kamalesh K|

Maruthu Pandiyan M|

Monish Praveen J|

---
