from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import pickle
import pandas as pd
from datetime import timedelta
from models import db, User

app = Flask(__name__, static_folder='maintenance-dashboard/build', static_url_path='/')
CORS(app)

# Configure MySQL Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Samuel%402004@localhost/Predictive_maintenance'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure JWT
app.config['JWT_SECRET_KEY'] = 'predictive-maintenance-super-secret-key'  # Change in production
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    
    if not user or not user.check_password(password):
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=str(user.id))
    return jsonify(access_token=access_token)

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"msg": "Username and password are required"}), 400

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"msg": "Username already exists"}), 400

    new_user = User(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    # Automatically issue JWT to seamlessly login the new user
    access_token = create_access_token(identity=str(new_user.id))
    return jsonify(access_token=access_token)

# Load models and encoders
model1 = pickle.load(open("model1.pkl", "rb"))  # Failure detection
model2 = pickle.load(open("model2.pkl", "rb"))  # Failure type
type_encoder = pickle.load(open("type_encoder.pkl", "rb"))
failure_encoder = pickle.load(open("failure_encoder.pkl", "rb"))

# Feature order (must match training)
FEATURE_COLS = [
    "Type",
    "Air temperature K",
    "Process temperature K",
    "Rotational speed rpm",
    "Torque Nm",
    "Tool wear min",
    "Temp Difference",
    "Power",
    "Strain"
]

@app.route("/predict", methods=["POST"])
@jwt_required()
def predict():
    try:
        data = request.json

        # Parse inputs for physical rules validation
        air_temp = float(data.get("Air temperature K", 0))
        process_temp = float(data.get("Process temperature K", 0))
        rpm = float(data.get("Rotational speed rpm", 0))
        torque = float(data.get("Torque Nm", 0))
        tool_wear = float(data.get("Tool wear min", 0))
        machine_type = str(data.get("Type", "L"))

        # Physical Rules Verification (Physics-Based Failure Detection & Classification)
        physical_failure = False
        physical_failure_type = "No Failure"

        # 1. Heat Dissipation Failure (HDF):
        # Difference Process - Air < 8.6 K AND Rotational speed < 1380 rpm
        temp_diff = process_temp - air_temp
        if temp_diff < 8.6 and rpm < 1380:
            physical_failure = True
            physical_failure_type = "Heat Dissipation Failure"

        # 2. Power Failure (PWF):
        # Power = Torque * RPM * (2 * pi / 60)
        # Power is below 3500 W or above 9000 W
        import numpy as np
        power_w = torque * rpm * (2 * np.pi / 60)
        if power_w < 3500 or power_w > 9000:
            physical_failure = True
            physical_failure_type = "Power Failure"

        # 3. Overstrain Failure (OSF):
        # Product of tool wear and torque exceeds: L: 11000, M: 12000, H: 13000
        strain = tool_wear * torque
        if machine_type == "L" and strain > 11000:
            physical_failure = True
            physical_failure_type = "Overstrain Failure"
        elif machine_type == "M" and strain > 12000:
            physical_failure = True
            physical_failure_type = "Overstrain Failure"
        elif machine_type == "H" and strain > 13000:
            physical_failure = True
            physical_failure_type = "Overstrain Failure"

        # 4. Tool Wear Failure (TWF):
        # Tool wear reaches 200 - 240 mins (we flag >= 200)
        if tool_wear >= 200:
            physical_failure = True
            physical_failure_type = "Tool Wear Failure"

        # Convert input to DataFrame for ML Model
        df = pd.DataFrame([data])

        # Encode Type (L, M, H)
        df["Type"] = type_encoder.transform(df[["Type"]])

        # Add engineered feature (IMPORTANT)
        df["Temp Difference"] = temp_diff
        df["Power"] = rpm * torque
        df["Strain"] = tool_wear * torque

        # Arrange columns properly
        df = df[FEATURE_COLS].astype(float)

        # ==============================
        # STEP 1: FAILURE DETECTION
        # ==============================
        failure_proba = model1.predict_proba(df)[0]
        
        # Determine failure using a tuned probability threshold of 0.35
        # plus the physical safety overrides
        ml_failure_detected = int(1 if failure_proba[1] >= 0.35 else 0)
        
        failure_detected = 1 if (ml_failure_detected or physical_failure) else 0

        if failure_detected == 0:
            return jsonify({
                "failure_detected": False,
                "failure_type": "No Failure",
                "confidence": float(failure_proba[0])
            })

        # ==============================
        # STEP 2: FAILURE TYPE
        # ==============================
        if physical_failure:
            # Physics override - 100% confidence in target failure mode!
            return jsonify({
                "failure_detected": True,
                "failure_type": physical_failure_type,
                "confidence": 1.0
            })

        type_pred = model2.predict(df)[0]
        type_proba = model2.predict_proba(df)[0]

        failure_type = failure_encoder.inverse_transform([type_pred])[0]

        return jsonify({
            "failure_detected": True,
            "failure_type": failure_type,
            "confidence": float(max(type_proba))
        })

    except Exception as e:
        import traceback
        with open("error_log.txt", "w") as f:
            f.write(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


import os
from flask import send_from_directory

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


if __name__ == "__main__":
    app.run(debug=True)