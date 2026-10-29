import pandas as pd


def analyze_suppliers(
    supplier_data,
    purchase_history,
    quotation_data,
    negotiation_case
):
    """
    Analyze suppliers for the current procurement negotiation case.

    Inputs:
        supplier_data       -> Supplier master information
        purchase_history   -> Historical purchasing information
        quotation_data     -> Current supplier quotations
        negotiation_case   -> Current negotiation case

    Returns:
        DataFrame containing supplier-level analysis.
    """

    # ============================================================
    # COPY INPUT DATA
    # ============================================================

    supplier_data = supplier_data.copy()
    purchase_history = purchase_history.copy()
    quotation_data = quotation_data.copy()
    negotiation_case = negotiation_case.copy()

    # ============================================================
    # CLEAN COLUMN NAMES
    # ============================================================

    supplier_data.columns = (
        supplier_data.columns
        .astype(str)
        .str.strip()
        .str.lower()
    )

    purchase_history.columns = (
        purchase_history.columns
        .astype(str)
        .str.strip()
        .str.lower()
    )

    quotation_data.columns = (
        quotation_data.columns
        .astype(str)
        .str.strip()
        .str.lower()
    )

    negotiation_case.columns = (
        negotiation_case.columns
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # ============================================================
    # VALIDATE QUOTATION DATA
    # ============================================================

    required_quotation_columns = [
        "rfq_id",
        "supplier_id",
        "material_id",
        "quantity",
        "initial_price",
        "delivery_days",
        "moq",
        "payment_terms_days"
    ]

    missing_columns = [
        column
        for column in required_quotation_columns
        if column not in quotation_data.columns
    ]

    if missing_columns:
        raise ValueError(
            "quotation_data is missing columns: "
            f"{missing_columns}\n"
            f"Available columns: {list(quotation_data.columns)}"
        )

    # ============================================================
    # VALIDATE SUPPLIER DATA
    # ============================================================

    required_supplier_columns = [
        "supplier_id",
        "supplier_name",
        "material_category",
        "capacity",
        "quality_score",
        "reliability_score",
        "lead_time_days",
        "qualification_status"
    ]

    missing_columns = [
        column
        for column in required_supplier_columns
        if column not in supplier_data.columns
    ]

    if missing_columns:
        raise ValueError(
            "supplier_data is missing columns: "
            f"{missing_columns}\n"
            f"Available columns: {list(supplier_data.columns)}"
        )

    # ============================================================
    # VALIDATE NEGOTIATION CASE
    # ============================================================

    required_case_columns = [
        "rfq_id",
        "material_id",
        "required_quantity",
        "current_supplier_id",
        "required_delivery_days"
    ]

    missing_columns = [
        column
        for column in required_case_columns
        if column not in negotiation_case.columns
    ]

    if missing_columns:
        raise ValueError(
            "negotiation_case is missing columns: "
            f"{missing_columns}\n"
            f"Available columns: {list(negotiation_case.columns)}"
        )

    # ============================================================
    # CURRENT NEGOTIATION CASE
    # ============================================================

    case = negotiation_case.iloc[0]

    rfq_id = str(case["rfq_id"]).strip()

    material_id = str(case["material_id"]).strip()

    required_quantity = pd.to_numeric(
        case["required_quantity"],
        errors="coerce"
    )

    current_supplier_id = str(
        case["current_supplier_id"]
    ).strip()

    required_delivery_days = pd.to_numeric(
        case["required_delivery_days"],
        errors="coerce"
    )

    # ============================================================
    # NORMALIZE KEY COLUMNS
    # ============================================================

    quotation_data["rfq_id"] = (
        quotation_data["rfq_id"]
        .astype(str)
        .str.strip()
    )

    quotation_data["material_id"] = (
        quotation_data["material_id"]
        .astype(str)
        .str.strip()
    )

    quotation_data["supplier_id"] = (
        quotation_data["supplier_id"]
        .astype(str)
        .str.strip()
    )

    supplier_data["supplier_id"] = (
        supplier_data["supplier_id"]
        .astype(str)
        .str.strip()
    )

    purchase_history["supplier_id"] = (
        purchase_history["supplier_id"]
        .astype(str)
        .str.strip()
    )

    purchase_history["material_id"] = (
        purchase_history["material_id"]
        .astype(str)
        .str.strip()
    )

    # ============================================================
    # FILTER CURRENT RFQ
    # ============================================================

    current_quotes = quotation_data[
        (quotation_data["rfq_id"] == rfq_id)
        &
        (quotation_data["material_id"] == material_id)
    ].copy()

    if current_quotes.empty:
        raise ValueError(
            f"No quotations found for RFQ={rfq_id}, "
            f"Material={material_id}"
        )

    # ============================================================
    # MERGE QUOTATIONS WITH SUPPLIER MASTER
    # ============================================================

    result = current_quotes.merge(
        supplier_data,
        on="supplier_id",
        how="left"
    )

    # ============================================================
    # HISTORICAL PURCHASE PRICE
    # ============================================================

    historical_prices = (
        purchase_history[
            purchase_history["material_id"] == material_id
        ]
        .groupby("supplier_id")["purchase_price"]
        .mean()
        .reset_index()
        .rename(
            columns={
                "purchase_price":
                    "historical_average_price"
            }
        )
    )

    result = result.merge(
        historical_prices,
        on="supplier_id",
        how="left"
    )

    # ============================================================
    # NUMERIC CONVERSIONS
    # ============================================================

    result["initial_price"] = pd.to_numeric(
        result["initial_price"],
        errors="coerce"
    )

    result["delivery_days"] = pd.to_numeric(
        result["delivery_days"],
        errors="coerce"
    )

    result["lead_time_days"] = pd.to_numeric(
        result["lead_time_days"],
        errors="coerce"
    )

    result["capacity"] = pd.to_numeric(
        result["capacity"],
        errors="coerce"
    )

    result["quality_score"] = pd.to_numeric(
        result["quality_score"],
        errors="coerce"
    )

    result["reliability_score"] = pd.to_numeric(
        result["reliability_score"],
        errors="coerce"
    )

    result["historical_average_price"] = pd.to_numeric(
        result["historical_average_price"],
        errors="coerce"
    )

    # ============================================================
    # CAPACITY FEASIBILITY
    # ============================================================

    result["capacity_feasible"] = (
        result["capacity"] >= required_quantity
    )

    # ============================================================
    # DELIVERY FEASIBILITY
    # ============================================================

    result["delivery_feasible"] = (
        result["delivery_days"]
        <=
        required_delivery_days
    )

    # ============================================================
    # QUALIFICATION
    # ============================================================

    result["qualified"] = (
        result["qualification_status"]
        .astype(str)
        .str.strip()
        .str.lower()
        .eq("qualified")
    )

    # ============================================================
    # PRICE VS HISTORICAL
    # ============================================================

    result["price_vs_historical"] = (
        result["initial_price"]
        -
        result["historical_average_price"]
    )

    # ============================================================
    # CURRENT SUPPLIER FLAG
    # ============================================================

    result["is_current_supplier"] = (
        result["supplier_id"]
        .astype(str)
        .str.strip()
        ==
        current_supplier_id
    )

    # ============================================================
    # SUPPLIER SCORE
    # ============================================================

    # Quality score: 0–1
    quality_score = (
        result["quality_score"] / 100
    ).fillna(0)

    # Reliability score: 0–1
    reliability_score = (
        result["reliability_score"] / 100
    ).fillna(0)

    # Capacity score
    result["capacity_score"] = (
        result["capacity"]
        /
        required_quantity
    ).clip(upper=1).fillna(0)

    # Delivery score
    result["delivery_score"] = (
        required_delivery_days
        /
        result["delivery_days"]
    ).clip(upper=1).fillna(0)

    # Overall supplier score
    result["supplier_score"] = (
        0.30 * quality_score
        +
        0.25 * reliability_score
        +
        0.20 * result["capacity_score"]
        +
        0.15 * result["delivery_score"]
        +
        0.10 * result["qualified"].astype(int)
    )

    # ============================================================
    # OUTPUT COLUMNS
    # ============================================================

    output_columns = [
        "supplier_id",
        "supplier_name",
        "material_category",
        "initial_price",
        "historical_average_price",
        "price_vs_historical",
        "delivery_days",
        "lead_time_days",
        "capacity",
        "quality_score",
        "reliability_score",
        "qualification_status",
        "capacity_feasible",
        "delivery_feasible",
        "qualified",
        "is_current_supplier",
        "supplier_score"
    ]

    result = result[
        [
            column
            for column in output_columns
            if column in result.columns
        ]
    ]

    # ============================================================
    # SORT BY SUPPLIER SCORE
    # ============================================================

    result = result.sort_values(
        by="supplier_score",
        ascending=False
    ).reset_index(drop=True)

    # ============================================================
    # DISPLAY
    # ============================================================

    print()
    print("===== SUPPLIER ANALYSIS =====")
    print()

    print(
        result.to_string(index=False)
    )

    print()
    print(
        "Current Supplier:",
        current_supplier_id
    )

    print(
        "Required Quantity:",
        int(required_quantity)
    )

    print(
        "Required Delivery Days:",
        int(required_delivery_days)
    )

    return result


# ============================================================
# STANDALONE TEST
# ============================================================

if __name__ == "__main__":

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

    analyze_suppliers(
        supplier_data,
        purchase_history,
        quotation_data,
        negotiation_case
    )