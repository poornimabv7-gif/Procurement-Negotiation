import pandas as pd


# ==========================================================
# NEGOTIATION STRATEGY
# ==========================================================


def build_negotiation_strategy(
    final_analysis,
    zopa_analysis,
    shapley_analysis
):
    """
    Build a rule-based procurement negotiation strategy.

    This is a prototype decision-support model based on
    synthetic/sample procurement data.

    Important price logic:

        Opening Price <= Target Price <= Walk-Away Price

    From the buyer's perspective:
        - Opening = aggressive starting position
        - Target = preferred negotiated outcome
        - Walk-away = maximum acceptable price

    The model does not predict supplier behaviour.
    """

    result = final_analysis.copy()

    # ---------------------------------------------------------
    # Helper functions
    # ---------------------------------------------------------

    def safe_float(value, default=None):
        try:
            if pd.isna(value):
                return default
            return float(value)
        except (TypeError, ValueError):
            return default

    def safe_text(value, default="Unknown"):
        if pd.isna(value):
            return default
        return str(value)

    # ---------------------------------------------------------
    # Determine required quantity
    # ---------------------------------------------------------

    required_quantity = None

    if "required_quantity" in result.columns:
        quantities = pd.to_numeric(
            result["required_quantity"],
            errors="coerce"
        ).dropna()

        if not quantities.empty:
            required_quantity = float(quantities.iloc[0])

    # ---------------------------------------------------------
    # Identify important negotiation levers
    # ---------------------------------------------------------

    shapley = shapley_analysis.copy()

    if (
        "lever" in shapley.columns
        and "shapley_value" in shapley.columns
    ):
        shapley["shapley_value"] = pd.to_numeric(
            shapley["shapley_value"],
            errors="coerce"
        )

        shapley = shapley.sort_values(
            by="shapley_value",
            ascending=False
        )

        top_levers = (
            shapley["lever"]
            .dropna()
            .head(2)
            .tolist()
        )
    else:
        top_levers = [
            "price_concession",
            "quantity_commitment"
        ]

    def format_levers(levers):
        lever_names = {
            "price_concession": "Price Concession",
            "quantity_commitment": "Quantity Commitment",
            "payment_terms": "Payment Terms",
            "delivery_improvement": "Delivery Improvement"
        }

        return ", ".join(
            lever_names.get(lever, lever)
            for lever in levers
        )

    primary_levers = format_levers(top_levers)

    # ---------------------------------------------------------
    # ZOPA helper
    # ---------------------------------------------------------

    def convert_zopa_to_unit(value, quantity):
        numeric_value = safe_float(value)

        if numeric_value is None:
            return None

        if quantity is not None and quantity > 0:

            # ZOPA output is normally a total value.
            if numeric_value > 1000:
                return numeric_value / quantity

        return numeric_value

    # ---------------------------------------------------------
    # Find ZOPA
    # ---------------------------------------------------------

    def get_zopa_status(supplier_id):

        if (
            zopa_analysis is None
            or zopa_analysis.empty
            or "supplier_id" not in zopa_analysis.columns
        ):
            return False, None, None

        rows = zopa_analysis[
            zopa_analysis["supplier_id"] == supplier_id
        ]

        if rows.empty:
            return False, None, None

        row = rows.iloc[0]

        zopa_exists = bool(
            row.get(
                "zopa_exists",
                False
            )
        )

        zopa_low = convert_zopa_to_unit(
            row.get("zopa_low"),
            required_quantity
        )

        zopa_high = convert_zopa_to_unit(
            row.get("zopa_high"),
            required_quantity
        )

        return (
            zopa_exists,
            zopa_low,
            zopa_high
        )

    strategies = []

    # =========================================================
    # BUILD SUPPLIER-SPECIFIC STRATEGY
    # =========================================================

    for _, row in result.iterrows():

        supplier_id = row["supplier_id"]

        supplier_name = safe_text(
            row.get("supplier_name"),
            supplier_id
        )

        # -----------------------------------------------------
        # ZOPA
        # -----------------------------------------------------

        (
            zopa_exists,
            zopa_low,
            zopa_high
        ) = get_zopa_status(
            supplier_id
        )

        # -----------------------------------------------------
        # Core negotiation values
        # -----------------------------------------------------

        nash_price = safe_float(
            row.get("nash_price_per_unit")
        )

        buyer_reservation = safe_float(
            row.get("buyer_reservation_per_unit")
        )

        initial_price = safe_float(
            row.get("initial_price")
        )

        current_offer = safe_float(
            row.get("current_offer")
        )

        if current_offer is None:
            current_offer = initial_price

        if initial_price is None:
            initial_price = current_offer

        # -----------------------------------------------------
        # Risk information
        # -----------------------------------------------------

        timing_risk = safe_text(
            row.get("timing_risk"),
            "Low Timing Risk"
        )

        information_level = safe_text(
            row.get("information_asymmetry_level"),
            "No Evidence Available"
        )

        delivery_risk = safe_text(
            row.get("delivery_risk"),
            "Unknown"
        )

        overall_risk_level = safe_text(
            row.get("overall_risk_level"),
            "Unknown"
        )

        # =====================================================
        # WALK-AWAY PRICE
        # =====================================================

        walk_away_price = buyer_reservation

        # =====================================================
        # TARGET PRICE
        # =====================================================
        #
        # Buyer-side logic:
        #
        # If ZOPA exists:
        #   use Nash only if it is BELOW the walk-away price.
        #
        # Otherwise:
        #   target below walk-away.
        #
        # The target should NEVER be above the walk-away.
        # =====================================================

        if buyer_reservation is not None:

            if (
                zopa_exists
                and nash_price is not None
                and nash_price < buyer_reservation
            ):
                target_price = nash_price

            elif (
                current_offer is not None
                and current_offer < buyer_reservation
            ):
                # Current supplier offer is already better
                # than the buyer's reservation.
                target_price = current_offer

            else:
                # Set target below reservation.
                # Use 98% of reservation as a conservative
                # prototype target.
                target_price = buyer_reservation * 0.98

        elif nash_price is not None:

            target_price = nash_price

        elif current_offer is not None:

            target_price = current_offer * 0.98

        else:

            target_price = None

        # -----------------------------------------------------
        # Make sure target remains below walk-away
        # -----------------------------------------------------

        if (
            target_price is not None
            and walk_away_price is not None
        ):
            target_price = min(
                target_price,
                walk_away_price
            )

        # =====================================================
        # OPENING PRICE
        # =====================================================
        #
        # Buyer starts at or below the target.
        #
        # If supplier's current offer is already below target,
        # preserve that attractive current offer.
        #
        # Otherwise open approximately 2% below target.
        # =====================================================

        if (
            current_offer is not None
            and target_price is not None
            and current_offer < target_price
        ):

            opening_price = current_offer

        elif target_price is not None:

            opening_price = target_price * 0.98

        else:

            opening_price = buyer_reservation

        # -----------------------------------------------------
        # Enforce price ordering
        # -----------------------------------------------------

        if (
            opening_price is not None
            and target_price is not None
        ):
            opening_price = min(
                opening_price,
                target_price
            )

        if (
            target_price is not None
            and walk_away_price is not None
        ):
            target_price = min(
                target_price,
                walk_away_price
            )

        if (
            opening_price is not None
            and walk_away_price is not None
        ):
            opening_price = min(
                opening_price,
                walk_away_price
            )

        # =====================================================
        # Negotiation posture
        # =====================================================

        if not zopa_exists:

            posture = (
                "Firm / Challenge Price / "
                "Seek Better Terms"
            )

        elif (
            information_level ==
            "High Information Asymmetry"
        ):

            posture = (
                "Verification First"
            )

        elif (
            information_level ==
            "Moderate Information Asymmetry"
        ):

            posture = (
                "Verify Supplier Claims"
            )

        elif timing_risk == "High Timing Risk":

            posture = (
                "Proceed with Caution / "
                "Mitigate Timing Risk"
            )

        elif delivery_risk == "High":

            posture = (
                "Commercially Protective / "
                "Mitigate Delivery Risk"
            )

        elif overall_risk_level == "High":

            posture = (
                "Risk-Controlled Negotiation"
            )

        else:

            posture = (
                "Collaborative Negotiation"
            )

        # =====================================================
        # Information / signal action
        # =====================================================

        if information_level in [
            "High Information Asymmetry",
            "Moderate Information Asymmetry"
        ]:

            signal_action = (
                "Request supporting evidence and "
                "validate supplier claims before "
                "using them in the negotiation."
            )

        elif (
            information_level ==
            "No Evidence Available"
        ):

            signal_action = (
                "Collect supplier evidence before "
                "relying on supplier claims."
            )

        else:

            signal_action = (
                "Use available supplier evidence "
                "as supporting negotiation input."
            )

        # =====================================================
        # Timing action
        # =====================================================

        if timing_risk == "High Timing Risk":

            timing_action = (
                "Reduce delivery dependency and "
                "negotiate firm delivery commitments."
            )

        elif timing_risk == "Moderate Timing Risk":

            timing_action = (
                "Address delivery timing and obtain "
                "clear delivery commitments."
            )

        elif delivery_risk == "High":

            timing_action = (
                "Negotiate delivery SLAs, service "
                "commitments and performance protection."
            )

        else:

            timing_action = (
                "No major timing dependency identified."
            )

        # =====================================================
        # Negotiation lever strategy
        # =====================================================

        lever_actions = []

        if "Price Concession" in primary_levers:

            lever_actions.append(
                "Prioritize direct price reduction."
            )

        if "Quantity Commitment" in primary_levers:

            lever_actions.append(
                "Use volume commitment as an exchange "
                "for price improvement."
            )

        if "Payment Terms" in primary_levers:

            lever_actions.append(
                "Use payment-term flexibility as a "
                "conditional negotiation lever."
            )

        if "Delivery Improvement" in primary_levers:

            lever_actions.append(
                "Use delivery improvement as a "
                "negotiation condition."
            )

        if not lever_actions:

            lever_actions.append(
                "Focus on price, delivery and "
                "commercial terms."
            )

        negotiation_levers = " ".join(
            lever_actions
        )

        # =====================================================
        # Carrot strategy
        # =====================================================

        if zopa_exists:

            carrot = (
                "Offer a measurable commercial concession "
                "such as quantity commitment, payment flexibility "
                "or delivery flexibility in exchange for "
                "supplier price or service improvement."
            )

        else:

            carrot = (
                "Offer non-price concessions only when they "
                "produce a measurable improvement in supplier "
                "commercial terms."
            )

        # =====================================================
        # Stick strategy
        # =====================================================

        stick = (
            "Maintain the BATNA and buyer reservation value "
            "as the negotiation boundary. If acceptable terms "
            "cannot be reached, evaluate qualified alternative "
            "suppliers."
        )

        # =====================================================
        # Risk mitigation
        # =====================================================

        risk_actions = []

        if delivery_risk == "High":

            risk_actions.append(
                "Include delivery SLAs and measurable "
                "performance commitments."
            )

        if information_level in [
            "High Information Asymmetry",
            "Moderate Information Asymmetry"
        ]:

            risk_actions.append(
                "Validate supplier claims with "
                "supporting evidence."
            )

        if (
            information_level ==
            "No Evidence Available"
        ):

            risk_actions.append(
                "Collect supplier evidence before "
                "relying on supplier claims."
            )

        if not zopa_exists:

            risk_actions.append(
                "Do not exceed the buyer "
                "reservation boundary."
            )

        if overall_risk_level == "High":

            risk_actions.append(
                "Apply stronger contractual and "
                "commercial safeguards."
            )

        if not risk_actions:

            risk_actions.append(
                "Maintain standard supplier monitoring."
            )

        risk_mitigation = " ".join(
            risk_actions
        )

        # =====================================================
        # Supplier-specific strategy
        # =====================================================

        if (
            supplier_id == "S002"
            and zopa_exists
            and delivery_risk == "High"
        ):

            supplier_strategy = (
                "Protect the strong commercial position while "
                "using delivery performance as the main negotiation "
                "condition. Retain the competitive price and "
                "obtain firm delivery commitments."
            )

        elif (
            supplier_id == "S001"
            and not zopa_exists
        ):

            supplier_strategy = (
                "Challenge the current ₹120 supplier offer. "
                "Use qualified alternatives and the buyer's "
                "₹110 reservation boundary to seek a materially "
                "lower price or improved commercial terms."
            )

        elif (
            supplier_id == "S003"
            and information_level ==
            "Moderate Information Asymmetry"
        ):

            supplier_strategy = (
                "Use the supplier's strong delivery performance "
                "as a positive commercial factor, but verify "
                "supplier claims before relying on them. "
                "Seek a limited price improvement toward ₹110 "
                "or obtain improved commercial terms."
            )

        elif not zopa_exists:

            supplier_strategy = (
                "No acceptable ZOPA is currently identified. "
                "Use the BATNA and qualified alternative suppliers "
                "as commercial leverage and seek better terms."
            )

        else:

            supplier_strategy = (
                "Use a balanced negotiation approach focused "
                "on price improvement, commercial terms and "
                "supplier risk mitigation."
            )

        # =====================================================
        # Final negotiation strategy
        # =====================================================

        if zopa_exists:

            if (
                opening_price is not None
                and target_price is not None
                and walk_away_price is not None
            ):

                strategy = (
                    f"Open around ₹{opening_price:,.2f} per unit, "
                    f"target approximately ₹{target_price:,.2f} "
                    f"per unit, and do not exceed the walk-away "
                    f"boundary of ₹{walk_away_price:,.2f} per unit. "
                    f"ZOPA is approximately ₹{zopa_low:,.2f}–"
                    f"₹{zopa_high:,.2f} per unit. "
                    f"Prioritize {primary_levers}. "
                    f"{supplier_strategy}"
                )

            else:

                strategy = (
                    "Use the identified ZOPA to negotiate toward "
                    "the best achievable commercial terms. "
                    f"Prioritize {primary_levers}. "
                    f"{supplier_strategy}"
                )

        else:

            if (
                opening_price is not None
                and target_price is not None
                and walk_away_price is not None
            ):

                strategy = (
                    "No acceptable ZOPA is currently identified. "
                    f"Open around ₹{opening_price:,.2f} per unit, "
                    f"target approximately ₹{target_price:,.2f} "
                    f"per unit, and do not exceed the buyer "
                    f"reservation boundary of "
                    f"₹{walk_away_price:,.2f} per unit. "
                    f"Prioritize {primary_levers}. "
                    f"{supplier_strategy}"
                )

            else:

                strategy = (
                    "No acceptable ZOPA is currently identified. "
                    "Use the BATNA and alternative suppliers to "
                    "seek better commercial terms."
                )

        # =====================================================
        # Append strategy result
        # =====================================================

        strategies.append(
            {
                "supplier_id":
                    supplier_id,

                "supplier_name":
                    supplier_name,

                "zopa_exists":
                    zopa_exists,

                "zopa_low_per_unit":
                    round(
                        zopa_low,
                        2
                    )
                    if zopa_low is not None
                    else None,

                "zopa_high_per_unit":
                    round(
                        zopa_high,
                        2
                    )
                    if zopa_high is not None
                    else None,

                "current_offer_per_unit":
                    round(
                        current_offer,
                        2
                    )
                    if current_offer is not None
                    else None,

                "opening_price_per_unit":
                    round(
                        opening_price,
                        2
                    )
                    if opening_price is not None
                    else None,

                "target_price_per_unit":
                    round(
                        target_price,
                        2
                    )
                    if target_price is not None
                    else None,

                "walk_away_price_per_unit":
                    round(
                        walk_away_price,
                        2
                    )
                    if walk_away_price is not None
                    else None,

                "primary_negotiation_levers":
                    primary_levers,

                "negotiation_posture":
                    posture,

                "signal_action":
                    signal_action,

                "timing_action":
                    timing_action,

                "negotiation_levers":
                    negotiation_levers,

                "carrot_strategy":
                    carrot,

                "stick_strategy":
                    stick,

                "risk_mitigation":
                    risk_mitigation,

                "supplier_specific_strategy":
                    supplier_strategy,

                "negotiation_strategy":
                    strategy
            }
        )

    return pd.DataFrame(strategies)


