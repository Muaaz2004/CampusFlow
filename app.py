
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import textwrap


from src.ml.prediction_service import (
    load_model,
    predict_demand
)

from src.streaming.dashboard_stream_reader import (
    get_streaming_data
)

@st.cache_resource
def get_prediction_resources():
    return load_model()

@st.cache_data(ttl=10, show_spinner=False)
def get_cached_streaming_data():
    return get_streaming_data()

@st.fragment(run_every="5s")

def live_monitoring_content():

    # ----------------------------------------
    # PAGE HEADER
    # ----------------------------------------

    st.markdown("""
    <div class="aurora-section-label">REAL-TIME CAMPUS MOBILITY</div>
    <div class="section-heading">Live Shuttle Monitoring</div>
    <div class="section-description">
        Monitor boarding and alighting events processed through
        Apache Kafka and Spark Structured Streaming.
    </div>
    """, unsafe_allow_html=True)

    # ----------------------------------------
    # MANUAL REFRESH
    # ----------------------------------------

    col1, col2 = st.columns([5, 1])

    with col1:
        st.caption(
            "Streaming records are automatically refreshed every 5 seconds."
        )

    with col2:
        if st.button(
            "Refresh Now",
            key="manual_stream_refresh",
            use_container_width=True
        ):
            get_cached_streaming_data.clear()

    # ----------------------------------------
    # LOAD STREAMING DATA
    # ----------------------------------------

    summary, events, metrics = get_cached_streaming_data()

    if summary is None or events is None or metrics is None:

        st.warning(
            "Streaming data is currently unavailable. "
            "Check the Kafka-to-Parquet pipeline."
        )
        return

    # ----------------------------------------
    # FILTER INVALID ROUTE RECORDS
    # ----------------------------------------

    valid_summary = summary[
        summary["route_id"].notna()
    ].copy()

    valid_events = events[
        events["route_id"].notna()
    ].copy()

    # ----------------------------------------
    # STREAMING KPI CARDS
    # ----------------------------------------

    st.markdown("""
    <div class="aurora-section-label">STREAMING OVERVIEW</div>
    <div class="section-heading">Network Activity</div>
    """, unsafe_allow_html=True)

    kpi_items = [
        (
            "TOTAL EVENTS",
            f'{metrics["total_events"]:,}',
            "#FFAD7A"
        ),
        (
            "UNIQUE EVENTS",
            f'{metrics["unique_events"]:,}',
            "#B69CFF"
        ),
        (
            "ACTIVE ROUTES",
            f'{metrics["active_routes"]:,}',
            "#38DDE0"
        ),
        (
            "BOARDING PASSENGERS",
            f'{int(metrics["boarding_passengers"]):,}',
            "#5DD6A0"
        )
    ]

    
    cols = st.columns(4)

    for col, (label, value, accent) in zip(cols, kpi_items):

        with col:

            st.html(f"""
        <div style="
            background: linear-gradient(145deg, rgba(255,255,255,0.09), rgba(255,255,255,0.035));
            border: 1px solid rgba(255,255,255,0.12);
            border-top: 3px solid {accent};
            border-radius: 13px;
            padding: 19px;
            min-height: 112px;
        ">
            <div style="
                color: #A9ADC3;
                font-size: 10px;
                font-weight: 800;
                letter-spacing: 1px;
            ">{label}</div>

            <div style="
                color: #FFFFFF;
                font-size: 29px;
                font-weight: 900;
                margin-top: 12px;
            ">{value}</div>
        </div>
        """)

    st.divider()

    # ----------------------------------------
    # ROUTE-WISE EVENT SUMMARY
    # ----------------------------------------

    st.markdown("""
    <div class="aurora-section-label">ROUTE PERFORMANCE</div>
    <div class="section-heading">Route-wise Event Summary</div>
    <div class="section-description">
        Compare boarding and alighting activity across campus routes.
    </div>
    """, unsafe_allow_html=True)

    if not valid_summary.empty:

        summary_display = valid_summary.copy()

        summary_display["passenger_total"] = (
            summary_display["passenger_total"].abs()
        )

        summary_display = summary_display.rename(columns={
            "route_id": "Route",
            "event_type": "Event Type",
            "event_count": "Total Events",
            "passenger_total": "Passenger Count"
        })

        st.dataframe(
            summary_display,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No route-wise event records are available yet.")

    # ----------------------------------------
    # BOARDING VS ALIGHTING CHART
    # ----------------------------------------

    st.markdown("""
    <div class="aurora-section-label">PASSENGER ACTIVITY</div>
    <div class="section-heading">Boarding vs Alighting</div>
    <div class="section-description">
        Visualize passenger movement across the shuttle network.
    </div>
    """, unsafe_allow_html=True)

    if not valid_summary.empty:

        event_chart = valid_summary.copy()

        event_chart["passenger_total"] = (
            event_chart["passenger_total"].abs()
        )

        fig = px.bar(
            event_chart,
            x="route_id",
            y="passenger_total",
            color="event_type",
            barmode="group",
            text_auto=True,
            labels={
                "route_id": "Shuttle Route",
                "passenger_total": "Passengers",
                "event_type": "Event Type"
            },
            color_discrete_map={
                "BOARD": "#FFAD7A",
                "ALIGHT": "#B69CFF"
            }
        )

        fig.update_layout(
            template="plotly_dark",
            height=420,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(12,15,29,0.65)",
            font=dict(
                family="Arial",
                color="#E8EAF6",
                size=12
            ),
            margin=dict(l=25, r=25, t=35, b=25),
            legend_title_text="Event Type",
            xaxis=dict(
                title="Shuttle Route",
                showgrid=False
            ),
            yaxis=dict(
                title="Passenger Count",
                gridcolor="rgba(255,255,255,0.10)",
                zeroline=False
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info("The passenger activity chart will appear when events arrive.")

    st.divider()

    # ----------------------------------------
    # RECENT SHUTTLE EVENTS
    # ----------------------------------------

    st.markdown("""
    <div class="aurora-section-label">EVENT LOG</div>
    <div class="section-heading">Recent Shuttle Events</div>
    <div class="section-description">
        Inspect the latest persisted shuttle events received by the system.
    </div>
    """, unsafe_allow_html=True)

    if not valid_events.empty:

        st.dataframe(
            valid_events,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No recent events with valid route information are available.")

    st.caption(
        "Automatic refresh: every 5 seconds. "
        "Event records are retrieved from persisted Kafka/Spark "
        "streaming data. The recent event table displays up to 20 records."
    )



# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="CampusFlow | Shuttle Analytics",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --------------------------------------------------
# 2. CAMPUSFLOW AURORA - PREMIUM GLASSMORPHISM
# --------------------------------------------------

st.markdown("""
<style>

/* GLOBAL BACKGROUND */

.stApp {
    background:
        radial-gradient(
            ellipse at 10% 0%,
            rgba(255, 157, 87, 0.13),
            transparent 35%
        ),
        radial-gradient(
            ellipse at 90% 5%,
            rgba(167, 139, 250, 0.15),
            transparent 35%
        ),
        linear-gradient(
            135deg,
            #101426 0%,
            #15172D 50%,
            #101426 100%
        );

    color: #F3F4FA;
}

/* MAIN CONTENT */

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1600px;
}

/* SIDEBAR */

section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #17182E 0%,
        #101426 100%
    );

    border-right: 1px solid rgba(167, 139, 250, 0.2);
}

section[data-testid="stSidebar"] h1 {
    color: #FFAD73;
    font-size: 27px;
    font-weight: 800;
}

section[data-testid="stSidebar"] p {
    color: #AEB4CA;
}

section[data-testid="stSidebar"] label {
    color: #F3F4FA;
}

/* HEADINGS */

h1, h2, h3 {
    color: #F3F4FA !important;
    font-weight: 700 !important;
}

.main-title {
    font-size: 38px;
    font-weight: 800;

    background: linear-gradient(
        90deg,
        #FFAD73,
        #C4A7FF,
        #42D9E8
    );

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.sub-title {
    font-size: 15px;
    color: #AEB4CA;
    margin-top: 6px;
}

/* GLASS KPI CARDS */

div[data-testid="stMetric"] {
    background: linear-gradient(
        145deg,
        rgba(255, 255, 255, 0.09),
        rgba(255, 255, 255, 0.025)
    );

    border: 1px solid rgba(255, 255, 255, 0.13);
    border-radius: 15px;

    padding: 19px;

    box-shadow:
        0 8px 28px rgba(0, 0, 0, 0.22),
        inset 0 1px 0 rgba(255, 255, 255, 0.05);

    backdrop-filter: blur(14px);
}

div[data-testid="stMetricLabel"] {
    color: #B8BED2;
}

div[data-testid="stMetricValue"] {
    color: #FFFFFF;
    font-weight: 750;
}

div[data-testid="stMetricDelta"] {
    color: #42D9E8;
}

/* BUTTONS */

.stButton button,
.stFormSubmitButton button {
    background: linear-gradient(
        110deg,
        #E98B55,
        #A78BFA
    );

    color: #FFFFFF;
    border: none;
    border-radius: 9px;

    font-weight: 650;
    transition: all 0.2s ease;
}

.stButton button:hover,
.stFormSubmitButton button:hover {
    filter: brightness(1.13);
    transform: translateY(-1px);
    color: #FFFFFF;
}

/* INPUT FIELDS */

.stSelectbox div[data-baseweb="select"] > div,
.stNumberInput input,
.stDateInput input {
    background-color: #20223C;
    color: #F3F4FA;
    border-color: rgba(167, 139, 250, 0.3);
    border-radius: 8px;
}

/* DATA TABLES */

div[data-testid="stDataFrame"] {
    border: 1px solid rgba(167, 139, 250, 0.2);
    border-radius: 12px;
    overflow: hidden;
}

/* DIVIDERS */

hr {
    border-color: rgba(255, 255, 255, 0.12);
}

/* CAPTIONS */

div[data-testid="stCaptionContainer"] {
    color: #929BB5;
}

/* ALERTS */

div[data-testid="stAlert"] {
    border-radius: 10px;
}

/* CHECKBOXES AND SLIDERS */

.stCheckbox label,
.stSlider label {
    color: #E2E5F0;
}

/* LINKS */

a {
    color: #42D9E8 !important;
}

/* SMOOTH TRANSITIONS */

div[data-testid="stMetric"],
div[data-testid="stDataFrame"] {
    transition: border-color 0.2s ease,
                box-shadow 0.2s ease;
}

div[data-testid="stMetric"]:hover {
    border-color: rgba(255, 157, 87, 0.45);

    box-shadow:
        0 10px 32px rgba(0, 0, 0, 0.3),
        0 0 14px rgba(167, 139, 250, 0.08);
}

/* =========================================
   AURORA OVERVIEW - HERO SECTION
========================================= */

.aurora-hero {
    position: relative;
    overflow: hidden;
    min-height: 245px;
    padding: 34px 38px;
    margin: 12px 0 28px 0;

    border: 1px solid rgba(255,255,255,0.16);
    border-radius: 22px;

    background:
        radial-gradient(
            circle at 82% 15%,
            rgba(255,177,115,0.35),
            transparent 25%
        ),
        radial-gradient(
            circle at 70% 85%,
            rgba(167,139,250,0.28),
            transparent 35%
        ),
        linear-gradient(
            115deg,
            #20213D 0%,
            #35264D 48%,
            #8B5262 100%
        );

    box-shadow: 0 18px 45px rgba(0,0,0,0.22);
}

.aurora-hero::before {
    content: "";
    position: absolute;
    width: 175px;
    height: 175px;
    right: 9%;
    top: 20px;
    border-radius: 50%;

    background: linear-gradient(
        145deg,
        #FFD39B,
        #FF936F
    );

    box-shadow: 0 0 65px rgba(255,157,87,0.3);
    opacity: 0.9;
}

.aurora-hero::after {
    content: "";
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    height: 65px;

    background: linear-gradient(
        180deg,
        transparent,
        rgba(15,18,39,0.65)
    );
}

.hero-content {
    position: relative;
    z-index: 2;
    max-width: 650px;
}

.hero-eyebrow {
    color: #FFD2B0;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 14px;
}

.hero-heading {
    color: #FFFFFF;
    font-size: 38px;
    font-weight: 850;
    line-height: 1.15;
    margin-bottom: 12px;
}

.hero-description {
    color: #F0DCE6;
    font-size: 14px;
    line-height: 1.7;
    max-width: 570px;
}

.hero-status {
    display: inline-block;
    margin-top: 18px;
    padding: 7px 13px;
    border-radius: 30px;

    color: #D7FFE9;
    background: rgba(35,190,125,0.15);
    border: 1px solid rgba(100,230,165,0.4);

    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
}

/* =========================================
   OVERVIEW MODULE CARDS
========================================= */

.module-card {
    height: 145px;
    padding: 20px;
    margin-bottom: 15px;

    background: linear-gradient(
        145deg,
        rgba(255,255,255,0.085),
        rgba(255,255,255,0.025)
    );

    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 15px;

    box-shadow: 0 8px 24px rgba(0,0,0,0.15);
    transition: all 0.2s ease;
}

.module-card:hover {
    border-color: rgba(255,173,115,0.55);
    transform: translateY(-3px);
    background: rgba(255,255,255,0.09);
}

.module-icon {
    font-size: 23px;
    margin-bottom: 10px;
}

.module-title {
    color: #FFFFFF;
    font-size: 16px;
    font-weight: 750;
    margin-bottom: 7px;
}

.module-description {
    color: #B9BBD0;
    font-size: 12px;
    line-height: 1.55;
}

.overview-section-title {
    color: #F5EFFF;
    font-size: 21px;
    font-weight: 750;
    margin: 10px 0 17px 0;
}

.overview-note {
    color: #A9A9C0;
    font-size: 11px;
    padding: 14px 0;
    border-top: 1px solid rgba(255,255,255,0.1);
}


/* =========================================
   AURORA PREMIUM KPI CARDS
========================================= */

.aurora-kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 16px;
    margin: 12px 0 26px 0;
}

.aurora-kpi-card {
    position: relative;
    overflow: hidden;
    min-height: 132px;
    padding: 21px;

    background: linear-gradient(
        145deg,
        rgba(255,255,255,0.105),
        rgba(255,255,255,0.035)
    );

    border: 1px solid rgba(255,255,255,0.13);
    border-radius: 16px;

    backdrop-filter: blur(16px);
    box-shadow: 0 9px 25px rgba(0,0,0,0.16);

    transition: transform 0.2s ease, border-color 0.2s ease;
}

.aurora-kpi-card:hover {
    transform: translateY(-4px);
    border-color: var(--accent);
}

.aurora-kpi-card::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 3px;
    background: var(--accent);
}

.aurora-kpi-icon {
    font-size: 23px;
    margin-bottom: 13px;
}

.aurora-kpi-value {
    color: #FFFFFF;
    font-size: 31px;
    line-height: 1.1;
    font-weight: 800;
    letter-spacing: -0.8px;
}

.aurora-kpi-label {
    color: #B9BED1;
    font-size: 12px;
    font-weight: 600;
    margin-top: 7px;
    letter-spacing: 0.3px;
}

@media (max-width: 850px) {
    .aurora-kpi-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

@media (max-width: 480px) {
    .aurora-kpi-grid {
        grid-template-columns: 1fr;
    }
}


/* =========================================
   AURORA SIDEBAR NAVIGATION
========================================= */

section[data-testid="stSidebar"] {
    background:
        radial-gradient(
            circle at 10% 5%,
            rgba(167,139,250,0.12),
            transparent 35%
        ),
        linear-gradient(
            180deg,
            #19182F,
            #111426 75%
        );

    border-right: 1px solid rgba(167,139,250,0.20);
}

/* Brand area */

section[data-testid="stSidebar"] h1 {
    color: #FFAD82 !important;
    font-size: 27px !important;
    font-weight: 800 !important;
    letter-spacing: -0.7px;
}

section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
    color: #A9ABC3 !important;
}

/* Navigation heading */

section[data-testid="stSidebar"] .stRadio > label {
    color: #FFB68D !important;
    font-size: 12px !important;
    font-weight: 750 !important;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 12px;
}

/* Navigation options */

section[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 7px;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label {
    padding: 9px 11px;
    border-radius: 9px;
    border: 1px solid transparent;
    transition: all 0.2s ease;
}

/* Hover */

section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: rgba(167,139,250,0.10);
    border-color: rgba(167,139,250,0.22);
}

/* Selected navigation item */

section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    background: linear-gradient(
        100deg,
        rgba(255,157,87,0.19),
        rgba(167,139,250,0.16)
    );

    border: 1px solid rgba(255,173,130,0.42);
    box-shadow: 0 4px 15px rgba(0,0,0,0.12);
}

/* Navigation text */

section[data-testid="stSidebar"] div[role="radiogroup"] label p {
    color: #E7E5F3 !important;
    font-size: 13px;
    font-weight: 550;
}

/* Radio selection colour */

section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {
    color: #FFD0AE !important;
    font-weight: 750;
}

/* Synthetic dataset information panel */

section[data-testid="stSidebar"] div[data-testid="stAlert"] {
    background: linear-gradient(
        135deg,
        rgba(255,157,87,0.10),
        rgba(167,139,250,0.12)
    );

    border: 1px solid rgba(255,173,130,0.25);
    border-radius: 12px;
}

/* Sidebar dividers */

section[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.12);
}

/* Sidebar footer */

section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
    color: #A9ABC3;
}


/* =========================================
   AURORA ROUTES & STOPS PAGE
========================================= */

.section-eyebrow {
    color: #FFB58C;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 2px;
    margin-bottom: 9px;
}

.section-heading {
    color: #FFFFFF;
    font-size: 27px;
    font-weight: 800;
    letter-spacing: -0.7px;
    margin-bottom: 7px;
}

.section-description {
    color: #AFAFC9;
    font-size: 13px;
    line-height: 1.7;
}

.aurora-section-label {
    color: #FFB58C;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1.8px;
    margin-bottom: 13px;
}

/* Route information banner */

.aurora-route-banner {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 20px;
    padding: 27px 30px;
    margin-top: 22px;

    background: linear-gradient(
        115deg,
        rgba(85, 63, 120, 0.62),
        rgba(190, 103, 116, 0.34),
        rgba(255, 166, 112, 0.20)
    );

    border: 1px solid rgba(255, 190, 170, 0.24);
    border-radius: 18px;
    backdrop-filter: blur(18px);
    box-shadow: 0 12px 32px rgba(0,0,0,0.14);
}

.aurora-route-name {
    color: #FFFFFF;
    font-size: 28px;
    font-weight: 800;
    margin-top: 7px;
}

.aurora-route-id {
    color: #D1C4E9;
    font-size: 12px;
    margin-top: 5px;
    letter-spacing: 1px;
}

.aurora-route-distance {
    color: #FFFFFF;
    font-size: 36px;
    font-weight: 800;
    white-space: nowrap;
}

.aurora-route-distance span {
    color: #FFD0B3;
    font-size: 13px;
    letter-spacing: 2px;
}

/* Route detail cards */

.aurora-detail-card {
    min-height: 105px;
    padding: 20px;
    border-radius: 15px;

    background: linear-gradient(
        145deg,
        rgba(255,255,255,0.09),
        rgba(255,255,255,0.025)
    );

    border: 1px solid rgba(255,255,255,0.12);
    border-left: 3px solid var(--accent);
    backdrop-filter: blur(14px);
    box-shadow: 0 7px 22px rgba(0,0,0,0.12);
}

.aurora-detail-label {
    color: #AAA9C4;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1.2px;
    margin-bottom: 12px;
}

.aurora-detail-value {
    color: #FFFFFF;
    font-size: 19px;
    font-weight: 750;
    overflow-wrap: anywhere;
}

/* Connected route timeline */

.aurora-timeline {
    position: relative;
    padding: 12px 8px 12px 5px;
    margin: 18px 0 25px 0;
}

.aurora-timeline::before {
    content: "";
    position: absolute;
    left: 20px;
    top: 31px;
    bottom: 32px;
    width: 2px;
    background: linear-gradient(
        to bottom,
        #FFAD7A,
        #B69CFF,
        #38DDE0
    );
    opacity: 0.65;
}

.aurora-timeline-item {
    position: relative;
    display: flex;
    align-items: flex-start;
    gap: 19px;
    margin-bottom: 17px;
}

.aurora-timeline-marker {
    position: relative;
    z-index: 1;
    flex-shrink: 0;

    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;

    border-radius: 50%;
    background: linear-gradient(135deg, #FFAD7A, #B69CFF);
    color: #20172D;
    font-size: 12px;
    font-weight: 900;
    box-shadow: 0 0 17px rgba(255,173,122,0.20);
}

.aurora-timeline-content {
    flex: 1;
    padding: 13px 17px;
    border-radius: 12px;

    background: linear-gradient(
        120deg,
        rgba(255,255,255,0.075),
        rgba(255,255,255,0.025)
    );

    border: 1px solid rgba(255,255,255,0.09);
    transition: border-color 0.2s ease,
                transform 0.2s ease;
}

.aurora-timeline-content:hover {
    border-color: rgba(255,173,122,0.55);
    transform: translateX(4px);
}

.aurora-timeline-name {
    color: #FFFFFF;
    font-size: 15px;
    font-weight: 750;
}

.aurora-timeline-meta {
    color: #B7B2D0;
    font-size: 11px;
    margin-top: 5px;
}

.aurora-timeline-distance {
    color: #FFBD98;
    font-size: 11px;
    font-weight: 650;
    margin-top: 8px;
}

/* Responsive layout */

@media (max-width: 768px) {

    .section-heading {
        font-size: 22px;
    }

    .aurora-route-banner {
        padding: 20px;
    }

    .aurora-route-name {
        font-size: 22px;
    }

    .aurora-route-distance {
        font-size: 27px;
    }

    .aurora-detail-card {
        margin-bottom: 10px;
    }

    .aurora-kpi-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}



</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 3. SIDEBAR
# --------------------------------------------------



st.sidebar.markdown("""<div style="padding: 12px 0 18px 0;">
    <div style="
        font-size: 27px;
        font-weight: 850;
        letter-spacing: -0.8px;
        background: linear-gradient(90deg, #FFAD82, #C4A7FF, #42D9E8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    ">🚌 CampusFlow</div>
    <div style="
        color: #A9ABC3;
        font-size: 11px;
        letter-spacing: 0.5px;
        margin-top: 6px;
    ">INTELLIGENT CAMPUS MOBILITY</div>
</div>""", unsafe_allow_html=True)


st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    [
        "Overview",
        "Routes & Stops",
        "Demand Analytics",
        "Demand Prediction",
        "Live Monitoring",
        "Network Analysis"
    ]
)

st.sidebar.divider()

st.sidebar.info(
    "CampusFlow uses a synthetic campus shuttle "
    "dataset for development and demonstration."
)


# --------------------------------------------------
# 4. MAIN HEADER
# --------------------------------------------------

# Overview has its own Aurora hero banner.
# Keep the standard header on the remaining pages.

if page != "Overview":

    st.markdown(
        '<div class="main-title">CampusFlow Dashboard</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sub-title">'
        'Intelligent Campus Shuttle Analytics, '
        'Real-Time Monitoring and Passenger Demand Prediction'
        '</div>',
        unsafe_allow_html=True
    )

    st.divider()


# --------------------------------------------------
# 5. PAGE CONTENT
# --------------------------------------------------


if page == "Overview":

    # -----------------------------------------
    # AURORA HERO BANNER
    # -----------------------------------------

    
    st.html("""
    <div class="aurora-hero">
        <div class="hero-content">

            <div class="hero-eyebrow">
                CAMPUS MOBILITY INTELLIGENCE PLATFORM
            </div>

            <div class="hero-heading">
                Move Smarter.<br>
                Connect Better.
            </div>

            <div class="hero-description">
                Welcome to CampusFlow — an intelligent campus
                shuttle analytics platform combining big data,
                real-time event processing and machine learning
                to understand campus transportation.
            </div>

            <div class="hero-status">
                ● SYSTEM OVERVIEW &nbsp; | &nbsp; DEMO ENVIRONMENT
            </div>

        </div>
    </div>
    """)

    # -----------------------------------------
    # CAMPUS NETWORK METRICS
    # -----------------------------------------

    st.markdown(
        '<div class="overview-section-title">'
        'Campus Network at a Glance'
        '</div>',
        unsafe_allow_html=True
    )

    
    st.html("""
    <div class="aurora-kpi-grid">

        <div class="aurora-kpi-card"
            style="--accent: #FF9D57;">
            <div class="aurora-kpi-icon">🚌</div>
            <div class="aurora-kpi-value">4</div>
            <div class="aurora-kpi-label">TOTAL ROUTES</div>
        </div>

        <div class="aurora-kpi-card"
            style="--accent: #A78BFA;">
            <div class="aurora-kpi-icon">📍</div>
            <div class="aurora-kpi-value">12</div>
            <div class="aurora-kpi-label">CAMPUS STOPS</div>
        </div>

        <div class="aurora-kpi-card"
            style="--accent: #42D9E8;">
            <div class="aurora-kpi-icon">📊</div>
            <div class="aurora-kpi-value">30,000</div>
            <div class="aurora-kpi-label">HISTORICAL TRIPS</div>
        </div>

        <div class="aurora-kpi-card"
            style="--accent: #5DD6A0;">
            <div class="aurora-kpi-icon">🚍</div>
            <div class="aurora-kpi-value">6</div>
            <div class="aurora-kpi-label">SHUTTLE FLEET</div>
        </div>

    </div>
    """)


    st.divider()

    # -----------------------------------------
    # PROJECT MODULES
    # -----------------------------------------

    st.markdown(
        '<div class="overview-section-title">'
        'Explore CampusFlow'
        '</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2, gap="large")

    with col1:

        st.markdown("""
        <div class="module-card">
            <div class="module-icon">📊</div>
            <div class="module-title">Historical Analytics</div>
            <div class="module-description">
                Discover passenger demand, hourly patterns,
                route utilization and historical trends.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="module-card">
            <div class="module-icon">🧠</div>
            <div class="module-title">Demand Prediction</div>
            <div class="module-description">
                Estimate future passenger demand using
                the trained PySpark MLlib model.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="module-card">
            <div class="module-icon">🗺️</div>
            <div class="module-title">Network Intelligence</div>
            <div class="module-description">
                Explore campus connectivity, stop degrees
                and GraphX PageRank analysis.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:

        st.markdown("""
        <div class="module-card">
            <div class="module-icon">📡</div>
            <div class="module-title">Real-Time Monitoring</div>
            <div class="module-description">
                Monitor shuttle events processed through
                Kafka and Spark Structured Streaming.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="module-card">
            <div class="module-icon">🚌</div>
            <div class="module-title">Route Management</div>
            <div class="module-description">
                Explore campus routes, stops and their
                ordered transportation connections.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="module-card">
            <div class="module-icon">⚙️</div>
            <div class="module-title">Big Data Processing</div>
            <div class="module-description">
                Process and analyze transportation data
                using Apache Spark and Spark SQL.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # -----------------------------------------
    # DATA DISCLAIMER
    # -----------------------------------------

    st.markdown("""
    <div class="overview-note">
        CAMPUSFLOW DEVELOPMENT ENVIRONMENT &nbsp; • &nbsp;
        All historical records and model outputs use
        synthetic demonstration data, not actual LPU shuttle records.
    </div>
    """, unsafe_allow_html=True)




elif page == "Routes & Stops":

    # ----------------------------------------
    # LOAD CAMPUS DATA
    # ----------------------------------------

    stops = pd.read_csv("data/raw/stops.csv")
    routes = pd.read_csv("data/raw/routes.csv")
    route_stops = pd.read_csv("data/raw/route_stops.csv")

    # ----------------------------------------
    # PAGE HEADER
    # ----------------------------------------

    st.markdown("""
    <div class="section-eyebrow">CAMPUS MOBILITY NETWORK</div>
    <div class="section-heading">Routes & Stops</div>
    <div class="section-description">
        Explore shuttle routes, campus destinations and network connectivity.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ----------------------------------------
    # NETWORK SUMMARY CARDS
    # ----------------------------------------

    st.markdown("""
    <div class="aurora-section-label">
        NETWORK AT A GLANCE
    </div>
    """, unsafe_allow_html=True)

    kpi_data = [
        ("🚌", len(routes), "TOTAL ROUTES", "#FFAD7A"),
        ("📍", len(stops), "CAMPUS STOPS", "#B69CFF"),
        ("🔗", len(route_stops), "ROUTE CONNECTIONS", "#38DDE0")
    ]

    kpi_cols = st.columns(3)

    for col, (icon, value, label, accent) in zip(kpi_cols, kpi_data):
        with col:
            st.markdown(f"""
            <div class="aurora-kpi-card" style="--accent:{accent};">
                <div class="aurora-kpi-icon">{icon}</div>
                <div class="aurora-kpi-value">{value}</div>
                <div class="aurora-kpi-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    # ----------------------------------------
    # ROUTE EXPLORER
    # ----------------------------------------

    st.markdown("""
    <div class="aurora-section-label">EXPLORE THE NETWORK</div>
    <div class="section-heading">Individual Route Explorer</div>
    <div class="section-description">
        Select a shuttle route to explore its distance, stops and journey sequence.
    </div>
    """, unsafe_allow_html=True)

    selected_route = st.selectbox(
        "Choose a shuttle route",
        routes["route_id"].tolist(),
        key="aurora_route_selector"
    )

    route_info = routes[
        routes["route_id"] == selected_route
    ].iloc[0]

    selected_stops = route_stops[
        route_stops["route_id"] == selected_route
    ].sort_values("stop_sequence")

    route_details = selected_stops.merge(
        stops,
        on="stop_id",
        how="left"
    )

    # ----------------------------------------
    # SELECTED ROUTE DETAILS
    # ----------------------------------------

    st.markdown(f"""
    <div class="aurora-route-banner">
        <div>
            <div class="aurora-section-label">SELECTED SHUTTLE ROUTE</div>
            <div class="aurora-route-name">{route_info["route_name"]}</div>
            <div class="aurora-route-id">{selected_route}</div>
        </div>
        <div class="aurora-route-distance">
            {route_info["distance_km"]} <span>KM</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    detail_cols = st.columns(3)

    detail_items = [
        ("STARTING POINT", route_info["start_stop"], "#FFAD7A"),
        ("DESTINATION", route_info["end_stop"], "#B69CFF"),
        ("TOTAL STOPS", len(selected_stops), "#38DDE0")
    ]

    for col, (label, value, accent) in zip(detail_cols, detail_items):
        with col:
            st.markdown(f"""
            <div class="aurora-detail-card" style="--accent:{accent};">
                <div class="aurora-detail-label">{label}</div>
                <div class="aurora-detail-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ----------------------------------------
    # ROUTE STOP TIMELINE
    # ----------------------------------------

    st.markdown("""
    <div class="aurora-section-label">JOURNEY BREAKDOWN</div>
    <div class="section-heading">Route Stop Sequence</div>
    <div class="section-description">
        Follow the shuttle journey through each campus stop.
    </div>
    """, unsafe_allow_html=True)

    timeline_html = """
    <div class="aurora-timeline">
    """

    for _, stop in route_details.iterrows():

        sequence = int(stop["stop_sequence"])
        stop_name = stop["stop_name"]
        stop_id = stop["stop_id"]
        zone = stop["zone"]
        distance = stop["distance_from_previous_km"]

        distance_text = (
            "Starting point"
            if sequence == 1
            else f"{distance} km from previous stop"
        )

        timeline_html += f"""
        <div class="aurora-timeline-item">
            <div class="aurora-timeline-marker">
                {sequence}
            </div>
            <div class="aurora-timeline-content">
                <div class="aurora-timeline-name">{stop_name}</div>
                <div class="aurora-timeline-meta">
                    {stop_id} &nbsp; • &nbsp; {zone}
                </div>
                <div class="aurora-timeline-distance">
                    {distance_text}
                </div>
            </div>
        </div>
        """

    timeline_html += "</div>"

    st.html(timeline_html)

    st.divider()

    # ----------------------------------------
    # CAMPUS STOP DIRECTORY
    # ----------------------------------------

    st.markdown("""
    <div class="aurora-section-label">CAMPUS DIRECTORY</div>
    <div class="section-heading">All Campus Stops</div>
    <div class="section-description">
        Browse all registered shuttle destinations and their campus zones.
    </div>
    """, unsafe_allow_html=True)

    st.dataframe(
        stops,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ----------------------------------------
    # CAMPUS STOP MAP
    # ----------------------------------------

    st.markdown("""
    <div class="aurora-section-label">GEOGRAPHIC OVERVIEW</div>
    <div class="section-heading">Campus Stop Locations</div>
    <div class="section-description">
        Explore the illustrative geographic distribution of campus stops.
    </div>
    """, unsafe_allow_html=True)

    st.map(
        stops.rename(
            columns={
                "latitude": "lat",
                "longitude": "lon"
            }
        ),
        latitude="lat",
        longitude="lon"
    )




elif page == "Demand Analytics":

    # ----------------------------------------
    # LOAD HISTORICAL DATA
    # ----------------------------------------

    trips = pd.read_csv(
        "data/raw/trips.csv",
        parse_dates=["travel_date"]
    )

    # ----------------------------------------
    # AURORA ANALYTICS HEADER
    # ----------------------------------------

    st.markdown("""
    <div class="aurora-section-label">
        CAMPUS MOBILITY INTELLIGENCE
    </div>

    <div class="section-heading">
        Historical Demand Analytics
    </div>

    <div class="section-description">
        Explore passenger demand patterns, route utilization,
        daily travel behaviour and campus shuttle performance.
    </div>
    """, unsafe_allow_html=True)

    # ----------------------------------------
    # CALCULATE KPI METRICS
    # ----------------------------------------

    total_trips = len(trips)

    total_passengers = trips["passenger_count"].sum()

    avg_passengers = trips["passenger_count"].mean()

    avg_occupancy = trips["occupancy_rate"].mean() * 100

    # ----------------------------------------
    # AURORA KPI CARD STYLING
    # ----------------------------------------

    st.markdown("""
    <style>

    .analytics-kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 16px;
        margin: 22px 0 28px 0;
    }

    .analytics-kpi-card {
        position: relative;
        overflow: hidden;
        min-height: 135px;
        padding: 21px;

        background: linear-gradient(
            145deg,
            rgba(255,255,255,0.105),
            rgba(255,255,255,0.035)
        );

        border: 1px solid rgba(255,255,255,0.13);
        border-radius: 16px;

        box-shadow: 0 9px 25px rgba(0,0,0,0.16);
        transition: transform 0.2s ease;
    }

    .analytics-kpi-card:hover {
        transform: translateY(-4px);
    }

    .analytics-kpi-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 3px;
        background: var(--accent);
    }

    .analytics-kpi-icon {
        font-size: 23px;
        margin-bottom: 13px;
    }

    .analytics-kpi-value {
        color: #FFFFFF;
        font-size: 29px;
        line-height: 1.2;
        font-weight: 800;
        letter-spacing: -0.6px;
    }

    .analytics-kpi-label {
        color: #A9ADC3;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 1px;
        margin-top: 8px;
        text-transform: uppercase;
    }

    @media (max-width: 900px) {
        .analytics-kpi-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
    }

    </style>
    """, unsafe_allow_html=True)

    # ----------------------------------------
    # DISPLAY KPI CARDS
    # ----------------------------------------

    
    st.html(
        textwrap.dedent(f"""
        <div class="analytics-kpi-grid">

            <div class="analytics-kpi-card"
                 style="--accent: #FFAD7A;">
                <div class="analytics-kpi-icon">&#9636;</div>
                <div class="analytics-kpi-value">{total_trips:,}</div>
                <div class="analytics-kpi-label">Total Trips</div>
            </div>

            <div class="analytics-kpi-card"
                 style="--accent: #B69CFF;">
                <div class="analytics-kpi-icon">&#9823;</div>
                <div class="analytics-kpi-value">{total_passengers:,}</div>
                <div class="analytics-kpi-label">Total Passengers</div>
            </div>

            <div class="analytics-kpi-card"
                 style="--accent: #38DDE0;">
                <div class="analytics-kpi-icon">&#9638;</div>
                <div class="analytics-kpi-value">{avg_passengers:.2f}</div>
                <div class="analytics-kpi-label">Average Passengers / Trip</div>
            </div>

            <div class="analytics-kpi-card"
                 style="--accent: #5DD6A0;">
                <div class="analytics-kpi-icon">&#9678;</div>
                <div class="analytics-kpi-value">{avg_occupancy:.1f}%</div>
                <div class="analytics-kpi-label">Average Occupancy</div>
            </div>

        </div>
        """)
    )

    st.divider()


    # Keep your existing chart sections below this point.


    # ----------------------------------------
    # HOURLY PASSENGER DEMAND
    # ----------------------------------------

    st.markdown("""
    <div class="aurora-section-label">DEMAND PATTERNS</div>
    <div class="section-heading">Passenger Demand by Hour</div>
    <div class="section-description">
        Identify peak and off-peak hours across the campus shuttle network.
    </div>
    """, unsafe_allow_html=True)

    hourly_demand = (
        trips.groupby("hour")["passenger_count"]
        .mean()
        .reset_index()
    )

    fig_hourly = px.bar(
        hourly_demand,
        x="hour",
        y="passenger_count",
        text_auto=".2f",
        labels={
            "hour": "Hour of Day",
            "passenger_count": "Average Passengers"
        }
    )

    fig_hourly.update_traces(
        marker_color="#FFAD7A",
        marker_line_width=0,
        textposition="outside"
    )

    fig_hourly.update_layout(
        template="plotly_dark",
        height=430,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(12,15,29,0.65)",
        font=dict(
            family="Arial",
            color="#E8EAF6",
            size=12
        ),
        margin=dict(l=25, r=25, t=35, b=25),
        showlegend=False,
        xaxis=dict(
            title="Hour of Day",
            dtick=1,
            showgrid=False
        ),
        yaxis=dict(
            title="Average Passengers",
            gridcolor="rgba(255,255,255,0.10)",
            zeroline=False
        )
    )

    st.plotly_chart(
        fig_hourly,
        use_container_width=True,
        config={"displayModeBar": True}
    )

    st.divider()


    # ----------------------------------------
    # ROUTE-WISE PASSENGER DEMAND
    # ----------------------------------------

    st.markdown("""
    <div class="aurora-section-label">ROUTE PERFORMANCE</div>
    <div class="section-heading">Route-wise Passenger Demand</div>
    <div class="section-description">
        Compare passenger demand and utilization across all shuttle routes.
    </div>
    """, unsafe_allow_html=True)

    route_demand = (
        trips.groupby("route_id")
        .agg(
            total_trips=("trip_id", "count"),
            total_passengers=("passenger_count", "sum"),
            avg_passengers=("passenger_count", "mean"),
            avg_occupancy=("occupancy_rate", "mean")
        )
        .reset_index()
    )

    fig_route = px.bar(
        route_demand,
        x="route_id",
        y="avg_passengers",
        text_auto=".2f",
        labels={
            "route_id": "Shuttle Route",
            "avg_passengers": "Average Passengers"
        }
    )

    fig_route.update_traces(
        marker_color=[
            "#FFAD7A",
            "#B69CFF",
            "#38DDE0",
            "#5DD6A0"
        ],
        marker_line_width=0,
        textposition="outside"
    )

    fig_route.update_layout(
        template="plotly_dark",
        height=430,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(12,15,29,0.65)",
        font=dict(
            family="Arial",
            color="#E8EAF6",
            size=12
        ),
        margin=dict(l=25, r=25, t=35, b=25),
        showlegend=False,
        xaxis=dict(
            title="Shuttle Route",
            showgrid=False
        ),
        yaxis=dict(
            title="Average Passengers",
            gridcolor="rgba(255,255,255,0.10)",
            zeroline=False
        )
    )

    st.plotly_chart(
        fig_route,
        use_container_width=True
    )

    # Route-level detailed statistics
    st.markdown("""
    <div class="aurora-section-label">ROUTE STATISTICS</div>
    <div class="section-heading">Route Performance Summary</div>
    """, unsafe_allow_html=True)

    route_display = route_demand.copy()
    route_display["avg_occupancy"] = (
        route_display["avg_occupancy"] * 100
    ).round(2)

    route_display = route_display.rename(columns={
        "route_id": "Route",
        "total_trips": "Total Trips",
        "total_passengers": "Total Passengers",
        "avg_passengers": "Average Passengers",
        "avg_occupancy": "Average Occupancy (%)"
    })

    st.dataframe(
        route_display.round(2),
        use_container_width=True,
        hide_index=True
    )

    st.divider()


    # ----------------------------------------
    # WEEKDAY VS WEEKEND DEMAND
    # ----------------------------------------

    st.markdown("""
    <div class="aurora-section-label">TRAVEL BEHAVIOUR</div>
    <div class="section-heading">Weekday vs Weekend Demand</div>
    <div class="section-description">
        Understand how passenger demand changes between weekdays and weekends.
    </div>
    """, unsafe_allow_html=True)

    day_demand = (
        trips.groupby("is_weekend")["passenger_count"]
        .mean()
        .reset_index()
    )

    day_demand["day_type"] = day_demand[
        "is_weekend"
    ].map({
        0: "Weekday",
        1: "Weekend"
    })

    fig_day = px.bar(
        day_demand,
        x="day_type",
        y="passenger_count",
        text_auto=".2f",
        labels={
            "day_type": "Day Type",
            "passenger_count": "Average Passengers"
        }
    )

    fig_day.update_traces(
        marker_color=["#FFAD7A", "#B69CFF"],
        marker_line_width=0,
        textposition="outside"
    )

    fig_day.update_layout(
        template="plotly_dark",
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(12,15,29,0.65)",
        font=dict(
            family="Arial",
            color="#E8EAF6",
            size=12
        ),
        margin=dict(l=25, r=25, t=35, b=25),
        showlegend=False,
        xaxis=dict(
            title="Day Type",
            showgrid=False
        ),
        yaxis=dict(
            title="Average Passengers",
            gridcolor="rgba(255,255,255,0.10)",
            zeroline=False
        )
    )

    st.plotly_chart(
        fig_day,
        use_container_width=True
    )

    st.divider()

    # ----------------------------------------
    # MONTHLY PASSENGER DEMAND TREND
    # ----------------------------------------

    st.markdown("""
    <div class="aurora-section-label">SEASONAL TRENDS</div>
    <div class="section-heading">Monthly Passenger Demand Trend</div>
    <div class="section-description">
        Track monthly changes in average passenger demand throughout 2025.
    </div>
    """, unsafe_allow_html=True)

    monthly_trips = trips.copy()

    monthly_trips["month"] = pd.to_datetime(
        monthly_trips["travel_date"]
    ).dt.to_period("M").astype(str)

    monthly_demand = (
        monthly_trips.groupby("month")["passenger_count"]
        .mean()
        .reset_index()
    )

    fig_monthly = px.line(
        monthly_demand,
        x="month",
        y="passenger_count",
        markers=True,
        labels={
            "month": "Month",
            "passenger_count": "Average Passengers"
        }
    )

    fig_monthly.update_traces(
        line=dict(
            color="#38DDE0",
            width=3
        ),
        marker=dict(
            color="#FFAD7A",
            size=9,
            line=dict(
                color="#FFFFFF",
                width=1
            )
        ),
        mode="lines+markers+text",
        text=monthly_demand["passenger_count"].round(2),
        textposition="top center"
    )

    fig_monthly.update_layout(
        template="plotly_dark",
        height=430,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(12,15,29,0.65)",
        font=dict(
            family="Arial",
            color="#E8EAF6",
            size=12
        ),
        margin=dict(l=25, r=25, t=45, b=25),
        showlegend=False,
        xaxis=dict(
            title="Month",
            showgrid=False
        ),
        yaxis=dict(
            title="Average Passengers",
            gridcolor="rgba(255,255,255,0.10)",
            zeroline=False
        )
    )

    st.plotly_chart(
        fig_monthly,
        use_container_width=True
    )

    st.divider()


    # ----------------------------------------
    # ROUTE OCCUPANCY ANALYSIS
    # ----------------------------------------

    st.markdown("""
    <div class="aurora-section-label">FLEET UTILIZATION</div>
    <div class="section-heading">Route Occupancy Analysis</div>
    <div class="section-description">
        Compare average passenger capacity utilization across shuttle routes.
    </div>
    """, unsafe_allow_html=True)

    occupancy = (
        trips.groupby("route_id")["occupancy_rate"]
        .mean()
        .reset_index()
    )

    occupancy["occupancy_percentage"] = (
        occupancy["occupancy_rate"] * 100
    )

    fig_occupancy = px.bar(
        occupancy,
        x="route_id",
        y="occupancy_percentage",
        text_auto=".2f",
        labels={
            "route_id": "Shuttle Route",
            "occupancy_percentage": "Average Occupancy (%)"
        }
    )

    fig_occupancy.update_traces(
        marker_color=[
            "#FFAD7A",
            "#B69CFF",
            "#38DDE0",
            "#5DD6A0"
        ],
        marker_line_width=0,
        textposition="outside"
    )

    fig_occupancy.update_layout(
        template="plotly_dark",
        height=430,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(12,15,29,0.65)",
        font=dict(
            family="Arial",
            color="#E8EAF6",
            size=12
        ),
        margin=dict(l=25, r=25, t=35, b=25),
        showlegend=False,
        xaxis=dict(
            title="Shuttle Route",
            showgrid=False
        ),
        yaxis=dict(
            title="Average Occupancy (%)",
            range=[0, 75],
            ticksuffix="%",
            gridcolor="rgba(255,255,255,0.10)",
            zeroline=False
        )
    )

    st.plotly_chart(
        fig_occupancy,
        use_container_width=True
    )

    st.caption(
        "Occupancy percentages are calculated from synthetic "
        "historical shuttle trip records."
    )




elif page == "Demand Prediction":

    # ----------------------------------------
    # PAGE HEADER
    # ----------------------------------------

    st.markdown("""
    <div class="aurora-section-label">CAMPUS MOBILITY INTELLIGENCE</div>
    <div class="section-heading">AI Passenger Demand Prediction</div>
    <div class="section-description">
        Estimate passenger demand for a selected shuttle journey
        using the trained PySpark MLlib model.
    </div>
    """, unsafe_allow_html=True)

    # ----------------------------------------
    # CUSTOM PAGE STYLING
    # ----------------------------------------

    st.markdown("""
    <style>
    .prediction-panel {
        background: linear-gradient(
            135deg,
            rgba(255,173,122,0.09),
            rgba(182,156,255,0.08)
        );
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 16px;
        padding: 20px;
        margin: 12px 0 22px 0;
    }

    .prediction-panel-title {
        color: #FFAD7A;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 7px;
    }

    .prediction-panel-description {
        color: #A9ADC3;
        font-size: 12px;
    }

    .prediction-result-card {
        background: linear-gradient(
            135deg,
            rgba(255,173,122,0.15),
            rgba(182,156,255,0.12)
        );
        border: 1px solid rgba(255,255,255,0.14);
        border-radius: 15px;
        padding: 23px;
        min-height: 140px;
    }

    .prediction-result-label {
        color: #B9BBD0;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 1.2px;
        text-transform: uppercase;
    }

    .prediction-result-value {
        color: #FFFFFF;
        font-size: 35px;
        font-weight: 900;
        margin-top: 12px;
    }

    .prediction-result-caption {
        color: #A9ADC3;
        font-size: 11px;
        margin-top: 5px;
    }

    .prediction-summary-card {
        background: rgba(255,255,255,0.045);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 13px;
        padding: 17px;
        margin-bottom: 10px;
    }

    .prediction-summary-label {
        color: #A9ADC3;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    .prediction-summary-value {
        color: #FFFFFF;
        font-size: 15px;
        font-weight: 700;
        margin-top: 7px;
    }

    </style>
    """, unsafe_allow_html=True)

    # ----------------------------------------
    # LOAD REQUIRED DATASETS
    # ----------------------------------------

    trips = pd.read_csv("data/raw/trips.csv")
    routes = pd.read_csv("data/raw/routes.csv")
    stops = pd.read_csv("data/raw/stops.csv")

    route_stops = pd.read_csv(
        "data/raw/route_stops.csv"
    )

    # ----------------------------------------
    # INPUT FORM HEADER
    # ----------------------------------------

    st.markdown("""
    <div class="prediction-panel">
        <div class="prediction-panel-title">
            Journey Configuration
        </div>
        <div class="prediction-panel-description">
            Enter the journey, weather and campus conditions
            to generate a passenger demand estimate.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ----------------------------------------
    # PREDICTION INPUT FORM
    # ----------------------------------------

    with st.form("prediction_form"):

        st.markdown(
            '<div class="aurora-section-label">01 / JOURNEY DETAILS</div>',
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)

        with col1:

            selected_date = st.date_input(
                "Travel Date",
                value=date.today()
            )

        with col2:

            selected_hour = st.slider(
                "Departure Hour",
                min_value=7,
                max_value=20,
                value=9
            )

        selected_route = st.selectbox(
            "Select Shuttle Route",
            routes["route_id"].tolist()
        )

        route_sequence = (
            route_stops[
                route_stops["route_id"] == selected_route
            ]
            .sort_values("stop_sequence")
            .reset_index(drop=True)
        )

        source_options = route_sequence[
            "stop_id"
        ].tolist()[:-1]

        source_stop = st.selectbox(
            "Starting Stop",
            source_options,
            format_func=lambda x: (
                stops.loc[
                    stops["stop_id"] == x,
                    "stop_name"
                ].iloc[0]
            )
        )

        source_index = route_sequence.index[
            route_sequence["stop_id"] == source_stop
        ][0]

        destination_options = route_sequence.iloc[
            source_index + 1:
        ]["stop_id"].tolist()

        destination_stop = st.selectbox(
            "Destination Stop",
            destination_options,
            format_func=lambda x: (
                stops.loc[
                    stops["stop_id"] == x,
                    "stop_name"
                ].iloc[0]
            )
        )

        st.divider()

        st.markdown(
            '<div class="aurora-section-label">02 / WEATHER CONDITIONS</div>',
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)

        with col1:

            season = st.selectbox(
                "Season",
                sorted(trips["season"].dropna().unique())
            )

            temperature = st.number_input(
                "Temperature (°C)",
                min_value=-10.0,
                max_value=55.0,
                value=20.0
            )

        with col2:

            weather = st.selectbox(
                "Weather",
                sorted(trips["weather"].dropna().unique())
            )

            rainfall = st.number_input(
                "Rainfall (mm)",
                min_value=0.0,
                max_value=500.0,
                value=0.0
            )

        st.divider()

        st.markdown(
            '<div class="aurora-section-label">03 / CAMPUS CONDITIONS</div>',
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)

        with col1:

            is_exam_day = st.checkbox(
                "Exam Day"
            )

        with col2:

            is_event_day = st.checkbox(
                "Campus Event Day"
            )

        st.markdown("<br>", unsafe_allow_html=True)

        predict_button = st.form_submit_button(
            "Generate Passenger Demand Prediction",
            use_container_width=True
        )

    # ----------------------------------------
    # RUN PREDICTION
    # ----------------------------------------

    if predict_button:

        destination_index = route_sequence.index[
            route_sequence["stop_id"] == destination_stop
        ][0]

        journey_segments = route_sequence.iloc[
            source_index + 1:
            destination_index + 1
        ]

        journey_distance = journey_segments[
            "distance_from_previous_km"
        ].sum()

        input_record = {
            "travel_date": str(selected_date),
            "hour": int(selected_hour),
            "day_of_week": int(selected_date.weekday()),
            "route_id": selected_route,
            "season": season,
            "weather": weather,
            "temperature_c": float(temperature),
            "rainfall_mm": float(rainfall),
            "is_exam_day": int(is_exam_day),
            "is_event_day": int(is_event_day),
            "source_stop": source_stop,
            "destination_stop": destination_stop,
            "distance_km": float(journey_distance)
        }

        try:

            with st.spinner(
                "Loading ML model and predicting passenger demand..."
            ):

                spark, model = get_prediction_resources()

                result = predict_demand(
                    spark,
                    model,
                    [input_record]
                )

                prediction = float(
                    result.first()["prediction"]
                )

            prediction = max(0, prediction)
            rounded_prediction = max(0, round(prediction))

            # --------------------------------
            # PREDICTION RESULTS
            # --------------------------------

            st.divider()

            st.markdown("""
            <div class="aurora-section-label">PREDICTION OUTPUT</div>
            <div class="section-heading">Passenger Demand Estimate</div>
            <div class="section-description">
                Results generated by the trained CampusFlow
                passenger demand prediction pipeline.
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            with col1:

                st.markdown(f"""
                <div class="prediction-result-card">
                    <div class="prediction-result-label">
                        Estimated Passengers
                    </div>
                    <div class="prediction-result-value">
                        {prediction:.2f}
                    </div>
                    <div class="prediction-result-caption">
                        Model-generated passenger estimate
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col2:

                st.markdown(f"""
                <div class="prediction-result-card">
                    <div class="prediction-result-label">
                        Rounded Passenger Estimate
                    </div>
                    <div class="prediction-result-value">
                        {rounded_prediction}
                    </div>
                    <div class="prediction-result-caption">
                        Nearest whole passenger
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.success(
                "Passenger demand prediction generated successfully!"
            )

            # --------------------------------
            # JOURNEY SUMMARY
            # --------------------------------

            st.markdown("""
            <div class="aurora-section-label">JOURNEY INFORMATION</div>
            <div class="section-heading">Prediction Journey Summary</div>
            """, unsafe_allow_html=True)

            source_name = stops.loc[
                stops["stop_id"] == source_stop,
                "stop_name"
            ].iloc[0]

            destination_name = stops.loc[
                stops["stop_id"] == destination_stop,
                "stop_name"
            ].iloc[0]

            col1, col2, col3 = st.columns(3)

            summary_items = [
                ("Selected Route", selected_route),
                ("Starting Point", source_name),
                ("Destination", destination_name),
                ("Travel Date", str(selected_date)),
                ("Departure Time", f"{selected_hour}:00"),
                ("Journey Distance", f"{journey_distance:.2f} km")
            ]

            for index, (label, value) in enumerate(summary_items):

                target_col = [col1, col2, col3][index % 3]

                with target_col:

                    st.markdown(f"""
                    <div class="prediction-summary-card">
                        <div class="prediction-summary-label">
                            {label}
                        </div>
                        <div class="prediction-summary-value">
                            {value}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            st.caption(
                "This prediction is a model-based estimate trained "
                "on synthetic 2025 shuttle data. It is not a "
                "guaranteed passenger count or live observation."
            )

        except Exception as e:

            st.error(
                f"Prediction failed: {str(e)}"
            )


elif page == "Live Monitoring":


    live_monitoring_content()


elif page == "Network Analysis":

    import pandas as pd
    import plotly.graph_objects as go
    from collections import Counter

    st.subheader("Campus Network Analysis")
    st.write("GraphX-based analysis of campus shuttle stops and route connectivity.")

    # ----------------------------------------------
    # 1. LOAD NETWORK DATA
    # ----------------------------------------------

    stops = pd.read_csv("data/raw/stops.csv")
    routes = pd.read_csv("data/raw/routes.csv")
    route_stops = pd.read_csv("data/raw/route_stops.csv")

    stops["latitude"] = pd.to_numeric(stops["latitude"])
    stops["longitude"] = pd.to_numeric(stops["longitude"])

    # ----------------------------------------------
    # 2. BUILD DIRECTED NETWORK EDGES
    # ----------------------------------------------

    edges = []

    for route_id, group in route_stops.groupby("route_id"):

        group = group.sort_values("stop_sequence")
        stop_ids = group["stop_id"].tolist()

        for i in range(len(stop_ids) - 1):

            edges.append({
                "route_id": route_id,
                "source": stop_ids[i],
                "target": stop_ids[i + 1]
            })

    edges_df = pd.DataFrame(edges)

    # ----------------------------------------------
    # 3. GRAPHX PAGERANK RESULTS
    # ----------------------------------------------

    pagerank_scores = {
        "ST01": 0.6764698091496428,
        "ST02": 0.21732758196291224,
        "ST03": 0.8083542034417335,
        "ST04": 1.6207520212699857,
        "ST05": 1.3907726983287496,
        "ST06": 2.272723981558082,
        "ST07": 1.3378608583661147,
        "ST08": 1.2458980115867793,
        "ST09": 0.8612660434043687,
        "ST10": 0.9491911823373298,
        "ST11": 0.4020560266313876,
        "ST12": 0.21732758196291224
    }

    stops["pagerank"] = stops["stop_id"].map(pagerank_scores)

    # ----------------------------------------------
    # 4. CALCULATE STOP CONNECTIVITY
    # ----------------------------------------------

    outgoing = Counter(edges_df["source"])
    incoming = Counter(edges_df["target"])

    stops["out_degree"] = stops["stop_id"].map(
        lambda x: outgoing[x]
    )

    stops["in_degree"] = stops["stop_id"].map(
        lambda x: incoming[x]
    )

    stops["total_degree"] = (
        stops["out_degree"] + stops["in_degree"]
    )

    # ----------------------------------------------
    # 5. NETWORK SUMMARY
    # ----------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Stops", len(stops))
    col2.metric("Total Connections", len(edges_df))
    col3.metric("Routes", routes["route_id"].nunique())
    col4.metric("Connected Components", 1)

    st.divider()

    # ----------------------------------------------
    # 6. NETWORK VISUALIZATION
    # ----------------------------------------------

    st.markdown("### Campus Shuttle Network")

    route_options = ["All Routes"] + sorted(
        edges_df["route_id"].unique().tolist()
    )

    selected_route = st.selectbox(
        "Select a route to visualize",
        route_options
    )

    if selected_route == "All Routes":
        displayed_edges = edges_df
    else:
        displayed_edges = edges_df[
            edges_df["route_id"] == selected_route
        ]

    fig = go.Figure()

    # Draw route connections
    for _, edge in displayed_edges.iterrows():

        source = stops[
            stops["stop_id"] == edge["source"]
        ].iloc[0]

        target = stops[
            stops["stop_id"] == edge["target"]
        ].iloc[0]

        fig.add_trace(go.Scatter(
            x=[source["longitude"], target["longitude"]],
            y=[source["latitude"], target["latitude"]],
            mode="lines",
            line=dict(width=2),
            hoverinfo="text",
            text=[
                f'{edge["route_id"]}: {source["stop_name"]} → {target["stop_name"]}',
                f'{edge["route_id"]}: {source["stop_name"]} → {target["stop_name"]}'
            ],
            showlegend=False
        ))

        # Direction arrow
        fig.add_annotation(
            x=target["longitude"],
            y=target["latitude"],
            ax=source["longitude"],
            ay=source["latitude"],
            xref="x",
            yref="y",
            axref="x",
            ayref="y",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=1.5
        )

    # Draw stops
    fig.add_trace(go.Scatter(
        x=stops["longitude"],
        y=stops["latitude"],
        mode="markers+text",
        text=stops["stop_name"],
        textposition="top center",
        customdata=stops[[
            "stop_id", "total_degree", "pagerank"
        ]],
        hovertemplate=(
            "<b>%{text}</b><br>"
            "Stop ID: %{customdata[0]}<br>"
            "Total Degree: %{customdata[1]}<br>"
            "PageRank: %{customdata[2]:.3f}"
            "<extra></extra>"
        ),
        marker=dict(
            size=15,
            color=stops["pagerank"],
            colorscale="Viridis",
            showscale=True,
            colorbar=dict(title="PageRank"),
            line=dict(width=1, color="white")
        ),
        showlegend=False
    ))

    fig.update_layout(
        height=600,
        xaxis_title="Longitude",
        yaxis_title="Latitude",
        template="plotly_dark",
        margin=dict(l=20, r=20, t=30, b=20),
        hovermode="closest"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "Arrows indicate the direction of consecutive shuttle stops. "
        "Stop positions use the illustrative coordinates in the synthetic dataset."
    )

    st.divider()

    # ----------------------------------------------
    # 7. STOP CONNECTIVITY ANALYSIS
    # ----------------------------------------------

    st.markdown("### Stop Connectivity Analysis")

    connectivity = stops[[
        "stop_id",
        "stop_name",
        "in_degree",
        "out_degree",
        "total_degree"
    ]].sort_values(
        "total_degree",
        ascending=False
    )

    st.dataframe(
        connectivity,
        use_container_width=True,
        hide_index=True
    )

    most_connected = connectivity.iloc[0]

    st.success(
        f"Most connected stop: {most_connected['stop_name']} "
        f"(Total degree: {most_connected['total_degree']})"
    )

    st.divider()

    # ----------------------------------------------
    # 8. PAGERANK ANALYSIS
    # ----------------------------------------------

    st.markdown("### GraphX PageRank Analysis")

    pagerank_table = stops[[
        "stop_id",
        "stop_name",
        "pagerank"
    ]].sort_values(
        "pagerank",
        ascending=False
    ).reset_index(drop=True)

    pagerank_table.index = pagerank_table.index + 1
    pagerank_table.index.name = "Rank"

    st.dataframe(
        pagerank_table,
        use_container_width=True
    )

    top_stop = pagerank_table.iloc[0]

    st.info(
        f"Highest PageRank: {top_stop['stop_name']} "
        f"({top_stop['pagerank']:.4f})"
    )

    st.caption(
        "PageRank values are loaded from the previously completed GraphX "
        "analysis. They indicate network importance, not passenger counts."
    )

    st.divider()

    st.markdown("### Network Analysis Interpretation")

    st.write(
        "- **Degree:** Measures the number of incoming and outgoing connections "
        "at each stop."
    )

    st.write(
        "- **Connected Components:** GraphX identified one connected component "
        "containing all 12 stops."
    )

    st.write(
        "- **PageRank:** Measures the relative structural importance of stops "
        "within the shuttle network."
    )


# --------------------------------------------------
# 6. FOOTER
# --------------------------------------------------

st.sidebar.caption("CampusFlow | Development Version 1.0")
