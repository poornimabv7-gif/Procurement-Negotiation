# Procurement Negotiation AI - Demo Case Result

## 1. Case Overview

This demonstration uses the synthetic procurement negotiation dataset created for the prototype.

| Field | Value |
|---|---|
| Case ID | NEG001 |
| RFQ ID | RFQ001 |
| Material | M001 |
| Required Quantity | 10,000 units |
| Current Supplier | S001 |
| Current Offer | ₹120 per unit |
| Required Delivery | 30 days |

---

## 2. Supplier and Outside-Option Analysis

The prototype evaluates alternative suppliers based on feasibility, supplier characteristics, quotation data and effective outside-option cost.

The current sample identifies Supplier C (S003) as the BATNA supplier.

---

## 3. BATNA

**BATNA Supplier:** Supplier C (S003)

**BATNA Effective Cost:** ₹1,130,000

The BATNA represents the lowest feasible effective outside-option cost identified by the prototype.

---

## 4. Reservation / Walk-Away Value

The current prototype defines the buyer reservation value as the BATNA effective cost.

**Buyer Reservation Value:** ₹1,130,000

**Buyer Reservation Value per Unit:** ₹113

This is the current prototype's walk-away boundary.

---

## 5. ZOPA Analysis

### Supplier C

ZOPA exists.

**ZOPA Range:** ₹1,110,000 – ₹1,130,000

Equivalent per-unit range:

**₹111 – ₹113 per unit**

### Supplier A

No acceptable ZOPA is identified under the current prototype assumptions.

---

## 6. Nash Bargaining

For Supplier C:

**Supplier reservation-price proxy:** ₹111 per unit

**Buyer reservation value:** ₹113 per unit

**Nash bargaining price:** ₹112 per unit

**Nash total:** ₹1,120,000

The supplier reservation value in this prototype is represented using historical average purchase price as a proxy.

---

## 7. Negotiation Strategy

### Supplier C

**Opening Position:** ₹109.76 per unit

**Target Price:** ₹112 per unit

**Walk-Away Price:** ₹113 per unit

The strategy prioritizes the highest-value negotiation levers identified by the prototype Shapley analysis.

### Supplier A

**Opening Position:** ₹110.74 per unit

**Target Price:** ₹113 per unit

**Walk-Away Price:** ₹113 per unit

Because no acceptable ZOPA is identified, the strategy focuses on challenging the supplier price and seeking improved commercial terms.

---

## 8. Information and Signalling

The prototype evaluates supplier signals using evidence availability and evidence strength.

Supplier claims with insufficient evidence are treated as requiring verification rather than being automatically accepted.

The signalling and information-asymmetry scores are prototype indicators and are not calibrated probabilities.

---

## 9. Timing Analysis

The prototype evaluates supplier lead time and quoted delivery time against the buyer's required delivery date.

The timing model identifies delivery dependency and timing risk.

It does not establish that a supplier has actually engaged in hold-up behaviour.

---

## 10. Negotiation Levers

The prototype uses Shapley-value analysis to estimate the relative contribution of negotiation levers.

Current prototype levers include:

- Price concession
- Quantity commitment
- Payment terms
- Delivery improvement

These values are synthetic prototype assumptions and are not KB findings.

---

## 11. Overall Demonstration Outcome

The prototype demonstrates an end-to-end procurement negotiation decision-support flow.

It combines:

- Supplier analysis
- Outside options
- BATNA
- Reservation value
- ZOPA
- Nash bargaining
- Signalling
- Credibility
- Information asymmetry
- Timing analysis
- Shapley value
- Negotiation strategy

The final outputs are intended to support negotiation preparation rather than automatically make procurement decisions.

---

## 12. Data Limitation

All numerical results in this demonstration are based on synthetic/sample data.

They must not be presented as actual Knorr-Bremse findings.

Actual KB data should be used for calibration, historical validation and production-level conclusions when it becomes available.