# ==========================================================
# STANDALONE TEST
# ==========================================================

if __name__ == "__main__":

    import sys

    try:
        sys.stdout.reconfigure(
            encoding="utf-8"
        )
    except AttributeError:
        pass

    print("\n========================================")
    print(" NEGOTIATION STRATEGY")
    print("========================================\n")

    final_analysis = pd.read_csv(
        "outputs/final_negotiation_decision.csv"
    )

    zopa_analysis = pd.read_csv(
        "outputs/zopa_analysis.csv"
    )

    shapley_analysis = pd.read_csv(
        "outputs/shapley_analysis.csv"
    )

    strategy = build_negotiation_strategy(
        final_analysis,
        zopa_analysis,
        shapley_analysis
    )

    pd.set_option(
        "display.max_columns",
        None
    )

    pd.set_option(
        "display.max_colwidth",
        None
    )

    pd.set_option(
        "display.width",
        250
    )

    print(
        strategy.to_string(
            index=False
        )
    )

    strategy.to_csv(
        "outputs/negotiation_strategy.csv",
        index=False,
        encoding="utf-8-sig"
    )

    print("\n========================================")
    print(" NEGOTIATION STRATEGY COMPLETED")
    print(" Output saved to:")
    print(" outputs/negotiation_strategy.csv")
    print("========================================\n")