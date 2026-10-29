import pandas as pd


# ============================================================
# FIND SUPPLIER ID COLUMN
# ============================================================

def find_supplier_column(df):
    possible_columns = [
        "supplier_id",
        "supplier",
        "supplier_code",
        "vendor_id",
        "vendor"
    ]

    normalized = {
        str(column).strip().lower(): column
        for column in df.columns
    }

    for column in possible_columns:
        if column in normalized:
            return normalized[column]

    # Fallback: search for a column containing supplier/vendor
    for column in df.columns:
        column_name = str(column).strip().lower()

        if "supplier" in column_name or "vendor" in column_name:
            return column

    raise ValueError(
        "Supplier_Timeline must contain a supplier column."
    )


# ============================================================
# FIND DATE COLUMN
# ============================================================

def find_date_column(df):
    # First try common names
    possible_columns = [
        "event_date",
        "date",
        "timeline_date",
        "activity_date",
        "transaction_date",
        "event_time",
        "event_datetime",
        "activity_time",
        "activity_datetime",
        "timestamp",
        "datetime",
        "created_date",
        "created_at",
        "updated_date",
        "updated_at"
    ]

    normalized = {
        str(column).strip().lower(): column
        for column in df.columns
    }

    for column in possible_columns:
        if column in normalized:
            return normalized[column]

    # --------------------------------------------------------
    # Automatic detection
    # --------------------------------------------------------

    best_column = None
    best_valid_ratio = 0

    for column in df.columns:

        # Do not try supplier ID as date
        column_name = str(column).strip().lower()

        if (
            "supplier" in column_name
            or "vendor" in column_name
            or "id" == column_name
        ):
            continue

        converted = pd.to_datetime(
            df[column],
            errors="coerce"
        )

        valid_ratio = converted.notna().mean()

        if valid_ratio > best_valid_ratio:
            best_valid_ratio = valid_ratio
            best_column = column

    # Require at least 50% of values to look like dates
    if best_column is not None and best_valid_ratio >= 0.50:
        return best_column

    raise ValueError(
        "Could not automatically identify the date column "
        "in Supplier_Timeline.\n\n"
        "Available columns are:\n"
        + "\n".join(
            f"- {column}"
            for column in df.columns
        )
    )


# ============================================================
# ANALYZE SUPPLIER TIMELINE
# ============================================================

def analyze_supplier_timeline(supplier_timeline):

    result = supplier_timeline.copy()

    # Clean column names
    result.columns = [
        str(column).strip()
        for column in result.columns
    ]

    # Find supplier column
    supplier_column = find_supplier_column(result)

    # Find date column automatically
    date_column = find_date_column(result)

    print()
    print("Supplier Timeline Detection:")
    print(f"Supplier Column : {supplier_column}")
    print(f"Date Column     : {date_column}")

    # Standardize supplier ID
    if supplier_column != "supplier_id":
        result["supplier_id"] = result[supplier_column]
    else:
        result["supplier_id"] = result[supplier_column]

    # Convert date
    result["timeline_event_date"] = pd.to_datetime(
        result[date_column],
        errors="coerce"
    )

    # Remove rows where supplier/date cannot be identified
    result = result.dropna(
        subset=[
            "supplier_id",
            "timeline_event_date"
        ]
    ).copy()

    # Sort
    result = result.sort_values(
        [
            "supplier_id",
            "timeline_event_date"
        ]
    ).reset_index(drop=True)

    # Previous event
    result["previous_event_date"] = (
        result
        .groupby("supplier_id")["timeline_event_date"]
        .shift(1)
    )

    # Days between events
    result["days_since_previous_event"] = (
        result["timeline_event_date"]
        - result["previous_event_date"]
    ).dt.days

    # Event sequence
    result["event_sequence"] = (
        result
        .groupby("supplier_id")
        .cumcount()
        + 1
    )

    return result


# ============================================================
# CALCULATE SUPPLIER TIMELINE KPIs
# ============================================================

