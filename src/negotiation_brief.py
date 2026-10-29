import pandas as pd


# ==========================================================
# NEGOTIATION BRIEF
# ==========================================================


def build_negotiation_brief(
    negotiation_case,
    final_decision_result,
    strategy_result,
    shapley_result
):
    """
    Build a manager-readable procurement negotiation brief.

    Uses:
        - Negotiation_Case
        - Stage 21 Final Negotiation Decision
        - Stage 22 Negotiation Strategy
        - Shapley negotiation levers

    Important:
        BATNA is taken from the authoritative BATNA
        calculation in outputs/batna_result.csv.

        BATNA cost is kept separate from TCO.

    Prototype / synthetic-data output only.
    """

    # =========================================================
    # CASE INFORMATION
    # =========================================================

    case = negotiation_case.iloc[0]

    case_id = case["case_id"]

    rfq_id = case["rfq_id"]

    material_id = case["material_id"]

    required_quantity = float(
        case["required_quantity"]
    )

    current_supplier_id = case["current_supplier_id"]

    current_offer = float(
        case["current_offer"]
    )

    required_delivery_days = float(
        case["required_delivery_days"]
    )

    # =========================================================
    # BATNA INFORMATION
    # =========================================================

    batna_supplier = None
    batna_supplier_id = None
    batna_cost = None

    # ---------------------------------------------------------
    # Read BATNA from the authoritative Stage 6 output
    # ---------------------------------------------------------

    batna_file = "outputs/batna_result.csv"

    batna_result = pd.read_csv(batna_file)

    if batna_result.empty:
        raise ValueError(
            "BATNA result file is empty: "
            "outputs/batna_result.csv"
        )

    required_batna_columns = [
        "batna_supplier_id",
        "batna_supplier_name",
        "batna_cost"
    ]

    missing_batna_columns = [
        column
        for column in required_batna_columns
        if column not in batna_result.columns
    ]

    if missing_batna_columns:
        raise ValueError(
            "BATNA result is missing required columns: "
            + ", ".join(missing_batna_columns)
        )

    batna_row = batna_result.iloc[0]

    batna_supplier_id = str(
        batna_row["batna_supplier_id"]
    )

    batna_supplier = str(
        batna_row["batna_supplier_name"]
    )

    batna_cost = float(
        pd.to_numeric(
            batna_row["batna_cost"],
            errors="raise"
        )
    )

    # ---------------------------------------------------------
    # BATNA is intentionally NOT derived from TCO.
    # ---------------------------------------------------------

    # =========================================================
    # BUYER RESERVATION VALUE
    # =========================================================

    reservation_value = None
    reservation_per_unit = None

    # ---------------------------------------------------------
    # Prefer authoritative Stage 21 reservation per-unit value
    # ---------------------------------------------------------

    if (
        "buyer_reservation_per_unit"
        in final_decision_result.columns
    ):

        reservation_candidates = pd.to_numeric(
            final_decision_result[
                "buyer_reservation_per_unit"
            ],
            errors="coerce"
        ).dropna()

        if not reservation_candidates.empty:

            reservation_per_unit = float(
                reservation_candidates.iloc[0]
            )

            reservation_value = (
                reservation_per_unit
                * required_quantity
            )

    # ---------------------------------------------------------
    # Otherwise use explicit reservation total value
    # ---------------------------------------------------------

    if (
        reservation_value is None
        and "buyer_reservation_value"
        in final_decision_result.columns
    ):

        reservation_candidates = pd.to_numeric(
            final_decision_result[
                "buyer_reservation_value"
            ],
            errors="coerce"
        ).dropna()

        if not reservation_candidates.empty:

            reservation_value = float(
                reservation_candidates.iloc[0]
            )

    # ---------------------------------------------------------
    # Legacy fallback
    # ---------------------------------------------------------

    if (
        reservation_value is None
        and "buyer_reservation"
        in final_decision_result.columns
    ):

        reservation_candidates = pd.to_numeric(
            final_decision_result[
                "buyer_reservation"
            ],
            errors="coerce"
        ).dropna()

        if not reservation_candidates.empty:

            reservation_value = float(
                reservation_candidates.iloc[0]
            )

    # ---------------------------------------------------------
    # Calculate reservation price per unit
    # ---------------------------------------------------------

    if (
        reservation_value is not None
        and required_quantity > 0
    ):

        reservation_per_unit = (
            reservation_value
            / required_quantity
        )

    # =========================================================
    # SHAPLEY / PRIMARY NEGOTIATION LEVERS
    # =========================================================

    shapley = shapley_result.copy()

    primary_levers = []

    if (
        "negotiation_lever" in shapley.columns
        and "shapley_value" in shapley.columns
    ):

        shapley["shapley_value"] = pd.to_numeric(
            shapley["shapley_value"],
            errors="coerce"
        )

        shapley_sorted = (
            shapley
            .sort_values(
                by="shapley_value",
                ascending=False
            )
        )

        primary_levers = (
            shapley_sorted[
                "negotiation_lever"
            ]
            .dropna()
            .head(2)
            .tolist()
        )

    elif (
        "lever" in shapley.columns
        and "shapley_value" in shapley.columns
    ):

        shapley["shapley_value"] = pd.to_numeric(
            shapley["shapley_value"],
            errors="coerce"
        )

        shapley_sorted = (
            shapley
            .sort_values(
                by="shapley_value",
                ascending=False
            )
        )

        primary_levers = (
            shapley_sorted[
                "lever"
            ]
            .dropna()
            .head(2)
            .tolist()
        )

    else:

        primary_levers = [
            "price_concession",
            "quantity_commitment"
        ]

    primary_levers_text = ", ".join(
        primary_levers
    )

    # =========================================================
    # CASE SUMMARY
    # =========================================================

    summary = pd.DataFrame([
        {
            "case_id": case_id,

            "rfq_id": rfq_id,

            "material_id": material_id,

            "required_quantity": required_quantity,

            "current_supplier_id": current_supplier_id,

            "current_offer_per_unit": current_offer,

            "required_delivery_days": required_delivery_days,

            # Authoritative BATNA
            "batna_supplier": batna_supplier,

            "batna_supplier_id": batna_supplier_id,

            "batna_total_cost": batna_cost,

            # Buyer reservation
            "buyer_reservation_value": reservation_value,

            "buyer_reservation_per_unit": reservation_per_unit,

            "primary_negotiation_levers":
                primary_levers_text
        }
    ])

    # =========================================================
    # SUPPLIER-SPECIFIC NEGOTIATION BRIEF
    # =========================================================

    desired_columns = [

        "supplier_id",

        "supplier_name",

        "zopa_exists",

        "zopa_low_per_unit",

        "zopa_high_per_unit",

        "current_offer_per_unit",

        "opening_price_per_unit",

        "target_price_per_unit",

        "walk_away_price_per_unit",

        "primary_negotiation_levers",

        "negotiation_posture",

        "signal_action",

        "timing_action",

        "negotiation_levers",

        "carrot_strategy",

        "stick_strategy",

        "risk_mitigation",

        "supplier_specific_strategy",

        "negotiation_strategy"
    ]

    available_columns = [
        column
        for column in desired_columns
        if column in strategy_result.columns
    ]

    supplier_strategy = strategy_result[
        available_columns
    ].copy()

    # =========================================================
    # ADD CASE INFORMATION
    # =========================================================

    supplier_strategy.insert(
        0,
        "case_id",
        case_id
    )

    supplier_strategy.insert(
        1,
        "rfq_id",
        rfq_id
    )

    supplier_strategy.insert(
        2,
        "material_id",
        material_id
    )

    supplier_strategy.insert(
        3,
        "required_quantity",
        required_quantity
    )

    supplier_strategy.insert(
        4,
        "required_delivery_days",
        required_delivery_days
    )

    # =========================================================
    # ADD BATNA / RESERVATION INFORMATION
    # =========================================================

    supplier_strategy["batna_supplier"] = (
        batna_supplier
    )

    supplier_strategy["batna_supplier_id"] = (
        batna_supplier_id
    )

    supplier_strategy["batna_total_cost"] = (
        batna_cost
    )

    supplier_strategy["buyer_reservation_value"] = (
        reservation_value
    )

    supplier_strategy["buyer_reservation_per_unit"] = (
        reservation_per_unit
    )

    # =========================================================
    # ADD PRIMARY LEVERS
    # =========================================================

    if (
        "primary_negotiation_levers"
        not in supplier_strategy.columns
    ):

        supplier_strategy[
            "primary_negotiation_levers"
        ] = primary_levers_text

    return summary, supplier_strategy


