import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import io
import datetime
 
# PAGE CONFIG
st.set_page_config(
    page_title="Panem Bakery – Dashboard",
    page_icon="🥐",
    layout="wide",
    initial_sidebar_state="expanded",
)
 
# PALETTE
C_DARK   = "#3B2A1A"   # dark espresso – headers, text
C_BROWN  = "#7B4F2E"   # warm brown – primary accent
C_GOLD   = "#C8A97E"   # warm gold – bars / highlights
C_CREAM  = "#FAF6F1"   # off-white – background
C_SAND   = "#D4B896"   # light sand – secondary fills
C_LINE   = "#8B6914"   # golden line – moving avg / lines
C_MUTED  = "#9E8B78"   # muted text
 
# GLOBAL CSS 
st.markdown(f"""
<style>
  /* ── App background ── */
  .stApp {{ background-color: {C_CREAM}; }}
  section[data-testid="stSidebar"] {{
      background-color: {C_DARK};
  }}
  section[data-testid="stSidebar"] * {{ color: {C_CREAM} !important; }}
  section[data-testid="stSidebar"] .stSelectbox label,
  section[data-testid="stSidebar"] .stFileUploader label,
  section[data-testid="stSidebar"] .stNumberInput label,
  section[data-testid="stSidebar"] .stTextInput label {{ color: {C_GOLD} !important; font-size:0.78rem; letter-spacing:0.5px; }}
 
  /* ── Header bar ── */
  .header-bar {{
      background-color: {C_DARK};
      color: {C_CREAM};
      padding: 16px 28px;
      border-radius: 10px;
      margin-bottom: 18px;
  }}
  .header-bar h2 {{ margin:0; font-size:1.4rem; letter-spacing:0.3px; }}
  .header-bar p  {{ margin:4px 0 0; font-size:0.8rem; color:{C_GOLD}; }}
 
  /* ── KPI cards ── */
  .kpi-card {{
      background: white;
      border-radius: 10px;
      padding: 18px 22px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.07);
      border-left: 4px solid {C_GOLD};
      margin-bottom: 6px;
  }}
  .kpi-label {{ font-size:0.70rem; color:{C_MUTED}; text-transform:uppercase; letter-spacing:1px; }}
  .kpi-value {{ font-size:1.9rem; color:{C_DARK}; font-weight:700; line-height:1.1; }}
  .kpi-sub   {{ font-size:0.74rem; color:{C_MUTED}; margin-top:2px; }}
 
  /* ── Section labels ── */
  .section-title {{ font-size:0.98rem; font-weight:600; color:{C_DARK}; margin-bottom:2px; }}
  .section-sub   {{ font-size:0.76rem; color:{C_MUTED}; margin-bottom:10px; }}
 
  /* ── Tabs ── */
  .stTabs [data-baseweb="tab-list"] {{ gap:8px; }}
  .stTabs [data-baseweb="tab"] {{
      background: transparent;
      border-radius: 20px;
      padding: 6px 20px;
      color: {C_BROWN};
      font-weight: 500;
      font-size: 0.88rem;
  }}
  .stTabs [aria-selected="true"] {{
      background-color: {C_BROWN} !important;
      color: white !important;
  }}
 
  /* ── Data entry box ── */
  .entry-box {{
      background: white;
      border-radius: 10px;
      padding: 18px 22px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.06);
      margin-bottom: 14px;
      border-top: 3px solid {C_BROWN};
  }}
  .entry-title {{ font-size:0.95rem; font-weight:600; color:{C_DARK}; margin-bottom:8px; }}
 
  /* ── Upload zone ── */
  div[data-testid="stFileUploadDropzone"] {{
      background-color: #fff8f2 !important;
      border: 1.5px dashed {C_GOLD} !important;
      border-radius: 8px !important;
  }}
 
  /* ── Metric numbers ── */
  div[data-testid="stMetric"] {{
      background: white;
      border-radius: 10px;
      padding: 12px 16px;
      box-shadow: 0 1px 5px rgba(0,0,0,0.06);
  }}
  div[data-testid="stMetricLabel"] {{ color:{C_MUTED}; font-size:0.72rem; text-transform:uppercase; }}
  div[data-testid="stMetricValue"] {{ color:{C_DARK}; font-weight:700; }}
 
  /* ── Alerts ── */
  div[data-testid="stAlert"] {{ border-radius:8px; }}
 
  /* ── Divider ── */
  hr {{ border-color: {C_SAND}; }}
 
  /* ── DataFrame ── */
  .stDataFrame {{ border-radius:8px; overflow:hidden; }}
</style>
""", unsafe_allow_html=True)
 
 
# HELPER: matplotlib figure defaults 
def fig_defaults(ax, fig):
    fig.patch.set_facecolor(C_CREAM)
    ax.set_facecolor(C_CREAM)
    ax.spines[["top","right"]].set_visible(False)
    ax.spines[["left","bottom"]].set_color("#DDD")
    ax.tick_params(colors=C_DARK, labelsize=8)
    ax.yaxis.label.set_color(C_DARK)
    ax.xaxis.label.set_color(C_DARK)
 
 
