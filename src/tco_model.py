
import pandas as pd

DEFAULT_FINANCING_RATE = 0.0


# ---------------------------------------------------------
# 1. DATA PREPARATION
# ---------------------------------------------------------

def normalize_columns(df):
    """Normalize column names for consistent matching."""
    result = df.copy()
    result.columns = [
        str(column).strip().lower().replace(" ", "_")
        for column in result.columns
    ]
    return result


def get_latest_transport_cost(market_cost_data):
    """Get the latest transport cost for each material."""
    df = normalize_columns(market_cost_data)

    required = {"material_id", "date", "transport_cost"}
    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Market_Cost_Data is missing columns: {sorted(missing)}"
        )

    df["material_id"] = df["material_id"].astype(str).str.strip()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["transport_cost"] = pd.to_numeric(
        df["transport_cost"], errors="coerce"
    )

    df = df.dropna(
        subset=["material_id", "date", "transport_cost"]
    )

    df = df.sort_values(["material_id", "date"])

    latest = (
        df.groupby("material_id", as_index=False)
        .tail(1)
        .rename(
            columns={
                "date": "transport_cost_date",
                "transport_cost": "transport_unit_cost",
            }
        )
    )

    return latest[
        [
            "material_id",
            "transport_cost_date",
            "transport_unit_cost",
        ]
    ]


def calculate_financing_cost(
    purchase_cost,
    payment_terms_days,
    annual_financing_rate=DEFAULT_FINANCING_RATE,
):
    """Calculate financing cost using the configured annual rate."""
    purchase_cost = pd.to_numeric(
        pd.Series([purchase_cost]), errors="coerce"
    ).iloc[0]

    payment_terms_days = pd.to_numeric(
        pd.Series([payment_terms_days]), errors="coerce"
    ).iloc[0]

    if pd.isna(purchase_cost):
        return 0.0

    if pd.isna(payment_terms_days):
        payment_terms_days = 0

    return (
        float(purchase_cost)
        * float(annual_financing_rate)
        * float(payment_terms_days)
        / 365
    )


# ---------------------------------------------------------
# 2. DELIVERY RISK
# ---------------------------------------------------------

def derive_delivery_risk(on_time_delivery_pct):
    """
    Derive a prototype delivery-risk category from on-time
    delivery percentage.

    Thresholds:
        Below 90%       -> High risk if <= 50%, otherwise Medium
        90% and above   -> Low risk

    These are illustrative rules and should be calibrated
    using actual procurement data.
    """
    value = pd.to_numeric(
        pd.Series([on_time_delivery_pct]), errors="coerce"
    ).iloc[0]

    if pd.isna(value):
        return None

    if value < 0 or value > 100:
        return None

    if value <= 50:
        return "High"

    if value < 90:
        return "Medium"

    return "Low"


# ---------------------------------------------------------
# 3. TCO RISK CLASSIFICATION
# ---------------------------------------------------------

def classify_tco_risk(
    quality_score,
    reliability_score,
    delivery_risk=None,
):
    """
    Classify qualitative supplier risk.

    Quality:
        Below 85 -> 2 risk points
        Below 90 -> 1 risk point

    Reliability:
        Below 85 -> 2 risk points
        Below 90 -> 1 risk point

    Delivery:
        High   -> 2 risk points
        Medium -> 1 risk point
        Low    -> 0 risk points

    Final classification:
        4+ points -> High
        2-3 points -> Medium
        0-1 points -> Low

    Returns Unknown when no valid risk indicators exist.
    These rules are a prototype, not calibrated probabilities.
    """
    risk_points = 0
    evidence_count = 0

    quality = pd.to_numeric(
        pd.Series([quality_score]), errors="coerce"
    ).iloc[0]

    reliability = pd.to_numeric(
        pd.Series([reliability_score]), errors="coerce"
    ).iloc[0]

    if pd.notna(quality):
        evidence_count += 1

        if quality < 85:
            risk_points += 2
        elif quality < 90:
            risk_points += 1

    if pd.notna(reliability):
        evidence_count += 1

        if reliability < 85:
            risk_points += 2
        elif reliability < 90:
            risk_points += 1

    if delivery_risk is not None and pd.notna(delivery_risk):
        risk = str(delivery_risk).strip().lower()

        if risk in {"high", "medium", "low"}:
            evidence_count += 1

            if risk == "high":
                risk_points += 2
            elif risk == "medium":
                risk_points += 1

    if evidence_count == 0:
        return "Unknown"

    if risk_points >= 4:
        return "High"

    if risk_points >= 2:
        return "Medium"

    return "Low"