# ==========================================================
# STANDALONE TEST
# ==========================================================


if __name__ == "__main__":

    print("\n========================================")
    print(" PROCUREMENT NEGOTIATION BRIEF")
    print("========================================\n")

    input_file = (
        "data/input/Procurement_Negotiation_Input.xlsx"
    )

    negotiation_case = pd.read_excel(
        input_file,
        sheet_name="Negotiation_Case"
    )

    final_decision_result = pd.read_csv(
        "outputs/final_negotiation_decision.csv"
    )

    strategy_result = pd.read_csv(
        "outputs/negotiation_strategy.csv"
    )

    shapley_result = pd.read_csv(
        "outputs/shapley_analysis.csv"
    )

    # ------------------------------------------------------
    # BUILD BRIEF
    # ------------------------------------------------------

    summary, supplier_strategy = (
        build_negotiation_brief(
            negotiation_case,
            final_decision_result,
            strategy_result,
            shapley_result
        )
    )

    # ------------------------------------------------------
    # SAVE OUTPUTS
    # ------------------------------------------------------

    summary.to_csv(
        "outputs/negotiation_brief_summary.csv",
        index=False,
        encoding="utf-8-sig"
    )

    supplier_strategy.to_csv(
        "outputs/negotiation_brief.csv",
        index=False,
        encoding="utf-8-sig"
    )

    # ------------------------------------------------------
    # DISPLAY
    # ------------------------------------------------------

    print("\n===== CASE SUMMARY =====\n")

    print(
        summary.to_string(
            index=False
        )
    )

    print(
        "\n===== SUPPLIER NEGOTIATION BRIEFS =====\n"
    )

    print(
        supplier_strategy.to_string(
            index=False
        )
    )

    print("\n========================================")
    print(" NEGOTIATION BRIEF COMPLETED")
    print("========================================\n")