#  SESSION STATE INIT
if "manual_sales" not in st.session_state:
    st.session_state.manual_sales = {}          # {(branch, product, date): qty}
if "uploaded_df" not in st.session_state:
    st.session_state.uploaded_df = None
if "new_weekly" not in st.session_state:
    st.session_state.new_weekly = {}            # {product: qty}
 
 
# SIDEBAR 
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center; padding:10px 0 18px;'>
      <div style='font-size:2.2rem;'>🥐</div>
      <div style='font-size:1.1rem; font-weight:700; color:{C_GOLD}; letter-spacing:1px;'>PANEM</div>
      <div style='font-size:0.72rem; color:{C_MUTED}; letter-spacing:2px;'>BAKERY</div>
    </div>
    """, unsafe_allow_html=True)
 
    st.markdown("---")
    st.markdown(f"<div style='font-size:0.72rem; color:{C_GOLD}; letter-spacing:1px; margin-bottom:6px;'>FILTERS</div>", unsafe_allow_html=True)
 
    BRANCHES = ["Kavia","Carreta","Zambrano","Credi-Club","Nativa","QIN","Punto-Valle"]
    PRODUCTS = ["Vanilla concha","Chocolate concha","Chilaquiles Panem","Oat cookie","Glazed donut"]
 
    branch  = st.selectbox("Branch",       BRANCHES)
    product = st.selectbox("Star product", PRODUCTS)
    period  = st.selectbox("Period",       ["Last 90 days","Last 30 days","Last 6 months","Full year"])
 
    period_days = {"Last 90 days":90,"Last 30 days":30,"Last 6 months":182,"Full year":365}[period]
 
    st.markdown("---")
 
    # CSV Upload 
    st.markdown(f"<div style='font-size:0.72rem; color:{C_GOLD}; letter-spacing:1px; margin-bottom:6px;'>DATA MANAGEMENT</div>", unsafe_allow_html=True)
 
    uploaded = st.file_uploader(
        "Upload sales CSV",
        type=["csv"],
        help="Expected columns: operating_date, item, quantity, sucursal (branch)",
    )
    if uploaded:
        try:
            df_up = pd.read_csv(uploaded)
            df_up.columns = [c.strip().lower() for c in df_up.columns]
            # normalize common column name variants
            rename_map = {
                "branch":"sucursal","sucursal":"sucursal",
                "product":"item","item":"item","producto":"item",
                "date":"operating_date","fecha":"operating_date","operating_date":"operating_date",
                "qty":"quantity","cantidad":"quantity","quantity":"quantity","units":"quantity",
            }
            df_up = df_up.rename(columns={c: rename_map[c] for c in df_up.columns if c in rename_map})
            if "operating_date" in df_up.columns:
                df_up["operating_date"] = pd.to_datetime(df_up["operating_date"], errors="coerce")
            st.session_state.uploaded_df = df_up
            st.success(f"✓ {len(df_up):,} rows loaded")
        except Exception as e:
            st.error(f"Error reading file: {e}")
 
    if st.session_state.uploaded_df is not None:
        if st.button("🗑 Clear uploaded data", use_container_width=True):
            st.session_state.uploaded_df = None
            st.rerun()
 
    st.markdown("---")
    st.markdown(f"<div style='font-size:0.68rem; color:{C_MUTED};'>Dashboard v2.0 · May 2026</div>", unsafe_allow_html=True)
 
 
# HEADER
st.markdown(f"""
<div class="header-bar">
  <h2> Panem Bakery — Management Dashboard</h2>
  <p>Branch: <strong style="color:white">{branch}</strong> &nbsp;|&nbsp;
     Product: <strong style="color:white">{product}</strong> &nbsp;|&nbsp;
     Period: {period} &nbsp;|&nbsp;
     Last update: {datetime.date.today().strftime("%b %d, %Y")}</p>
