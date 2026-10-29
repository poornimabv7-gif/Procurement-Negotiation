# Procurement Negotiation AI — Model Assumptions

## 1. Supplier Analysis

Supplier evaluation is based on quality, reliability, capacity feasibility, delivery feasibility and qualification status.

The prototype supplier score uses the following weighting:

- Quality: 30%
- Reliability: 25%
- Capacity: 20%
- Delivery: 15%
- Qualification: 10%

The resulting score is used as a supplier-analysis indicator and not as a prediction of supplier performance.

---

## 2. Outside Option

The effective outside-option cost is calculated as:

**Effective Outside Option Cost = Base Cost + Switching Cost + Expected Delivery Risk**

Where:

**Base Cost = Initial Supplier Price × Required Quantity**

The current prototype uses a fixed switching-cost assumption of:

**₹20,000**

Expected delivery risk is currently assigned based on delivery feasibility.

This assumption should be replaced or calibrated using actual KB procurement data.

---

## 3. BATNA

BATNA represents the buyer's best feasible alternative to the current negotiation.

The prototype selects the feasible supplier with the lowest effective outside-option cost.

For the current sample:

**BATNA = Supplier C (S003)**

**BATNA Cost = ₹11,30,000**

The BATNA calculation depends on supplier feasibility, quotation price and the outside-option cost assumptions.

---

## 4. Reservation / Walk-Away Value

The current prototype assumes:

**Reservation Value = BATNA Effective Cost**

Therefore, the buyer's current reservation value is:

**₹11,30,000**

This represents the prototype's buyer-side walk-away boundary.

In a production implementation, the reservation value should also consider factors such as risk, switching costs, strategic importance, market conditions and validated procurement constraints.

---

## 5. ZOPA

ZOPA represents the range in which a negotiation may be feasible between the buyer and supplier.

The current prototype compares the supplier's quoted total against the buyer's reservation value.

For the current implementation:

**Supplier Quoted Total = Initial Price × Required Quantity**

A prototype ZOPA exists when:

**Supplier Quoted Total ≤ Buyer Reservation Value**

For Supplier C:

**Supplier Quoted Total = ₹11,10,000**

**Buyer Reservation Value = ₹11,30,000**

Therefore:

**Prototype ZOPA = ₹11,10,000 to ₹11,30,000**

### Limitation

The supplier quotation is being used as a simplified supplier-side boundary. It is not the supplier's actual reservation price or minimum acceptable price.

---

## 6. Nash Bargaining

The prototype uses an equal-bargaining-power Nash reference point.

The calculation is:

**Nash Price = (Supplier Reservation Proxy + Buyer Reservation Price) / 2**

The supplier reservation proxy is currently based on historical average purchase price.

For Supplier C:

**Historical Average Price = ₹111/unit**

**Buyer Reservation Price = ₹113/unit**

Therefore:

**Nash Price = (111 + 113) / 2 = ₹112/unit**

For 10,000 units:

**Nash Total = ₹11,20,000**

### Limitation

Historical average purchase price is only a proxy for supplier reservation value. It does not represent the supplier's actual cost or minimum acceptable price.

---

## 7. Signalling

Supplier signals are evaluated using available evidence.

The prototype calculates:

**Signal Credibility Score = Evidence Strength × Evidence Availability Score**

Evidence availability is converted into:

- Yes = 1
- No = 0

For example, a signal with evidence strength of 0.8 and available evidence receives:

**0.8 × 1 = 0.8**

The resulting score is classified as:

- 0.70 or above → Strong Evidence
- 0.40 to below 0.70 → Partial Evidence
- Below 0.40 → Weak / Unverified

### Limitation

This score is an evidence-strength indicator. It is not a calibrated probability that the supplier's claim is truthful.

---

## 8. Credibility

The prototype converts signal credibility scores into three categories:

- 0.70 or above → Credible - Can Be Considered
- 0.40 to below 0.70 → Partially Credible - Verify
- Below 0.40 → Unverified - Do Not Rely Without Verification

The credibility classification is used to determine whether a supplier signal can be considered in the analytical process.

---

## 9. Outside-Option Verification

The verification layer converts credibility assessments into analytical decisions:

- Credible → Verified for Analysis
- Partially Credible → Requires Verification
- Unverified → Exclude from Verified Analysis

This creates a verification gate before relying on supplier claims in the negotiation analysis.

---

## 10. Information Asymmetry

The prototype uses the following indicator:

**Information Asymmetry Score = 1 − Signal Credibility Score**

The score is classified as:

- 0.70 or above → High Information Asymmetry
- 0.40 to below 0.70 → Moderate Information Asymmetry
- Below 0.40 → Low Information Asymmetry

### Limitation

This is a prototype indicator rather than a formal statistical measurement of information asymmetry.

---

## 11. Timing / Hold-Up Analysis

The timing analysis compares supplier lead time and quoted delivery time against the required delivery time.

The prototype calculates:

**Lead-Time Gap = Supplier Lead Time − Required Delivery Time**

**Delivery Gap = Quoted Delivery Time − Required Delivery Time**

The current classification is:

- Both within requirement → Low Timing Risk
- Within requirement plus up to 5 days → Moderate Timing Risk
- Beyond this range → High Timing Risk

The model identifies timing dependency that may be relevant to negotiation.

### Limitation

Timing risk does not by itself establish that supplier hold-up behaviour will occur. Hold-up analysis should be strengthened using actual contractual, investment and negotiation-history data.

---

## 12. Shapley Value

The Shapley analysis is used to attribute the contribution of negotiation levers to the total prototype negotiation value.

Current prototype negotiation levers are:

- Price concession = ₹50,000
- Quantity commitment = ₹20,000
- Payment terms = ₹10,000
- Delivery improvement = ₹15,000

Total negotiation value:

**₹95,000**

The current prototype uses an additive value structure, so the Shapley contribution of each lever corresponds to its supplied contribution.

### Limitation

These lever values are synthetic prototype assumptions. They are not actual KB negotiation findings and should be calculated from real negotiation outcomes when available.

---

## 13. Final Negotiation Decision

The final decision layer combines:

- Nash bargaining
- ZOPA
- Timing risk
- Information asymmetry

The prototype uses rule-based logic to produce a negotiation recommendation.

Examples include:

- Review / Seek Better Terms
- Proceed with Negotiation
- Proceed with Negotiation / Verify Signals
- Proceed with Caution / Mitigate Timing Risk
- Proceed with Verification

### Limitation

The final recommendation is a rule-based analytical output. It is not a prediction of supplier behaviour or a machine-learning probability.

---

## 14. Overall Prototype Assumptions

The current implementation is an applied research prototype using sample procurement data.

The main assumptions requiring future calibration are:

1. Switching cost
2. Delivery-risk cost
3. Buyer reservation value
4. Supplier reservation-price proxy
5. ZOPA supplier-side boundary
6. Signal credibility thresholds
7. Information asymmetry thresholds
8. Timing-risk thresholds
9. Negotiation lever values
10. Final negotiation decision rules

These assumptions should be reviewed and calibrated using actual KB procurement and negotiation data before production use.

---

## 15. Data Status

The current results are based on the project's sample dataset.

The current numerical results should therefore be treated as:

**Prototype / Demonstration Results**

They should not be presented as actual KB negotiation findings until the model is run and validated using real KB data.