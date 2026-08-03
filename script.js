/* ======================================================================
   script.js
   Vanilla JavaScript for the Fuzzy-CDSS front-end.

   Responsibilities:
     - Client-side validation of the vitals form (mirrors backend rules)
     - Sending vitals to the Flask /calculate endpoint via fetch()
     - Rendering the risk badge, gauge, reasons, and technical details
     - Small UI niceties: FAQ accordion, mobile nav toggle
   ====================================================================== */

document.addEventListener('DOMContentLoaded', () => {

  /* --------------------------------------------------------------
     Config: must match the validation ranges used in app.py
  -------------------------------------------------------------- */
  const FIELD_RULES = {
    heartRate:  { min: 30, max: 220, label: 'Heart Rate' },
    systolicBp: { min: 70, max: 220, label: 'Systolic Blood Pressure' },
    spo2:       { min: 50, max: 100, label: 'SpO2' },
  };

  const form          = document.getElementById('vitalsForm');
  const formNote      = document.getElementById('formNote');
  const resultEmpty   = document.getElementById('resultEmpty');
  const resultContent = document.getElementById('resultContent');
  const riskBadge     = document.getElementById('riskBadge');
  const riskScoreText = document.getElementById('riskScoreText');
  const reasonsList   = document.getElementById('reasonsList');
  const gaugeFill     = document.getElementById('gaugeFill');
  const gaugeNeedle   = document.getElementById('gaugeNeedle');
  const techToggle    = document.getElementById('techToggle');
  const techDetails   = document.getElementById('techDetails');
  const membershipTbl = document.getElementById('membershipTable');
  const ruleTbl       = document.getElementById('ruleTable');

  /* --------------------------------------------------------------
     Validation helpers
  -------------------------------------------------------------- */
  function validateField(id) {
    const input = document.getElementById(id);
    const errorEl = document.getElementById(id + 'Error');
    const rules = FIELD_RULES[id];
    const raw = input.value.trim();

    if (raw === '') {
      setFieldError(input, errorEl, `${rules.label} is required.`);
      return null;
    }

    const value = Number(raw);

    if (Number.isNaN(value)) {
      setFieldError(input, errorEl, `${rules.label} must be a number.`);
      return null;
    }

    if (value < rules.min || value > rules.max) {
      setFieldError(
        input, errorEl,
        `${rules.label} must be between ${rules.min} and ${rules.max}.`
      );
      return null;
    }

    clearFieldError(input, errorEl);
    return value;
  }

  function setFieldError(input, errorEl, message) {
    input.classList.add('invalid');
    errorEl.textContent = message;
  }

  function clearFieldError(input, errorEl) {
    input.classList.remove('invalid');
    errorEl.textContent = '';
  }

  /* --------------------------------------------------------------
     Form submit -> validate -> call backend -> render result
  -------------------------------------------------------------- */
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    formNote.textContent = '';

    const heartRate  = validateField('heartRate');
    const systolicBp = validateField('systolicBp');
    const spo2       = validateField('spo2');

    if (heartRate === null || systolicBp === null || spo2 === null) {
      formNote.textContent = 'Please fix the highlighted fields before calculating.';
      return;
    }

    const calculateBtn = document.getElementById('calculateBtn');
    calculateBtn.disabled = true;
    calculateBtn.textContent = 'Calculating...';

    try {
      const response = await fetch('/calculate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          heart_rate: heartRate,
          systolic_bp: systolicBp,
          spo2: spo2,
        }),
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        formNote.textContent = data.error || 'Something went wrong. Please try again.';
        return;
      }

      renderResult(data);
    } catch (err) {
      formNote.textContent = 'Could not reach the server. Please check the Flask app is running.';
    } finally {
      calculateBtn.disabled = false;
      calculateBtn.textContent = 'Calculate Risk';
    }
  });

  form.addEventListener('reset', () => {
    ['heartRate', 'systolicBp', 'spo2'].forEach((id) => {
      const input = document.getElementById(id);
      const errorEl = document.getElementById(id + 'Error');
      clearFieldError(input, errorEl);
    });
    formNote.textContent = '';
    resultEmpty.hidden = false;
    resultContent.hidden = true;
    techDetails.hidden = true;
    techToggle.setAttribute('aria-expanded', 'false');
    techToggle.textContent = 'Show technical fuzzy details ▾';
  });

  /* --------------------------------------------------------------
     Render the result panel: badge, score, gauge, reasons, tech table
  -------------------------------------------------------------- */
  function renderResult(data) {
    resultEmpty.hidden = true;
    resultContent.hidden = false;

    const category = data.risk_category; // "Low" | "Medium" | "High"
    const score = data.risk_score;       // 0-100

    riskBadge.textContent = category.toUpperCase();
    riskBadge.className = 'risk-badge ' + category.toLowerCase();
    riskScoreText.textContent = `${score}%`;

    // ---- Gauge: semicircular arc from 0-100 ----
    // Arc path length is 251.2 (see style.css / SVG path length).
    const ARC_LENGTH = 251.2;
    const fraction = Math.max(0, Math.min(100, score)) / 100;
    const offset = ARC_LENGTH - (fraction * ARC_LENGTH);
    gaugeFill.style.strokeDashoffset = offset;

    const gaugeColor = category === 'Low' ? 'var(--color-low)'
                      : category === 'Medium' ? 'var(--color-medium)'
                      : 'var(--color-high)';
    gaugeFill.style.stroke = gaugeColor;

    // Needle sweeps from -90deg (0 score) to +90deg (100 score)
    const angle = -90 + (fraction * 180);
    gaugeNeedle.style.transform = `rotate(${angle}deg)`;

    // ---- Reasons ----
    reasonsList.innerHTML = '';
    data.reasons.forEach((reason) => {
      const li = document.createElement('li');
      li.textContent = reason;
      reasonsList.appendChild(li);
    });

    // ---- Technical details: membership degrees + rule strengths ----
    renderMembershipTable(data.membership);
    renderRuleTable(data.rule_strengths);

    resultContent.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  function renderMembershipTable(membership) {
    const rows = [
      ['Heart Rate', membership.heart_rate],
      ['Blood Pressure', membership.blood_pressure],
      ['SpO2', membership.spo2],
    ];

    let html = '<thead><tr><th>Vital Sign</th><th>Low</th><th>Normal</th><th>High</th></tr></thead><tbody>';
    rows.forEach(([label, m]) => {
      html += `<tr><td>${label}</td><td>${m.low.toFixed(2)}</td><td>${m.normal.toFixed(2)}</td><td>${m.high.toFixed(2)}</td></tr>`;
    });
    html += '</tbody>';
    membershipTbl.innerHTML = html;
  }

  function renderRuleTable(ruleStrengths) {
    let html = '<thead><tr><th>Rule #</th><th>Firing Strength</th></tr></thead><tbody>';
    Object.keys(ruleStrengths).forEach((ruleId) => {
      html += `<tr><td>Rule ${ruleId}</td><td>${ruleStrengths[ruleId].toFixed(3)}</td></tr>`;
    });
    html += '</tbody>';
    ruleTbl.innerHTML = html;
  }

  /* --------------------------------------------------------------
     Technical details toggle
  -------------------------------------------------------------- */
  techToggle.addEventListener('click', () => {
    const isOpen = techToggle.getAttribute('aria-expanded') === 'true';
    techToggle.setAttribute('aria-expanded', String(!isOpen));
    techDetails.hidden = isOpen;
    techToggle.textContent = isOpen
      ? 'Show technical fuzzy details ▾'
      : 'Hide technical fuzzy details ▴';
  });

  /* --------------------------------------------------------------
     FAQ accordion
  -------------------------------------------------------------- */
  document.querySelectorAll('.accordion-trigger').forEach((trigger) => {
    trigger.addEventListener('click', () => {
      const panel = trigger.nextElementSibling;
      const isOpen = trigger.getAttribute('aria-expanded') === 'true';

      // Close all other panels (simple single-open accordion)
      document.querySelectorAll('.accordion-trigger').forEach((t) => {
        t.setAttribute('aria-expanded', 'false');
        t.nextElementSibling.style.maxHeight = null;
      });

      if (!isOpen) {
        trigger.setAttribute('aria-expanded', 'true');
        panel.style.maxHeight = panel.scrollHeight + 'px';
      }
    });
  });

  /* --------------------------------------------------------------
     Mobile nav toggle
  -------------------------------------------------------------- */
  const navToggle = document.getElementById('navToggle');
  const siteHeader = document.querySelector('.site-header');
  navToggle.addEventListener('click', () => {
    const isOpen = siteHeader.classList.toggle('nav-open');
    navToggle.setAttribute('aria-expanded', String(isOpen));
  });

  document.querySelectorAll('.main-nav a').forEach((link) => {
    link.addEventListener('click', () => {
      siteHeader.classList.remove('nav-open');
      navToggle.setAttribute('aria-expanded', 'false');
    });
  });

  /* --------------------------------------------------------------
     Live inline validation as the user types
  -------------------------------------------------------------- */
  Object.keys(FIELD_RULES).forEach((id) => {
    const input = document.getElementById(id);
    input.addEventListener('blur', () => validateField(id));
  });
});
