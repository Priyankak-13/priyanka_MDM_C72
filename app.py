"""
app.py
----------------------------------------------------------------------
Flask backend for the Fuzzy Logic-Based Clinical Decision Support
System (CDSS).

Responsibilities of this file:
    1. Serve the front-end (templates/index.html, static/ assets).
    2. Receive vital-sign input from the browser (via AJAX/fetch).
    3. Validate that input.
    4. Call the hand-written Mamdani fuzzy engine in fuzzy_logic.py.
    5. Return the risk score / category / reasons as JSON.

IMPORTANT: This is an educational mini-project. It is NOT a certified
medical device and must never be used for real diagnosis or treatment.
----------------------------------------------------------------------
"""

from flask import Flask, render_template, request, jsonify
from fuzzy_logic import evaluate_risk

app = Flask(__name__)

# ----------------------------------------------------------------------
# Safe / physiologically plausible input ranges used for validation.
# Anything outside these ranges is rejected with a friendly error
# message instead of being silently accepted.
# ----------------------------------------------------------------------
VALID_RANGES = {
    "heart_rate":  {"min": 30,  "max": 220, "label": "Heart Rate"},
    "systolic_bp": {"min": 70,  "max": 220, "label": "Systolic Blood Pressure"},
    "spo2":        {"min": 50,  "max": 100, "label": "SpO2"},
}


def validate_inputs(data):
    """
    Validate the incoming request payload.
    Returns (cleaned_values, error_message).
    If error_message is not None, the request is invalid.
    """
    cleaned = {}

    for field, rules in VALID_RANGES.items():
        raw_value = data.get(field, None)

        if raw_value is None or str(raw_value).strip() == "":
            return None, f"{rules['label']} is required."

        try:
            value = float(raw_value)
        except (TypeError, ValueError):
            return None, f"{rules['label']} must be a number."

        if value < rules["min"] or value > rules["max"]:
            return None, (
                f"{rules['label']} must be between "
                f"{rules['min']} and {rules['max']}."
            )

        cleaned[field] = value

    return cleaned, None


@app.route("/")
def home():
    """Render the single-page website (home, about, form, results, etc.)."""
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/calculate", methods=["POST"])
def calculate():
    """
    Receive vital signs as JSON, run them through the manual fuzzy
    inference engine, and return the risk assessment as JSON.

    Expected JSON body:
        {
            "heart_rate": 95,
            "systolic_bp": 128,
            "spo2": 94
        }
    """
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({"success": False, "error": "Invalid or missing JSON body."}), 400

    cleaned, error = validate_inputs(data)
    if error:
        return jsonify({"success": False, "error": error}), 400

    # Run the manual Mamdani fuzzy inference pipeline
    result = evaluate_risk(
        heart_rate=cleaned["heart_rate"],
        systolic_bp=cleaned["systolic_bp"],
        spo2=cleaned["spo2"],
    )

    return jsonify({
        "success": True,
        "risk_score": result["risk_score"],
        "risk_category": result["risk_category"],
        "reasons": result["reasons"],
        "membership": result["membership"],
        "rule_strengths": result["rule_strengths"],
    })


if __name__ == "__main__":
    # debug=True is fine for local development / demonstration purposes
    app.run(debug=True)