def calculate_supplier_timeline_kpis(supplier_timeline):

    analysis = analyze_supplier_timeline(
        supplier_timeline
    )

    # Aggregate supplier-level timeline metrics
    kpis = (
        analysis
        .groupby("supplier_id")
        .agg(
            total_timeline_events=(
                "supplier_id",
                "count"
            ),

            first_activity_date=(
                "timeline_event_date",
                "min"
            ),

            latest_activity_date=(
                "timeline_event_date",
                "max"
            ),

            average_days_between_events=(
                "days_since_previous_event",
                "mean"
            ),

            maximum_days_between_events=(
                "days_since_previous_event",
                "max"
            )
        )
        .reset_index()
    )

    # --------------------------------------------------------
    # Relationship duration
    # --------------------------------------------------------

    kpis["relationship_duration_days"] = (
        kpis["latest_activity_date"]
        - kpis["first_activity_date"]
    ).dt.days

    # --------------------------------------------------------
    # Activity frequency
    # --------------------------------------------------------

    def classify_activity_frequency(row):

        duration = row[
            "relationship_duration_days"
        ]

        events = row[
            "total_timeline_events"
        ]

        if pd.isna(duration):
            return "Unknown"

        if duration <= 0:
            return "Single / New Activity"

        events_per_year = (
            events / duration * 365
        )

        if events_per_year >= 12:
            return "High Activity"

        if events_per_year >= 4:
            return "Medium Activity"

        return "Low Activity"

    kpis["activity_frequency"] = kpis.apply(
        classify_activity_frequency,
        axis=1
    )

    # --------------------------------------------------------
    # Timeline dependency
    # --------------------------------------------------------

    def classify_timeline_dependency(row):

        average_gap = row[
            "average_days_between_events"
        ]

        if pd.isna(average_gap):
            return "Unknown"

        if average_gap <= 30:
            return "High"

        if average_gap <= 90:
            return "Medium"

        return "Low"

    kpis["timeline_dependency"] = kpis.apply(
        classify_timeline_dependency,
        axis=1
    )

    # --------------------------------------------------------
    # Timeline risk
    # --------------------------------------------------------

    def classify_timeline_risk(row):

        dependency = row[
            "timeline_dependency"
        ]

        frequency = row[
            "activity_frequency"
        ]

        if dependency == "High":
            return "High"

        if dependency == "Medium":
            return "Medium"

        if frequency == "High Activity":
            return "Medium"

        if dependency == "Low":
            return "Low"

        return "Unknown"

    kpis["timeline_risk"] = kpis.apply(
        classify_timeline_risk,
        axis=1
    )

    return kpis


# ============================================================
# MAIN FUNCTION USED BY main.py
# ============================================================

def calculate_supplier_timeline(
    supplier_timeline
):

    return calculate_supplier_timeline_kpis(
        supplier_timeline
    )


# ============================================================
# STANDALONE TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("SUPPLIER TIMELINE MODULE TEST")
    print("=" * 70)

    input_file = (
        "data/input/"
        "Procurement_Negotiation_Input.xlsx"
    )

    # Load Excel sheet
    timeline_data = pd.read_excel(
        input_file,
        sheet_name="Supplier_Timeline"
    )

    print()
    print("Supplier Timeline Columns:")
    print(
        timeline_data.columns.tolist()
    )

    print()
    print("Supplier Timeline Dataset:")
    print(
        timeline_data.to_string(
            index=False
        )
    )

    print()
    print("Running timeline analysis...")

    timeline_analysis = (
        calculate_supplier_timeline(
            timeline_data
        )
    )

    print()
    print(
        "===== SUPPLIER TIMELINE ANALYSIS ====="
    )

    print(
        timeline_analysis.to_string(
            index=False
        )
    )

    print()
    print("=" * 70)
    print(
        "SUPPLIER TIMELINE MODULE TEST COMPLETED"
    )
    print("=" * 70)