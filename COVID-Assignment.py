import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
 
# PAGE CONFIG
st.set_page_config(
    page_title="COVID-19 Global Pulse",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)
 
# CUSTOM CSS - light theme
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500&display=swap');
 
:root {
  --bg:        #f5f7fa;
  --surface:   #ffffff;
  --border:    #dde3ed;
  --red:       #c0392b;
  --red-light: #e74c3c;
  --blue:      #2563eb;
  --blue-soft: #3b82f6;
  --dark:      #1a202c;
  --muted:     #64748b;
}
 
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main {
  background-color: var(--bg) !important;
  color: var(--dark) !important;
  font-family: 'DM Sans', sans-serif;
}
 
[data-testid="stMain"] {
  background-color: var(--bg) !important;
}
 
[data-testid="stSidebar"] {
  background-color: var(--surface) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * {
  color: var(--dark) !important;
}
 
.block-container {
  padding-top: 1.5rem !important;
  padding-bottom: 2rem !important;
  background-color: var(--bg) !important;
}
 
/* Header */
.dash-header {
  border-bottom: 2px solid var(--border);
  padding-bottom: 1.2rem;
  margin-bottom: 1.5rem;
}
.dash-title {
  font-family: 'Syne', sans-serif;
  font-weight: 800;
  font-size: 2.4rem;
  letter-spacing: -1px;
  line-height: 1;
  color: var(--dark);
  margin: 0;
}
.dash-title span { color: var(--red); }
.dash-subtitle {
  font-size: 0.82rem;
  color: var(--muted);
  margin-top: 0.4rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}
 
/* KPI cards */
.kpi-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1.1rem 1.3rem;
  margin-bottom: 0.5rem;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.kpi-label {
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--muted);
  margin-bottom: 0.3rem;
}
.kpi-value {
  font-family: 'Syne', sans-serif;
  font-size: 2rem;
  font-weight: 700;
  line-height: 1;
}
.kpi-value.red   { color: var(--red-light); }
.kpi-value.blue  { color: var(--blue-soft); }
.kpi-value.dark  { color: var(--dark); }
.kpi-sub {
  font-size: 0.7rem;
  color: var(--muted);
  margin-top: 0.3rem;
}
 
/* Section labels */
.section-label {
  font-family: 'Syne', sans-serif;
  font-size: 0.66rem;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 0.4rem;
  margin-top: 1rem;
}
 
/* Narrative box */
.narrative {
  background: var(--surface);
  border-left: 3px solid var(--red);
  border-radius: 0 8px 8px 0;
  padding: 0.9rem 1.1rem;
  font-size: 0.86rem;
  line-height: 1.65;
  color: #374151;
  margin-bottom: 1rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.narrative strong { color: var(--dark); }
 
/* Divider */
.divider {
  border: none;
  border-top: 1px solid var(--border);
  margin: 1.2rem 0;
}
 
/* Footer */
.footer {
  text-align: center;
  font-size: 0.7rem;
  color: var(--muted);
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border);
}
</style>
""", unsafe_allow_html=True)
 
 
# DATA LOADING
@st.cache_data(show_spinner=False)
def load_data():
    url = "https://srhdpeuwpubsa.blob.core.windows.net/whdh/COVID/WHO-COVID-19-global-data.csv"
    try:
        df = pd.read_csv(url)
        return df, None
    except Exception as e:
        return None, str(e)
 
 
# CHART THEME - light background
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", color="#374151", size=11),
    margin=dict(l=10, r=10, t=36, b=10),
    legend=dict(
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor="#dde3ed",
        borderwidth=1,
        font=dict(size=10),
    ),
    xaxis=dict(gridcolor="#e5e9f0", linecolor="#dde3ed", zerolinecolor="#dde3ed"),
    yaxis=dict(gridcolor="#e5e9f0", linecolor="#dde3ed", zerolinecolor="#dde3ed"),
)
 
RED   = "#e74c3c"
BLUE  = "#2563eb"
DARK  = "#1a202c"
 
 
# LOAD DATA
with st.spinner("Loading WHO data..."):
    df_raw, load_error = load_data()
 
 
# HEADER
st.markdown("""
<div class="dash-header">
  <p class="dash-title">COVID-19 <span>Global Pulse</span></p>
  <p class="dash-subtitle">Global Epidemiological Analysis &nbsp;|&nbsp; Role: Public Health Analyst &nbsp;|&nbsp; Source: WHO</p>
