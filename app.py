
import os, io, warnings
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px

warnings.filterwarnings("ignore")

# =========================================================
# PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="NCR Ride Intelligence",
    page_icon="🚕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# COLOR PALETTE — CHARCOAL + POWER BI INSPIRED BLUE
# =========================================================
PASTELS = [
    "#78B7E0",  # sky blue
    "#F6BD60",  # warm yellow
    "#8BD3C7",  # mint
    "#F284A7",  # pink
    "#A9A6E8",  # lavender
    "#E6D38A",  # soft gold
    "#83C5BE",  # teal
    "#F4A261"   # orange
]

appearance = st.sidebar.selectbox(
    "Appearance",
    ["Dark", "Light"],
    index=0
)

if appearance == "Dark":
    BG = "#303030"
    SIDEBAR = "#252525"
    PANEL = "#393939"
    PLOT_BG = "#393939"
    TEXT = "#FFFFFF"
    MUTED = "#E0E0E0"
    BORDER = "#555555"
    INPUT_BG = "#2B2B2B"
    TEMPLATE = "plotly_dark"
else:
    BG = "#F2F5F8"
    SIDEBAR = "#FFFFFF"
    PANEL = "#FFFFFF"
    PLOT_BG = "#FFFFFF"
    TEXT = "#202938"
    MUTED = "#526174"
    BORDER = "#D4DEE8"
    INPUT_BG = "#FFFFFF"
    TEMPLATE = "plotly_white"

# Light red used for selected filter tags
TAG_BG = "#F9B8B8"
TAG_TEXT = "#7A1F1F"

