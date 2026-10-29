import pandas as pd


# ============================================================
# HELPER FUNCTIONS
# ============================================================


def _merge_supplier_output(base, addition):
    """
    Merge supplier-level analytical results into the final result.

    Only one row per supplier is retained from the addition.
    Existing columns are preserved unless they are explicitly
    removed before this function is called.
    """

    if addition is None or addition.empty:
        return base

    if "supplier_id" not in addition.columns:
        return base

    addition = (
        addition
        .drop_duplicates(subset=["supplier_id"])
        .reset_index(drop=True)
    )

    columns_to_add = [
        column
        for column in addition.columns
        if column != "supplier_id"
        and column not in base.columns
    ]

    if not columns_to_add:
        return base

    return base.merge(
        addition[
            ["supplier_id"] + columns_to_add
        ],
        on="supplier_id",
        how="left",
        validate="one_to_one",
    )


def _prepare_supplier_summary(data):
    """
    Convert a supplier-level analytical dataframe into
    one row per supplier.
    """

    if data is None or data.empty:
        return pd.DataFrame()

    if "supplier_id" not in data.columns:
        return pd.DataFrame()

    return (
        data
        .drop_duplicates(subset=["supplier_id"])
        .reset_index(drop=True)
    )


def _prepare_information_asymmetry(information_result):
    """
    Prepare authoritative supplier-level information-asymmetry
    results from the dedicated information_asymmetry model.

    Important:
    Suppliers with no signals are NOT assigned a fabricated
    asymmetry score.
    """

    if (
        information_result is None
        or information_result.empty
        or "supplier_id" not in information_result.columns
    ):
        return pd.DataFrame(
            columns=[
                "supplier_id",
                "average_signal_credibility",
                "verified_signal_count",
                "total_signal_count",
                "verification_rate",
                "information_asymmetry_score",
                "information_asymmetry_level",
                "information_asymmetry_action",
                "information_signal_count",
            ]
        )

    info = information_result.copy()

    # --------------------------------------------------------
    # Numeric conversions
    # --------------------------------------------------------

    if "signal_credibility_score" in info.columns:
        info["signal_credibility_score"] = pd.to_numeric(
            info["signal_credibility_score"],
            errors="coerce"
        )

    # --------------------------------------------------------
    # Signal count
    # --------------------------------------------------------

    signal_count = (
        info.groupby("supplier_id")
        .size()
        .rename("information_signal_count")
        .reset_index()
    )

    # --------------------------------------------------------
    # Average signal credibility
    # --------------------------------------------------------

    if "signal_credibility_score" in info.columns:

        credibility_summary = (
            info.groupby("supplier_id")[
                "signal_credibility_score"
            ]
            .mean()
            .rename("average_signal_credibility")
            .reset_index()
        )

    else:

        credibility_summary = pd.DataFrame(
            columns=[
                "supplier_id",
                "average_signal_credibility"
            ]
        )

    # --------------------------------------------------------
    # Total signals
    # --------------------------------------------------------

    total_signals = (
        info.groupby("supplier_id")
        .size()
        .rename("total_signal_count")
        .reset_index()
    )

    # --------------------------------------------------------
    # Verified signals
    # --------------------------------------------------------

    if "verification_decision" in info.columns:

        verified = (
            info["verification_decision"]
            .astype(str)
            .eq("Verified for Analysis")
        )

        info["_verified_flag"] = verified.astype(int)

        verified_summary = (
            info.groupby("supplier_id")["_verified_flag"]
            .sum()
            .rename("verified_signal_count")
            .reset_index()
        )

    else:

        verified_summary = pd.DataFrame(
            columns=[
                "supplier_id",
                "verified_signal_count"
            ]
        )

    # --------------------------------------------------------
    # Combine signal summaries
    # --------------------------------------------------------

    summary = signal_count.copy()

    summary = summary.merge(
        credibility_summary,
        on="supplier_id",
        how="left"
    )

    summary = summary.merge(
        total_signals,
        on="supplier_id",
        how="left"
    )

    summary = summary.merge(
        verified_summary,
        on="supplier_id",
        how="left"
    )

    summary["verified_signal_count"] = (
        summary["verified_signal_count"]
        .fillna(0)
    )

    summary["total_signal_count"] = (
        summary["total_signal_count"]
        .fillna(0)
    )

    # --------------------------------------------------------
    # Verification rate
    # --------------------------------------------------------

    summary["verification_rate"] = summary.apply(
        lambda row:
        (
            row["verified_signal_count"]
            /
            row["total_signal_count"]
        )
        if row["total_signal_count"] > 0
        else None,
        axis=1
    )

    # --------------------------------------------------------
    # Information asymmetry
    #
    # Use the dedicated model's score.
    # Do NOT create a score for suppliers without signals.
    # --------------------------------------------------------

    if "information_asymmetry_score" in info.columns:

        asymmetry_summary = (
            info.groupby("supplier_id")[
                "information_asymmetry_score"
            ]
            .mean()
            .rename("information_asymmetry_score")
            .reset_index()
        )

        summary = summary.merge(
            asymmetry_summary,
            on="supplier_id",
            how="left"
        )

    else:

        summary["information_asymmetry_score"] = pd.NA

    # --------------------------------------------------------
    # Classify information asymmetry
    # --------------------------------------------------------

    def classify_information(score):

        if pd.isna(score):
            return "No Evidence Available"

        if score >= 0.70:
            return "High Information Asymmetry"

        if score >= 0.40:
            return "Moderate Information Asymmetry"

        return "Low Information Asymmetry"

    summary["information_asymmetry_level"] = (
        summary["information_asymmetry_score"]
        .apply(classify_information)
    )

    # --------------------------------------------------------
    # Recommended information action
    # --------------------------------------------------------

    def information_action(row):

        signal_count = row["information_signal_count"]
        score = row["information_asymmetry_score"]

        if signal_count == 0:
            return (
                "Collect supplier evidence before relying on claims"
            )

        if pd.isna(score):
            return "Collect additional evidence"

        if score >= 0.70:
            return (
                "Request evidence before relying on supplier claim"
            )

        if score >= 0.40:
            return (
                "Seek additional information during negotiation"
            )

        return (
            "Information is sufficient for preliminary analysis"
        )

    summary["information_asymmetry_action"] = (
        summary.apply(
            information_action,
            axis=1
        )
    )

    # --------------------------------------------------------
    # Final column order
    # --------------------------------------------------------

    columns = [
        "supplier_id",
        "average_signal_credibility",
        "verified_signal_count",
        "total_signal_count",
        "verification_rate",
        "information_asymmetry_score",
        "information_asymmetry_level",
        "information_asymmetry_action",
        "information_signal_count",
    ]

    return summary[columns]


