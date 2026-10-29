# SOW Deliverable Mapping

## 1. Purpose

This document maps the current Procurement Negotiation AI prototype to the
defined SOW deliverables for the Knorr-Bremse procurement negotiation use case.

The current implementation is a research/prototype implementation using
synthetic sample data. Numerical outputs must not be presented as actual
Knorr-Bremse findings.

---

# 2. SOW Deliverable 1
## Literature Foundation for Procurement Negotiation

### Required concepts

The analytical framework covers the following game-theoretic concepts:

| Concept | Prototype Application |
|---|---|
| Bargaining | Nash Bargaining |
| Signalling | Supplier signal analysis |
| Credibility | Evidence-based credibility assessment |
| Outside Options | Alternative supplier analysis |
| Hold-up / Timing | Timing dependency analysis |
| Cooperative Attribution | Shapley value |
| Information Asymmetry | Supplier information asymmetry indicator |

### Procurement negotiation concepts

The prototype also incorporates:

- BATNA
- Reservation / Walk-Away Value
- ZOPA
- Supplier historical pricing
- Supplier quotations
- Negotiation levers
- Carrot and stick strategies

---

# 3. SOW Deliverable 2
## Working Game-Theory / Quantitative Models

The current Python prototype implements the following analytical stages:

1. Supplier Analysis
2. Outside Option Analysis
3. BATNA
4. Reservation Value
5. ZOPA
6. Nash Bargaining
7. Supplier Signalling
8. Credibility
9. Outside-Option Verification
10. Information Asymmetry
11. Timing / Hold-up Analysis
12. Shapley Value
13. Final Negotiation Decision
14. Negotiation Strategy
15. Negotiation Brief

The complete workflow is integrated through:

`main.py`

---

# 4. SOW Deliverable 3
## Demonstration on Negotiation Data

A synthetic demonstration case has been implemented.

### Current sample case

| Field | Value |
|---|---|
| Case ID | NEG001 |
| RFQ | RFQ001 |
| Material | M001 |
| Quantity | 10,000 |
| Current Supplier | S001 |
| Current Offer | ₹120/unit |
| Required Delivery | 30 days |

### Current prototype BATNA

Supplier C (S003)

BATNA effective cost:

₹1,130,000

### Current prototype reservation value

₹1,130,000 total

₹113/unit

### Current prototype ZOPA

Supplier C:

₹111 – ₹113/unit

### Current prototype Nash price

Supplier C:

₹112/unit

These values are generated from synthetic sample data and prototype assumptions.

---

# 5. SOW Deliverable 4
## Research Report and Adoption Guidance

The current project contains supporting documentation for:

- Model assumptions
- Model validation
- KB data mapping
- Demonstration case
- SOW deliverable mapping

The final research/adoption report should be expanded after actual KB data
is available and the models have been calibrated and validated.

---

# 6. Current Project Architecture

```text
Procurement / Supplier Data
            |
            v
     Data Preparation
            |
            v
     Supplier Analysis
            |
            v
     Outside Options
            |
            v
           BATNA
            |
            v
 Reservation / Walk-Away
            |
            v
           ZOPA
            |
            v
     Game-Theory Layer
            |
     +------+-------+--------+--------+
     |              |        |        |
     v              v        v        v
 Nash          Signalling  Timing   Shapley
 Bargaining   Credibility  /Hold-up  Value
     |              |        |        |
     +--------------+--------+--------+
                    |
                    v
       Final Negotiation Decision
                    |
                    v
        Negotiation Strategy
                    |
                    v
         Negotiation Brief