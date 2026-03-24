from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import os
import numpy as np
from datetime import datetime
import pandas as pd
import json
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)

# Load Haarcascade
face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

# Load recognizer
recognizer = cv2.face.LBPHFaceRecognizer_create()

os.makedirs("trainer", exist_ok=True)
os.makedirs("attendance", exist_ok=True)
os.makedirs("captures", exist_ok=True)

# Load student info
def load_student_info():
    try:
        with open("trainer/student_info.json", "r") as f:
            return json.load(f)
    except:
        return {}

student_info = load_student_info()

# Load trained model
try:
    recognizer.read("trainer/trainer.yml")
    print("Face model loaded")
except:
    recognizer = None
    print("Trainer model not found")

# ================= FACE RECOGNITION =================

@app.route("/api/recognize", methods=["POST"])
def recognize():
    if recognizer is None:
        return jsonify({"error": "Model not loaded"}), 500

    if "image" not in request.files:
        return jsonify({"error": "No image"}), 400

    file = request.files["image"]
    nparr = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_detector.detectMultiScale(gray, 1.1, 5)

    if len(faces) == 0:
        return jsonify({"status": "no_face"})

    results = []

    for (x, y, w, h) in faces:
        id_, confidence = recognizer.predict(gray[y:y+h, x:x+w])

        print(f"Predicted internal ID: {id_}, Confidence: {confidence}")

        # 🔥 Removed strict confidence threshold for testing
        if str(id_) in student_info:

            student = student_info[str(id_)]

            roll = student["roll"]
            clean_roll = roll.replace("R", "").strip()

            save_attendance({
                "roll": clean_roll,
                "name": student["name"],
                "branch": student["branch"]
            })

            results.append({
                "status": "success",
                "roll": clean_roll,
                "name": student["name"],
                "branch": student["branch"],
                "confidence": float(confidence)
            })

        else:
            results.append({
                "status": "unknown",
                "confidence": float(confidence)
            })

    # ✅ VERY IMPORTANT — ADD THIS
    return jsonify({
        "status": "processed",
        "results": results
    })


# ================= SAVE ATTENDANCE =================

def save_attendance(student):
    date_file = datetime.now().strftime("%Y-%m-%d")
    date_display = datetime.now().strftime("%d/%m/%Y")
    time_display = datetime.now().strftime("%H:%M:%S")

    file_path = f"attendance/attendance_{date_file}.xlsx"

    new_row = {
        "Roll Number": student["roll"],  # CLEAN NUMBER
        "Name": student["name"],
        "Branch & Section": student["branch"],
        "Date": date_display,
        "Time": time_display
    }

    if os.path.exists(file_path):
        df = pd.read_excel(file_path)

        if not df.empty:
            if (
                (df["Roll Number"].astype(str) == student["roll"]) &
                (df["Date"] == date_display)
            ).any():
                print("Already marked")
                return False
    else:
        df = pd.DataFrame(columns=new_row.keys())

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_excel(file_path, index=False)

    print("Attendance saved:", new_row)
    return True


# ================= STUDENT VIEW =================

@app.route("/api/student-attendance/<roll>", methods=["GET"])
def student_attendance(roll):
    date_file = datetime.now().strftime("%Y-%m-%d")
    file_path = f"attendance/attendance_{date_file}.xlsx"

    if not os.path.exists(file_path):
        return jsonify({"status": "absent"})

    df = pd.read_excel(file_path)

    row = df[df["Roll Number"].astype(str) == str(roll)]

    if row.empty:
        return jsonify({"status": "absent"})

    return jsonify({
        "status": "present",
        "name": row.iloc[0]["Name"],
        "time": row.iloc[0]["Time"]
    })

# ================= LECTURER STORAGE =================

def load_lecturers():
    try:
        with open("trainer/lecturers.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_lecturers(data):
    with open("trainer/lecturers.json", "w") as f:
        json.dump(data, f, indent=4)

lecturers = load_lecturers()

# ================= REGISTER LECTURER =================

@app.route("/api/register-lecturer", methods=["POST"])
def register_lecturer():
    data = request.json

    username = data.get("username")
    password = data.get("password")
    subject = data.get("subject")

    if not username or not password or not subject:
        return jsonify({"error": "All fields required"}), 400

    file_path = os.path.join("trainer", "lecturers.json")

    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            lecturers = json.load(f)
    else:
        lecturers = {}

    # Prevent duplicate usernames
    if username in lecturers:
        return jsonify({"error": "Username already exists"}), 400

    lecturers[username] = {
        "password": password,
        "subject": subject
    }

    with open(file_path, "w") as f:
        json.dump(lecturers, f, indent=4)

    return jsonify({"message": "Lecturer registered successfully"})

# ================= LOGIN LECTURER =================

@app.route("/api/login-lecturer", methods=["POST"])
def login_lecturer():
    data = request.json

    username = data.get("username")
    password = data.get("password")
    file_path = os.path.join("trainer", "lecturers.json")

    if not os.path.exists(file_path):
        return jsonify({"error": "No lecturers registered"}), 400

    with open(file_path, "r") as f:
        lecturers = json.load(f)

    if username not in lecturers:
        return jsonify({"error": "Lecturer not found"}), 400

    if lecturers[username]["password"] != password:
        return jsonify({"error": "Invalid password"}), 400

    return jsonify({
        "message": "Login successful",
        "subject": lecturers[username]["subject"]
    })


# ================= RUN =================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