# =========================================================
# GLOBAL CSS — TITLE, SIDEBAR, KPI AND CHART FIXES
# =========================================================
st.markdown(f"""
<style>
    .stApp {{
        background: {BG};
        color: {TEXT};
    }}

    [data-testid="stHeader"] {{
        background: {BG};
    }}

    .block-container {{
        max-width: 100%;
        padding: 0.65rem 1.05rem 0.35rem 1.05rem !important;
    }}

    /* ---------- SIDEBAR ---------- */
    [data-testid="stSidebar"] {{
        background: {SIDEBAR};
        border-right: 1px solid {BORDER};
        min-width: 250px !important;
        max-width: 250px !important;
    }}

    [data-testid="stSidebar"] > div {{
        padding-top: 0.55rem;
    }}

    /* ---------- TEXT COLOURS (works for both themes) ---------- */
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
    .stApp .stMarkdown, .stApp .stMarkdown p,
    .stApp .stMarkdown h1, .stApp .stMarkdown h2, .stApp .stMarkdown h3,
    .stApp .stMarkdown h4,
    .stApp label, .stApp label p, .stApp label span,
    [data-testid="stWidgetLabel"] p,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span,
    [data-testid="stRadio"] label p,
    [data-testid="stRadio"] label div,
    button[data-baseweb="tab"] p {{
        color: {TEXT} !important;
    }}

    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] p,
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {{
        color: {MUTED} !important;
        font-size: 11px;
        line-height: 1.25;
    }}

    /* ---------- INPUTS / DROPDOWNS ---------- */
    [data-baseweb="select"] > div,
    [data-baseweb="input"] > div,
    [data-baseweb="base-input"],
    [data-testid="stDateInput"] > div > div,
    [data-testid="stFileUploaderDropzone"] {{
        background: {INPUT_BG} !important;
        border-color: {BORDER} !important;
    }}

    [data-baseweb="select"] *,
    [data-baseweb="input"] input,
    [data-baseweb="base-input"] input,
    [data-testid="stDateInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stTextInput"] input,
    [data-testid="stFileUploaderDropzone"] *,
    [data-testid="stFileUploaderDropzone"] small {{
        color: {TEXT} !important;
    }}

    [data-baseweb="select"] svg,
    [data-testid="stDateInput"] svg {{
        fill: {TEXT} !important;
    }}

    /* dropdown option list */
    [data-baseweb="popover"] ul,
    [data-baseweb="popover"] li,
    [data-baseweb="popover"] [role="listbox"],
    [data-baseweb="calendar"],
    [data-baseweb="calendar"] * {{
        background: {INPUT_BG} !important;
        color: {TEXT} !important;
    }}

    [data-baseweb="popover"] li:hover {{
        background: {BORDER} !important;
    }}

    /* ---------- SELECTED FILTER TAGS: LIGHT RED ---------- */
    span[data-baseweb="tag"] {{
        background-color: {TAG_BG} !important;
        border-radius: 6px;
    }}

    span[data-baseweb="tag"] *,
    span[data-baseweb="tag"] span {{
        color: {TAG_TEXT} !important;
        background: transparent !important;
    }}

    span[data-baseweb="tag"] svg {{
        fill: {TAG_TEXT} !important;
    }}

    /* ---------- BRAND ---------- */
    .brand {{
        font-size: 16px;
        font-weight: 850;
        letter-spacing: -0.2px;
        white-space: normal;
        word-break: keep-all;
        margin: 0 0 1px 0;
        line-height: 1.25;
        color: {TEXT};
    }}

    .brand-sub {{
        color: {MUTED};
        font-size: 10px;
        letter-spacing: 0.5px;
        margin: 2px 0 12px 0;
        white-space: normal;
        line-height: 1.3;
    }}

    .page-heading {{
        color: {TEXT} !important;
        font-size: 26px;
        line-height: 1.35;
        font-weight: 800;
        margin: 0 0 2px 0;
        padding-top: 0;
    }}

    .page-subtitle {{
        color: {MUTED} !important;
        font-size: 11px;
        margin-bottom: 9px;
    }}

    h1, h2, h3 {{
        margin-top: 0.1rem !important;
        margin-bottom: 0.2rem !important;
    }}

    h3 {{
        font-size: 15px !important;
    }}

    p {{
        margin-bottom: 0.2rem;
    }}

    /* ---------- KPI CARDS (always dark text on blue) ---------- */
    div[data-testid="stMetric"] {{
        background: #78B7E0;
        border: 1px solid #91C7E7;
        border-radius: 8px;
        padding: 8px 10px;
        min-height: 76px;
    }}

    div[data-testid="stMetric"] * {{
        color: #102A43 !important;
    }}

    div[data-testid="stMetricLabel"] p {{
        font-size: 11px !important;
        font-weight: 700 !important;
        color: #17334A !important;
    }}

    div[data-testid="stMetricValue"],
    div[data-testid="stMetricValue"] div {{
        font-size: 24px !important;
        font-weight: 850 !important;
        color: #102A43 !important;
    }}

    div[data-testid="stMetricDelta"] {{
        font-size: 10px;
    }}

    /* ---------- ALERT BOXES (keep readable) ---------- */
    [data-testid="stAlert"] *,
    [data-testid="stAlert"] p {{
        color: #1F2937 !important;
    }}

    /* ---------- CONTAINERS ---------- */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: {PANEL};
        border: 1px solid {BORDER};
        border-radius: 9px;
        padding: 7px !important;
    }}

    div[data-testid="stPlotlyChart"] {{
        margin: 0 !important;
        padding: 0 !important;
    }}

    [data-testid="stDataFrame"] {{
        border: 1px solid {BORDER};
        border-radius: 8px;
    }}

    hr {{
        margin: 0.35rem 0 !important;
        border-color: {BORDER};
    }}

    .stButton button,
    .stDownloadButton button {{
        border-radius: 7px;
    }}

    [data-testid="stSidebar"] .stRadio label {{
        padding-top: 0;
        padding-bottom: 0;
        font-size: 13px;
    }}
</style>
""", unsafe_allow_html=True)

# =========================================================
# DATA LOADING
# =========================================================
DATA_PATH = "/content/ncr_ride_bookings.csv"

@st.cache_data(show_spinner="Loading ride-booking data...")
def load_data(raw=None):
    if raw is not None:
        d = pd.read_csv(io.BytesIO(raw))
    elif os.path.exists(DATA_PATH):
        d = pd.read_csv(DATA_PATH)
    else:
        return pd.DataFrame()

    d.columns = d.columns.astype(str).str.strip()

    for col in d.select_dtypes(include=["object", "string"]).columns:
        d[col] = d[col].astype("string").str.strip()

    return d


# =========================================================
# SIDEBAR BRAND AND UPLOAD
# =========================================================
st.sidebar.markdown(
    '<div class="brand">🚕 NCR RIDE<br>INTELLIGENCE</div>'
    '<div class="brand-sub">BOOKING & OPERATIONS ANALYTICS</div>',
    unsafe_allow_html=True
)

uploaded = st.sidebar.file_uploader(
    "Upload another CSV",
    type=["csv"]
)

df = load_data(uploaded.getvalue() if uploaded else None)

if df.empty:
    st.title("Upload ride-booking data")
    st.info(
        "Upload your NCR ride-booking CSV in the sidebar, "
        "or save it at /content/ncr_ride_bookings.csv."
    )
    st.stop()

