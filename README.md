# Procurement Negotiation AI

## Applied Game-Theory Modelling for Procurement Negotiation

A Python-based procurement negotiation decision-support capstone project that combines supplier analysis, quantitative procurement models, and applied game-theory concepts to prepare negotiation strategies.

> **Data Note:** This project uses a synthetic/sample procurement dataset created for demonstration purposes. It does not contain real Knorr-Bremse procurement data.

---

# 1. Project Objective

The objective of this project is to demonstrate how procurement and game-theory analysis can be combined to support supplier negotiation preparation.

The system analyzes supplier alternatives, procurement history, quotations, negotiation information, supplier signals, timing dependencies, and negotiation levers.

The final output provides a structured negotiation strategy and negotiation brief for the procurement user.

---

# 2. Business Problem

Procurement negotiations involve several uncertainties:

- Which alternative suppliers are feasible?
- What is the buyer's BATNA?
- What is the buyer's reservation / walk-away value?
- Is there a feasible bargaining range?
- What price provides a reasonable bargaining reference?
- Which supplier claims require verification?
- Is the buyer dependent on the supplier because of timing?
- Which negotiation levers can create additional value?
- What should the buyer use as an opening position?
- What concessions or conditions can be used during negotiation?

This project provides a structured analytical framework to answer these questions.

---

# 3. End-to-End Architecture

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
     +------+------+------+------+
     |      |      |      |
     v      v      v      v
   Nash  Signalling Timing Shapley
          Credibility /Hold-up Value
     |      |      |      |
     +------+------+------+------+
            |
            v
   Final Negotiation Decision
            |
            v
    Negotiation Strategy
            |
            v
     Negotiation Brief