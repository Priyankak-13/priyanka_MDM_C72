# Fuzzy-CDSS — Fuzzy Logic-Based Clinical Decision Support System

A college mini-project that estimates a patient's health risk from three
vital signs using a **hand-built Mamdani fuzzy inference engine** — no
fuzzy-logic libraries involved. Every stage (fuzzification, rule base,
inference, defuzzification) is implemented manually in plain Python and
NumPy.

> ⚠️ **Educational project only.** This system is **not** a certified
> medical device and must never be used for real diagnosis, triage, or
> treatment decisions. Always consult a qualified healthcare professional.

---

## 1. Project Overview

Traditional clinical alerting systems use hard thresholds
("IF HR > 100 THEN alert"), which don't reflect how clinicians actually
reason about borderline or overlapping symptoms. This project
demonstrates how **fuzzy logic** can model that nuance by representing
each vital sign as partially belonging to multiple categories (e.g. a
heart rate can be simultaneously 70% "Normal" and 30% "High").

The system takes three vital signs as input:

- **Heart Rate** (bpm)
- **Systolic Blood Pressure** (mmHg)
- **SpO₂** — Oxygen Saturation (%)

...and outputs:

- A **Risk Score** from 0–100 (crisp number)
- A **Risk Category**: Low / Medium / High
- Plain-English **reasons** explaining the result

## 2. Objectives

1. Implement a complete Mamdani fuzzy inference system **from scratch**,
   without relying on any fuzzy-logic library (e.g. scikit-fuzzy).
2. Demonstrate all four classical fuzzy logic stages: fuzzification,
   rule base, inference (min/max), and centroid defuzzification.
3. Build a clean, responsive, hospital-themed website around the engine
   using Flask, HTML5, CSS3, and vanilla JavaScript.
4. Make the reasoning process transparent and explainable, in line with
   the educational goals of the assignment.

## 3. Technologies Used

**Backend**
- Python 3
- Flask (web framework, routing, JSON API)
- NumPy (array math for the centroid defuzzification integral only —
  **not** used for any fuzzy logic operations themselves)

**Frontend**
- HTML5
- CSS3 (hand-written, no Bootstrap/Tailwind)
- Vanilla JavaScript (no frameworks)

**Explicitly not used:** React, Angular, Vue, Django, Bootstrap,
Tailwind CSS, and any fuzzy logic library (e.g. scikit-fuzzy).

## 4. Installation Steps

```bash
# 1. Clone / unzip the project, then move into the folder
cd Fuzzy-CDSS

# 2. (Recommended) create a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the Flask development server
python3 app.py

# 5. Open the site
# Visit http://127.0.0.1:5000 in your browser
```

## 5. Folder Structure

```
Fuzzy-CDSS/
├── app.py                 # Flask app: routes, validation, JSON API
├── fuzzy_logic.py          # Manual Mamdani fuzzy engine (core logic)
├── requirements.txt        # Python dependencies
├── README.md                # This file
├── templates/
│   └── index.html          # Single-page site (all sections)
└── static/
    ├── style.css            # Hospital-themed design system
    ├── script.js            # Form handling, fetch calls, UI behavior
    └── images/              # (reserved for any additional image assets)
```

## 6. Working of the Fuzzy Logic System

The pipeline in `fuzzy_logic.py` runs in four stages for every request:

### Stage 1 — Fuzzification
Each crisp vital-sign value is converted into membership degrees
(0–1) for **Low**, **Normal**, and **High** using hand-written
trapezoidal membership functions (`trapmf()`).

### Stage 2 — Rule Base
12 IF–THEN rules (see below) relate combinations of Heart Rate, Blood
Pressure, and SpO₂ to a risk outcome (Low / Medium / High).

### Stage 3 — Inference
- **AND** conditions are combined using the **minimum** operator.
- **OR** conditions are combined using the **maximum** operator.
- Rules that share the same output label are aggregated together using
  **maximum** (standard Mamdani aggregation).