# =========================================================
# AUTOMATIC COLUMN DETECTION
# =========================================================
def find_col(candidates):
    exact = {str(c).lower().strip(): c for c in df.columns}

    for name in candidates:
        if name.lower() in exact:
            return exact[name.lower()]

    for name in candidates:
        for col in df.columns:
            if name.lower() in str(col).lower():
                return col

    return None


COL = {
    "date": find_col(["Date", "Booking Date"]),
    "time": find_col(["Time", "Booking Time"]),
    "status": find_col(["Booking Status", "Status"]),
    "vehicle": find_col(["Vehicle Type", "Vehicle"]),
    "value": find_col(["Booking Value", "Ride Fare", "Fare", "Revenue"]),
    "distance": find_col(["Ride Distance", "Distance"]),
    "vtat": find_col(["Avg VTAT", "VTAT"]),
    "ctat": find_col(["Avg CTAT", "CTAT"]),
    "driver_rating": find_col(["Driver Ratings", "Driver Rating"]),
    "customer_rating": find_col(["Customer Rating", "Customer Ratings"]),
    "payment": find_col(["Payment Method", "Payment Type"]),
    "customer_cancel": find_col([
        "Reason for cancelling by Customer",
        "Customer Cancellation Reason"
    ]),
    "driver_cancel": find_col([
        "Driver Cancellation Reason",
        "Reason for cancelling by Driver"
    ]),
    "incomplete_reason": find_col([
        "Incomplete Rides Reason",
        "Incomplete Ride Reason"
    ]),
    "pickup": find_col(["Pickup Location", "Pickup"]),
    "drop": find_col(["Drop Location", "Destination"])
}

for key in [
    "value", "distance", "vtat", "ctat",
    "driver_rating", "customer_rating"
]:
    col = COL[key]
    if col:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(",", "", regex=False),
            errors="coerce"
        )

# Parse dates and hours
df["_date"] = (
    pd.to_datetime(df[COL["date"]], errors="coerce", dayfirst=True)
    if COL["date"] else pd.NaT
)

df["_hour"] = np.nan

if COL["time"]:
    parsed = pd.to_datetime(
        df[COL["time"]].astype(str),
        format="mixed",
        errors="coerce"
    )
    df["_hour"] = parsed.dt.hour

if df["_hour"].notna().sum() == 0 and COL["date"]:
    parsed = pd.to_datetime(
        df[COL["date"]].astype(str),
        format="mixed",
        errors="coerce",
        dayfirst=True
    )
    df["_hour"] = parsed.dt.hour

df["_weekday"] = df["_date"].dt.day_name()

# =========================================================
# HELPER FUNCTIONS
# =========================================================
def cat(s):
    return s.astype("string").fillna("Unknown").replace("", "Unknown")


def money(v):
    return f"₹{v:,.0f}" if pd.notna(v) else "—"


def heading(title, subtitle=""):
    st.markdown(f"### {title}")
    if subtitle:
        st.caption(subtitle)


def draw(fig, height=175):
    fig.update_layout(
        template=TEMPLATE,
        height=height,
        margin=dict(l=4, r=5, t=12, b=4),
        paper_bgcolor=PLOT_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=TEXT, size=10),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="left",
            x=0,
            font=dict(size=9),
            bgcolor="rgba(0,0,0,0)"
        ),
        xaxis=dict(
            gridcolor=BORDER,
            zerolinecolor=BORDER,
            automargin=True,
            title_font=dict(size=10)
        ),
        yaxis=dict(
            gridcolor=BORDER,
            zerolinecolor=BORDER,
            automargin=True,
            title_font=dict(size=10)
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False}
    )


# =========================================================
# NAVIGATION
# =========================================================
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "NAVIGATION",
    [
        "Executive Overview",
        "Demand & Revenue",
        "Route Intelligence",
        "Cancellation Analysis",
        "Service Quality",
        "Early-Warning Model",
        "Data Explorer"
    ],
    label_visibility="visible"
)

# =========================================================
# GLOBAL FILTERS
# =========================================================
st.sidebar.markdown("---")
st.sidebar.markdown("### FILTERS")

data = df.copy()

if df["_date"].notna().any():
    low = df["_date"].min().date()
    high = df["_date"].max().date()

    date_range = st.sidebar.date_input(
        "Booking date",
        value=(low, high),
        min_value=low,
        max_value=high
    )

    if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
        start, end = date_range
        data = data[
            data["_date"].isna()
            | (
                (data["_date"].dt.date >= start)
                & (data["_date"].dt.date <= end)
            )
        ]