# ---------------------------------------------------------
# 4. PREPARE SUPPLIER DATA
# ---------------------------------------------------------

def prepare_supplier_data(supplier_data):
    """Prepare supplier scores and standardize column names."""
    if supplier_data is None:
        return None

    df = normalize_columns(supplier_data)

    aliases = {
        "supplierid": "supplier_id",
        "supplier": "supplier_name",
        "quality": "quality_score",
        "reliability": "reliability_score",
        "lead_time": "lead_time_days",
    }

    for old_name, new_name in aliases.items():
        if old_name in df.columns and new_name not in df.columns:
            df = df.rename(columns={old_name: new_name})

    if "supplier_id" not in df.columns:
        raise ValueError(
            "Supplier_Data must contain a supplier_id column."
        )

    df["supplier_id"] = df["supplier_id"].astype(str).str.strip()

    available_columns = [
        column
        for column in [
            "supplier_id",
            "supplier_name",
            "quality_score",
            "reliability_score",
            "lead_time_days",
        ]
        if column in df.columns
    ]

    df = df[available_columns].drop_duplicates(
        subset=["supplier_id"]
    )

    for column in ["quality_score", "reliability_score", "lead_time_days"]:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column], errors="coerce"
            )

    return df


# ---------------------------------------------------------
# 5. PREPARE DELIVERY DATA
# ---------------------------------------------------------

def prepare_delivery_data(delivery_performance):
    """Prepare delivery-risk data for supplier-level matching."""
    if delivery_performance is None:
        return None

    df = normalize_columns(delivery_performance)

    aliases = {
        "supplierid": "supplier_id",
        "deliveryrisk": "delivery_risk",
        "ontimedeliverypct": "on_time_delivery_pct",
        "on_time_delivery_percentage": "on_time_delivery_pct",
        "on_time_percentage": "on_time_delivery_pct",
    }

    for old_name, new_name in aliases.items():
        if old_name in df.columns and new_name not in df.columns:
            df = df.rename(columns={old_name: new_name})

    if "supplier_id" not in df.columns:
        raise ValueError(
            "Delivery data must contain a supplier_id column. "
            f"Available columns: {df.columns.tolist()}"
        )

    df["supplier_id"] = df["supplier_id"].astype(str).str.strip()

    if "on_time_delivery_pct" in df.columns:
        df["on_time_delivery_pct"] = pd.to_numeric(
            df["on_time_delivery_pct"], errors="coerce"
        )

    selected_columns = [
        column
        for column in [
            "supplier_id",
            "delivery_risk",
            "on_time_delivery_pct",
        ]
        if column in df.columns
    ]

    df = df[selected_columns].copy()

    if df.empty:
        return df

    # If multiple delivery records exist for a supplier,
    # aggregate the on-time percentage rather than selecting
    # an arbitrary record.
    aggregation = {}

    if "on_time_delivery_pct" in df.columns:
        aggregation["on_time_delivery_pct"] = "mean"

    if "delivery_risk" in df.columns:
        aggregation["delivery_risk"] = (
            lambda values: next(
                (
                    str(value).strip().title()
                    for value in values
                    if pd.notna(value)
                    and str(value).strip().lower()
                    in {"high", "medium", "low"}
                ),
                None,
            )
        )

    if aggregation:
        df = df.groupby(
            "supplier_id", as_index=False
        ).agg(aggregation)

    # Derive risk from on-time delivery when risk is missing
    # or is not a recognized category.
    if "delivery_risk" not in df.columns:
        df["delivery_risk"] = None

    for index in df.index:
        current_risk = df.at[index, "delivery_risk"]

        if (
            pd.isna(current_risk)
            or str(current_risk).strip().lower()
            not in {"high", "medium", "low"}
        ):
            percentage = (
                df.at[index, "on_time_delivery_pct"]
                if "on_time_delivery_pct" in df.columns
                else None
            )

            df.at[index, "delivery_risk"] = derive_delivery_risk(
                percentage
            )

    return df


