import os

import pandas as pd
import plotly.express as px
import streamlit as st

from engine import MarkovAttributionKernel

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Markov Attribution Nexus Enterprise",
    page_icon="🕸️",
    layout="wide"
)

# ==========================================================
# HEADER
# ==========================================================

st.title("🕸️ Markov Attribution Nexus Enterprise")

st.caption(
    "Revenue Attribution • Markov Modeling • Customer Journey Intelligence"
)

st.divider()

# ==========================================================
# DATA PATH
# ==========================================================

DATA_PATH = os.path.join(
    "core_logic",
    "user_journey_sequences.csv"
)

# ==========================================================
# LOAD ENGINE
# ==========================================================

@st.cache_resource
def load_kernel():

    kernel = MarkovAttributionKernel(
        DATA_PATH
    )

    kernel.execute_pipeline()

    return kernel


kernel = load_kernel()

# ==========================================================
# CORE METRICS
# ==========================================================

summary = kernel.get_summary()

removal_effects = kernel.removal_effects

attribution_weights = (
    kernel.get_attribution_weights()
)

revenue_attribution = (
    kernel.get_revenue_attribution()
)

revenue_loss = (
    kernel.get_revenue_loss_estimates()
)

base_conversion = (
    summary["baseline_conversion"]
)

# ==========================================================
# BUILD UI DATAFRAME
# ==========================================================

ui_data = pd.DataFrame([
    {
        "Marketing_Channel": channel,
        "Removal_Effect":
            removal_effects.get(channel, 0),

        "Removal_Effect_Percent":
            removal_effects.get(channel, 0) * 100,

        "Attribution_Share":
            attribution_weights.get(channel, 0) * 100,

        "Revenue_Attributed":
            revenue_attribution.get(channel, 0),

        "Revenue_Loss":
            revenue_loss.get(channel, 0)
    }

    for channel in kernel.channels
])

ui_data = ui_data.sort_values(
    "Removal_Effect_Percent",
    ascending=False
)

# ==========================================================
# SIDEBAR
# ==========================================================

st.sidebar.header(
    "Simulation Center"
)

blackout_channels = st.sidebar.multiselect(
    "Remove Channels",
    kernel.channels
)

# ==========================================================
# SIMULATION
# ==========================================================

if blackout_channels:

    simulated_conversion = (
        kernel.simulate_multi_channel_removal(
            blackout_channels
        )
    )

else:

    simulated_conversion = (
        base_conversion
    )

conversion_delta = (
    simulated_conversion
    - base_conversion
)

# ==========================================================
# KPI DASHBOARD
# ==========================================================

st.subheader(
    "Executive Overview"
)

m1, m2, m3, m4, m5, m6 = st.columns(6)

m1.metric(
    "Journeys",
    f"{summary['journeys']:,}"
)

m2.metric(
    "Channels",
    summary["channels"]
)

m3.metric(
    "Conversion Rate",
    f"{base_conversion:.2%}"
)

m4.metric(
    "Current Conversion",
    f"{simulated_conversion:.2%}",
    delta=f"{conversion_delta:.2%}"
)

m5.metric(
    "Revenue",
    f"${summary['total_revenue']:,.0f}"
)

m6.metric(
    "AOV",
    f"${summary['avg_order_value']:,.2f}"
)

st.divider()

# ==========================================================
# TOP INSIGHTS
# ==========================================================

a, b, c = st.columns(3)

a.metric(
    "Most Critical Channel",
    summary["most_critical_channel"]
)

b.metric(
    "Least Critical Channel",
    summary["least_critical_channel"]
)

c.metric(
    "Revenue At Risk",
    f"${ui_data['Revenue_Loss'].max():,.0f}"
)

# ==========================================================
# REMOVAL EFFECTS
# ==========================================================

st.subheader(
    "Channel Removal Effects"
)

fig_removal = px.bar(
    ui_data,
    x="Marketing_Channel",
    y="Removal_Effect_Percent",
    text="Removal_Effect_Percent",
    color="Removal_Effect_Percent"
)

fig_removal.update_traces(
    texttemplate="%{text:.2f}",
    textposition="outside"
)

st.plotly_chart(
    fig_removal,
    use_container_width=True
)