for key, label in [
    ("vehicle", "Vehicle"),
    ("status", "Booking status"),
    ("payment", "Payment")
]:
    col = COL[key]

    if col:
        options = sorted(cat(df[col]).unique().tolist())

        selected = st.sidebar.multiselect(
            label,
            options,
            default=options,
            key="filter_" + key
        )

        data = data[cat(data[col]).isin(selected)]

st.sidebar.caption(f"{len(data):,} / {len(df):,} records")

if data.empty:
    st.warning("No data matches your filters.")
    st.stop()

# =========================================================
# KPI CALCULATIONS
# =========================================================
if COL["status"]:
    s = cat(data[COL["status"]]).str.lower()

    completed = (
        s.str.contains("complete|success", na=False)
        & ~s.str.contains("incomplete", na=False)
    )
    cancelled = s.str.contains("cancel", na=False)
    incomplete = s.str.contains("incomplete", na=False)
    no_driver = s.str.contains("no driver|driver not found", na=False)
else:
    completed = pd.Series(False, index=data.index)
    cancelled = completed.copy()
    incomplete = completed.copy()
    no_driver = completed.copy()

n = len(data)
n_done = int(completed.sum())
n_cancel = int(cancelled.sum())
n_incomplete = int(incomplete.sum())
n_no_driver = int(no_driver.sum())

completion_rate = n_done / n * 100 if n else 0
cancel_rate = n_cancel / n * 100 if n else 0

revenue = data.loc[completed, COL["value"]].sum() if COL["value"] else np.nan
avg_fare = data.loc[completed, COL["value"]].mean() if COL["value"] and n_done else np.nan
avg_distance = data[COL["distance"]].mean() if COL["distance"] else np.nan

# =========================================================
# MAIN PAGE TITLE — NO DUPLICATE BRAND
# =========================================================
st.markdown(
    f'<div class="page-heading">{page}</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="page-subtitle">'
    'Ride demand &nbsp; · &nbsp; Revenue &nbsp; · &nbsp; Operations'
    '</div>',
    unsafe_allow_html=True
)

# =========================================================
# PAGE 1: EXECUTIVE OVERVIEW
# =========================================================
if page == "Executive Overview":

    k = st.columns(5, gap="small")

    for col, (label, value) in zip(k, [
        ("TOTAL BOOKINGS", f"{n:,}"),
        ("COMPLETED RIDES", f"{n_done:,}"),
        ("COMPLETION RATE", f"{completion_rate:.1f}%"),
        ("COMPLETED REVENUE", money(revenue)),
        ("CANCELLED RIDES", f"{n_cancel:,}")
    ]):
        col.metric(label, value)

    left, right = st.columns(2, gap="small")

    with left:
        with st.container(border=True):
            heading("Booking outcomes")

            if COL["status"]:
                x = cat(data[COL["status"]]).value_counts().reset_index()
                x.columns = ["Status", "Bookings"]

                fig = px.pie(
                    x, names="Status", values="Bookings",
                    hole=.55, color_discrete_sequence=PASTELS
                )
                fig.update_traces(textinfo="percent", textposition="inside")
                draw(fig, 175)

    with right:
        with st.container(border=True):
            heading("Booking trend")

            x = data.dropna(subset=["_date"])

            if not x.empty:
                x = x.groupby(x["_date"].dt.date).size().reset_index(name="Bookings")
                x.columns = ["Date", "Bookings"]
                x["Date"] = pd.to_datetime(x["Date"])

                fig = px.area(
                    x, x="Date", y="Bookings",
                    color_discrete_sequence=[PASTELS[0]]
                )
                draw(fig, 175)

    left, right = st.columns(2, gap="small")

    with left:
        with st.container(border=True):
            heading("Vehicle mix")

            if COL["vehicle"]:
                x = cat(data[COL["vehicle"]]).value_counts().sort_values().reset_index()
                x.columns = ["Vehicle", "Bookings"]

                fig = px.bar(
                    x, x="Bookings", y="Vehicle", orientation="h",
                    color_discrete_sequence=[PASTELS[0]]
                )
                draw(fig, 165)

    with right:
        with st.container(border=True):
            heading("Hourly demand")

            if data["_hour"].notna().any():
                x = data.dropna(subset=["_hour"]).groupby("_hour").size()
                x = x.reindex(range(24), fill_value=0).reset_index(name="Bookings")
                x["_hour"] = x["_hour"].astype(int)

                fig = px.bar(
                    x, x="_hour", y="Bookings",
                    color_discrete_sequence=[PASTELS[2]]
                )
                fig.update_layout(xaxis_title="Hour", yaxis_title="Bookings")
                draw(fig, 165)