### Stage 4 — Defuzzification (Centroid Method)
The aggregated fuzzy output shape (built from the Low/Medium/High
output membership functions, each clipped at its rule's firing
strength) is converted into a single crisp number using the **centroid
(center of gravity)** formula:

```
risk_score = Σ(x · μ(x)) / Σ(μ(x))     for x in the 0–100 universe
```

This integral is discretized and computed with NumPy for efficiency —
NumPy is used purely for the numeric summation, not for any fuzzy logic
itself.

## 7. Membership Functions

| Vital Sign | Low | Normal | High |
|---|---|---|---|
| Heart Rate (bpm) | 30–65 | 55–105 | 95–220 |
| Systolic BP (mmHg) | 70–100 | 95–130 | 125–220 |
| SpO₂ (%) | 70–92 | 90–97 | 96–100 |

(Each range is a trapezoid: the two inner numbers are the flat-top /
full-membership zone, the two outer numbers are where membership
rises from / falls to zero. See the "Membership Functions" section on
the website for a visual chart of these exact shapes.)

Output risk score (0–100) also uses three trapezoidal sets: **Low**
(0–40), **Medium** (30–70), **High** (60–100).

## 8. Rule Base

| # | Rule | Operator | Output |
|---|---|---|---|
| 1 | HR Low AND BP Low AND SpO₂ Low | AND | High |
| 2 | HR High AND BP High AND SpO₂ Low | AND | High |
| 3 | HR Normal AND BP Normal AND SpO₂ High | AND | Low |
| 4 | HR Normal AND BP Normal AND SpO₂ Normal | AND | Low |
| 5 | HR High OR BP High | OR | Medium |
| 6 | SpO₂ Low | — | High |
| 7 | HR Low AND BP Low | AND | Medium |
| 8 | HR High AND SpO₂ Low | AND | High |
| 9 | BP High AND SpO₂ Low | AND | High |
| 10 | HR Low OR SpO₂ Low | OR | Medium |
| 11 | HR Normal AND BP Low AND SpO₂ Normal | AND | Medium |
| 12 | HR High AND BP High AND SpO₂ High | AND | Medium |

## 9. Test Cases

Manually verified via `python3 fuzzy_logic.py` and the `/calculate` API:

| Heart Rate | Systolic BP | SpO₂ | Risk Score | Category | Notes |
|---|---|---|---|---|---|
| 72 | 118 | 98 | ~16 | Low | All vitals healthy |
| 110 | 145 | 88 | ~66 | High | Tachycardia + hypertension + hypoxemia |
| 95 | 128 | 94 | ~34 | Low | Mildly elevated but within safe overlap |
| 140 | 180 | 80 | ~71 | High | Severe combined abnormality |
| 60 | 85 | 97 | ~50 | Medium | Borderline low HR/BP, good oxygen |
| 45 | 80 | 99 | ~50 | Medium | Bradycardia, otherwise healthy |

You can reproduce these by running:

```bash
python3 fuzzy_logic.py
```

or via curl against the running Flask server:

```bash
curl -X POST http://127.0.0.1:5000/calculate \
  -H "Content-Type: application/json" \
  -d '{"heart_rate": 110, "systolic_bp": 145, "spo2": 88}'
```

## 10. Future Improvements

- Add more vital signs (respiratory rate, temperature, diastolic BP).
- Allow adjustable membership function ranges via an admin panel.
- Add a Sugeno-style variant for comparison against Mamdani.
- Persist assessment history per session for trend analysis.
- Add unit tests (pytest) covering the fuzzy engine's edge cases.
- Support multi-language UI text.

## 11. Disclaimer

Fuzzy-CDSS is a **student mini-project** created purely to demonstrate
fuzzy logic concepts in a clinical-inspired context. It has **not** been
clinically validated, is **not** a certified or regulated medical
device, and must **never** be used to make real decisions about any
patient's health. If you or someone else is experiencing a medical
emergency, contact local emergency services or a qualified healthcare
professional immediately.