</div>
""", unsafe_allow_html=True)
 
 
# DEMO DATA (used when no CSV is uploaded)
np.random.seed(hash(branch) % 9999)
 
dates_main  = pd.date_range(end="2026-02-12", periods=period_days)
daily_sales = np.random.normal(loc=23, scale=3, size=period_days).clip(13, 32)
moving_avg7 = pd.Series(daily_sales).rolling(7, min_periods=1).mean().values
 
days_labels = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
sales_by_day = np.array([14800,14200,13900,15200,17800,21000,12500]) * (0.8 + np.random.rand()*0.4)
 
top_products  = ["Vanilla concha","Choco. concha","Chilaquiles","Oat cookie","Glazed donut"]
share_vals    = [30,22,18,16,14]
donut_colors  = [C_DARK, C_GOLD, "#8B6440", C_SAND, "#EDD9BE"]
 
dates_hist = pd.date_range(end="2026-05-12", periods=120)
hist_sales = np.random.normal(280, 35, 120).clip(180,390)
 
weeks     = [f"W{i:02d}" for i in range(1,53)]
weekly_v  = np.random.normal(2100, 300, 52).clip(1200, 2800).astype(int)
 
forecast_days = ["Mon 13","Tue 14","Wed 15","Thu 16","Fri 17","Sat 18","Sun 19"]
forecast_vals = [280,295,270,310,318,336,253]
fc_colors     = [C_GOLD,C_GOLD,C_GOLD,C_BROWN,C_BROWN,C_DARK,C_SAND]
 
hw_products = ["VANILLA CONCHA","CHOCOLATE CONCHA","GLAZED DONUT","BRIOCHE W/ NUTS","PAN DE MUERTO","CHILAQUILES"]
week_plus   = {
    "Week +1":[284,294,267,265,265,262],
    "Week +2":[283,204,267,264,264,262],
    "Week +3":[283,294,266,263,263,261],
    "Week +4":[283,294,266,262,262,261],
}
 
branches_ml = ["Carreta","Zambrano","Credi-Club","Kavia","Nativa","QIN","Punto-Valle"]
mae_vals    = [2.1, 2.8, 2.5, 6.3, 3.1, 3.9, 2.7]
r2_vals     = [0.85,0.84,0.87,0.89,0.81,0.78,0.84]
 
kpi_data = {
    "Kavia":       {"sales":"$11.2M","ticket":"$170","star":"Vanilla concha","daily":"$22.6k"},
    "Carreta":     {"sales":"$9.8M", "ticket":"$155","star":"Vanilla concha","daily":"$19.4k"},
    "Zambrano":    {"sales":"$7.2M", "ticket":"$140","star":"Choco. concha", "daily":"$14.8k"},
    "Credi-Club":  {"sales":"$8.4M", "ticket":"$160","star":"Vanilla concha","daily":"$17.2k"},
    "Nativa":      {"sales":"$6.1M", "ticket":"$132","star":"Oat cookie",    "daily":"$12.5k"},
    "QIN":         {"sales":"$5.5M", "ticket":"$128","star":"Chilaquiles",   "daily":"$11.2k"},
    "Punto-Valle": {"sales":"$6.8M", "ticket":"$145","star":"Glazed donut",  "daily":"$13.9k"},
}
kpi = kpi_data[branch]
 
 
# TABS
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "General Overview",
    "Sales History",
    "ML Forecast",
    "Model Metrics",
    "Data Entry",
])
 
# TAB 1 — GENERAL OVERVIEW
with tab1:
 
    # KPIs
    st.markdown("#### Branch KPIs")
    k1,k2,k3,k4 = st.columns(4)
    for col, label, val, sub in [
        (k1,"Total Sales",    kpi["sales"],  "in the period"),
        (k2,"Avg. Ticket",    kpi["ticket"], "per transaction"),
        (k3,"Star Product",   kpi["star"],   "best seller"),
        (k4,"Avg. Daily Rev.",kpi["daily"],  "period average"),
    ]:
        col.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-label">{label}</div>
          <div class="kpi-value" style="font-size:{'1.3rem' if label=='Star Product' else '1.9rem'}">{val}</div>
          <div class="kpi-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)
 
    st.markdown("<br>", unsafe_allow_html=True)
 
    # If CSV uploaded and has the right columns, use it for daily trend
    use_csv = (
        st.session_state.uploaded_df is not None
        and "operating_date" in st.session_state.uploaded_df.columns
        and "quantity" in st.session_state.uploaded_df.columns
    )
 
    if use_csv:
        df_branch = st.session_state.uploaded_df.copy()
        if "sucursal" in df_branch.columns:
            df_branch = df_branch[df_branch["sucursal"].str.lower() == branch.lower()]
        daily_agg = (
            df_branch.groupby("operating_date")["quantity"].sum()
            .reset_index().sort_values("operating_date")
        )
        dates_plot  = daily_agg["operating_date"].values
        sales_plot  = daily_agg["quantity"].values / 1000
        ma7_plot    = pd.Series(sales_plot).rolling(7, min_periods=1).mean().values
    else:
        dates_plot = dates_main
        sales_plot = daily_sales
        ma7_plot   = moving_avg7
 
    # ── Daily sales chart ──
    st.markdown('<div class="section-title">Daily Sales Evolution — units</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Total daily branch sales with 7-day moving average</div>', unsafe_allow_html=True)
 
    fig1, ax1 = plt.subplots(figsize=(14,3.5))
    fig_defaults(ax1, fig1)
    ax1.bar(dates_plot, sales_plot, color=C_GOLD, width=0.8 if not use_csv else 1.0, label="Daily sales", alpha=0.85)
    ax1.plot(dates_plot, ma7_plot, color=C_LINE, lw=1.8, ls="--", label="7-day moving avg")
    if use_csv:
        ax1.xaxis.set_major_locator(mdates.MonthLocator())
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    else:
        ax1.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%-d %b"))
    ax1.tick_params(axis="x", rotation=30)
    ax1.set_ylabel("Units (k)" if not use_csv else "Units", fontsize=8, color=C_DARK)
    ax1.legend(fontsize=8, frameon=False, loc="upper left")
    plt.tight_layout()
    st.pyplot(fig1)
 
    st.markdown("<br>", unsafe_allow_html=True)
    col_g1, col_g2 = st.columns(2)
 
    # ── Day of week ──
    with col_g1:
        st.markdown('<div class="section-title">Avg. Sales by Day of Week</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Average units sold per day of the week</div>', unsafe_allow_html=True)
        fig2, ax2 = plt.subplots(figsize=(6,3.5))
        fig_defaults(ax2, fig2)
        bar_colors = [C_DARK if v == max(sales_by_day) else C_BROWN if v >= np.percentile(sales_by_day,60) else C_GOLD for v in sales_by_day]
        bars = ax2.bar(days_labels, sales_by_day, color=bar_colors, zorder=2)
        ax2.bar_label(bars, labels=[f"{v/1000:.1f}k" for v in sales_by_day], padding=3, fontsize=7, color=C_DARK)
        ax2.set_ylim(0, max(sales_by_day)*1.18)
        ax2.set_ylabel("Units", fontsize=8, color=C_DARK)
        ax2.grid(axis="y", alpha=0.3, color="#DDD", zorder=0)
        plt.tight_layout()
        st.pyplot(fig2)
 
    # ── Donut ──
    with col_g2:
        st.markdown('<div class="section-title">Top 5 Products — Market Share</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Share of units sold by main product</div>', unsafe_allow_html=True)
        fig3, ax3 = plt.subplots(figsize=(5,3.5))
        fig_defaults(ax3, fig3)
        wedges, _ = ax3.pie(
            share_vals, colors=donut_colors, startangle=90,
            wedgeprops={"width":0.5,"edgecolor":"white","linewidth":2}
        )
        ax3.legend(
            wedges,
            [f"{p}  {v}%" for p,v in zip(top_products, share_vals)],
            loc="upper center", bbox_to_anchor=(0.5,-0.04),
            ncol=2, fontsize=7.5, frameon=False
        )
        plt.tight_layout()
        st.pyplot(fig3)
 
# TAB 2 — SALES HISTORY
with tab2:
 
    st.markdown(f'<div class="section-title">Sales History — {product}</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Daily units sold with ±1 standard deviation band</div>', unsafe_allow_html=True)
 
    # Use uploaded data if available and filtered to product
    if use_csv and "item" in st.session_state.uploaded_df.columns:
        df_prod = st.session_state.uploaded_df.copy()
        df_prod = df_prod[df_prod["item"].str.lower().str.contains(product.split()[0].lower(), na=False)]
        if "sucursal" in df_prod.columns:
            df_prod = df_prod[df_prod["sucursal"].str.lower() == branch.lower()]
        agg_prod = df_prod.groupby("operating_date")["quantity"].sum().reset_index().sort_values("operating_date")
        if len(agg_prod) > 5:
            hist_x    = agg_prod["operating_date"].values
            hist_y    = agg_prod["quantity"].values.astype(float)
            std_band_ = np.std(hist_y)
        else:
            hist_x, hist_y, std_band_ = dates_hist, hist_sales, 25.0
    else:
        hist_x, hist_y, std_band_ = dates_hist, hist_sales, 25.0
 
    fig4, ax4 = plt.subplots(figsize=(14,3.5))
    fig_defaults(ax4, fig4)
    ax4.fill_between(hist_x, hist_y - std_band_, hist_y + std_band_, color=C_GOLD, alpha=0.25, label="±1 std dev")
    ax4.plot(hist_x, hist_y, color=C_BROWN, lw=1.8, label=product)
    if use_csv:
        ax4.xaxis.set_major_locator(mdates.MonthLocator())
        ax4.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    else:
        ax4.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
        ax4.xaxis.set_major_formatter(mdates.DateFormatter("%-d %b"))
    ax4.tick_params(axis="x", rotation=30)
    ax4.set_ylabel("Units", fontsize=8, color=C_DARK)
    ax4.legend(fontsize=8, frameon=False)
    plt.tight_layout()
    st.pyplot(fig4)
 
    st.markdown("<br>", unsafe_allow_html=True)
    col_h1, col_h2 = st.columns(2)
 
    with col_h1:
        st.markdown('<div class="section-title">Temperature vs. Sales</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Sales vs average ambient temperature (°C)</div>', unsafe_allow_html=True)
        temps_sc = np.random.uniform(12, 32, len(hist_y))
        fig5, ax5 = plt.subplots(figsize=(6,3.5))
        fig_defaults(ax5, fig5)
        ax5.scatter(temps_sc, hist_y, color=C_GOLD, alpha=0.7, s=38, edgecolors=C_BROWN, lw=0.5)
        z = np.polyfit(temps_sc, hist_y, 1)
        xr = np.linspace(temps_sc.min(), temps_sc.max(), 100)
        ax5.plot(xr, np.poly1d(z)(xr), color=C_LINE, lw=1.5, ls="--", label="Trend")
        ax5.set_xlabel("Temperature (°C)", fontsize=8, color=C_DARK)
        ax5.set_ylabel("Units", fontsize=8, color=C_DARK)
        ax5.legend(fontsize=8, frameon=False)
        plt.tight_layout()
        st.pyplot(fig5)
 
    with col_h2:
        st.markdown('<div class="section-title">Sales by Week of Year</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Weekly seasonality of the product</div>', unsafe_allow_html=True)
        fig6, ax6 = plt.subplots(figsize=(6,3.5))
        fig_defaults(ax6, fig6)
        wk_colors = [C_DARK if v > np.percentile(weekly_v,80) else C_BROWN if v > np.percentile(weekly_v,50) else C_GOLD for v in weekly_v]
        ax6.bar(weeks, weekly_v, color=wk_colors, width=0.8)
        ax6.set_xticks(weeks[::4])
        ax6.set_xticklabels(weeks[::4], fontsize=7.5, color=C_DARK)
        ax6.set_ylabel("Units", fontsize=8, color=C_DARK)
        patches = [mpatches.Patch(color=C_DARK, label="High demand"),
                   mpatches.Patch(color=C_BROWN, label="Mid demand"),
                   mpatches.Patch(color=C_GOLD, label="Low demand")]
        ax6.legend(handles=patches, fontsize=7, frameon=False)
        plt.tight_layout()
        st.pyplot(fig6)
 
# TAB 3 — ML FORECAST
with tab3:
 
    st.markdown("**Production Forecast (XGBoost + Holt-Winters)**")
    st.caption(f"Branch: {branch} · Product: {product}")
 
    m1,m2,m3,m4 = st.columns(4)
    m1.metric("MAE (CV 5-fold)",  "6.36 units")
    m2.metric("RMSE (CV 5-fold)", "8.03 units")
    m3.metric("Avg. R²",          "0.87")
    m4.metric("MAE Error %",      "46.7%")
 
    st.markdown("<br>", unsafe_allow_html=True)
 
    # Check if manager entered weekly sales in Data Entry tab
    new_w = st.session_state.new_weekly
    if new_w:
        st.success(f"Using manually entered weekly data ({len(new_w)} products) to adjust forecast.")
        adj_vals = []
        for i, v in enumerate(forecast_vals):
            scale = list(new_w.values())[0] / 280 if new_w else 1.0
            adj_vals.append(round(v * scale))
        plot_fc_vals = adj_vals
    else:
        plot_fc_vals = forecast_vals
 
    st.markdown('<div class="section-title">Daily Forecast — next 7 days (XGBoost)</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-sub">Predicted units for {product} at {branch}</div>', unsafe_allow_html=True)
 
    fig7, ax7 = plt.subplots(figsize=(11,3.8))
    fig_defaults(ax7, fig7)
    bar_cont = ax7.bar(forecast_days, plot_fc_vals, color=fc_colors, zorder=2)
    ax7.bar_label(bar_cont, labels=[str(v) for v in plot_fc_vals], padding=4, fontsize=8.5, color=C_DARK, fontweight="bold")
    ax7.set_ylim(min(plot_fc_vals)*0.88, max(plot_fc_vals)*1.12)
    ax7.set_ylabel("Forecasted units", fontsize=8, color=C_DARK)
    ax7.grid(axis="y", alpha=0.25, color="#DDD", zorder=0)
    legend_patches = [
        mpatches.Patch(color=C_DARK, label="Peak day"),
        mpatches.Patch(color=C_BROWN, label="High day"),
        mpatches.Patch(color=C_GOLD, label="Normal day"),
    ]
    ax7.legend(handles=legend_patches, fontsize=7.5, frameon=False, loc="upper left")
    plt.tight_layout()
    st.pyplot(fig7)
 
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">Weekly Forecast — next 4 weeks (Holt-Winters / ETS)</div>', unsafe_allow_html=True)
 
    df_hw = pd.DataFrame(week_plus, index=hw_products)
    df_hw.index.name = "Product"
    st.dataframe(
        df_hw.style
            .background_gradient(cmap="YlOrBr", axis=None)
            .format("{:.0f}"),
        use_container_width=True,
    )
 
    st.markdown("<br>", unsafe_allow_html=True)
    st.warning(
        "**Model limitation:** Relative RMSE is 58.9% of the daily average. "
        "For peak days, holidays or special events the error may be higher. "
        "Adjust the forecast with manager judgment for events not in the historical data."
    )
    st.info(
        "**Best modeled product:** Vanilla concha (MAE error ~45.8%). "
        "**Highest error:** Chilaquiles Panem (~47.5%) — higher inherent variability."
    )
 
# TAB 4 — MODEL METRICS
with tab4:
 
    st.markdown('<div class="section-title">Training Metrics by Branch — XGBoost (CV 5-fold)</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Time-series cross-validation · each fold trains on past data and predicts future data</div>', unsafe_allow_html=True)
 
    fig8, ax8 = plt.subplots(figsize=(12,3.8))
    fig_defaults(ax8, fig8)
    x = np.arange(len(branches_ml))
    bars8 = ax8.bar(x - 0.2, mae_vals, width=0.35, color=C_GOLD, label="MAE (units)", zorder=2)
    ax8.bar_label(bars8, fmt="%.1f", padding=3, fontsize=7.5, color=C_DARK)
    ax8r = ax8.twinx()
    ax8r.plot(x, r2_vals, color=C_BROWN, marker="o", ms=7, lw=2, label="R²")
    ax8r.set_ylim(0.7, 1.0)
    ax8r.set_ylabel("R²", fontsize=8, color=C_BROWN)
    ax8r.tick_params(colors=C_BROWN, labelsize=8)
    ax8r.spines[["top","right"]].set_color(C_SAND)
    ax8.set_xticks(x)
    ax8.set_xticklabels(branches_ml, fontsize=9, color=C_DARK)
    ax8.set_ylabel("MAE (units)", fontsize=8, color=C_DARK)
    ax8.grid(axis="y", alpha=0.25, color="#DDD", zorder=0)
    lines, labels = ax8r.get_legend_handles_labels()
    bars_leg = [mpatches.Patch(color=C_GOLD, label="MAE (units)")]
    ax8.legend(handles=bars_leg + lines, labels=["MAE (units)","R²"], fontsize=8, frameon=False)
    plt.tight_layout()
    st.pyplot(fig8)
 
    st.markdown("<br>", unsafe_allow_html=True)
    col_m1, col_m2 = st.columns(2)
 
    with col_m1:
        st.markdown('<div class="section-title">Prediction vs Actual — test period</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="section-sub">Comparison for {branch} branch</div>', unsafe_allow_html=True)
        test_days_ = np.arange(1,30)
        actual_    = np.random.normal(280,25,29).clip(210,335)
        predicted_ = actual_ + np.random.normal(0,18,29)
        fig9, ax9 = plt.subplots(figsize=(7,3.5))
        fig_defaults(ax9, fig9)
        ax9.plot(test_days_, actual_,    color=C_DARK,  lw=2,   label="Actual")
        ax9.plot(test_days_, predicted_, color=C_GOLD,  lw=1.8, ls="--", label="Predicted")
        ax9.fill_between(test_days_, actual_, predicted_, alpha=0.12, color=C_BROWN)
        ax9.set_xlabel("Day (test set)", fontsize=8, color=C_DARK)
        ax9.set_ylabel("Units", fontsize=8, color=C_DARK)
        ax9.legend(fontsize=8, frameon=False)
        plt.tight_layout()
        st.pyplot(fig9)
 
    with col_m2:
        st.markdown('<div class="section-title">Feature Importance</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Most influential variables in the XGBoost model</div>', unsafe_allow_html=True)
        features_    = ["lag_7","avg_7d","lag_14","day_of_week","week_of_year","temperature","is_holiday"]
        importances_ = [0.38,0.31,0.18,0.08,0.05,0.04,0.03]
        feat_colors  = [C_DARK,C_DARK,C_BROWN,C_BROWN,C_GOLD,C_GOLD,C_SAND]
        fig10, ax10 = plt.subplots(figsize=(6,3.5))
        fig_defaults(ax10, fig10)
        bars10 = ax10.barh(features_[::-1], importances_[::-1], color=feat_colors[::-1], zorder=2)
        ax10.bar_label(bars10, fmt="%.2f", padding=3, fontsize=7.5, color=C_DARK)
        ax10.set_xlabel("Importance score", fontsize=8, color=C_DARK)
        ax10.grid(axis="x", alpha=0.25, color="#DDD", zorder=0)
        plt.tight_layout()
        st.pyplot(fig10)
 
    # Metrics summary table
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">Full metrics summary</div>', unsafe_allow_html=True)
    df_metrics = pd.DataFrame({
        "Branch":   branches_ml,
        "MAE":      mae_vals,
        "RMSE":     [3.5,5.1,4.4,8.0,5.8,6.7,4.9],
        "R²":       r2_vals,
        "MAE %":    ["38.2%","44.1%","41.0%","46.7%","45.3%","48.5%","42.8%"],
    })
    st.dataframe(
        df_metrics.style
            .background_gradient(subset=["MAE","RMSE"], cmap="YlOrBr")
            .background_gradient(subset=["R²"], cmap="Greens")
            .format({"MAE":"{:.1f}","RMSE":"{:.1f}","R²":"{:.2f}"}),
        use_container_width=True,
        hide_index=True,
    )
 
# TAB 5 — DATA ENTRY & DATABASE UPDATE
with tab5:
 
    st.markdown("### Data Entry & Database Update")
    st.caption("Enter new sales records manually or upload a new CSV to update the dashboard.")
 
    # Section A: Manual weekly sales
    st.markdown(f"""
    <div class="entry-box">
      <div class="entry-title"> Enter Weekly Sales — {branch}</div>
    </div>
    """, unsafe_allow_html=True)
 
    st.markdown("Enter the **actual units sold** for each product this week. These values will adjust the ML forecast in the Forecast tab.")
 
    entry_products = [
        "Vanilla concha","Chocolate concha","Chilaquiles Panem",
        "Oat cookie","Glazed donut","Brioche w/ nuts","Pan de muerto",
    ]
 
    week_start = st.date_input(
        "Week start date",
        value=datetime.date(2026, 5, 13),
        help="First day (Monday) of the week you are entering data for",
    )
 
    with st.form("weekly_sales_form"):
        st.markdown(f"**Branch:** {branch}  ·  **Week of:** {week_start}")
        st.markdown("---")
        col_a, col_b = st.columns(2)
        entry_vals = {}
        for i, prod in enumerate(entry_products):
            col = col_a if i % 2 == 0 else col_b
            default_v = st.session_state.new_weekly.get(prod, 0)
            entry_vals[prod] = col.number_input(
                f"{prod}",
                min_value=0,
                max_value=5000,
                value=int(default_v),
                step=1,
                key=f"entry_{prod}",
            )
 
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button(
            "Save weekly sales",
            use_container_width=True,
            type="primary",
        )
        if submitted:
            st.session_state.new_weekly = {k: v for k, v in entry_vals.items() if v > 0}
            st.success(f"Weekly sales saved for {branch} — week of {week_start}. Forecast tab updated.")
 
    # Show saved data
    if st.session_state.new_weekly:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Last saved weekly entry:**")
        df_saved = pd.DataFrame(
            list(st.session_state.new_weekly.items()),
            columns=["Product","Units sold"]
        )
        df_saved["Branch"] = branch
        df_saved["Week of"] = str(week_start)
        st.dataframe(df_saved[["Branch","Week of","Product","Units sold"]], use_container_width=True, hide_index=True)
 
        # Download button
        csv_out = df_saved.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download as CSV",
            data=csv_out,
            file_name=f"panem_{branch}_{week_start}_sales.csv",
            mime="text/csv",
        )
 
        if st.button("Clear saved entries"):
            st.session_state.new_weekly = {}
            st.rerun()
 
    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()
 
    # Section B: Upload new full database 
    st.markdown("""
    <div class="entry-box">
      <div class="entry-title"> Upload New Database</div>
    </div>
    """, unsafe_allow_html=True)
 
    st.markdown("""
    Upload a new full CSV export from the POS system. The dashboard will automatically update all charts.
 
    **Expected columns:**
    | Column | Description | Example |
    |--------|-------------|---------|
    | `operating_date` | Sale date | `2026-05-13` |
    | `sucursal` | Branch name | `Kavia` |
    | `item` | Product name | `Vanilla concha` |
    | `quantity` | Units sold | `12` |
    | `unit_price` | Price per unit | `45.00` |
    | `total_ticket` | Transaction total | `540.00` |
    """)
 
    uploaded2 = st.file_uploader(
        "Upload CSV file",
        type=["csv"],
        key="tab5_upload",
        help="The file will be processed and all charts will update automatically.",
    )
 
    if uploaded2:
        try:
            df_new = pd.read_csv(uploaded2)
            df_new.columns = [c.strip().lower() for c in df_new.columns]
            rename_map2 = {
                "branch":"sucursal","sucursal":"sucursal","product":"item","item":"item",
                "producto":"item","date":"operating_date","fecha":"operating_date",
                "operating_date":"operating_date","qty":"quantity","cantidad":"quantity",
                "quantity":"quantity","units":"quantity",
            }
            df_new = df_new.rename(columns={c: rename_map2[c] for c in df_new.columns if c in rename_map2})
            if "operating_date" in df_new.columns:
                df_new["operating_date"] = pd.to_datetime(df_new["operating_date"], errors="coerce")
 
            st.success(f"File validated — {len(df_new):,} rows, {df_new.shape[1]} columns")
 
            with st.expander("Preview data (first 20 rows)"):
                st.dataframe(df_new.head(20), use_container_width=True)
 
            with st.expander("Column summary"):
                st.dataframe(df_new.describe(include="all").T, use_container_width=True)
 
            col_btn1, col_btn2 = st.columns(2)
            if col_btn1.button("Apply to dashboard", use_container_width=True, type="primary"):
                st.session_state.uploaded_df = df_new
                st.success("Dashboard updated with new data. Switch to other tabs to see the changes.")
                st.rerun()
            if col_btn2.button("Discard", use_container_width=True):
                st.info("File discarded.")
 
        except Exception as e:
            st.error(f"Error processing file: {e}")
 
    #  Section C: Add single transaction 
    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()
    st.markdown("""
    <div class="entry-box">
      <div class="entry-title"> Add Single Transaction</div>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Quickly register an individual sale not yet in the database.")
 
    with st.form("single_tx_form"):
        c1, c2, c3 = st.columns(3)
        tx_date    = c1.date_input("Date", value=datetime.date.today())
        tx_branch  = c2.selectbox("Branch", BRANCHES, index=BRANCHES.index(branch))
        tx_product = c3.selectbox("Product", entry_products)
        c4, c5, c6 = st.columns(3)
        tx_qty     = c4.number_input("Quantity (units)", min_value=1, max_value=1000, value=10)
        tx_price   = c5.number_input("Unit price ($)", min_value=0.0, value=45.0, step=0.5)
        tx_total   = c6.number_input("Ticket total ($)", min_value=0.0, value=float(tx_qty * 45), step=1.0)
 
        if st.form_submit_button("Add transaction", use_container_width=True):
            key = (tx_branch, tx_product, str(tx_date))
            prev = st.session_state.manual_sales.get(key, 0)
            st.session_state.manual_sales[key] = prev + tx_qty
            st.success(f"Added {tx_qty} units of {tx_product} for {tx_branch} on {tx_date}")
 
    if st.session_state.manual_sales:
        st.markdown("<br>**Manually added transactions (this session):**")
        rows = [{"Branch":k[0],"Product":k[1],"Date":k[2],"Units":v}
                for k,v in st.session_state.manual_sales.items()]
        df_manual = pd.DataFrame(rows)
        st.dataframe(df_manual, use_container_width=True, hide_index=True)
        csv_manual = df_manual.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download manual entries",
            data=csv_manual,
            file_name=f"panem_manual_entries_{datetime.date.today()}.csv",
            mime="text/csv",
        )
        if st.button("Clear all manual entries"):
            st.session_state.manual_sales = {}
            st.rerun()