# ---------------------------------------------------------
# 6. CALCULATE TCO
# ---------------------------------------------------------

def calculate_tco(
    quotation_data,
    market_cost_data,
    supplier_data=None,
    delivery_performance=None,
    annual_financing_rate=DEFAULT_FINANCING_RATE,
):
    """Calculate supplier TCO and qualitative supplier risk."""
    quote = normalize_columns(quotation_data)

    required = {
        "supplier_id",
        "material_id",
        "quantity",
        "initial_price",
        "payment_terms_days",
    }

    missing = required - set(quote.columns)

    if missing:
        raise ValueError(
            f"Quotation_Data is missing columns: {sorted(missing)}"
        )

    quote["supplier_id"] = (
        quote["supplier_id"].astype(str).str.strip()
    )

    quote["material_id"] = (
        quote["material_id"].astype(str).str.strip()
    )

    for column in [
        "quantity",
        "initial_price",
        "payment_terms_days",
    ]:
        quote[column] = pd.to_numeric(
            quote[column], errors="coerce"
        )

    # Add latest transport cost.
    transport = get_latest_transport_cost(market_cost_data)

    quote = quote.merge(
        transport,
        on="material_id",
        how="left",
    )

    # Calculate known cost components.
    quote["purchase_cost"] = (
        quote["quantity"] * quote["initial_price"]
    )

    quote["transport_cost"] = (
        quote["quantity"]
        * quote["transport_unit_cost"].fillna(0)
    )

    quote["financing_cost"] = quote.apply(
        lambda row: calculate_financing_cost(
            row["purchase_cost"],
            row["payment_terms_days"],
            annual_financing_rate,
        ),
        axis=1,
    )

    quote["known_tco"] = (
        quote["purchase_cost"]
        + quote["transport_cost"]
        + quote["financing_cost"]
    )

    quote["tco_per_unit"] = (
        quote["known_tco"]
        / quote["quantity"].where(quote["quantity"] != 0)
    )

    # Merge supplier information.
    supplier_info = prepare_supplier_data(supplier_data)

    if supplier_info is not None:
        quote = quote.drop(
            columns=[
                column
                for column in [
                    "supplier_name",
                    "quality_score",
                    "reliability_score",
                    "lead_time_days",
                ]
                if column in quote.columns
            ],
            errors="ignore",
        )

        quote = quote.merge(
            supplier_info,
            on="supplier_id",
            how="left",
        )

    # Merge delivery information.
    delivery_info = prepare_delivery_data(delivery_performance)

    if delivery_info is not None:
        quote = quote.drop(
            columns=[
                column
                for column in [
                    "delivery_risk",
                    "on_time_delivery_pct",
                ]
                if column in quote.columns
            ],
            errors="ignore",
        )

        quote = quote.merge(
            delivery_info,
            on="supplier_id",
            how="left",
        )

    # Ensure risk input columns exist.
    for column in [
        "quality_score",
        "reliability_score",
        "delivery_risk",
        "on_time_delivery_pct",
    ]:
        if column not in quote.columns:
            quote[column] = None

    # Derive delivery risk when the direct risk value is missing.
    for index in quote.index:
        risk = quote.at[index, "delivery_risk"]

        if (
            pd.isna(risk)
            or str(risk).strip().lower()
            not in {"high", "medium", "low"}
        ):
            quote.at[index, "delivery_risk"] = derive_delivery_risk(
                quote.at[index, "on_time_delivery_pct"]
            )

    # Calculate TCO risk classification.
    quote["tco_risk"] = [
        classify_tco_risk(quality, reliability, delivery)
        for quality, reliability, delivery in zip(
            quote["quality_score"],
            quote["reliability_score"],
            quote["delivery_risk"],
        )
    ]

    # Generate recommendations.
    def recommendation(row):
        risk = row["tco_risk"]

        if risk == "High":
            return (
                "Investigate supplier risk before award; "
                "low cost may be offset by risk."
            )

        if risk == "Medium":
            return (
                "Evaluate cost alongside delivery and "
                "supplier performance."
            )

        if risk == "Unknown":
            return (
                "Collect supplier risk information before "
                "making a risk-based award decision."
            )

        return (
            "Competitive known TCO with relatively low modeled risk."
        )

    quote["tco_recommendation"] = quote.apply(
        recommendation, axis=1
    )

    # Rank by total known TCO, with 1 representing the lowest cost.
    quote["tco_rank"] = (
        quote["known_tco"]
        .rank(method="dense", ascending=True)
        .astype("Int64")
    )

    preferred_columns = [
        "rfq_id",
        "supplier_id",
        "supplier_name",
        "material_id",
        "quantity",
        "initial_price",
        "payment_terms_days",
        "transport_unit_cost",
        "purchase_cost",
        "transport_cost",
        "financing_cost",
        "known_tco",
        "tco_per_unit",
        "quality_score",
        "reliability_score",
        "delivery_risk",
        "on_time_delivery_pct",
        "tco_risk",
        "tco_rank",
        "tco_recommendation",
    ]

    return quote[
        [
            column
            for column in preferred_columns
            if column in quote.columns
        ]
    ].copy()