</div>
""", unsafe_allow_html=True)
 
 
# ERROR STATE / MANUAL UPLOAD
if df_raw is None:
    st.error(f"Could not load the WHO dataset: {load_error}")
    st.info("Please upload WHO-COVID-19-global-data.csv manually from https://data.who.int/dashboards/covid19/data")
    uploaded = st.file_uploader("Upload CSV manually", type="csv")
    if uploaded:
        df_raw = pd.read_csv(uploaded)
    else:
        st.stop()
 
 
# PREPROCESSING
df = df_raw.copy()
df.columns = df.columns.str.strip()
 
date_col = next((c for c in df.columns if "date" in c.lower() or "week" in c.lower()), df.columns[0])
df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
df = df.dropna(subset=[date_col]).sort_values(date_col)
 
def find_col(df, keywords):
    for kw in keywords:
        for c in df.columns:
            if kw.lower() in c.lower():
                return c
    return None
 
country_col    = find_col(df, ["country", "name", "territory"])
region_col     = find_col(df, ["who_region", "region"])
new_cases_col  = find_col(df, ["new_cases", "cases_new", "new case"])
new_deaths_col = find_col(df, ["new_deaths", "deaths_new", "new death"])
cum_cases_col  = find_col(df, ["cumulative_cases", "cum_cases", "total_cases"])
cum_deaths_col = find_col(df, ["cumulative_deaths", "cum_deaths", "total_deaths"])
 
for col in [new_cases_col, new_deaths_col, cum_cases_col, cum_deaths_col]:
    if col:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).clip(lower=0)
 
 
# SIDEBAR FILTERS
st.sidebar.markdown("### Filters")
 
min_date = df[date_col].min().date()
max_date = df[date_col].max().date()
date_range = st.sidebar.date_input(
    "Time Period",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)
if len(date_range) == 2:
    start_d, end_d = date_range
    df_f = df[(df[date_col].dt.date >= start_d) & (df[date_col].dt.date <= end_d)].copy()
else:
    df_f = df.copy()
 
if region_col:
    regions = sorted(df_f[region_col].dropna().unique().tolist())
    sel_regions = st.sidebar.multiselect("WHO Region", regions, default=regions)
    if sel_regions:
        df_f = df_f[df_f[region_col].isin(sel_regions)]
 
metric = st.sidebar.radio("Primary Metric", ["Cases", "Deaths"], index=0)
main_col   = new_cases_col  if metric == "Cases"  else new_deaths_col
main_label = "New Cases"    if metric == "Cases"  else "New Deaths"
main_color = BLUE           if metric == "Cases"  else RED
 
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='font-size:0.72rem; color:#64748b; line-height:1.7;'>
<strong style='color:#1a202c;'>Role:</strong><br>
Public Health Analyst<br><br>
<strong style='color:#1a202c;'>Stakeholders:</strong><br>
Ministries of Health, international health organizations, and public health decision-makers<br><br>
<strong style='color:#1a202c;'>Source:</strong><br>
WHO COVID-19 Global Data<br>
License: CC BY 4.0
</div>
""", unsafe_allow_html=True)
 
 
# KPI ROW
def fmt(n):
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000:     return f"{n/1_000:.0f}K"
    return str(n)
 
total_cases  = int(df_f[cum_cases_col].max())  if cum_cases_col  else (int(df_f[new_cases_col].sum())  if new_cases_col  else 0)
total_deaths = int(df_f[cum_deaths_col].max()) if cum_deaths_col else (int(df_f[new_deaths_col].sum()) if new_deaths_col else 0)
cfr          = (total_deaths / total_cases * 100) if total_cases > 0 else 0
n_countries  = df_f[country_col].nunique() if country_col else 0
 
col1, col2, col3, col4 = st.columns(4)
 
with col1:
    st.markdown(f"""<div class="kpi-card">
      <div class="kpi-label">Total Cases</div>
      <div class="kpi-value blue">{fmt(total_cases)}</div>
      <div class="kpi-sub">Cumulative confirmed cases</div>
    </div>""", unsafe_allow_html=True)
 
with col2:
    st.markdown(f"""<div class="kpi-card">
      <div class="kpi-label">Total Deaths</div>
      <div class="kpi-value red">{fmt(total_deaths)}</div>
      <div class="kpi-sub">Cumulative confirmed deaths</div>
    </div>""", unsafe_allow_html=True)
 
with col3:
    st.markdown(f"""<div class="kpi-card">
      <div class="kpi-label">Case Fatality Rate (CFR)</div>
      <div class="kpi-value dark">{cfr:.2f}%</div>
      <div class="kpi-sub">Deaths / Cases x 100</div>
    </div>""", unsafe_allow_html=True)
 