# =========================================================
# PAGE 2: DEMAND & REVENUE
# =========================================================
elif page == "Demand & Revenue":

    k = st.columns(4, gap="small")

    for col, (label, value) in zip(k, [
        ("COMPLETED REVENUE", money(revenue)),
        ("AVERAGE FARE", money(avg_fare)),
        ("AVERAGE DISTANCE", f"{avg_distance:.1f} km" if pd.notna(avg_distance) else "—"),
        ("COMPLETED RIDES", f"{n_done:,}")
    ]):
        col.metric(label, value)

    left, right = st.columns(2, gap="small")

    with left:
        with st.container(border=True):
            heading("Hourly demand")

            if data["_hour"].notna().any():
                x = data.dropna(subset=["_hour"]).groupby("_hour").size()
                x = x.reindex(range(24), fill_value=0).reset_index(name="Bookings")
                x["_hour"] = x["_hour"].astype(int)

                fig = px.bar(
                    x, x="_hour", y="Bookings",
                    color_discrete_sequence=[PASTELS[0]]
                )
                fig.update_layout(xaxis_title="Hour", yaxis_title="Bookings")
                draw(fig, 175)

    with right:
        with st.container(border=True):
            heading("Demand by weekday")

            x = data.dropna(subset=["_weekday"])

            if not x.empty:
                order = ["Monday", "Tuesday", "Wednesday", "Thursday",
                         "Friday", "Saturday", "Sunday"]

                x = x["_weekday"].value_counts().reindex(order, fill_value=0).reset_index()
                x.columns = ["Weekday", "Bookings"]

                fig = px.bar(
                    x, x="Weekday", y="Bookings",
                    color_discrete_sequence=[PASTELS[1]]
                )
                fig.update_layout(xaxis_title=None)
                draw(fig, 175)

    left, right = st.columns(2, gap="small")

    with left:
        with st.container(border=True):
            heading("Revenue by vehicle")

            if COL["vehicle"] and COL["value"]:
                x = data.loc[completed].copy()

                if not x.empty:
                    x["_vehicle"] = cat(x[COL["vehicle"]])
                    x = x.groupby("_vehicle")[COL["value"]].sum().sort_values().reset_index()
                    x.columns = ["Vehicle", "Revenue"]

                    fig = px.bar(
                        x, x="Revenue", y="Vehicle", orientation="h",
                        color_discrete_sequence=[PASTELS[2]]
                    )
                    draw(fig, 175)

    with right:
        with st.container(border=True):
            heading("Fare vs distance")

            if COL["value"] and COL["distance"]:
                x = data.dropna(subset=[COL["value"], COL["distance"]])

                if len(x) > 1500:
                    x = x.sample(1500, random_state=42)

                fig = px.scatter(
                    x, x=COL["distance"], y=COL["value"],
                    color=COL["vehicle"] if COL["vehicle"] else None,
                    color_discrete_sequence=PASTELS,
                    opacity=.75
                )
                fig.update_layout(xaxis_title="Distance", yaxis_title="Booking value")
                draw(fig, 175)


# =========================================================
# PAGE 3: ROUTE INTELLIGENCE
# =========================================================
elif page == "Route Intelligence":

    if COL["pickup"] and COL["drop"]:

        x = data.copy()
        x["_pickup"] = cat(x[COL["pickup"]])
        x["_drop"] = cat(x[COL["drop"]])
        x["_route"] = x["_pickup"] + " → " + x["_drop"]
        x["_completed"] = completed.astype(int)

        routes = x.groupby("_route").agg(
            Bookings=("_route", "size"),
            Completed=("_completed", "sum")
        ).reset_index()

        routes["Completion rate (%)"] = routes["Completed"] / routes["Bookings"] * 100
        routes["Unsuccessful rate (%)"] = 100 - routes["Completion rate (%)"]

        max_n = max(2, int(routes["Bookings"].max()))

        min_n = st.slider(
            "Minimum bookings per route",
            1, max_n, min(5, max_n)
        )

        ranking = st.radio(
            "Rank routes by",
            ["Most bookings", "Highest unsuccessful rate"],
            horizontal=True
        )

        shown = routes[routes["Bookings"] >= min_n].copy()

        if ranking == "Most bookings":
            shown = shown.sort_values("Bookings", ascending=False)
        else:
            shown = shown.sort_values("Unsuccessful rate (%)", ascending=False)

        shown = shown.head(12)

        left, right = st.columns(2, gap="small")

        with left:
            with st.container(border=True):
                heading("Route ranking")

                fig = px.bar(
                    shown.sort_values("Bookings"),
                    x="Bookings", y="_route", orientation="h",
                    color_discrete_sequence=[PASTELS[0]]
                )
                draw(fig, 205)

        with right:
            with st.container(border=True):
                heading("Popular pickup locations")

                x = x["_pickup"].value_counts().head(12).sort_values().reset_index()
                x.columns = ["Pickup", "Bookings"]

                fig = px.bar(
                    x, x="Bookings", y="Pickup", orientation="h",
                    color_discrete_sequence=[PASTELS[1]]
                )
                draw(fig, 205)

        with st.container(border=True):
            heading("Route performance table")

            shown = shown.rename(columns={"_route": "Route"})
            shown[["Completion rate (%)", "Unsuccessful rate (%)"]] = (
                shown[["Completion rate (%)", "Unsuccessful rate (%)"]].round(1)
            )

            st.dataframe(
                shown,
                use_container_width=True,
                hide_index=True,
                height=150
            )

    else:
        st.info("Pickup Location and Drop Location columns are required.")


