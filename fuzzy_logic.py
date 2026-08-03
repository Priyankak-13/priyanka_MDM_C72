"""
fuzzy_logic.py
===========================================================
Fuzzy Logic-Based Clinical Decision Support System (CDSS)

Educational project only.
This is NOT a real medical diagnostic tool and must not be
used for actual medical decisions.

The fuzzy system is implemented manually:

1. Fuzzification
2. Rule evaluation
3. Mamdani inference
4. Aggregation
5. Centroid defuzzification

No NumPy or fuzzy-logic library is used.
===========================================================
"""


# =========================================================
# 1. MEMBERSHIP FUNCTION
# =========================================================

def trapmf(x, a, b, c, d):
    """
    Trapezoidal membership function.

    Returns a value between 0 and 1.

    a = beginning of the membership
    b = beginning of full membership
    c = end of full membership
    d = end of the membership
    """

    if x <= a or x >= d:
        return 0.0

    elif b <= x <= c:
        return 1.0

    elif a < x < b:
        return (x - a) / (b - a)

    else:
        return (d - x) / (d - c)


# =========================================================
# 2. MEMBERSHIP FUNCTION BOUNDARIES
# =========================================================

# -------------------------
# Heart Rate (BPM)
# -------------------------

HR_LOW = (30, 30, 50, 65)

HR_NORMAL = (55, 65, 85, 100)

HR_HIGH = (90, 105, 220, 220)


# -------------------------
# Systolic Blood Pressure
# -------------------------

BP_LOW = (70, 70, 90, 100)

BP_NORMAL = (95, 105, 120, 130)

BP_HIGH = (125, 140, 220, 220)


# -------------------------
# SpO2 (%)
# -------------------------

SPO2_LOW = (70, 70, 88, 93)

SPO2_NORMAL = (90, 94, 97, 99)

SPO2_HIGH = (97, 99, 100, 100)


# =========================================================
# 3. OUTPUT MEMBERSHIP FUNCTIONS
# =========================================================

# Risk score is between 0 and 100.

RISK_LOW = (0, 0, 20, 40)

RISK_MEDIUM = (30, 45, 60, 75)

RISK_HIGH = (65, 80, 100, 100)


# =========================================================
# 4. FUZZIFICATION
# =========================================================

def fuzzify_heart_rate(hr):

    return {
        "low": trapmf(hr, *HR_LOW),
        "normal": trapmf(hr, *HR_NORMAL),
        "high": trapmf(hr, *HR_HIGH)
    }


def fuzzify_blood_pressure(bp):

    return {
        "low": trapmf(bp, *BP_LOW),
        "normal": trapmf(bp, *BP_NORMAL),
        "high": trapmf(bp, *BP_HIGH)
    }


def fuzzify_spo2(spo2):

    return {
        "low": trapmf(spo2, *SPO2_LOW),
        "normal": trapmf(spo2, *SPO2_NORMAL),
        "high": trapmf(spo2, *SPO2_HIGH)
    }


# =========================================================
# 5. FUZZY RULE BASE
# =========================================================

"""
Each rule follows:

IF condition
AND/OR condition
THEN risk

Risk:
    low
    medium
    high
"""

RULES = [

    # Rule 1
    {
        "id": 1,
        "op": "AND",
        "terms": [
            ("hr", "normal"),
            ("bp", "normal"),
            ("spo2", "normal")
        ],
        "output": "low"
    },

    # Rule 2
    {
        "id": 2,
        "op": "AND",
        "terms": [
            ("hr", "normal"),
            ("bp", "normal"),
            ("spo2", "high")
        ],
        "output": "low"
    },

    # Rule 3
    {
        "id": 3,
        "op": "AND",
        "terms": [
            ("hr", "high"),
            ("bp", "normal"),
            ("spo2", "normal")
        ],
        "output": "medium"
    },

    # Rule 4
    {
        "id": 4,
        "op": "AND",
        "terms": [
            ("hr", "normal"),
            ("bp", "high"),
            ("spo2", "normal")
        ],
        "output": "medium"
    },

    # Rule 5
    {
        "id": 5,
        "op": "AND",
        "terms": [
            ("hr", "high"),
            ("bp", "high"),
            ("spo2", "normal")
        ],
        "output": "high"
    },

    # Rule 6
    {
        "id": 6,
        "op": "AND",
        "terms": [
            ("hr", "high"),
            ("bp", "normal"),
            ("spo2", "low")
        ],
        "output": "high"
    },

    # Rule 7
    {
        "id": 7,
        "op": "AND",
        "terms": [
            ("hr", "normal"),
            ("bp", "high"),
            ("spo2", "low")
        ],
        "output": "high"
    },

    # Rule 8
    {
        "id": 8,
        "op": "AND",
        "terms": [
            ("hr", "high"),
            ("bp", "high"),
            ("spo2", "low")
        ],
        "output": "high"
    },

    # Rule 9
    {
        "id": 9,
        "op": "AND",
        "terms": [
            ("hr", "low"),
            ("bp", "low"),
            ("spo2", "normal")
        ],
        "output": "medium"
    },

    # Rule 10
    {
        "id": 10,
        "op": "AND",
        "terms": [
            ("hr", "low"),
            ("bp", "low"),
            ("spo2", "low")
        ],
        "output": "high"
    },

    # Rule 11
    {
        "id": 11,
        "op": "OR",
        "terms": [
            ("hr", "high"),
            ("bp", "high")
        ],
        "output": "medium"
    },

    # Rule 12
    {
        "id": 12,
        "op": "OR",
        "terms": [
            ("hr", "low"),
            ("spo2", "low")
        ],
        "output": "medium"
    }
]