with col4:
    st.markdown(f"""<div class="kpi-card">
      <div class="kpi-label">Countries Affected</div>
      <div class="kpi-value dark">{n_countries}</div>
      <div class="kpi-sub">Territories with reported data</div>
    </div>""", unsafe_allow_html=True)
 
st.markdown("<hr class='divider'>", unsafe_allow_html=True)
 
 
# CHART 1: GLOBAL TREND
st.markdown('<p class="section-label">01 — Pandemic Timeline</p>', unsafe_allow_html=True)
 
st.markdown("""<div class="narrative">
The global pandemic curve reveals <strong>successive waves</strong> of contagion.
Identifying their peaks and the valleys between them is essential for evaluating
the effectiveness of containment measures and anticipating future outbreaks.
Use the sidebar filters to focus the analysis on a specific period or region.
</div>""", unsafe_allow_html=True)
 
if main_col and date_col:
    trend = df_f.groupby(date_col)[main_col].sum().reset_index()
    trend.columns = ["date", "value"]
    trend["rolling_avg"] = trend["value"].rolling(4, min_periods=1).mean()
 
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Bar(
        x=trend["date"], y=trend["value"],
        name=main_label,
        marker_color=main_color,
        opacity=0.35,
    ))
    fig_trend.add_trace(go.Scatter(
        x=trend["date"], y=trend["rolling_avg"],
        name="4-week rolling average",
        line=dict(color=DARK, width=2),
        mode="lines",
    ))
    fig_trend.update_layout(
        **PLOTLY_LAYOUT,
        height=320,
        title=dict(text=f"Weekly {main_label} — Global", font=dict(size=12, color="#64748b")),
        hovermode="x unified",
        bargap=0.1,
    )
    st.plotly_chart(fig_trend, use_container_width=True)
 
 
# CHART 2 + 3: REGIONAL & TOP COUNTRIES
st.markdown("<hr class='divider'>", unsafe_allow_html=True)
st.markdown('<p class="section-label">02 — Where Did It Hit Hardest? Regional and Country Breakdown</p>', unsafe_allow_html=True)
 
st.markdown("""<div class="narrative">
The pandemic did not affect the world uniformly.
<strong>The Americas and Europe</strong> concentrated the highest case burden,
while regions with limited diagnostic capacity show signs of underreporting.
This comparison is a key tool for prioritizing public health resources.
</div>""", unsafe_allow_html=True)
 
c_left, c_right = st.columns([1, 1])
 
with c_left:
    if region_col and main_col:
        reg_agg = df_f.groupby(region_col)[main_col].sum().reset_index()
        reg_agg.columns = ["region", "value"]
        reg_agg = reg_agg.sort_values("value", ascending=True)
 
        fig_reg = go.Figure(go.Bar(
            x=reg_agg["value"],
            y=reg_agg["region"],
            orientation="h",
            marker=dict(
                color=reg_agg["value"],
                colorscale=[[0, "#bfdbfe"], [0.5, BLUE], [1.0, RED]],
                showscale=False,
            ),
            text=[fmt(v) for v in reg_agg["value"]],
            textposition="outside",
            textfont=dict(size=10, color=DARK),
        ))
        fig_reg.update_layout(
            **PLOTLY_LAYOUT,
            height=310,
            title=dict(text=f"Total {main_label} by WHO Region", font=dict(size=12, color="#64748b")),
        )
        fig_reg.update_xaxes(showticklabels=False, gridcolor="#e5e9f0")
        st.plotly_chart(fig_reg, use_container_width=True)
 
with c_right:
    if country_col and main_col:
        top_n = st.slider("Top N countries", 5, 20, 10, key="top_n")
        top_countries = (
            df_f.groupby(country_col)[main_col]
            .sum()
            .nlargest(top_n)
            .reset_index()
        )
        top_countries.columns = ["country", "value"]
        top_countries = top_countries.sort_values("value", ascending=True)
 
        fig_top = go.Figure(go.Bar(
            x=top_countries["value"],
            y=top_countries["country"],
            orientation="h",
            marker_color=RED,
            opacity=0.8,
            text=[fmt(v) for v in top_countries["value"]],
            textposition="outside",
            textfont=dict(size=9, color=DARK),
        ))
        fig_top.update_layout(
            **PLOTLY_LAYOUT,
            height=310,
            title=dict(text=f"Top {top_n} Countries — {main_label}", font=dict(size=12, color="#64748b")),
        )
        fig_top.update_xaxes(showticklabels=False, gridcolor="#e5e9f0")
        st.plotly_chart(fig_top, use_container_width=True)
 
 
