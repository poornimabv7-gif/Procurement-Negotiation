# KB Data Mapping

## 1. Purpose

This document defines how actual Knorr-Bremse (KB) procurement and negotiation data will be mapped to the current Procurement Negotiation AI prototype.

The current Python implementation uses sample datasets. Actual KB data will be mapped to these structures before model calibration and validation.

---

## 2. Data Mapping

| KB Data Source | Required Information | Current Prototype Dataset | Used By |
|---|---|---|---|
| Supplier Master | Supplier ID, supplier name, capacity, quality, reliability, lead time, qualification status | supplier_data.csv | Supplier Analysis, Outside Option |
| Purchase History | Supplier, material, quantity, purchase date, historical purchase price | purchase_history.csv | BATNA, Nash Bargaining |
| RFQ / Quotation Data | RFQ, supplier, material, quantity, quoted price, delivery time, payment terms | quotation_data.csv | Supplier Analysis, Outside Option, ZOPA |
| Negotiation History | Negotiation rounds, buyer offers, supplier offers, final price, outcome | negotiation_history.csv | Nash Bargaining, Calibration, Validation |
| Market / Cost Data | Commodity price, market price, transport cost | market_cost_data.csv | Outside Option |
| Supplier Claims / Signals | Supplier claims, evidence availability, evidence strength | supplier_signals.csv | Signalling, Credibility, Information Asymmetry |
| Negotiation Case | RFQ, material, required quantity, current supplier, current offer, required delivery | negotiation_case.csv | BATNA, Reservation Value, ZOPA, Timing |

---

## 3. Supplier Master Mapping

Actual KB supplier master data should be mapped to:

- supplier_id
- supplier_name
- material_category
- capacity
- quality_score
- reliability_score
- lead_time_days
- qualification_status
- payment_terms_days

Used for:

- Supplier Analysis
- Supplier feasibility
- Outside Option calculation
- Timing analysis

---

## 4. Purchase History Mapping

Actual KB purchase history should provide, where available:

- purchase order ID
- supplier ID
- material ID
- quantity
- purchase date
- historical purchase price
- currency

Used for:

- Historical supplier price analysis
- BATNA analysis
- Supplier reservation-price proxy
- Nash Bargaining
- Historical calibration

---

## 5. RFQ / Quotation Mapping

Actual RFQ and quotation data should provide:

- RFQ ID
- Supplier ID
- Material ID
- Required quantity
- Initial supplier quotation
- Delivery days
- MOQ
- Payment terms

Used for:

- Supplier Analysis
- Outside Option
- ZOPA
- Negotiation analysis

---

## 6. Negotiation History Mapping

Actual negotiation records should provide, where available:

- negotiation ID
- RFQ ID
- supplier ID
- negotiation round
- buyer offer
- supplier offer
- timestamp
- final negotiated price
- negotiation outcome

Used for:

- Nash Bargaining calibration
- Negotiation behaviour analysis
- Historical validation
- Model calibration

---

## 7. Market and Cost Data Mapping

Actual market or cost information may include:

- Material ID
- Date
- Commodity price
- Market price
- Transport cost
- Other relevant cost components

Used for:

- Outside Option calculation
- Market-price comparison
- Cost-boundary calibration

The current prototype accepts market cost data, but the outside-option model has not yet fully incorporated all market-cost fields.

---

## 8. Supplier Signals Mapping

Supplier claims or negotiation signals should be mapped to:

- supplier ID
- signal type
- signal value
- evidence availability
- evidence strength

Used for:

- Signalling analysis
- Credibility assessment
- Outside-option verification
- Information asymmetry analysis

The current evidence score is a prototype indicator and should not be interpreted as a calibrated probability.

---

## 9. Important Data Gaps to Check

Before integrating actual KB data, check whether the following information is available:

1. Supplier capacity
2. Supplier quality/reliability metrics
3. Supplier qualification status
4. Historical purchase prices
5. Supplier quotations
6. Historical negotiation offers
7. Final negotiated prices
8. Negotiation outcomes
9. Market/cost information
10. Evidence supporting supplier claims
11. Delivery performance
12. Payment terms

If some fields are unavailable, the model should not invent values. The affected model or calculation should instead be documented as unavailable or use a clearly stated proxy.

---

## 10. Integration Approach

The integration should follow these stages:

1. Obtain actual KB datasets.
2. Inspect file names, columns, data types and sample records.
3. Map KB columns to the prototype schema.
4. Identify missing fields.
5. Create required transformations.
6. Keep the original KB data unchanged.
7. Create a standardized input dataset for the model.
8. Run `main.py`.
9. Compare model outputs with historical negotiation outcomes.
10. Calibrate model assumptions and thresholds.
11. Document validation results.

---

## 11. Current Data Status

Current prototype:

**Data:** Synthetic/sample data

**Purpose:** Development and functional validation

**Actual KB data:** Not yet integrated

Therefore, current numerical outputs must not be presented as actual KB findings.

---

## 12. Next Action

The next action is to inspect the actual KB procurement and negotiation datasets and create the column-level mapping required for integration and calibration.