# =========================================================
# PAGE 4: CANCELLATION ANALYSIS
# =========================================================
elif page == "Cancellation Analysis":

    k = st.columns(4, gap="small")

    for col, (label, value) in zip(k, [
        ("CANCELLED BOOKINGS", f"{n_cancel:,}"),
        ("CANCELLATION RATE", f"{cancel_rate:.1f}%"),
        ("NO DRIVER FOUND", f"{n_no_driver:,}"),
        ("INCOMPLETE RIDES", f"{n_incomplete:,}")
    ]):
        col.metric(label, value)

    fields = [
        ("customer_cancel", "Customer cancellations"),
        ("driver_cancel", "Driver cancellations"),
        ("incomplete_reason", "Incomplete rides")
    ]

    available = [(key, label, COL[key]) for key, label in fields if COL[key]]

    if available:
        tabs = st.tabs([label for _, label, _ in available])

        for tab, (key, label, col) in zip(tabs, available):
            with tab:
                vals = cat(data[col])
                vals = vals[
                    ~vals.str.lower().isin(
                        ["unknown", "nan", "none", "", "n/a", "not applicable"]
                    )
                ]

                if vals.empty:
                    st.info("No recorded reasons for this selection.")
                    continue

                left, right = st.columns(2, gap="small")

                with left:
                    with st.container(border=True):
                        heading("Most common reasons")

                        x = vals.value_counts().head(8).sort_values().reset_index()
                        x.columns = ["Reason", "Bookings"]

                        fig = px.bar(
                            x, x="Bookings", y="Reason", orientation="h",
                            color_discrete_sequence=[PASTELS[3]]
                        )
                        draw(fig, 205)

                with right:
                    with st.container(border=True):
                        heading("Reason distribution")

                        x = vals.value_counts().head(6).reset_index()
                        x.columns = ["Reason", "Bookings"]

                        fig = px.pie(
                            x, names="Reason", values="Bookings",
                            hole=.52, color_discrete_sequence=PASTELS
                        )
                        draw(fig, 205)

    else:
        st.info("Cancellation-reason columns were not found.")


# =========================================================
# PAGE 5: SERVICE QUALITY
# =========================================================
elif page == "Service Quality":

    driver_rating = data[COL["driver_rating"]].mean() if COL["driver_rating"] else np.nan
    customer_rating = data[COL["customer_rating"]].mean() if COL["customer_rating"] else np.nan
    vtat = data[COL["vtat"]].mean() if COL["vtat"] else np.nan
    ctat = data[COL["ctat"]].mean() if COL["ctat"] else np.nan

    k = st.columns(4, gap="small")

    for col, (label, value) in zip(k, [
        ("DRIVER RATING", f"{driver_rating:.2f}" if pd.notna(driver_rating) else "—"),
        ("CUSTOMER RATING", f"{customer_rating:.2f}" if pd.notna(customer_rating) else "—"),
        ("AVERAGE VTAT", f"{vtat:.1f} min" if pd.notna(vtat) else "—"),
        ("AVERAGE CTAT", f"{ctat:.1f} min" if pd.notna(ctat) else "—")
    ]):
        col.metric(label, value)

    left, right = st.columns(2, gap="small")

    with left:
        with st.container(border=True):
            heading("Rating distribution")

            rating_col = COL["customer_rating"] or COL["driver_rating"]

            if rating_col and data[rating_col].notna().any():
                x = data[rating_col].dropna().round(1).value_counts().sort_index().reset_index()
                x.columns = ["Rating", "Count"]

                fig = px.bar(
                    x, x="Rating", y="Count",
                    color_discrete_sequence=[PASTELS[0]]
                )
                draw(fig, 175)
            else:
                st.info("Rating data is unavailable.")

    with right:
        with st.container(border=True):
            heading("Waiting-time indicators")

            vals = []
            if pd.notna(vtat):
                vals.append({"Metric": "VTAT", "Minutes": vtat})
            if pd.notna(ctat):
                vals.append({"Metric": "CTAT", "Minutes": ctat})

            if vals:
                fig = px.bar(
                    pd.DataFrame(vals),
                    x="Metric", y="Minutes", color="Metric",
                    color_discrete_sequence=PASTELS[:2]
                )
                draw(fig, 175)
            else:
                st.info("Waiting-time data is unavailable.")

    left, right = st.columns(2, gap="small")

    for box, key, title, color in [
        (left, "pickup", "Top pickup locations", PASTELS[1]),
        (right, "drop", "Top destinations", PASTELS[4])
    ]:
        with box:
            with st.container(border=True):
                heading(title)

                if COL[key]:
                    x = cat(data[COL[key]]).value_counts().head(8).sort_values().reset_index()
                    x.columns = ["Location", "Bookings"]

                    fig = px.bar(
                        x, x="Bookings", y="Location", orientation="h",
                        color_discrete_sequence=[color]
                    )
                    draw(fig, 175)
                else:
                    st.info("Location data is unavailable.")


