import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title="Sales Dashboard",
    layout="wide"
)

sns.set_style("whitegrid")

# Load Data
df = pd.read_excel("sellers.xlsx")

# Create Vendor Name
df["VENDOR"] = df["NAME"] + " " + df["LASTNAME"]

st.title("Sales Dashboard")
st.write("Sales performance analysis by region and vendor.")

# Sidebar Filters
st.sidebar.header("Filters")

selected_region = st.sidebar.selectbox(
    "Select Region",
    ["All"] + sorted(df["REGION"].unique())
)

if selected_region == "All":
    filtered_df = df.copy()
else:
    filtered_df = df[df["REGION"] == selected_region]

# KPI SECTION
with st.container():

    st.subheader("Sales Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Units Sold",
            int(filtered_df["SOLD UNITS"].sum())
        )

    with col2:
        st.metric(
            "Total Sales",
            f"${filtered_df['TOTAL SALES'].sum():,.0f}"
        )

    with col3:
        st.metric(
            "Average Sales",
            round(filtered_df["SALES AVERAGE"].mean(), 2)
        )

st.divider()

# TABLE AND CHARTS
with st.container():

    st.subheader("Sales Data")

    st.dataframe(
        filtered_df,
        use_container_width=True
    )

st.divider()

# TOP 10 CHARTS
with st.container():

    st.subheader("Sales Performance")

    col1, col2 = st.columns(2)

# TOP 10 UNITS SOLD AND TOTAL SALES
    with col1:

        top_units = (
            filtered_df
            .sort_values("SOLD UNITS", ascending=False)
            .head(10)
        )

        fig1, ax1 = plt.subplots(figsize=(8,5))

        sns.barplot(
            data=top_units,
            x="SOLD UNITS",
            y="VENDOR",
            ax=ax1
        )

        ax1.set_title("Top 10 Vendors by Units Sold")

        st.pyplot(fig1)

    with col2:

        top_sales = (
            filtered_df
            .sort_values("TOTAL SALES", ascending=False)
            .head(10)
        )

        fig2, ax2 = plt.subplots(figsize=(8,5))

        sns.barplot(
            data=top_sales,
            x="TOTAL SALES",
            y="VENDOR",
            ax=ax2
        )

        ax2.set_title("Top 10 Vendors by Total Sales")

        st.pyplot(fig2)

st.divider()

# AVERAGE SALES
with st.container():

    st.subheader("Average Sales Analysis")

    top_avg = (
        filtered_df
        .sort_values("SALES AVERAGE", ascending=False)
        .head(10)
    )

    fig3, ax3 = plt.subplots(figsize=(10,5))

    sns.barplot(
        data=top_avg,
        x="VENDOR",
        y="SALES AVERAGE",
        ax=ax3
    )

    average_line = filtered_df["SALES AVERAGE"].mean()

    ax3.axhline(
        average_line,
        color="red",
        linestyle="--",
        label=f"Mean = {average_line:.2f}"
    )

    ax3.legend()

    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    st.pyplot(fig3)

st.divider()

# VENDOR INFORMATION
with st.container():

    st.subheader("Vendor Information")

    selected_vendor = st.selectbox(
        "Select a Vendor",
        sorted(filtered_df["VENDOR"].unique())
    )

    vendor_data = filtered_df[
        filtered_df["VENDOR"] == selected_vendor
    ]

    if st.button("Show Vendor Details"):

        metric1, metric2, metric3 = st.columns(3)

        with metric1:
            st.metric(
                "Units Sold",
                int(vendor_data["SOLD UNITS"].iloc[0])
            )

        with metric2:
            st.metric(
                "Total Sales",
                f"${vendor_data['TOTAL SALES'].iloc[0]:,.0f}"
            )

        with metric3:
            st.metric(
                "Average Sales",
                round(vendor_data["SALES AVERAGE"].iloc[0], 2)
            )

        st.dataframe(
            vendor_data,
            use_container_width=True
        )

st.divider()

# REGION COMPARISON
with st.container():

    st.subheader("Region Comparison")

    region_summary = (
        filtered_df
        .groupby("REGION")["TOTAL SALES"]
        .sum()
        .reset_index()
        .sort_values("TOTAL SALES", ascending=False)
    )

    fig4, ax4 = plt.subplots(figsize=(8,5))

    sns.barplot(
        data=region_summary,
        x="REGION",
        y="TOTAL SALES",
        ax=ax4
    )

    ax4.set_title("Total Sales by Region")

    plt.tight_layout()

    st.pyplot(fig4)