# CHART 4: CASE-FATALITY SCATTERPLOT
st.markdown("<hr class='divider'>", unsafe_allow_html=True)
st.markdown('<p class="section-label">03 — Lethality: Cases vs Deaths by Country</p>', unsafe_allow_html=True)
 
st.markdown("""<div class="narrative">
The <strong>case fatality rate (CFR)</strong> varies enormously between countries,
reflecting differences in hospital capacity, demographics, and reporting quality.
Countries with few cases but high proportional mortality require priority attention
in epidemiological surveillance systems and international cooperation.
</div>""", unsafe_allow_html=True)
 
if country_col and new_cases_col and new_deaths_col:
    try:
        # Aggregate cases and deaths per country
        scatter_df = df_f.groupby(country_col, as_index=False).agg(
            cases=(new_cases_col, "sum"),
            deaths=(new_deaths_col, "sum"),
        )
 
        # Merge region using a safe left-join on country column
        if region_col:
            region_map = (
                df_f[[country_col, region_col]]
                .drop_duplicates(subset=[country_col])
            )
            scatter_df = scatter_df.merge(region_map, on=country_col, how="left")
 
        # Filter noise and compute CFR
        scatter_df = scatter_df[scatter_df["cases"] > 100].copy()
        scatter_df["cfr"] = (scatter_df["deaths"] / scatter_df["cases"] * 100).clip(0, 30)
        scatter_df["size_col"] = scatter_df["cases"].clip(upper=scatter_df["cases"].quantile(0.95))
 
        color_col_scatter = region_col if (region_col and region_col in scatter_df.columns) else None
 
        fig_scatter = px.scatter(
            scatter_df,
            x="cases",
            y="deaths",
            size="size_col",
            size_max=40,
            color=color_col_scatter if color_col_scatter else "cfr",
            hover_name=country_col,
            hover_data={"cfr": ":.2f", "cases": ":,.0f", "deaths": ":,.0f", "size_col": False},
            labels={"cases": "Total Cases", "deaths": "Total Deaths", "cfr": "CFR (%)"},
            color_continuous_scale=[[0, "#bfdbfe"], [0.5, BLUE], [1.0, RED]] if not color_col_scatter else None,
            color_discrete_sequence=px.colors.qualitative.Safe if color_col_scatter else None,
            log_x=True,
            log_y=True,
        )
        fig_scatter.update_layout(
            **PLOTLY_LAYOUT,
            height=400,
            title=dict(text="Cases vs Deaths by Country (log scale)", font=dict(size=12, color="#64748b")),
        )
        fig_scatter.update_traces(marker=dict(opacity=0.75, line=dict(width=0.6, color="#ffffff")))
        st.plotly_chart(fig_scatter, use_container_width=True)
 
    except Exception as e:
        st.error(f"Could not render scatter plot: {e}")
 
 
# LIMITATIONS AND RECOMMENDATIONS
st.markdown("<hr class='divider'>", unsafe_allow_html=True)
st.markdown('<p class="section-label">04 — Limitations and Recommendations</p>', unsafe_allow_html=True)
 
lim_col, rec_col = st.columns(2)
 
with lim_col:
    st.markdown("""<div class="narrative">
<strong>Data Limitations</strong><br><br>
- <strong>Underreporting:</strong> many countries lacked diagnostic capacity, underestimating real case counts.<br>
- <strong>Case definition changes:</strong> WHO and individual countries adjusted criteria throughout the pandemic.<br>
- <strong>Reporting delays:</strong> weekly data carries variable lag times depending on the country.<br>
- <strong>Indirect mortality:</strong> registered deaths do not reflect total excess mortality.
</div>""", unsafe_allow_html=True)
 
with rec_col:
    st.markdown("""<div class="narrative">
<strong>Recommendations for Decision-Makers</strong><br><br>
- Invest in <strong>diagnostic capacity</strong> in low-income regions to reduce underreporting.<br>
- Establish <strong>permanent sentinel surveillance systems</strong>, not only during emergencies.<br>
- Use <strong>adjusted fatality rates</strong> rather than crude CFR for international comparisons.<br>
- Prioritize resources toward countries with high proportional mortality identified in the scatter plot.
</div>""", unsafe_allow_html=True)
 
 
# FOOTER
st.markdown("""
<div class="footer">
  COVID-19 Global Pulse &nbsp;|&nbsp; Data: WHO COVID-19 Dashboard (CC BY 4.0) &nbsp;|&nbsp;
  Role: Public Health Analyst &nbsp;|&nbsp; Built with Streamlit and Plotly
</div>
""", unsafe_allow_html=True)
 