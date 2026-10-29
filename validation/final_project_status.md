# Procurement Negotiation AI
# Final Project Status

## 1. Project Objective

Build an AI-assisted procurement negotiation decision-support framework
using quantitative procurement analysis and applied game-theory models.

The framework is designed to support:

- Supplier analysis
- Outside-option identification
- BATNA calculation
- Reservation / walk-away value
- ZOPA analysis
- Bargaining analysis
- Supplier signalling and credibility
- Information asymmetry analysis
- Timing / hold-up analysis
- Negotiation-lever attribution
- Negotiation strategy preparation

---

## 2. Current Implementation Status

| Component | Status |
|---|---|
| Project structure | Completed |
| Sample procurement data | Completed |
| Supplier analysis | Completed |
| Outside-option analysis | Completed |
| BATNA | Completed |
| Reservation value | Completed |
| ZOPA | Completed |
| Nash bargaining | Completed |
| Supplier signalling | Completed |
| Credibility analysis | Completed |
| Outside-option verification | Completed |
| Information asymmetry | Completed |
| Timing / hold-up analysis | Completed |
| Shapley-value analysis | Completed |
| Final negotiation decision | Completed |
| Negotiation strategy | Completed |
| Negotiation brief | Completed |
| End-to-end main.py pipeline | Completed |
| Model assumptions documentation | Completed |
| Model validation documentation | Completed |
| KB data mapping | Completed |
| Demo case documentation | Completed |
| SOW mapping | Completed |
| Actual KB data integration | Pending |
| Model calibration | Pending |
| Historical validation | Pending |
| Final research/adoption report | Pending |

---

## 3. Current Data Status

The current implementation uses synthetic/sample procurement data.

The sample data contains:

- Supplier data
- Purchase history
- Quotation data
- Negotiation history
- Market cost data
- Negotiation case data
- Supplier signals

The sample data is used only to demonstrate the analytical workflow.

The numerical outputs must not be presented as actual
Knorr-Bremse findings.

---

## 4. End-to-End Workflow

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
          Credibility /Hold-up
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