# =========================================================
# 6. FUZZY AND / OR
# =========================================================

def fuzzy_and(values):
    """
    Fuzzy AND = minimum membership value.
    """

    result = values[0]

    for value in values:

        if value < result:
            result = value

    return result


def fuzzy_or(values):
    """
    Fuzzy OR = maximum membership value.
    """

    result = values[0]

    for value in values:

        if value > result:
            result = value

    return result


# =========================================================
# 7. RULE INFERENCE
# =========================================================

def apply_rules(hr_fuzzy, bp_fuzzy, spo2_fuzzy):

    lookup = {
        "hr": hr_fuzzy,
        "bp": bp_fuzzy,
        "spo2": spo2_fuzzy
    }

    fired_rules = []

    for rule in RULES:

        degrees = []

        for variable, term in rule["terms"]:

            degree = lookup[variable][term]

            degrees.append(degree)

        # -------------------------
        # Fuzzy AND
        # -------------------------

        if rule["op"] == "AND":

            strength = fuzzy_and(degrees)

        # -------------------------
        # Fuzzy OR
        # -------------------------

        else:

            strength = fuzzy_or(degrees)

        fired_rules.append({
            "id": rule["id"],
            "output": rule["output"],
            "strength": strength
        })

    return fired_rules


# =========================================================
# 8. AGGREGATION
# =========================================================

def aggregate_outputs(fired_rules):

    aggregated = {
        "low": 0.0,
        "medium": 0.0,
        "high": 0.0
    }

    for rule in fired_rules:

        output = rule["output"]

        strength = rule["strength"]

        # MAX operation for aggregation

        if strength > aggregated[output]:

            aggregated[output] = strength

    return aggregated


# =========================================================
# 9. CENTROID DEFUZZIFICATION
# =========================================================

def centroid_defuzzify(aggregated):

    """
    Centroid formula:

                 SUM(x * membership)
    Score = -----------------------------
                    SUM(membership)

    We manually examine values from 0 to 100.
    """

    numerator = 0.0

    denominator = 0.0

    # Examine the complete risk-score range.

    for x in range(0, 101):

        # Membership of x in LOW risk

        low_membership = trapmf(
            x,
            *RISK_LOW
        )

        # Membership of x in MEDIUM risk

        medium_membership = trapmf(
            x,
            *RISK_MEDIUM
        )

        # Membership of x in HIGH risk

        high_membership = trapmf(
            x,
            *RISK_HIGH
        )

        # Clip each output using its rule strength.

        low_value = min(
            aggregated["low"],
            low_membership
        )

        medium_value = min(
            aggregated["medium"],
            medium_membership
        )

        high_value = min(
            aggregated["high"],
            high_membership
        )

        # Combine output fuzzy sets using MAX.

        combined_membership = fuzzy_or([
            low_value,
            medium_value,
            high_value
        ])

        numerator += x * combined_membership

        denominator += combined_membership

    if denominator == 0:

        return 0.0

    score = numerator / denominator

    return score


# =========================================================
# 10. RISK CATEGORY
# =========================================================

def score_to_category(score):

    if score < 40:

        return "Low"

    elif score < 65:

        return "Medium"

    else:

        return "High"


# =========================================================
# 11. FIND DOMINANT MEMBERSHIP
# =========================================================

def dominant_label(fuzzy_values):

    label = "normal"

    highest = -1

    for key in fuzzy_values:

        if fuzzy_values[key] > highest:

            highest = fuzzy_values[key]

            label = key

    return label


# =========================================================
# 12. GENERATE REASONS
# =========================================================