# ---------------------------------------------------------
# 7. BUILD SUPPLIER-LEVEL TCO SUMMARY
# ---------------------------------------------------------

def build_tco_summary(tco_result):
    """Create a supplier-level TCO comparison."""
    required = {
        "supplier_id",
        "known_tco",
        "tco_per_unit",
    }

    missing = required - set(tco_result.columns)

    if missing:
        raise ValueError(
            f"TCO result is missing columns: {sorted(missing)}"
        )

    aggregations = {
        "total_known_tco": ("known_tco", "sum"),
        "average_tco_per_unit": ("tco_per_unit", "mean"),
        "quotation_count": ("supplier_id", "count"),
    }

    if "tco_risk" in tco_result.columns:
        aggregations["tco_risk"] = (
            "tco_risk",
            lambda values: (
                "High" if "High" in set(values)
                else "Medium" if "Medium" in set(values)
                else "Low" if "Low" in set(values)
                else "Unknown"
            ),
        )

    summary = (
        tco_result.groupby("supplier_id", as_index=False)
        .agg(**aggregations)
    )

    summary["tco_rank"] = (
        summary["total_known_tco"]
        .rank(method="dense", ascending=True)
        .astype("Int64")
    )

    summary["tco_position"] = summary["tco_rank"].apply(
        lambda rank: "Lowest TCO" if rank == 1 else "Higher TCO"
    )

    return summary


# ---------------------------------------------------------
# 8. COMPLETE TCO PIPELINE
# ---------------------------------------------------------

def calculate_complete_tco(
    quotation_data,
    market_cost_data,
    supplier_data=None,
    delivery_performance=None,
    annual_financing_rate=DEFAULT_FINANCING_RATE,
):
    """Return detailed TCO results and supplier summary."""
    detail = calculate_tco(
        quotation_data=quotation_data,
        market_cost_data=market_cost_data,
        supplier_data=supplier_data,
        delivery_performance=delivery_performance,
        annual_financing_rate=annual_financing_rate,
    )

    summary = build_tco_summary(detail)

    return detail, summary