# ============================================================
# FINAL NEGOTIATION DECISION
# ============================================================


def build_negotiation_decision(
    nash_result,
    zopa_result,
    timing_result,
    supplier_risk_result,
    should_cost_result,
    tco_result,
    value_at_stake_result,
    credibility_result,
    verification_result,
    information_result,
    shapley_result
):
    """
    Build the final supplier-level negotiation decision.

    This is a rule-based analytical prototype combining:
        - Nash bargaining
        - ZOPA
        - Timing / hold-up risk
        - Supplier risk
        - Should-cost
        - TCO
        - Value-at-stake
        - Credibility
        - Verification
        - Information asymmetry
        - Shapley negotiation levers

    It is not a prediction of supplier behaviour.
    """

    # ========================================================
    # BASE RESULT
    # ========================================================

    result = nash_result.copy()

    if "supplier_id" not in result.columns:
        raise ValueError(
            "Nash result must contain supplier_id."
        )

    # Remove accidental duplicate supplier rows

    result = (
        result
        .drop_duplicates(subset=["supplier_id"])
        .reset_index(drop=True)
    )

    # ========================================================
    # ZOPA
    # ========================================================

    if (
        zopa_result is not None
        and not zopa_result.empty
        and "supplier_id" in zopa_result.columns
    ):

        zopa_columns = [
            column
            for column in [
                "supplier_id",
                "zopa_exists",
                "zopa_low",
                "zopa_high",
            ]
            if column in zopa_result.columns
        ]

        zopa_summary = (
            zopa_result[zopa_columns]
            .drop_duplicates(subset=["supplier_id"])
            .reset_index(drop=True)
        )

        result = _merge_supplier_output(
            result,
            zopa_summary
        )

    # ========================================================
    # TIMING
    # ========================================================

    timing_summary = _prepare_supplier_summary(
        timing_result
    )

    if not timing_summary.empty:

        timing_columns = [
            column
            for column in [
                "supplier_id",
                "timing_risk",
                "timing_dependency",
            ]
            if column in timing_summary.columns
        ]

        result = _merge_supplier_output(
            result,
            timing_summary[timing_columns]
        )

    # ========================================================
    # SUPPLIER RISK
    # ========================================================

    supplier_risk_summary = _prepare_supplier_summary(
        supplier_risk_result
    )

    if not supplier_risk_summary.empty:

        result = _merge_supplier_output(
            result,
            supplier_risk_summary
        )

    # ========================================================
    # SHOULD-COST
    # ========================================================

    should_cost_summary = _prepare_supplier_summary(
        should_cost_result
    )

    if not should_cost_summary.empty:

        result = _merge_supplier_output(
            result,
            should_cost_summary
        )

    # ========================================================
    # TCO
    # ========================================================

    tco_summary = _prepare_supplier_summary(
        tco_result
    )

    if not tco_summary.empty:

        result = _merge_supplier_output(
            result,
            tco_summary
        )

    # ========================================================
    # VALUE AT STAKE
    # ========================================================

    value_summary = _prepare_supplier_summary(
        value_at_stake_result
    )

    if not value_summary.empty:

        result = _merge_supplier_output(
            result,
            value_summary
        )

    # ========================================================
    # CREDIBILITY
    # ========================================================

    credibility_summary = _prepare_information_asymmetry(
        credibility_result
    )

    if not credibility_summary.empty:

        result = _merge_supplier_output(
            result,
            credibility_summary[
                [
                    "supplier_id",
                    "average_signal_credibility",
                    "verified_signal_count",
                    "total_signal_count",
                    "verification_rate",
                ]
            ]
        )

    # ========================================================
    # VERIFICATION
    # ========================================================

    if (
        verification_result is not None
        and not verification_result.empty
        and "supplier_id" in verification_result.columns
    ):

        verification = verification_result.copy()

        if "verification_decision" in verification.columns:

            verification["_verified_flag"] = (
                verification[
                    "verification_decision"
                ]
                .astype(str)
                .eq("Verified for Analysis")
                .astype(int)
            )

            verification_summary = (
                verification
                .groupby("supplier_id")
                .agg(
                    verified_signal_count=(
                        "_verified_flag",
                        "sum"
                    ),
                    total_signal_count=(
                        "_verified_flag",
                        "size"
                    )
                )
                .reset_index()
            )

            verification_summary[
                "verification_rate"
            ] = verification_summary.apply(
                lambda row:
                (
                    row["verified_signal_count"]
                    /
                    row["total_signal_count"]
                )
                if row["total_signal_count"] > 0
                else None,
                axis=1
            )

            result = _merge_supplier_output(
                result,
                verification_summary
            )

    # ========================================================
    # INFORMATION ASYMMETRY
    #
    # IMPORTANT FIX
    #
    # These columns must be authoritative from the dedicated
    # information-asymmetry model.
    #
    # Supplier-risk output may already contain stale versions
    # of these columns. Remove them before merging the correct
    # information result.
    # ========================================================

    information_summary = _prepare_information_asymmetry(
        information_result
    )

    information_columns = [
        "average_signal_credibility",
        "verified_signal_count",
        "total_signal_count",
        "verification_rate",
        "information_asymmetry_score",
        "information_asymmetry_level",
        "information_asymmetry_action",
        "information_signal_count",
    ]

    for column in information_columns:

        if column in result.columns:

            result = result.drop(
                columns=[column]
            )

    if not information_summary.empty:

        result = _merge_supplier_output(
            result,
            information_summary
        )

    # ========================================================
    # SHAPLEY VALUE
    # ========================================================

    if (
        shapley_result is not None
        and not shapley_result.empty
    ):

        shapley = shapley_result.copy()

        if (
            "negotiation_lever" in shapley.columns
            and "contribution_percentage"
            in shapley.columns
        ):

            top_shapley = (
                shapley
                .sort_values(
                    by="contribution_percentage",
                    ascending=False
                )
                .iloc[0]
            )

            result[
                "top_negotiation_lever"
            ] = top_shapley[
                "negotiation_lever"
            ]

            result[
                "top_lever_contribution_percentage"
            ] = top_shapley[
                "contribution_percentage"
            ]

    # ========================================================
    # DEFAULT / MISSING VALUES
    # ========================================================

    if "zopa_exists" in result.columns:

        result["zopa_exists"] = (
            result["zopa_exists"]
            .fillna(False)
            .astype(bool)
        )

    if "timing_risk" in result.columns:

        result["timing_risk"] = (
            result["timing_risk"]
            .fillna("Unknown")
        )

    if "timing_dependency" in result.columns:

        result["timing_dependency"] = (
            pd.to_numeric(
                result["timing_dependency"],
                errors="coerce"
            )
            .fillna(0)
        )

    # ========================================================
    # INFORMATION ASYMMETRY DEFAULTS
    # ========================================================

    if "information_signal_count" not in result.columns:

        result["information_signal_count"] = 0

    result["information_signal_count"] = (
        pd.to_numeric(
            result["information_signal_count"],
            errors="coerce"
        )
        .fillna(0)
        .astype(int)
    )

    if "information_asymmetry_level" not in result.columns:

        result["information_asymmetry_level"] = (
            "No Evidence Available"
        )

    if "information_asymmetry_action" not in result.columns:

        result["information_asymmetry_action"] = (
            "Collect supplier evidence before relying on claims"
        )

    # ========================================================
    # TCO RANK / RISK
    # ========================================================

    if "tco_rank" not in result.columns:

        if "known_tco" in result.columns:

            result["tco_rank"] = (
                result["known_tco"]
                .rank(
                    method="dense",
                    ascending=True
                )
                .astype(int)
            )

    if "tco_risk" not in result.columns:

        result["tco_risk"] = "Unknown"

    # ========================================================
    # VALUE AT STAKE
    # ========================================================

    if "total_value_at_stake" not in result.columns:

        result["total_value_at_stake"] = 0

    if "value_at_stake_rank" not in result.columns:

        result["value_at_stake_rank"] = (
            result["total_value_at_stake"]
            .rank(
                method="dense",
                ascending=False
            )
            .astype(int)
        )

    if "value_at_stake_priority" not in result.columns:

        def value_priority(value):

            try:
                value = float(value)
            except (TypeError, ValueError):
                return "Low"

            if value >= 100000:
                return "High"

            if value >= 25000:
                return "Medium"

            return "Low"

        result["value_at_stake_priority"] = (
            result["total_value_at_stake"]
            .apply(value_priority)
        )

    # ========================================================
    # SUPPLIER RESERVATION / BUYER RESERVATION
    # ========================================================

    if "buyer_reservation_per_unit" not in result.columns:

        if "walk_away_price" in result.columns:

            result["buyer_reservation_per_unit"] = (
                result["walk_away_price"]
            )

    # ========================================================
    # NEGOTIATION TARGET
    # ========================================================

    def calculate_recommended_target(row):

        # ----------------------------------------------------
        # Buyer reservation / maximum acceptable price
        # ----------------------------------------------------

        reservation = row.get(
            "buyer_reservation_per_unit",
            pd.NA
        )

        try:

            if pd.notna(reservation):
                reservation = float(reservation)
            else:
                reservation = None

        except (TypeError, ValueError):

            reservation = None

        # ----------------------------------------------------
        # Nash bargaining price
        # ----------------------------------------------------

        nash_price = row.get(
            "nash_price_per_unit",
            pd.NA
        )

        try:

            if pd.notna(nash_price):
                nash_price = float(nash_price)
            else:
                nash_price = None

        except (TypeError, ValueError):

            nash_price = None

        # ----------------------------------------------------
        # Current supplier offer
        # ----------------------------------------------------

        current_offer = row.get(
            "current_offer_per_unit",
            pd.NA
        )

        if pd.isna(current_offer):

            current_offer = row.get(
                "initial_price",
                pd.NA
            )

        try:

            if pd.notna(current_offer):
                current_offer = float(current_offer)
            else:
                current_offer = None

        except (TypeError, ValueError):

            current_offer = None

        # ----------------------------------------------------
        # ZOPA status
        # ----------------------------------------------------

        zopa_exists = bool(
            row.get(
                "zopa_exists",
                False
            )
        )

        # ----------------------------------------------------
        # Buyer-side target logic
        #
        # For a buyer:
        #
        # Opening <= Target <= Walk-away
        #
        # Nash is used only when it is inside the buyer's
        # acceptable range.
        # ----------------------------------------------------

        if reservation is not None:

            # ------------------------------------------------
            # Case 1:
            # ZOPA exists and Nash price is within reservation.
            # ------------------------------------------------

            if (
                zopa_exists
                and nash_price is not None
                and nash_price <= reservation
            ):

                return nash_price

            # ------------------------------------------------
            # Case 2:
            # Current supplier offer is already below
            # reservation. Preserve that attractive offer.
            # ------------------------------------------------

            if (
                current_offer is not None
                and current_offer < reservation
            ):

                return current_offer

            # ------------------------------------------------
            # Case 3:
            # No acceptable ZOPA / supplier offer is above
            # reservation.
            #
            # Use a buyer target below the reservation boundary.
            # ------------------------------------------------

            return reservation * 0.98

        # ----------------------------------------------------
        # Fallback when reservation is unavailable
        # ----------------------------------------------------

        if nash_price is not None:

            return nash_price

        if current_offer is not None:

            return current_offer * 0.98

        return pd.NA

    result["recommended_target_price"] = (
        result.apply(
            calculate_recommended_target,
            axis=1
        )
    )

    # ========================================================
    # ENFORCE BUYER-SIDE TARGET BOUNDARY
    #
    # The recommended target must never exceed the buyer's
    # reservation / walk-away price.
    # ========================================================

    if "buyer_reservation_per_unit" in result.columns:

        result["recommended_target_price"] = result.apply(
            lambda row: (
                min(
                    float(row["recommended_target_price"]),
                    float(row["buyer_reservation_per_unit"])
                )
                if (
                    pd.notna(
                        row["recommended_target_price"]
                    )
                    and pd.notna(
                        row["buyer_reservation_per_unit"]
                    )
                )
                else row["recommended_target_price"]
            ),
            axis=1
        )

    # ========================================================
    # WALK-AWAY PRICE
    # ========================================================

    if "walk_away_price" not in result.columns:

        if "buyer_reservation_per_unit" in result.columns:

            result["walk_away_price"] = (
                result[
                    "buyer_reservation_per_unit"
                ]
            )

    # ========================================================
    # NEGOTIATION PRIORITY
    # ========================================================

    def calculate_priority(row):

        value_priority = str(
            row.get(
                "value_at_stake_priority",
                "Low"
            )
        )

        if value_priority == "High":
            return "High"

        if row.get(
            "zopa_exists",
            False
        ):
            return "High"

        if value_priority == "Medium":
            return "Medium"

        return "Low"

    result["negotiation_priority"] = (
        result.apply(
            calculate_priority,
            axis=1
        )
    )

    # ========================================================
    # OVERALL RISK
    # ========================================================

    if "overall_risk_level" not in result.columns:

        def calculate_overall_risk(row):

            risk_values = []

            for column in [
                "delivery_risk",
                "quotation_slippage_risk",
                "tco_risk",
            ]:

                value = row.get(
                    column,
                    None
                )

                if pd.notna(value):

                    risk_values.append(
                        str(value)
                    )

            if "High" in risk_values:
                return "High"

            if "Medium" in risk_values:
                return "Medium"

            if "Low" in risk_values:
                return "Low"

            return "Unknown"

        result["overall_risk_level"] = (
            result.apply(
                calculate_overall_risk,
                axis=1
            )
        )

    # ========================================================
    # NEGOTIATION RECOMMENDATION
    # ========================================================

    def recommendation(row):

        zopa_exists = bool(
            row.get(
                "zopa_exists",
                False
            )
        )

        overall_risk = str(
            row.get(
                "overall_risk_level",
                "Unknown"
            )
        )

        timing_risk = str(
            row.get(
                "timing_risk",
                "Unknown"
            )
        )

        information_level = str(
            row.get(
                "information_asymmetry_level",
                "No Evidence Available"
            )
        )

        delivery_risk = str(
            row.get(
                "delivery_risk",
                "Unknown"
            )
        )

        if not zopa_exists:

            return (
                "Review / Seek Better Terms or "
                "Alternative Supplier"
            )

        if overall_risk == "High":

            return (
                "Proceed with Caution - "
                "Mitigate Supplier Risk"
            )

        if timing_risk == "High Timing Risk":

            return (
                "Proceed with Caution - "
                "Mitigate Timing Risk"
            )

        if delivery_risk == "High":

            return (
                "Proceed with Negotiation - "
                "Mitigate Delivery Risk"
            )

        if (
            information_level
            == "High Information Asymmetry"
        ):

            return (
                "Proceed with Verification"
            )

        if (
            information_level
            == "Moderate Information Asymmetry"
        ):

            return (
                "Proceed with Negotiation - "
                "Verify Signals"
            )

        return (
            "Proceed with Negotiation - "
            "Protect Current Commercial Advantage"
        )

    result["negotiation_recommendation"] = (
        result.apply(
            recommendation,
            axis=1
        )
    )

    # ========================================================
    # RECOMMENDED BUYER ACTION
    # ========================================================

    def buyer_action(row):

        zopa_exists = bool(
            row.get(
                "zopa_exists",
                False
            )
        )

        target = row.get(
            "recommended_target_price",
            pd.NA
        )

        walk_away = row.get(
            "walk_away_price",
            pd.NA
        )

        information_level = str(
            row.get(
                "information_asymmetry_level",
                "No Evidence Available"
            )
        )

        delivery_risk = str(
            row.get(
                "delivery_risk",
                "Unknown"
            )
        )

        if (
            information_level
            == "High Information Asymmetry"
        ):

            return (
                "Request supporting evidence before "
                "using supplier claims in negotiation"
            )

        if not zopa_exists:

            return (
                "Compare BATNA and alternative suppliers "
                "before committing"
            )

        if delivery_risk == "High":

            return (
                "Negotiate delivery protection and "
                "service commitments alongside price"
            )

        if (
            pd.notna(target)
            and pd.notna(walk_away)
        ):

            return (
                f"Protect the current quotation and "
                f"negotiate non-price terms; target "
                f"₹{float(target):.2f}/unit and do not "
                f"exceed ₹{float(walk_away):.2f}/unit"
            )

        return (
            "Proceed with negotiation using the "
            "analytical target and BATNA"
        )

    result["recommended_buyer_action"] = (
        result.apply(
            buyer_action,
            axis=1
        )
    )

    # ========================================================
    # NEGOTIATION DECISION SCORE
    # ========================================================

    def decision_score(row):

        score = 50

        if bool(
            row.get(
                "zopa_exists",
                False
            )
        ):

            score += 20

        else:

            score -= 10

        priority = str(
            row.get(
                "negotiation_priority",
                "Low"
            )
        )

        if priority == "High":

            score += 10

        elif priority == "Medium":

            score += 5

        risk = str(
            row.get(
                "overall_risk_level",
                "Unknown"
            )
        )

        if risk == "Low":

            score += 10

        elif risk == "High":

            score -= 15

        information_level = str(
            row.get(
                "information_asymmetry_level",
                "No Evidence Available"
            )
        )

        if information_level == "Low Information Asymmetry":

            score += 5

        elif information_level == "High Information Asymmetry":

            score -= 10

        return max(
            0,
            min(
                100,
                score
            )
        )

    result["negotiation_decision_score"] = (
        result.apply(
            decision_score,
            axis=1
        )
    )

    # ========================================================
    # DECISION RANK
    # ========================================================

    result["decision_rank"] = (
        result[
            "negotiation_decision_score"
        ]
        .rank(
            method="dense",
            ascending=False
        )
        .astype(int)
    )

    # ========================================================
    # SORT FINAL RESULT
    # ========================================================

    result = (
        result
        .sort_values(
            by=[
                "decision_rank",
                "supplier_id"
            ],
            ascending=[
                True,
                True
            ]
        )
        .reset_index(drop=True)
    )

    return result