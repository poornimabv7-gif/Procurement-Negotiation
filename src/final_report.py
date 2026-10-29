import os
import html
import pandas as pd


# ============================================================
# PROCUREMENT NEGOTIATION AI
# FINAL REPORT GENERATOR
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "outputs"
)

INPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "input",
    "Procurement_Negotiation_Input.xlsx"
)

REPORT_FILE = os.path.join(
    OUTPUT_DIR,
    "final_negotiation_report.html"
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def safe_float(value, default=None):
    try:
        if value is None:
            return default

        if pd.isna(value):
            return default

        return float(value)

    except (TypeError, ValueError):
        return default


def safe_text(value, default="N/A"):
    if value is None:
        return default

    try:
        if pd.isna(value):
            return default
    except Exception:
        pass

    text = str(value).strip()

    if text.lower() in ("", "nan", "none", "null"):
        return default

    return text


def escape_html(value):
    return html.escape(
        safe_text(value)
    )


def normalize_column(column):
    return (
        str(column)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
        .replace("/", "_")
        .replace("%", "pct")
    )


def normalize_dataframe(dataframe):
    if dataframe is None:
        return pd.DataFrame()

    result = dataframe.copy()

    result.columns = [
        normalize_column(column)
        for column in result.columns
    ]

    return result


def find_column(dataframe, candidates):
    if dataframe is None:
        return None

    if dataframe.empty:
        return None

    columns = set(dataframe.columns)

    for candidate in candidates:

        normalized = normalize_column(
            candidate
        )

        if normalized in columns:
            return normalized

    return None


def get_column_value(
    row,
    candidates,
    default=None
):
    if row is None:
        return default

    for candidate in candidates:

        normalized = normalize_column(
            candidate
        )

        if normalized in row.index:

            value = row[normalized]

            if value is not None:

                try:
                    if not pd.isna(value):
                        return value
                except Exception:
                    return value

    return default


def money(value):
    number = safe_float(value)

    if number is None:
        return "N/A"

    return f"₹{number:,.2f}"


def percentage(value):
    number = safe_float(value)

    if number is None:
        return "N/A"

    return f"{number:.2f}%"


def number(value, decimals=2):
    number_value = safe_float(value)

    if number_value is None:
        return "N/A"

    return f"{number_value:,.{decimals}f}"


# ============================================================
# CSV LOADER
# ============================================================

def load_csv(filename):

    path = os.path.join(
        OUTPUT_DIR,
        filename
    )

    if not os.path.exists(path):
        return pd.DataFrame()

    try:

        dataframe = pd.read_csv(path)

        return normalize_dataframe(
            dataframe
        )

    except Exception:

        return pd.DataFrame()


# ============================================================
# LOAD OUTPUT FILES
# ============================================================

def load_all_outputs():

    return {

        "supplier_analysis":
            load_csv("supplier_analysis.csv"),

        "outside_options":
            load_csv("outside_option_analysis.csv"),

        "batna":
            load_csv("batna_result.csv"),

        "reservation":
            load_csv("reservation_value.csv"),

        "zopa":
            load_csv("zopa_analysis.csv"),

        "nash":
            load_csv("nash_bargaining.csv"),

        "credibility":
            load_csv("credibility_analysis.csv"),

        "verification":
            load_csv(
                "outside_option_verification.csv"
            ),

        "information":
            load_csv(
                "information_asymmetry.csv"
            ),

        "timing":
            load_csv("timing_analysis.csv"),

        "supplier_risk":
            load_csv(
                "supplier_risk_analysis.csv"
            ),

        "should_cost":
            load_csv(
                "should_cost_analysis.csv"
            ),

        "tco_detail":
            load_csv("tco_analysis.csv"),

        "tco_summary":
            load_csv(
                "tco_supplier_summary.csv"
            ),

        "value_detail":
            load_csv(
                "value_at_stake_analysis.csv"
            ),

        "value_summary":
            load_csv(
                "value_at_stake_supplier_summary.csv"
            ),

        "shapley":
            load_csv("shapley_analysis.csv"),

        "final_decision":
            load_csv(
                "final_negotiation_decision.csv"
            ),

        "strategy":
            load_csv(
                "negotiation_strategy.csv"
            ),

        "brief":
            load_csv(
                "negotiation_brief.csv"
            )
    }


# ============================================================
# SUPPLIER NAME MAP
# ============================================================

def build_supplier_map(data):

    mapping = {}

    datasets = [
        data.get(
            "supplier_analysis",
            pd.DataFrame()
        ),
        data.get(
            "tco_summary",
            pd.DataFrame()
        ),
        data.get(
            "value_summary",
            pd.DataFrame()
        ),
        data.get(
            "final_decision",
            pd.DataFrame()
        )
    ]

    for dataframe in datasets:

        if dataframe.empty:
            continue

        supplier_id_column = find_column(
            dataframe,
            ["supplier_id"]
        )

        supplier_name_column = find_column(
            dataframe,
            [
                "supplier_name",
                "supplier"
            ]
        )

        if (
            supplier_id_column is None
            or supplier_name_column is None
        ):
            continue

        for _, row in dataframe.iterrows():

            supplier_id = safe_text(
                row[supplier_id_column],
                None
            )

            supplier_name = safe_text(
                row[supplier_name_column],
                None
            )

            if (
                supplier_id
                and supplier_name
            ):

                mapping[
                    supplier_id
                ] = supplier_name

    return mapping


# ============================================================
# TCO ANALYSIS
# ============================================================

def build_tco_rows(data):

    tco = data.get(
        "tco_summary",
        pd.DataFrame()
    )

    if tco.empty:
        return []

    supplier_map = build_supplier_map(
        data
    )

    supplier_id_column = find_column(
        tco,
        ["supplier_id"]
    )

    if supplier_id_column is None:
        return []

    purchase_column = find_column(
        tco,
        [
            "purchase_cost",
            "purchase_cost_total",
            "total_purchase_cost",
            "purchase_total"
        ]
    )

    transport_column = find_column(
        tco,
        [
            "transport_cost",
            "transport_cost_total",
            "total_transport_cost",
            "transport_total"
        ]
    )

    financing_column = find_column(
        tco,
        [
            "financing_cost",
            "financing_cost_total",
            "total_financing_cost",
            "financing_total"
        ]
    )

    known_tco_column = find_column(
        tco,
        [
            "known_tco",
            "known_total_cost",
            "total_tco",
            "tco"
        ]
    )

    tco_unit_column = find_column(
        tco,
        [
            "tco_per_unit",
            "tco_unit",
            "tco_per_unit_cost",
            "known_tco_per_unit",
            "total_cost_per_unit"
        ]
    )

    risk_column = find_column(
        tco,
        [
            "tco_risk",
            "tco_risk_level",
            "risk"
        ]
    )

    rank_column = find_column(
        tco,
        [
            "rank",
            "tco_rank"
        ]
    )

    rows = []

    for _, row in tco.iterrows():

        supplier_id = safe_text(
            row[supplier_id_column]
        )

        supplier_name = supplier_map.get(
            supplier_id,
            supplier_id
        )

        purchase_cost = None

        if purchase_column:
            purchase_cost = safe_float(
                row[purchase_column]
            )

        transport_cost = None

        if transport_column:
            transport_cost = safe_float(
                row[transport_column]
            )

        financing_cost = None

        if financing_column:
            financing_cost = safe_float(
                row[financing_column]
            )

        known_tco = None

        if known_tco_column:
            known_tco = safe_float(
                row[known_tco_column]
            )

        tco_per_unit = None

        if tco_unit_column:
            tco_per_unit = safe_float(
                row[tco_unit_column]
            )

        risk = "Unknown"

        if risk_column:
            risk = safe_text(
                row[risk_column],
                "Unknown"
            )

        rank = None

        if rank_column:
            rank = safe_float(
                row[rank_column]
            )

        rows.append(
            {
                "supplier_id": supplier_id,
                "supplier_name": supplier_name,
                "purchase_cost": purchase_cost,
                "transport_cost": transport_cost,
                "financing_cost": financing_cost,
                "known_tco": known_tco,
                "tco_per_unit": tco_per_unit,
                "tco_risk": risk,
                "rank": rank
            }
        )

    # --------------------------------------------------------
    # Read quantity from case
    # --------------------------------------------------------

    quantity = None

    try:

        case = pd.read_excel(
            INPUT_FILE,
            sheet_name="Negotiation_Case"
        )

        case = normalize_dataframe(
            case
        )

        if not case.empty:

            quantity = safe_float(
                get_column_value(
                    case.iloc[0],
                    [
                        "required_quantity"
                    ]
                )
            )

    except Exception:

        quantity = None

    # --------------------------------------------------------
    # Recalculate missing TCO fields
    # --------------------------------------------------------

    for row in rows:

        if (
            row["known_tco"] is None
            and (
                row["purchase_cost"] is not None
                or row["transport_cost"] is not None
                or row["financing_cost"] is not None
            )
        ):

            row["known_tco"] = sum(
                [
                    row["purchase_cost"] or 0,
                    row["transport_cost"] or 0,
                    row["financing_cost"] or 0
                ]
            )

        if (
            row["tco_per_unit"] is None
            and row["known_tco"] is not None
            and quantity
            and quantity > 0
        ):

            row["tco_per_unit"] = (
                row["known_tco"]
                /
                quantity
            )

    # --------------------------------------------------------
    # IMPORTANT FALLBACK
    #
    # If the generated TCO CSV has different column names,
    # reconstruct TCO from the original Excel input.
    # --------------------------------------------------------

    try:

        quotation = pd.read_excel(
            INPUT_FILE,
            sheet_name="Quotation_Data"
        )

        market = pd.read_excel(
            INPUT_FILE,
            sheet_name="Market_Cost_Data"
        )

        quotation = normalize_dataframe(
            quotation
        )

        market = normalize_dataframe(
            market
        )

        quotation_supplier_column = find_column(
            quotation,
            ["supplier_id"]
        )

        quotation_price_column = find_column(
            quotation,
            ["initial_price"]
        )

        quotation_quantity_column = find_column(
            quotation,
            ["quantity"]
        )

        market_transport_column = find_column(
            market,
            ["transport_cost"]
        )

        latest_transport = 0.0

        if (
            market_transport_column
            and not market.empty
        ):

            latest_transport = safe_float(
                market.iloc[-1][
                    market_transport_column
                ],
                0.0
            )

        if (
            quotation_supplier_column
            and quotation_price_column
        ):

            for row in rows:

                matching = quotation[
                    quotation[
                        quotation_supplier_column
                    ].astype(str)
                    ==
                    str(row["supplier_id"])
                ]

                if matching.empty:
                    continue

                quotation_row = matching.iloc[0]

                price = safe_float(
                    quotation_row[
                        quotation_price_column
                    ]
                )

                if price is None:
                    continue

                row_quantity = quantity

                if quotation_quantity_column:

                    excel_quantity = safe_float(
                        quotation_row[
                            quotation_quantity_column
                        ]
                    )

                    if (
                        excel_quantity
                        and excel_quantity > 0
                    ):

                        row_quantity = (
                            excel_quantity
                        )

                if (
                    row["purchase_cost"]
                    is None
                    and row_quantity
                ):

                    row["purchase_cost"] = (
                        price
                        *
                        row_quantity
                    )

                if (
                    row["transport_cost"]
                    is None
                    and row_quantity
                ):

                    row["transport_cost"] = (
                        latest_transport
                        *
                        row_quantity
                    )

                if row["financing_cost"] is None:

                    row["financing_cost"] = 0.0

                if row["known_tco"] is None:

                    row["known_tco"] = (
                        row["purchase_cost"]
                        +
                        row["transport_cost"]
                        +
                        row["financing_cost"]
                    )

                if (
                    row["tco_per_unit"]
                    is None
                    and row_quantity
                ):

                    row["tco_per_unit"] = (
                        row["known_tco"]
                        /
                        row_quantity
                    )

    except Exception:

        pass

    # --------------------------------------------------------
    # Generate missing TCO ranks
    # --------------------------------------------------------

    valid_rows = [
        row
        for row in rows
        if row["tco_per_unit"] is not None
    ]

    valid_rows.sort(
        key=lambda item:
        item["tco_per_unit"]
    )

    for index, row in enumerate(
        valid_rows,
        start=1
    ):

        if row["rank"] is None:
            row["rank"] = index

    return rows


# ============================================================
# VALUE AT STAKE
# ============================================================

def build_value_rows(data):

    summary = data.get(
        "value_summary",
        pd.DataFrame()
    )

    detail = data.get(
        "value_detail",
        pd.DataFrame()
    )

    if summary.empty:
        return []

    supplier_map = build_supplier_map(
        data
    )

    supplier_id_column = find_column(
        summary,
        ["supplier_id"]
    )

    if supplier_id_column is None:
        return []

    value_column = find_column(
        summary,
        [
            "total_value_at_stake",
            "value_at_stake",
            "value_at_stake_total",
            "savings_opportunity"
        ]
    )

    savings_column = find_column(
        summary,
        [
            "savings_percentage",
            "savings_percent",
            "savings_pct"
        ]
    )

    priority_column = find_column(
        summary,
        [
            "value_at_stake_priority",
            "priority",
            "negotiation_priority"
        ]
    )

    rank_column = find_column(
        summary,
        [
            "value_at_stake_rank",
            "rank"
        ]
    )

    rows = []

    for _, row in summary.iterrows():

        supplier_id = safe_text(
            row[supplier_id_column]
        )

        supplier_name = supplier_map.get(
            supplier_id,
            supplier_id
        )

        value = None

        if value_column:
            value = safe_float(
                row[value_column]
            )

        savings = None

        if savings_column:
            savings = safe_float(
                row[savings_column]
            )

        priority = None

        if priority_column:
            priority = safe_text(
                row[priority_column],
                None
            )

        rank = None

        if rank_column:
            rank = safe_float(
                row[rank_column]
            )

        rows.append(
            {
                "supplier_id": supplier_id,
                "supplier_name": supplier_name,
                "value_at_stake": value,
                "savings_percentage": savings,
                "priority": priority,
                "rank": rank
            }
        )

    # --------------------------------------------------------
    # Detail fallback
    # --------------------------------------------------------

    if not detail.empty:

        detail_supplier_column = find_column(
            detail,
            ["supplier_id"]
        )

        detail_value_column = find_column(
            detail,
            [
                "total_value_at_stake",
                "value_at_stake",
                "value_at_stake_total"
            ]
        )

        if (
            detail_supplier_column
            and detail_value_column
        ):

            detail_map = {}

            for _, detail_row in detail.iterrows():

                supplier_id = safe_text(
                    detail_row[
                        detail_supplier_column
                    ],
                    None
                )

                value = safe_float(
                    detail_row[
                        detail_value_column
                    ]
                )

                if (
                    supplier_id
                    and value is not None
                ):

                    detail_map[
                        supplier_id
                    ] = value

            for row in rows:

                if (
                    row["value_at_stake"]
                    is None
                    and row["supplier_id"]
                    in detail_map
                ):

                    row["value_at_stake"] = (
                        detail_map[
                            row["supplier_id"]
                        ]
                    )

    # --------------------------------------------------------
    # Reconstruct Value-at-Stake from Excel
    #
    # Benchmark = lowest initial quotation price
    #
    # Value at Stake =
    # (Supplier Price - Benchmark Price)
    # * Required Quantity
    # --------------------------------------------------------

    try:

        case = pd.read_excel(
            INPUT_FILE,
            sheet_name="Negotiation_Case"
        )

        quotation = pd.read_excel(
            INPUT_FILE,
            sheet_name="Quotation_Data"
        )

        case = normalize_dataframe(
            case
        )

        quotation = normalize_dataframe(
            quotation
        )

        if case.empty:
            return rows

        case_row = case.iloc[0]

        quantity = safe_float(
            get_column_value(
                case_row,
                ["required_quantity"]
            )
        )

        supplier_column = find_column(
            quotation,
            ["supplier_id"]
        )

        price_column = find_column(
            quotation,
            ["initial_price"]
        )

        if (
            quantity
            and quantity > 0
            and supplier_column
            and price_column
        ):

            supplier_prices = {}

            for _, quotation_row in quotation.iterrows():

                supplier_id = safe_text(
                    quotation_row[
                        supplier_column
                    ],
                    None
                )

                price = safe_float(
                    quotation_row[
                        price_column
                    ]
                )

                if (
                    supplier_id
                    and price is not None
                ):

                    supplier_prices[
                        supplier_id
                    ] = price

            if supplier_prices:

                benchmark_price = min(
                    supplier_prices.values()
                )

                for row in rows:

                    supplier_id = row[
                        "supplier_id"
                    ]

                    supplier_price = (
                        supplier_prices.get(
                            supplier_id
                        )
                    )

                    if supplier_price is None:
                        continue

                    # ------------------------------------------------
                    # Keep the existing Value-at-Stake calculation
                    # exactly the same.
                    # ------------------------------------------------

                    if (
                        row["value_at_stake"]
                        is None
                    ):

                        row["value_at_stake"] = max(
                            (
                                supplier_price
                                -
                                benchmark_price
                            )
                            *
                            quantity,
                            0
                        )

                    # ------------------------------------------------
                    # FIX:
                    #
                    # Savings % must use THIS supplier's spend
                    # as the denominator, not the current supplier's
                    # spend.
                    #
                    # Example:
                    #
                    # Supplier D:
                    # ₹70,000 / (₹115 × 10,000)
                    # = 6.09%
                    #
                    # Supplier C:
                    # ₹30,000 / (₹111 × 10,000)
                    # = 2.70%
                    # ------------------------------------------------

                    if (
                        row["value_at_stake"]
                        is not None
                        and supplier_price > 0
                    ):

                        supplier_spend = (
                            supplier_price
                            *
                            quantity
                        )

                        row[
                            "savings_percentage"
                        ] = (
                            row[
                                "value_at_stake"
                            ]
                            /
                            supplier_spend
                            *
                            100
                        )

    except Exception:

        pass

    # --------------------------------------------------------
    # Priority
    # --------------------------------------------------------

    for row in rows:

        if not row["priority"]:

            value = row[
                "value_at_stake"
            ]

            if value is None:

                row["priority"] = "Low"

            elif value >= 100000:

                row["priority"] = "High"

            elif value >= 25000:

                row["priority"] = "Medium"

            else:

                row["priority"] = "Low"

    # --------------------------------------------------------
    # Rank
    # --------------------------------------------------------

    valid_rows = [
        row
        for row in rows
        if row["value_at_stake"] is not None
    ]

    valid_rows.sort(
        key=lambda item:
        item["value_at_stake"],
        reverse=True
    )

    for index, row in enumerate(
        valid_rows,
        start=1
    ):

        if row["rank"] is None:
            row["rank"] = index

    return rows


# ============================================================
# BATNA
# ============================================================

def get_batna(data):

    batna = data.get(
        "batna",
        pd.DataFrame()
    )

    if batna.empty:

        return {
            "supplier_id": "N/A",
            "supplier_name": "N/A",
            "total_cost": None,
            "per_unit": None
        }

    row = batna.iloc[0]

    supplier_id = get_column_value(
        row,
        [
            "batna_supplier_id",
            "supplier_id"
        ]
    )

    supplier_name = get_column_value(
        row,
        [
            "batna_supplier_name",
            "supplier_name",
            "supplier"
        ]
    )

    total_cost = get_column_value(
        row,
        [
            "batna_cost",
            "batna_total_cost",
            "total_cost"
        ]
    )

    per_unit = get_column_value(
        row,
        [
            "buyer_reservation_per_unit",
            "reservation_value_per_unit",
            "batna_per_unit"
        ]
    )

    if per_unit is None:

        try:

            case = pd.read_excel(
                INPUT_FILE,
                sheet_name="Negotiation_Case"
            )

            case = normalize_dataframe(
                case
            )

            if not case.empty:

                quantity = safe_float(
                    get_column_value(
                        case.iloc[0],
                        [
                            "required_quantity"
                        ]
                    )
                )

                total_numeric = safe_float(
                    total_cost
                )

                if (
                    quantity
                    and total_numeric is not None
                ):

                    per_unit = (
                        total_numeric
                        /
                        quantity
                    )

        except Exception:

            pass

    return {
        "supplier_id": safe_text(
            supplier_id
        ),
        "supplier_name": safe_text(
            supplier_name
        ),
        "total_cost": safe_float(
            total_cost
        ),
        "per_unit": safe_float(
            per_unit
        )
    }


# ============================================================
# FINAL RECOMMENDATION
# ============================================================

def get_recommendation(data):

    final = data.get(
        "final_decision",
        pd.DataFrame()
    )

    if final.empty:
        return {}

    rank_column = find_column(
        final,
        [
            "decision_rank",
            "rank"
        ]
    )

    if rank_column:

        final = final.copy()

        final[rank_column] = pd.to_numeric(
            final[rank_column],
            errors="coerce"
        )

        final = final.sort_values(
            by=rank_column,
            ascending=True
        )

    row = final.iloc[0]

    return {
        "supplier_id": safe_text(
            get_column_value(
                row,
                ["supplier_id"]
            )
        ),
        "supplier_name": safe_text(
            get_column_value(
                row,
                [
                    "supplier_name",
                    "supplier"
                ]
            )
        ),
        "target": safe_float(
            get_column_value(
                row,
                [
                    "recommended_target_price",
                    "target_price"
                ]
            )
        ),
        "walkaway": safe_float(
            get_column_value(
                row,
                [
                    "walk_away_price",
                    "walk_away_price_per_unit"
                ]
            )
        ),
        "priority": safe_text(
            get_column_value(
                row,
                [
                    "negotiation_priority",
                    "priority"
                ]
            )
        ),
        "action": safe_text(
            get_column_value(
                row,
                [
                    "recommended_buyer_action",
                    "buyer_action"
                ]
            )
        )
    }


# ============================================================
# NEGOTIATION STRATEGY
# ============================================================

def build_strategy_rows(data):

    strategy = data.get(
        "strategy",
        pd.DataFrame()
    )

    if strategy.empty:
        return []

    rows = []

    for _, row in strategy.iterrows():

        rows.append(
            {
                "supplier_id": safe_text(
                    get_column_value(
                        row,
                        ["supplier_id"]
                    )
                ),

                "supplier_name": safe_text(
                    get_column_value(
                        row,
                        [
                            "supplier_name",
                            "supplier"
                        ]
                    )
                ),

                "current_offer": safe_float(
                    get_column_value(
                        row,
                        [
                            "current_offer_per_unit",
                            "current_offer",
                            "initial_price"
                        ]
                    )
                ),

                "opening": safe_float(
                    get_column_value(
                        row,
                        [
                            "opening_price_per_unit",
                            "opening_price"
                        ]
                    )
                ),

                "target": safe_float(
                    get_column_value(
                        row,
                        [
                            "target_price_per_unit",
                            "target_price"
                        ]
                    )
                ),

                "walkaway": safe_float(
                    get_column_value(
                        row,
                        [
                            "walk_away_price_per_unit",
                            "walk_away_price"
                        ]
                    )
                ),

                "zopa": safe_text(
                    get_column_value(
                        row,
                        ["zopa_exists"]
                    )
                ),

                "levers": safe_text(
                    get_column_value(
                        row,
                        [
                            "primary_negotiation_levers"
                        ]
                    )
                ),

                "posture": safe_text(
                    get_column_value(
                        row,
                        [
                            "negotiation_posture"
                        ]
                    )
                ),

                "strategy": safe_text(
                    get_column_value(
                        row,
                        [
                            "supplier_specific_strategy"
                        ]
                    )
                )
            }
        )

    return rows


# ============================================================
# HTML CSS
# ============================================================

def get_css():

    return """
    * {
        box-sizing: border-box;
    }

    body {
        margin: 0;
        background: #f4f6f8;
        color: #17212b;
        font-family: Arial, Helvetica, sans-serif;
        line-height: 1.6;
    }

    .container {
        width: 94%;
        max-width: 1500px;
        margin: auto;
    }

    .header {
        background: #17212b;
        color: white;
        padding: 42px 0;
    }

    .header h1 {
        margin: 0;
        font-size: 38px;
    }

    .header p {
        margin: 8px 0 0;
        color: #dce3e8;
        font-size: 17px;
    }

    .section {
        background: white;
        margin: 28px 0;
        padding: 34px;
        border-radius: 14px;
        box-shadow: 0 3px 15px rgba(0,0,0,0.07);
    }

    .section h2 {
        margin-top: 0;
        font-size: 29px;
    }

    .summary-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 18px;
    }

    .summary-card {
        background: #f7f9fb;
        padding: 21px;
        border-radius: 11px;
        border-left: 5px solid #17212b;
    }

    .summary-card span {
        display: block;
        color: #66717a;
        font-size: 14px;
    }

    .summary-card strong {
        display: block;
        font-size: 24px;
        margin-top: 5px;
    }

    .recommendation {
        margin-top: 25px;
        background: #f1f6fa;
        border-left: 6px solid #17212b;
        border-radius: 10px;
        padding: 25px;
    }

    .recommendation h3 {
        margin-top: 0;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 20px;
    }

    th {
        background: #17212b;
        color: white;
        padding: 14px;
        text-align: left;
        white-space: nowrap;
    }

    td {
        padding: 14px;
        border-bottom: 1px solid #dfe4e8;
    }

    tr:nth-child(even) {
        background: #f7f9fb;
    }

    .strong {
        font-weight: 700;
    }

    .note {
        margin-top: 22px;
        background: #f7f9fb;
        border-left: 5px solid #17212b;
        padding: 21px;
        border-radius: 9px;
    }

    .flow {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        align-items: center;
        gap: 10px;
    }

    .flow-box {
        background: #17212b;
        color: white;
        padding: 12px 17px;
        border-radius: 8px;
        font-weight: 700;
        text-align: center;
    }

    .arrow {
        font-size: 23px;
        font-weight: 700;
    }

    .strategy-card {
        background: #f7f9fb;
        border: 1px solid #dfe4e8;
        border-radius: 11px;
        padding: 22px;
        margin: 18px 0;
    }

    .strategy-card h3 {
        margin-top: 0;
    }

    .price-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 12px;
        margin: 18px 0;
    }

    .price-box {
        background: white;
        border: 1px solid #dfe4e8;
        border-radius: 8px;
        padding: 15px;
    }

    .price-box span {
        display: block;
        color: #66717a;
        font-size: 13px;
    }

    .price-box strong {
        font-size: 20px;
    }

    .footer {
        text-align: center;
        color: #66717a;
        padding: 35px;
        font-size: 13px;
    }

    @media (max-width: 900px) {

        .section {
            padding: 22px;
            overflow-x: auto;
        }

        table {
            min-width: 900px;
        }

        .header h1 {
            font-size: 30px;
        }
    }
    """


# ============================================================
# TCO TABLE HTML
# ============================================================

def create_tco_html(rows):

    if not rows:

        return """
        <div class="note">
            TCO data is not available.
        </div>
        """

    table_rows = ""

    for row in rows:

        table_rows += f"""
        <tr>
            <td class="strong">
                {escape_html(row["supplier_id"])}
            </td>

            <td>
                {escape_html(row["supplier_name"])}
            </td>

            <td class="strong">
                {money(row["purchase_cost"])}
            </td>

            <td class="strong">
                {money(row["transport_cost"])}
            </td>

            <td class="strong">
                {money(row["financing_cost"])}
            </td>

            <td class="strong">
                {money(row["known_tco"])}
            </td>

            <td class="strong">
                {money(row["tco_per_unit"])}
            </td>

            <td>
                {escape_html(row["tco_risk"])}
            </td>

            <td>
                {number(row["rank"], 0)}
            </td>
        </tr>
        """

    return f"""
    <table>

        <thead>
            <tr>
                <th>Supplier ID</th>
                <th>Supplier</th>
                <th>Purchase Cost</th>
                <th>Transport Cost</th>
                <th>Financing Cost</th>
                <th>Known TCO</th>
                <th>TCO / Unit</th>
                <th>TCO Risk</th>
                <th>Rank</th>
            </tr>
        </thead>

        <tbody>
            {table_rows}
        </tbody>

    </table>
    """


# ============================================================
# VALUE AT STAKE TABLE HTML
# ============================================================

def create_value_html(rows):

    if not rows:

        return """
        <div class="note">
            Value-at-Stake data is not available.
        </div>
        """

    table_rows = ""

    for row in rows:

        table_rows += f"""
        <tr>
            <td class="strong">
                {escape_html(row["supplier_id"])}
            </td>

            <td>
                {escape_html(row["supplier_name"])}
            </td>

            <td class="strong">
                {money(row["value_at_stake"])}
            </td>

            <td>
                {percentage(row["savings_percentage"])}
            </td>

            <td>
                {escape_html(row["priority"])}
            </td>

            <td>
                {number(row["rank"], 0)}
            </td>
        </tr>
        """

    return f"""
    <table>

        <thead>
            <tr>
                <th>Supplier ID</th>
                <th>Supplier</th>
                <th>Value at Stake</th>
                <th>Savings %</th>
                <th>Priority</th>
                <th>Rank</th>
            </tr>
        </thead>

        <tbody>
            {table_rows}
        </tbody>

    </table>
    """


# ============================================================
# STRATEGY HTML
# ============================================================

def create_strategy_html(rows):

    if not rows:

        return """
        <div class="note">
            Negotiation strategy output is not available.
        </div>
        """

    content = ""

    for row in rows:

        content += f"""
        <div class="strategy-card">

            <h3>
                {escape_html(row["supplier_name"])}
                ({escape_html(row["supplier_id"])})
            </h3>

            <div class="price-grid">

                <div class="price-box">
                    <span>Current Offer</span>
                    <strong>
                        {money(row["current_offer"])}
                    </strong>
                </div>

                <div class="price-box">
                    <span>Opening Price</span>
                    <strong>
                        {money(row["opening"])}
                    </strong>
                </div>

                <div class="price-box">
                    <span>Target Price</span>
                    <strong>
                        {money(row["target"])}
                    </strong>
                </div>

                <div class="price-box">
                    <span>Walk-Away Price</span>
                    <strong>
                        {money(row["walkaway"])}
                    </strong>
                </div>

            </div>

            <p>
                <strong>ZOPA:</strong>
                {escape_html(row["zopa"])}
            </p>

            <p>
                <strong>Negotiation Levers:</strong>
                {escape_html(row["levers"])}
            </p>

            <p>
                <strong>Negotiation Posture:</strong>
                {escape_html(row["posture"])}
            </p>

            <p>
                <strong>Supplier Strategy:</strong>
                {escape_html(row["strategy"])}
            </p>

        </div>
        """

    return content


# ============================================================
# GENERATE FINAL REPORT
# ============================================================

def generate_final_report(data=None, **kwargs):

    if not isinstance(data, dict):
        data = {}

    disk_data = load_all_outputs()

    for key, dataframe in disk_data.items():

        if (
            key not in data
            or not isinstance(
                data[key],
                pd.DataFrame
            )
            or data[key].empty
        ):

            data[key] = dataframe

    for key, value in kwargs.items():
        data[key] = value

    # --------------------------------------------------------
    # Main analyses
    # --------------------------------------------------------

    batna = get_batna(data)

    tco_rows = build_tco_rows(data)

    value_rows = build_value_rows(data)

    recommendation = get_recommendation(
        data
    )

    strategy_rows = build_strategy_rows(
        data
    )

    # --------------------------------------------------------
    # Best TCO
    # --------------------------------------------------------

    valid_tco = [
        row
        for row in tco_rows
        if row["tco_per_unit"] is not None
    ]

    best_tco = None

    if valid_tco:

        best_tco = min(
            valid_tco,
            key=lambda row:
            row["tco_per_unit"]
        )

    # --------------------------------------------------------
    # Highest Value at Stake
    # --------------------------------------------------------

    valid_value = [
        row
        for row in value_rows
        if row["value_at_stake"] is not None
    ]

    highest_value = None

    if valid_value:

        highest_value = max(
            valid_value,
            key=lambda row:
            row["value_at_stake"]
        )

    # --------------------------------------------------------
    # Read case information
    # --------------------------------------------------------

    case_id = "N/A"
    material_id = "N/A"
    quantity = None
    current_supplier = "N/A"

    try:

        case = pd.read_excel(
            INPUT_FILE,
            sheet_name="Negotiation_Case"
        )

        case = normalize_dataframe(
            case
        )

        if not case.empty:

            case_row = case.iloc[0]

            case_id = safe_text(
                get_column_value(
                    case_row,
                    ["case_id"]
                )
            )

            material_id = safe_text(
                get_column_value(
                    case_row,
                    ["material_id"]
                )
            )

            quantity = safe_float(
                get_column_value(
                    case_row,
                    ["required_quantity"]
                )
            )

            current_supplier = safe_text(
                get_column_value(
                    case_row,
                    ["current_supplier_id"]
                )
            )

    except Exception:

        pass

    # --------------------------------------------------------
    # Build optional TCO note
    # --------------------------------------------------------

    tco_note = ""

    if best_tco is not None:

        tco_note = f"""
        <div class="note">

            <strong>
                TCO interpretation:
            </strong>

            {escape_html(best_tco["supplier_name"])}
            has the lowest modeled TCO per unit at

            <strong>
                {money(best_tco["tco_per_unit"])}
            </strong>

            per unit.

        </div>
        """

    # --------------------------------------------------------
    # Build optional Value-at-Stake note
    # --------------------------------------------------------

    value_note = ""

    if highest_value is not None:

        value_note = f"""
        <div class="note">

            <strong>
                Largest modeled Value-at-Stake:
            </strong>

            {escape_html(
                highest_value["supplier_name"]
            )}

            with

            <strong>
                {money(
                    highest_value["value_at_stake"]
                )}
            </strong>.

        </div>
        """

    # --------------------------------------------------------
    # Build final HTML
    # --------------------------------------------------------

    css = get_css()

    tco_table = create_tco_html(
        tco_rows
    )

    value_table = create_value_html(
        value_rows
    )

    strategy_html = create_strategy_html(
        strategy_rows
    )

    recommendation_supplier = escape_html(
        recommendation.get(
            "supplier_name",
            "N/A"
        )
    )

    recommendation_id = escape_html(
        recommendation.get(
            "supplier_id",
            "N/A"
        )
    )

    recommendation_target = money(
        recommendation.get(
            "target"
        )
    )

    recommendation_walkaway = money(
        recommendation.get(
            "walkaway"
        )
    )

    recommendation_priority = escape_html(
        recommendation.get(
            "priority",
            "N/A"
        )
    )

    recommendation_action = escape_html(
        recommendation.get(
            "action",
            "N/A"
        )
    )

    html_document = f"""
<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>
Procurement Negotiation AI - Final Report
</title>

<style>
{css}
</style>

</head>

<body>

<header class="header">

    <div class="container">

        <h1>
            Procurement Negotiation AI
        </h1>

        <p>
            Final Negotiation Analysis &amp; Decision Report
        </p>

    </div>

</header>


<main class="container">


<!-- =====================================================
     EXECUTIVE SUMMARY
     ===================================================== -->

<section class="section">

    <h2>
        Executive Summary
    </h2>

    <div class="summary-grid">

        <div class="summary-card">
            <span>
                Negotiation Case
            </span>

            <strong>
                {escape_html(case_id)}
            </strong>
        </div>


        <div class="summary-card">
            <span>
                Material
            </span>

            <strong>
                {escape_html(material_id)}
            </strong>
        </div>


        <div class="summary-card">
            <span>
                Required Quantity
            </span>

            <strong>
                {number(quantity, 0)}
            </strong>
        </div>


        <div class="summary-card">
            <span>
                Current Supplier
            </span>

            <strong>
                {escape_html(current_supplier)}
            </strong>
        </div>


        <div class="summary-card">
            <span>
                BATNA Supplier
            </span>

            <strong>
                {escape_html(batna["supplier_name"])}
            </strong>
        </div>


        <div class="summary-card">
            <span>
                BATNA / Unit
            </span>

            <strong>
                {money(batna["per_unit"])}
            </strong>
        </div>

    </div>


    <div class="recommendation">

        <h3>
            Final Negotiation Recommendation
        </h3>

        <p>

            <strong>
                {recommendation_supplier}
            </strong>

            ({recommendation_id})
            is the top-ranked negotiation candidate.

        </p>


        <p>

            <strong>
                Target Price:
            </strong>

            {recommendation_target}

            &nbsp;&nbsp;&nbsp;

            <strong>
                Walk-Away:
            </strong>

            {recommendation_walkaway}

        </p>


        <p>

            <strong>
                Priority:
            </strong>

            {recommendation_priority}

        </p>


        <p>

            <strong>
                Buyer Action:
            </strong>

            {recommendation_action}

        </p>

    </div>

</section>


<!-- =====================================================
     ANALYTICAL FLOW
     ===================================================== -->

<section class="section">

    <h2>
        Analytical Flow
    </h2>

    <div class="flow">

        <div class="flow-box">
            Procurement Data
        </div>

        <div class="arrow">
            →
        </div>

        <div class="flow-box">
            Supplier Analysis
        </div>

        <div class="arrow">
            →
        </div>

        <div class="flow-box">
            Outside Options
        </div>

        <div class="arrow">
            →
        </div>

        <div class="flow-box">
            BATNA
        </div>

        <div class="arrow">
            →
        </div>

        <div class="flow-box">
            Reservation Value
        </div>

        <div class="arrow">
            →
        </div>

        <div class="flow-box">
            ZOPA
        </div>

        <div class="arrow">
            →
        </div>

        <div class="flow-box">
            Game Theory
        </div>

        <div class="arrow">
            →
        </div>

        <div class="flow-box">
            Negotiation Strategy
        </div>

        <div class="arrow">
            →
        </div>

        <div class="flow-box">
            Final Decision
        </div>

    </div>

</section>


<!-- =====================================================
     BATNA
     ===================================================== -->

<section class="section">

    <h2>
        BATNA and Reservation Value
    </h2>

    <table>

        <thead>

            <tr>
                <th>Item</th>
                <th>Result</th>
            </tr>

        </thead>

        <tbody>

            <tr>

                <td>
                    BATNA Supplier
                </td>

                <td class="strong">

                    {escape_html(
                        batna["supplier_name"]
                    )}

                    (
                    {escape_html(
                        batna["supplier_id"]
                    )}
                    )

                </td>

            </tr>


            <tr>

                <td>
                    BATNA Total Cost
                </td>

                <td class="strong">

                    {money(
                        batna["total_cost"]
                    )}

                </td>

            </tr>


            <tr>

                <td>
                    BATNA / Unit
                </td>

                <td class="strong">

                    {money(
                        batna["per_unit"]
                    )}

                </td>

            </tr>


            <tr>

                <td>
                    Buyer Reservation / Unit
                </td>

                <td class="strong">

                    {money(
                        batna["per_unit"]
                    )}

                </td>

            </tr>

        </tbody>

    </table>

</section>


<!-- =====================================================
     NEGOTIATION STRATEGY
     ===================================================== -->

<section class="section">

    <h2>
        Negotiation Strategy
    </h2>

    {strategy_html}

</section>


<!-- =====================================================
     TCO
     ===================================================== -->

<section class="section">

    <h2>
        Total Cost of Ownership
    </h2>

    <p>

        TCO represents the known cost components currently
        modeled by the procurement analysis.

    </p>

    {tco_table}

    {tco_note}

</section>


<!-- =====================================================
     VALUE AT STAKE
     ===================================================== -->

<section class="section">

    <h2>
        Value at Stake
    </h2>

    <p>

        Value-at-Stake represents the modeled incremental
        savings opportunity relative to the benchmark used
        by the analysis.

    </p>

    {value_table}


    <div class="note">

        <strong>
            Value-at-Stake interpretation:
        </strong>

        <p>

            The Value-at-Stake calculation uses the benchmark
            price from the procurement quotation data and the
            required quantity for the negotiation case.

        </p>

        <p>

            A supplier at the benchmark price has zero
            incremental price savings opportunity against
            that benchmark.

        </p>

    </div>

    {value_note}

</section>


<!-- =====================================================
     FINAL DECISION
     ===================================================== -->

<section class="section">

    <h2>
        Final Negotiation Decision
    </h2>

    <div class="recommendation">

        <h3>
            {recommendation_supplier}
        </h3>

        <p>

            <strong>
                Supplier ID:
            </strong>

            {recommendation_id}

        </p>

        <p>

            <strong>
                Target Price:
            </strong>

            {recommendation_target}

        </p>

        <p>

            <strong>
                Walk-Away Price:
            </strong>

            {recommendation_walkaway}

        </p>

        <p>

            <strong>
                Priority:
            </strong>

            {recommendation_priority}

        </p>

        <p>

            <strong>
                Recommended Buyer Action:
            </strong>

            {recommendation_action}

        </p>

    </div>

</section>


<!-- =====================================================
     INTERPRETATION
     ===================================================== -->

<section class="section">

    <h2>
        Interpretation
    </h2>

    <p>

        The model combines quantitative procurement analysis
        with game-theory concepts to support negotiation
        preparation.

    </p>

    <p>

        The quantitative layer establishes supplier
        alternatives, BATNA, reservation value, ZOPA,
        should-cost, TCO and Value-at-Stake.

    </p>

    <p>

        The game-theory layer adds Nash bargaining,
        signalling, credibility, information asymmetry,
        timing / hold-up analysis and Shapley-based
        negotiation lever attribution.

    </p>

    <p>

        These analytical outputs are converted into a
        practical buyer strategy containing an opening
        position, target price, walk-away boundary and
        supplier-specific negotiation actions.

    </p>


    <div class="note">

        <strong>
            Important:
        </strong>

        <p>

            This capstone uses synthetic/sample procurement
            data for demonstration and modelling purposes.
            The results should not be presented as actual
            Knorr-Bremse supplier findings or real company
            data.

        </p>

    </div>

</section>


</main>


<footer class="footer">

    Procurement Negotiation AI
    &nbsp;|&nbsp;
    Final Negotiation Analysis

</footer>


</body>

</html>
"""

    # --------------------------------------------------------
    # Save report
    # --------------------------------------------------------

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            html_document
        )

    return html_document


# ============================================================
# COMPATIBILITY FUNCTION
# ============================================================

def generate_report(data=None, **kwargs):

    return generate_final_report(
        data=data,
        **kwargs
    )


# ============================================================
# STANDALONE EXECUTION
# ============================================================

def main():

    print()
    print("=" * 70)
    print(" PROCUREMENT NEGOTIATION AI")
    print(" FINAL HTML REPORT")
    print("=" * 70)

    data = load_all_outputs()

    generate_final_report(
        data
    )

    print()
    print("✓ Final HTML report generated")
    print(
        f"✓ Report: {REPORT_FILE}"
    )
    print()


if __name__ == "__main__":

    main()