# =========================================================
# PAGE 6: EARLY-WARNING MODEL
# =========================================================
elif page == "Early-Warning Model":

    st.caption("Prototype model for estimating ride-completion probability.")

    st.warning(
        "Use only features available at prediction time. "
        "Validate on future bookings before considering operational use."
    )

    if not COL["status"]:
        st.info("Booking Status is required.")
    else:
        from sklearn.model_selection import train_test_split
        from sklearn.compose import ColumnTransformer
        from sklearn.preprocessing import OneHotEncoder
        from sklearn.impute import SimpleImputer
        from sklearn.pipeline import Pipeline
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import (
            accuracy_score, precision_score, recall_score,
            f1_score, roc_auc_score, confusion_matrix
        )

        md = data.copy()
        s = cat(md[COL["status"]]).str.lower()

        md["_target"] = (
            s.str.contains("complete|success", na=False)
            & ~s.str.contains("incomplete", na=False)
        ).astype(int)

        # Avoid post-booking outcome and performance fields
        features = [
            COL[key]
            for key in ["vehicle", "time", "pickup", "drop"]
            if COL[key]
        ]

        if COL["date"]:
            md["_hour_feature"] = md["_hour"]
            md["_weekday_feature"] = md["_weekday"].fillna("Unknown")
            features += ["_hour_feature", "_weekday_feature"]

        features = list(dict.fromkeys(features))

        if not features or md["_target"].nunique() < 2:
            st.info("Predictors and both outcome classes are required.")
        elif int(md["_target"].value_counts().min()) < 2:
            st.info("Too few records in one outcome class.")
        else:
            choice = st.radio(
                "Model",
                ["Random Forest", "Logistic Regression"],
                horizontal=True
            )

            if st.button("Train and evaluate", type="primary"):
                X = md[features].copy()
                y = md["_target"].astype(int)

                cats = [
                    c for c in X.columns
                    if (
                        X[c].dtype == "object"
                        or str(X[c].dtype).startswith("string")
                        or X[c].dtype == "category"
                    )
                ]
                nums = [c for c in X.columns if c not in cats]

                for c in cats:
                    X[c] = X[c].astype("string").fillna("Unknown").astype(str)

                transformers = []

                if nums:
                    transformers.append((
                        "numeric", SimpleImputer(strategy="median"), nums
                    ))

                if cats:
                    cat_pipe = Pipeline([
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(
                            handle_unknown="ignore",
                            min_frequency=5
                        ))
                    ])
                    transformers.append(("categorical", cat_pipe, cats))

                prep = ColumnTransformer(transformers)

                if choice == "Random Forest":
                    clf = RandomForestClassifier(
                        n_estimators=100,
                        max_depth=12,
                        min_samples_leaf=3,
                        class_weight="balanced",
                        random_state=42,
                        n_jobs=-1
                    )
                else:
                    clf = LogisticRegression(
                        max_iter=1000,
                        class_weight="balanced"
                    )

                model = Pipeline([
                    ("preprocessor", prep),
                    ("classifier", clf)
                ])

                X_train, X_test, y_train, y_test = train_test_split(
                    X, y,
                    test_size=.25,
                    random_state=42,
                    stratify=y
                )

                with st.spinner("Training model..."):
                    model.fit(X_train, y_train)
                    pred = model.predict(X_test)
                    prob = model.predict_proba(X_test)[:, 1]

                auc = roc_auc_score(y_test, prob) if y_test.nunique() == 2 else np.nan

                metrics = [
                    ("Accuracy", accuracy_score(y_test, pred) * 100),
                    ("Precision", precision_score(y_test, pred, zero_division=0) * 100),
                    ("Recall", recall_score(y_test, pred, zero_division=0) * 100),
                    ("F1 score", f1_score(y_test, pred, zero_division=0) * 100),
                    ("ROC-AUC", auc * 100 if pd.notna(auc) else np.nan)
                ]

                k = st.columns(5)
                for col, (label, value) in zip(k, metrics):
                    col.metric(label, f"{value:.1f}%" if pd.notna(value) else "—")

                with st.container(border=True):
                    heading("Confusion matrix")

                    cm = confusion_matrix(y_test, pred, labels=[0, 1])
                    fig = px.imshow(
                        cm,
                        text_auto=True,
                        x=["Not completed", "Completed"],
                        y=["Not completed", "Completed"],
                        color_continuous_scale=["#F4A7BB", "#78B7E0"]
                    )
                    fig.update_layout(coloraxis_showscale=False)
                    draw(fig, 190)

                st.session_state["ride_model"] = model
                st.session_state["ride_features"] = features
                st.session_state["ride_cats"] = cats
                st.session_state["ride_md"] = md

                st.success("Model evaluation completed.")

            if (
                "ride_model" in st.session_state
                and st.session_state.get("ride_features") == features
            ):
                st.markdown("#### Test a sample booking")

                model = st.session_state["ride_model"]
                md2 = st.session_state["ride_md"]
                saved_cats = st.session_state["ride_cats"]

                sample = {}
                cols = st.columns(3)

                for i, col in enumerate(features):
                    with cols[i % 3]:
                        if col in saved_cats:
                            opts = sorted(cat(md2[col]).unique().tolist())
                            sample[col] = st.selectbox(
                                col, opts, key="test_cat_" + col
                            )
                        else:
                            series = pd.to_numeric(md2[col], errors="coerce")
                            default = float(series.median()) if series.notna().any() else 0.0
                            sample[col] = st.number_input(
                                col, value=default, key="test_num_" + col
                            )

                if st.button("Estimate completion probability"):
                    p = model.predict_proba(
                        pd.DataFrame([sample], columns=features)
                    )[0, 1]

                    a, b = st.columns(2)
                    a.metric("Completion probability", f"{p * 100:.1f}%")
                    b.metric("Non-completion risk", f"{(1-p) * 100:.1f}%")