def generate_reasons(
    heart_rate,
    blood_pressure,
    spo2,
    hr_fuzzy,
    bp_fuzzy,
    spo2_fuzzy
):

    reasons = []

    hr_label = dominant_label(hr_fuzzy)

    bp_label = dominant_label(bp_fuzzy)

    spo2_label = dominant_label(spo2_fuzzy)


    # Heart rate reason

    if hr_label == "high":

        reasons.append(
            f"Heart rate is high ({heart_rate} bpm)."
        )

    elif hr_label == "low":

        reasons.append(
            f"Heart rate is low ({heart_rate} bpm)."
        )

    else:

        reasons.append(
            f"Heart rate is normal ({heart_rate} bpm)."
        )


    # Blood pressure reason

    if bp_label == "high":

        reasons.append(
            f"Systolic blood pressure is high ({blood_pressure} mmHg)."
        )

    elif bp_label == "low":

        reasons.append(
            f"Systolic blood pressure is low ({blood_pressure} mmHg)."
        )

    else:

        reasons.append(
            f"Systolic blood pressure is normal ({blood_pressure} mmHg)."
        )


    # SpO2 reason

    if spo2_label == "low":

        reasons.append(
            f"Oxygen saturation is low ({spo2}%)."
        )

    elif spo2_label == "high":

        reasons.append(
            f"Oxygen saturation is excellent ({spo2}%)."
        )

    else:

        reasons.append(
            f"Oxygen saturation is normal ({spo2}%)."
        )


    return reasons


# =========================================================
# 13. MAIN FUZZY SYSTEM
# =========================================================

def evaluate_risk(
    heart_rate,
    systolic_bp,
    spo2
):

    # -----------------------------------------------------
    # STAGE 1: FUZZIFICATION
    # -----------------------------------------------------

    hr_fuzzy = fuzzify_heart_rate(
        heart_rate
    )

    bp_fuzzy = fuzzify_blood_pressure(
        systolic_bp
    )

    spo2_fuzzy = fuzzify_spo2(
        spo2
    )


    # -----------------------------------------------------
    # STAGE 2 + 3: RULES AND INFERENCE
    # -----------------------------------------------------

    fired_rules = apply_rules(
        hr_fuzzy,
        bp_fuzzy,
        spo2_fuzzy
    )


    # -----------------------------------------------------
    # STAGE 3: AGGREGATION
    # -----------------------------------------------------

    aggregated = aggregate_outputs(
        fired_rules
    )


    # -----------------------------------------------------
    # STAGE 4: DEFUZZIFICATION
    # -----------------------------------------------------

    risk_score = centroid_defuzzify(
        aggregated
    )


    # Keep score between 0 and 100.

    if risk_score < 0:

        risk_score = 0

    if risk_score > 100:

        risk_score = 100


    risk_score = round(
        risk_score,
        2
    )


    # -----------------------------------------------------
    # RISK CATEGORY
    # -----------------------------------------------------

    risk_category = score_to_category(
        risk_score
    )


    # -----------------------------------------------------
    # REASONS
    # -----------------------------------------------------

    reasons = generate_reasons(
        heart_rate,
        systolic_bp,
        spo2,
        hr_fuzzy,
        bp_fuzzy,
        spo2_fuzzy
    )


    # -----------------------------------------------------
    # RETURN RESULT TO WEBSITE
    # -----------------------------------------------------

    return {

        "risk_score": risk_score,

        "risk_category": risk_category,

        "reasons": reasons,

        "membership": {

            "heart_rate": hr_fuzzy,

            "blood_pressure": bp_fuzzy,

            "spo2": spo2_fuzzy
        },

        "rule_strengths": {

            rule["id"]: round(
                rule["strength"],
                3
            )

            for rule in fired_rules
        },

        "aggregated_output": {

            key: round(
                value,
                3
            )

            for key, value in aggregated.items()
        }
    }


# =========================================================
# 14. TEST CASES
# =========================================================

if __name__ == "__main__":

    test_cases = [

        # Clearly healthy
        {
            "name": "Healthy Patient",
            "hr": 72,
            "bp": 118,
            "spo2": 98
        },

        # Slightly abnormal
        {
            "name": "Mild Risk",
            "hr": 95,
            "bp": 128,
            "spo2": 95
        },

        # Moderate risk
        {
            "name": "Moderate Risk",
            "hr": 105,
            "bp": 140,
            "spo2": 94
        },

        # High risk
        {
            "name": "High Risk",
            "hr": 115,
            "bp": 155,
            "spo2": 90
        },

        # Clearly high risk
        {
            "name": "Critical Risk",
            "hr": 130,
            "bp": 170,
            "spo2": 85
        }
    ]


    print("=" * 60)

    print("FUZZY LOGIC CLINICAL DECISION SUPPORT SYSTEM")

    print("=" * 60)

    print()

    print("Educational project only.")
    print("Not a medical diagnostic tool.")

    print()


    for patient in test_cases:

        result = evaluate_risk(
            patient["hr"],
            patient["bp"],
            patient["spo2"]
        )

        print("-" * 60)

        print(
            "Test Case:",
            patient["name"]
        )

        print(
            "Heart Rate:",
            patient["hr"],
            "bpm"
        )

        print(
            "Blood Pressure:",
            patient["bp"],
            "mmHg"
        )

        print(
            "SpO2:",
            patient["spo2"],
            "%"
        )

        print()

        print(
            "Risk Score:",
            result["risk_score"]
        )

        print(
            "Risk Category:",
            result["risk_category"]
        )

        print()

        print("Reasons:")

        for reason in result["reasons"]:

            print(
                " -",
                reason
            )

    print("-" * 60)