# ==========================================================
# ATTRIBUTION SHARE
# ==========================================================

st.subheader(
    "Attribution Share"
)

fig_pie = px.pie(
    ui_data,
    values="Attribution_Share",
    names="Marketing_Channel",
    hole=0.4
)

st.plotly_chart(
    fig_pie,
    use_container_width=True
)

# ==========================================================
# REVENUE ATTRIBUTION
# ==========================================================

st.subheader(
    "Revenue Attribution"
)

fig_revenue = px.bar(
    ui_data,
    x="Marketing_Channel",
    y="Revenue_Attributed",
    text="Revenue_Attributed",
    color="Revenue_Attributed"
)

fig_revenue.update_traces(
    texttemplate="$%{text:,.0f}",
    textposition="outside"
)

st.plotly_chart(
    fig_revenue,
    use_container_width=True
)

# ==========================================================
# REVENUE LOSS
# ==========================================================

st.subheader(
    "Estimated Revenue Loss"
)

fig_loss = px.bar(
    ui_data,
    x="Marketing_Channel",
    y="Revenue_Loss",
    text="Revenue_Loss",
    color="Revenue_Loss"
)

fig_loss.update_traces(
    texttemplate="$%{text:,.0f}",
    textposition="outside"
)

st.plotly_chart(
    fig_loss,
    use_container_width=True
)

# ==========================================================
# CUSTOMER SEGMENTS
# ==========================================================

segment_df = (
    kernel.get_segment_summary()
)

if not segment_df.empty:

    st.subheader(
        "Customer Segments"
    )

    left, right = st.columns(2)

    with left:

        fig_seg = px.pie(
            segment_df,
            names="customer_segment",
            values="users"
        )

        st.plotly_chart(
            fig_seg,
            use_container_width=True
        )

    with right:

        fig_conv = px.bar(
            segment_df,
            x="customer_segment",
            y="conversion_rate",
            text="conversion_rate"
        )

        fig_conv.update_traces(
            texttemplate="%{text:.2%}"
        )

        st.plotly_chart(
            fig_conv,
            use_container_width=True
        )

# ==========================================================
# MONTE CARLO
# ==========================================================

st.subheader(
    "Conversion Stability Forecast"
)

forecast = (
    kernel.monte_carlo_forecast(
        simulations=1000
    )
)

forecast_df = pd.DataFrame(
    {"conversion": forecast}
)

fig_forecast = px.histogram(
    forecast_df,
    x="conversion",
    nbins=30
)

st.plotly_chart(
    fig_forecast,
    use_container_width=True
)

# ==========================================================
# ATTRIBUTION TABLE
# ==========================================================

st.subheader(
    "Attribution Ledger"
)

display_df = ui_data.copy()

display_df[
    "Removal_Effect_Percent"
] = display_df[
    "Removal_Effect_Percent"
].map(
    "{:.2f}%".format
)

display_df[
    "Attribution_Share"
] = display_df[
    "Attribution_Share"
].map(
    "{:.2f}%".format
)

display_df[
    "Revenue_Attributed"
] = display_df[
    "Revenue_Attributed"
].map(
    "${:,.2f}".format
)

display_df[
    "Revenue_Loss"
] = display_df[
    "Revenue_Loss"
].map(
    "${:,.2f}".format
)

st.dataframe(
    display_df,
    hide_index=True,
    use_container_width=True
)

# ==========================================================
# DOWNLOAD
# ==========================================================

csv_data = ui_data.to_csv(
    index=False
)

st.download_button(
    label="Download Attribution Report",
    data=csv_data,
    file_name="markov_attribution_report.csv",
    mime="text/csv"
)

# ==========================================================
# TRANSITION MATRIX
# ==========================================================

with st.expander(
    "Transition Matrix"
):

    st.dataframe(
        kernel.get_transition_matrix_df(),
        use_container_width=True
    )

# ==========================================================
# RAW DATA
# ==========================================================

with st.expander(
    "Dataset Preview"
):

    st.dataframe(
        kernel.df.head(100),
        use_container_width=True
    )

# ==========================================================
# FOOTER
# ==========================================================

st.divider()

st.caption(
    "Markov Attribution Nexus Enterprise"
)
