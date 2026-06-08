import streamlit as st
import pandas as pd
import plotly.express as px
import os
from engine import MarkovAttributionKernel

# =====================================================
# PAGE CONFIGURATION
# =====================================================
st.set_page_config(
    page_title="Markov Chain Attribution Nexus",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.main { background-color: #0e1117; color: white; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# HEADER
# =====================================================
st.title("🕸️ Algorithmic Markov Chain Attribution Nexus")
st.markdown("### Predictive State-Transition Modeling & Removal Effect Engine")
st.markdown("---")

# =====================================================
# DATA & KERNEL INGESTION
# =====================================================
DATA_PATH = os.path.join("core_logic", "user_journey_sequences.csv")


@st.cache_resource
def initialize_kernel():
    if not os.path.exists(DATA_PATH):
        return None
    kernel = MarkovAttributionKernel(DATA_PATH)
    kernel.build_transition_matrix()
    return kernel


kernel = initialize_kernel()

if kernel is None:
    st.error(
        "⚠️ Ingestion Error: Base user journey sequence data missing. Please run 'python generate_journeys.py' first.")
    st.stop()

# Run the base calculations
base_conversion = kernel.simulate_conversion_probability()
removal_effects = kernel.execute_pipeline()

# Transform results to DataFrame for charting
ui_data = pd.DataFrame([
    {"Marketing_Channel": channel, "Removal_Effect_Percent": effect * 100}
    for channel, effect in removal_effects.items()
]).sort_values("Removal_Effect_Percent", ascending=False)

# =====================================================
# SIDEBAR CONTROLS
# =====================================================
st.sidebar.header("⚙️ Simulation Center")
st.sidebar.markdown(
    "Select a channel to simulate a **complete programmatic blackout** and witness the cascading structural "
    "failure across your conversion paths.")

active_blackout = st.sidebar.selectbox(
    "Simulate Channel Blackout",
    ["None"] + kernel.channels
)

# Calculate simulated blackout shift
if active_blackout != "None":
    simulated_conversion = kernel.simulate_conversion_probability(removal_state=active_blackout)
    conversion_delta = simulated_conversion - base_conversion
else:
    simulated_conversion = base_conversion
    conversion_delta = 0.0

# =====================================================
# KPI METRICS DASHBOARD
# =====================================================
st.markdown("## 📈 Core Funnel Stability Metrics")
m1, m2, m3 = st.columns(3)

with m1:
    st.metric(
        label="Baseline Conversion Rate",
        value=f"{base_conversion:.2%}"
    )

with m2:
    st.metric(
        label="Simulated System Health" if active_blackout != "None" else "System Operational Status",
        value=f"{simulated_conversion:.2%}",
        delta=f"{conversion_delta:.2%}" if active_blackout != "None" else None,
        delta_color="inverse"
    )

with m3:
    critical_channel = ui_data.iloc[0]["Marketing_Channel"]
    st.metric(
        label="Highest Risk Dependency",
        value=critical_channel.replace("_", " ").title()
    )

st.markdown("---")

# =====================================================
# ANALYTICS GRAPH SECTION
# =====================================================
left, right = st.columns([3, 2])

with left:
    st.subheader("📊 Channel Removal Effect Index")
    st.markdown(
        "This visualization maps out the net conversion volume drop-off incurred if a single node is extracted "
        "from the transition architecture.")

    fig_bar = px.bar(
        ui_data,
        x="Marketing_Channel",
        y="Removal_Effect_Percent",
        color="Removal_Effect_Percent",
        labels={"Removal_Effect_Percent": "Conversion Loss (%)", "Marketing_Channel": "Channel Name"},
        color_continuous_scale=px.colors.sequential.Reds
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with right:
    st.subheader("🏆 Risk Assessment Ledger")
    st.markdown("Auditable algorithmic weights mapped directly out of our raw transition matrix calculations.")

    # Format for clean display
    display_df = ui_data.copy()
    display_df["Removal_Effect_Percent"] = display_df["Removal_Effect_Percent"].map("{:.2f}%".format)
    st.dataframe(display_df, use_container_width=True, hide_index=True)

# =====================================================
# DEEP INTERACTION RAW PATH DATA EXPANSER
# =====================================================
st.markdown("---")
with st.expander("🔍 Inspect Underlying User Journey Sequence Paths"):
    st.dataframe(kernel.df.head(100), use_container_width=True)

# =====================================================
# FOOTER
# =====================================================
st.markdown("---")
st.caption(
    "Project Markov Nexus • Advanced Algorithmic Attribution Engine • Developed under standard mathematical guidelines")
