from flask import Flask, render_template, request
import joblib
import numpy as np
import pandas as pd  # <-- add this

app = Flask(__name__)
MODEL_PATH = "artifacts/models/model.pkl"
model = joblib.load(MODEL_PATH)

HARDCODED_FEATURES = [
    'Year_of_Manufacture', 'Vehicle_Type', 'Usage_Hours', 'Load_Capacity',
    'Actual_Load', 'Maintenance_Cost', 'Engine_Temperature', 'Tire_Pressure',
    'Fuel_Consumption', 'Battery_Status', 'Vibration_Levels', 'Oil_Quality',
    'Brake_Condition', 'Delivery_Times', 'Impact_on_Efficiency',
    'Maintenance_Year', 'Maintenance_Month', 'Maintenance_Day', 'Maintenance_Weekday',
    'Maintenance_Type_Engine Overhaul', 'Maintenance_Type_Oil Change',
    'Maintenance_Type_Tire Rotation', 'Weather_Conditions_Clear',
    'Weather_Conditions_Rainy', 'Weather_Conditions_Snowy',
    'Weather_Conditions_Windy', 'Road_Conditions_Highway',
    'Road_Conditions_Rural', 'Road_Conditions_Urban'
]

FEATURES = list(getattr(model, "feature_names_in_", HARDCODED_FEATURES))
LABELS = {0: "Maintenance not Required", 1: "Maintenance Required"}

@app.route("/", methods=["GET", "POST"])
def index():
    prediction = error = None
    if request.method == "POST":
        try:
            # collect values in the same order as FEATURES
            vals = []
            for f in FEATURES:
                raw = request.form.get(f, "").strip()
                # treat empty as 0; coerce to float
                v = float(raw) if raw != "" else 0.0
                vals.append(v)

            # ✅ Use a DataFrame so string column selectors work
            X_in = pd.DataFrame([vals], columns=FEATURES)

            pred = model.predict(X_in)[0]
            prediction = LABELS.get(int(pred), str(pred))
        except Exception as e:
            error = f"{e}"

    return render_template("index.html", features=FEATURES, prediction=prediction, error=error)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
