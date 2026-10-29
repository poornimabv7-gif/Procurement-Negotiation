import pandas as pd


def calculate_zopa(
    reservation_value,
    supplier_analysis,
    quotation_data,
    negotiation_case
):
    """
    Calculate prototype ZOPA.

    Buyer boundary:
        Buyer Reservation Value

    Supplier boundary:
        Current supplier quotation

    Note:
        The quotation is used as a prototype supplier-side
        boundary. It is not the supplier's true reservation price.
    """

    # ======================================================
    # Clean column names
    # ======================================================

    quotations = quotation_data.copy()
    suppliers = supplier_analysis.copy()
    case_data = negotiation_case.copy()

    quotations.columns = (
        quotations.columns
        .astype(str)
        .str.strip()
    )

    suppliers.columns = (
        suppliers.columns
        .astype(str)
        .str.strip()
    )

    case_data.columns = (
        case_data.columns
        .astype(str)
        .str.strip()
    )

    # ======================================================
    # Get negotiation case
    # ======================================================

    case = case_data.iloc[0]

    rfq_id = case.get("rfq_id")
    material_id = case.get("material_id")
    required_quantity = case.get("required_quantity")

    if pd.isna(rfq_id):
        raise ValueError(
            "negotiation_case.csv does not contain a valid rfq_id."
        )

    if pd.isna(material_id):
        raise ValueError(
            "negotiation_case.csv does not contain a valid material_id."
        )

    if pd.isna(required_quantity):
        raise ValueError(
            "negotiation_case.csv does not contain a valid required_quantity."
        )

    # ======================================================
    # Check quotation columns
    # ======================================================

    required_quotation_columns = [
        "rfq_id",
        "supplier_id",
        "material_id",
        "quantity",
        "initial_price"
    ]

    missing = [
        column
        for column in required_quotation_columns
        if column not in quotations.columns
    ]

    if missing:
        raise ValueError(
            "quotation_data.csv is missing columns: "
            + ", ".join(missing)
        )

    # ======================================================
    # Create supplier feasibility
    # ======================================================

    suppliers["feasible"] = (
        suppliers["capacity_feasible"].astype(bool)
        & suppliers["delivery_feasible"].astype(bool)
        & suppliers["qualified"].astype(bool)
    )

    feasible_supplier_ids = suppliers.loc[
        suppliers["feasible"],
        "supplier_id"
    ].tolist()

    # ======================================================
    # Filter quotation data
    # ======================================================

    quotations = quotations[
        quotations["rfq_id"] == rfq_id
    ].copy()

    quotations = quotations[
        quotations["material_id"] == material_id
    ].copy()

    quotations = quotations[
        quotations["quantity"] == required_quantity
    ].copy()

    quotations = quotations[
        quotations["supplier_id"].isin(
            feasible_supplier_ids
        )
    ].copy()

    # ======================================================
    # Calculate supplier quoted total
    # ======================================================

    quotations["supplier_quoted_total"] = (
        quotations["initial_price"]
        * required_quantity
    )

    # ======================================================
    # Buyer reservation value
    # ======================================================

    quotations["buyer_reservation_value"] = (
        float(reservation_value)
    )

    # ======================================================
    # Determine ZOPA
    # ======================================================

    quotations["zopa_exists"] = (
        quotations["supplier_quoted_total"]
        <= float(reservation_value)
    )

    # ======================================================
    # ZOPA boundaries
    # ======================================================

    quotations["zopa_low"] = quotations[
        "supplier_quoted_total"
    ]

    quotations["zopa_high"] = float(
        reservation_value
    )

    # No ZOPA → boundaries are not meaningful
    quotations.loc[
        quotations["zopa_exists"] == False,
        "zopa_low"
    ] = pd.NA

    quotations.loc[
        quotations["zopa_exists"] == False,
        "zopa_high"
    ] = pd.NA

    # ======================================================
    # Final result
    # ======================================================

    result = quotations[
        [
            "rfq_id",
            "supplier_id",
            "material_id",
            "quantity",
            "initial_price",
            "supplier_quoted_total",
            "buyer_reservation_value",
            "zopa_exists",
            "zopa_low",
            "zopa_high"
        ]
    ].copy()

    return result


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    print("\n========================================")
    print(" ZOPA ANALYSIS")
    print("========================================\n")

    supplier_data = pd.read_csv(
        "data/sample/supplier_data.csv"
    )

    purchase_history = pd.read_csv(
        "data/sample/purchase_history.csv"
    )

    quotation_data = pd.read_csv(
        "data/sample/quotation_data.csv"
    )

    negotiation_case = pd.read_csv(
        "data/sample/negotiation_case.csv"
    )

    market_cost_data = pd.read_csv(
        "data/sample/market_cost_data.csv"
    )

    # ------------------------------------------------------
    # Supplier analysis
    # ------------------------------------------------------

    from supplier_analysis import analyze_suppliers

    supplier_analysis = analyze_suppliers(
        supplier_data,
        purchase_history,
        quotation_data,
        negotiation_case
    )

    # ------------------------------------------------------
    # Outside options
    # ------------------------------------------------------

    from outside_option import calculate_outside_options

    required_quantity = negotiation_case.iloc[0][
        "required_quantity"
    ]

    outside_options = calculate_outside_options(
        supplier_analysis,
        market_cost_data,
        required_quantity
    )

    # ------------------------------------------------------
    # BATNA
    # ------------------------------------------------------

    from batna import calculate_batna

    batna = calculate_batna(
        outside_options
    )

    # ------------------------------------------------------
    # Reservation value
    # ------------------------------------------------------

    from reservation_value import calculate_reservation_value

    reservation_value = calculate_reservation_value(
        batna
    )

    # ------------------------------------------------------
    # ZOPA
    # ------------------------------------------------------

    result = calculate_zopa(
        reservation_value,
        supplier_analysis,
        quotation_data,
        negotiation_case
    )

    print(result.to_string(index=False))

    print("\n========================================")
    print(" ZOPA ANALYSIS COMPLETED")
    print("========================================\n")