# =========================================================
# PAGE 7: DATA EXPLORER
# =========================================================
elif page == "Data Explorer":

    a, b, c = st.columns(3)

    a.metric("ROWS", f"{len(data):,}")
    b.metric("COLUMNS", f"{len(df.columns):,}")
    c.metric("MISSING CELLS", f"{int(data.isna().sum().sum()):,}")

    with st.container(border=True):
        heading("Booking records")

        search = st.text_input(
            "Search",
            placeholder="Location, vehicle, status, payment..."
        )

        shown = data.drop(
            columns=["_date", "_hour", "_weekday"],
            errors="ignore"
        ).copy()

        if search:
            text_cols = shown.select_dtypes(
                include=["object", "string"]
            ).columns

            mask = pd.Series(False, index=shown.index)

            for col in text_cols:
                mask |= shown[col].astype(str).str.contains(
                    search, case=False, na=False
                )

            shown = shown[mask]

        st.dataframe(
            shown,
            use_container_width=True,
            height=245,
            hide_index=True
        )

        st.download_button(
            "Download filtered CSV",
            data=shown.to_csv(index=False).encode("utf-8"),
            file_name="ncr_ride_bookings_filtered.csv",
            mime="text/csv"
        )

    with st.container(border=True):
        heading("Data quality")

        quality = pd.DataFrame({
            "Column": data.columns,
            "Type": [str(data[c].dtype) for c in data.columns],
            "Missing": [int(data[c].isna().sum()) for c in data.columns],
            "Missing (%)": [
                round(data[c].isna().mean() * 100, 1)
                for c in data.columns
            ]
        }).sort_values("Missing (%)", ascending=False)

        st.dataframe(
            quality,
            use_container_width=True,
            height=150,
            hide_index=True
        )


# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.caption("NCR Ride Intelligence · Ride booking analytics")
