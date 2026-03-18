from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import pandas as pd

app = Flask(__name__)
CORS(app)

# Load correct model + encoder
model = pickle.load(open("model.pkl", "rb"))
type_encoder = pickle.load(open("type_encoder.pkl", "rb"))

@app.route("/predict", methods=["POST"])
def predict():
    data = request.json

    df = pd.DataFrame([data])

    # Encode Type properly
    df["Type"] = type_encoder.transform(df[["Type"]])

    # Ensure correct order
    df = df[[
        "Type",
        "Air temperature [K]",
        "Process temperature [K]",
        "Rotational speed [rpm]",
        "Torque [Nm]",
        "Tool wear [min]"
    ]]

    df = df.astype(float)

    prediction = model.predict(df)[0]
    probability = model.predict_proba(df)[0][1]

    result = "Machine Failure Likely" if prediction == 1 else "Machine Operating Normally"

    return jsonify({
        "prediction": result,
        "probability": float(probability)
    })

if __name__ == "__main__":
    app.run(debug=True)