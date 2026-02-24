import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os, io

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="Netflix Data Explorer", layout="wide", page_icon="🍿")

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }

/* ── App background ───────────────────────────── */
.stApp { background: #111317; }

/* ── Sidebar ──────────────────────────────────── */
section[data-testid="stSidebar"] > div {
    background: #0d0f12;
    border-right: 1px solid #1f2227;
}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span  { color: #b0b4bc !important; }

/* ── Main layout ──────────────────────────────── */
.main .block-container { padding: 1.8rem 2.6rem 3rem; max-width: 1500px; }

/* ── KPI cards ────────────────────────────────── */
div[data-testid="stMetric"] {
    background: linear-gradient(145deg, #1c1e24 0%, #14161a 100%);
    padding: 1.3rem 1.6rem 1.1rem;
    border-radius: 14px;
    border: 1px solid #25282f;
    box-shadow: 0 3px 18px rgba(0,0,0,.55), inset 0 1px 0 rgba(255,255,255,.04);
    transition: transform .22s ease, box-shadow .22s ease, border-color .22s ease;
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-5px);
    border-color: #E50914;
    box-shadow: 0 8px 30px rgba(229,9,20,.2);
}
div[data-testid="stMetricValue"] {
    font-size: 2.2rem !important; font-weight: 900 !important;
    background: linear-gradient(135deg, #FF3B47, #C20018);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
div[data-testid="stMetricLabel"] {
    font-size: 0.72rem !important; font-weight: 700 !important;
    color: #6b7280 !important; text-transform: uppercase; letter-spacing: 1.5px;
}

/* ── Chart card ───────────────────────────────── */
.chart-card {
    background: linear-gradient(145deg, #18191f 0%, #13141a 100%);
    border: 1px solid #23252c;
    border-radius: 16px;
    padding: 1.4rem 1.6rem 0.8rem;
    box-shadow: 0 2px 20px rgba(0,0,0,.4);
    margin-bottom: 0.5rem;
}
.chart-card h3 {
    font-size: 1rem !important; font-weight: 700 !important;
    color: #e5e7eb !important; margin: 0 0 0.8rem 0 !important;
}

/* ── Section pill ─────────────────────────────── */
.pill {
    display: inline-block;
    background: linear-gradient(90deg, #E50914 0%, #8B0000 100%);
    color: #fff;
    font-size: 0.68rem; font-weight: 800;
    letter-spacing: 2px; text-transform: uppercase;
    padding: 5px 15px; border-radius: 999px; margin-bottom: 1rem;
}

/* ── Divider ──────────────────────────────────── */
hr { border: none; border-top: 1px solid #1f2227; margin: 2rem 0; }

/* ── Footer ───────────────────────────────────── */
.footer {
    text-align: center; color: #3d4148;
    font-size: 0.78rem; padding: 1.8rem 0 .5rem;
    border-top: 1px solid #1a1d22;
}

/* ── DataFrame ────────────────────────────────── */
.stDataFrame { border-radius: 12px !important; border: 1px solid #23252c !important; }
</style>
""", unsafe_allow_html=True)

# ─── Shared chart constants ───────────────────────────────────────────────────
BG   = "rgba(0,0,0,0)"
FC   = "#9ca3af"          # axis / label colour
GRID = "#1f2227"
M    = dict(t=10, b=10, l=0, r=0)
RED  = "#E50914"
PALE = "#f3f4f6"

# One-stop chart layout helper
def styled(fig, *, xgrid=False, ygrid=True, legend_bottom=False, **kw):
    fig.update_layout(
        paper_bgcolor=BG, plot_bgcolor=BG,
        font=dict(color=FC, family="Inter"),
        margin=M,
        hoverlabel=dict(bgcolor="#1a1d22", font_color="#e5e7eb", font_family="Inter",
                        bordercolor="#333"),
    )
    # Axis grid + tick colours
    fig.update_xaxes(showgrid=xgrid, gridcolor=GRID, zeroline=False,
                     tickfont=dict(color=FC), title_font=dict(color=FC))
    fig.update_yaxes(showgrid=ygrid, gridcolor=GRID, zeroline=False,
                     tickfont=dict(color=FC), title_font=dict(color=FC))
    if legend_bottom:
        fig.update_layout(legend=dict(orientation="h", y=-0.18, x=0.5,
                                      xanchor="center", bgcolor="rgba(0,0,0,0)",
                                      font=dict(color=FC)))
    if kw:
        fig.update_layout(**kw)
    return fig

# ─── Data helpers ─────────────────────────────────────────────────────────────
@st.cache_data
def load_default():
    base = os.path.dirname(os.path.abspath(__file__))
    return pd.read_csv(os.path.join(base, "..", "netflix_titles.csv"))

@st.cache_data
def load_uploaded(b, name):
    return pd.read_csv(io.BytesIO(b))

def clean(df):
    df = df.dropna(subset=["type","release_year","rating","country","duration"]).copy()
    m = df["type"] == "Movie"
    df.loc[m, "duration_int"] = (df.loc[m, "duration"]
                                   .str.replace(" min", "", regex=False).astype(float))
    return df

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg", width=128)
    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("#### 📂 Data Source")
    uploaded = st.file_uploader("Upload your CSV", type=["csv"],
                                help="Needs: type, title, release_year, rating, country, duration, listed_in")
    if uploaded:
        df  = clean(load_uploaded(uploaded.read(), uploaded.name))
        src = f"📄 {uploaded.name}"
    else:
        if st.button("▶  Use Default Netflix Dataset", use_container_width=True):
            st.session_state["df"] = clean(load_default())
        if "df" not in st.session_state:
            try:    st.session_state["df"] = clean(load_default())
            except: st.error("`netflix_titles.csv` not found."); st.stop()
        df  = st.session_state["df"]
        src = "📺 Default Netflix Dataset"

    st.caption(f"**Source:** {src}")
    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("#### 🔍 Filters")
    f_type   = st.multiselect("Content Type",   df["type"].unique(),          list(df["type"].unique()))
    yr0, yr1 = int(df["release_year"].min()), int(df["release_year"].max())
    f_year   = st.slider("Release Year", yr0, yr1, (yr0, yr1))
    f_rating = st.multiselect("Ratings", sorted(df["rating"].unique()),       list(df["rating"].unique()))
    st.caption("Charts update in real-time.")

# ─── Filter ───────────────────────────────────────────────────────────────────
fdf = df[df["type"].isin(f_type) & df["release_year"].between(*f_year) & df["rating"].isin(f_rating)]
if fdf.empty:
    st.warning("⚠️ No data matches the current filters."); st.stop()

mvs = fdf[fdf["type"] == "Movie"]
tvs = fdf[fdf["type"] == "TV Show"]
avg = mvs["duration_int"].mean()

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("<h1 style='margin:0 0 4px;color:#f3f4f6;font-size:2rem;'>🍿 Netflix Data Explorer</h1>",
            unsafe_allow_html=True)
st.markdown(f"<p style='color:#4b5563;font-size:.9rem;margin:0 0 1.5rem'>"
            f"Interactive analysis of Netflix's catalog &nbsp;·&nbsp; {src}</p>",
            unsafe_allow_html=True)

# ─── KPIs ─────────────────────────────────────────────────────────────────────
k = st.columns(5)
k[0].metric("Total Titles",      f"{len(fdf):,}")
k[1].metric("Movies",            f"{len(mvs):,}")
k[2].metric("TV Shows",          f"{len(tvs):,}")
k[3].metric("Unique Countries",  f"{fdf['country'].nunique():,}")
k[4].metric("Avg Movie Length",  f"{avg:.0f} min" if pd.notna(avg) else "—")

st.markdown("<hr>", unsafe_allow_html=True)

# ═══════════ SECTION 1 — Composition ═════════════════════════════════════════
st.markdown('<div class="pill">Catalog Composition</div>', unsafe_allow_html=True)

c1, c2 = st.columns(2, gap="large")

with c1:
    st.markdown('<div class="chart-card"><h3>Movies vs TV Shows</h3>', unsafe_allow_html=True)
    tc = fdf["type"].value_counts().reset_index(); tc.columns = ["Type","Count"]
    fig = go.Figure(go.Pie(
        labels=tc["Type"], values=tc["Count"], hole=0.62,
        marker=dict(colors=[RED, "#e5e7eb"],
                    line=dict(color="#111317", width=3)),
        textposition="outside",
        texttemplate="<b>%{label}</b><br>%{value:,} (%{percent})",
        textfont=dict(size=12, color=FC),
        pull=[0.04, 0],
    ))
    fig.add_annotation(text="Catalog", x=0.5, y=0.5, showarrow=False,
                       font=dict(size=15, color="#e5e7eb", family="Inter"))
    styled(fig, legend_bottom=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown('<div class="chart-card"><h3>Content Ratings Breakdown</h3>', unsafe_allow_html=True)
    rc = fdf["rating"].value_counts().reset_index(); rc.columns = ["Rating","Count"]
    fig = px.bar(rc, x="Count", y="Rating", orientation="h",
                 color="Count",
                 color_continuous_scale=["#2d0607","#6b0c10","#b00d15",RED],
                 text="Count")
    fig.update_traces(texttemplate="%{text:,}", textposition="outside",
                      textfont=dict(color=FC, size=10), cliponaxis=False)
    styled(fig, xgrid=False, ygrid=False,
           yaxis_categoryorder="total ascending",
           coloraxis_showscale=False, xaxis_title="", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ═══════════ SECTION 2 — Trends ══════════════════════════════════════════════
st.markdown('<div class="pill">Trends Over Time</div>', unsafe_allow_html=True)

c3, c4 = st.columns(2, gap="large")

with c3:
    st.markdown('<div class="chart-card"><h3>Movie Duration Distribution</h3>', unsafe_allow_html=True)
    if not mvs.empty:
        fig = px.histogram(mvs, x="duration_int", nbins=40,
                           color_discrete_sequence=[RED], opacity=0.9)
        fig.update_traces(
            texttemplate="%{y}", textposition="outside",
            textfont=dict(color=FC, size=9),
            marker_line_color="#111317", marker_line_width=0.8
        )
        styled(fig, xgrid=False, ygrid=True, bargap=0.05)
        fig.update_xaxes(title_text="Duration (minutes)")
        fig.update_yaxes(title_text="# of Movies")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No movies in current selection.")
    st.markdown("</div>", unsafe_allow_html=True)

with c4:
    st.markdown('<div class="chart-card"><h3>Titles Released Per Year</h3>', unsafe_allow_html=True)
    cy = fdf.groupby(["release_year","type"]).size().reset_index(name="Count")
    fig = px.line(cy, x="release_year", y="Count", color="type",
                  color_discrete_map={"Movie": RED, "TV Show": PALE},
                  markers=True)
    fig.update_traces(line=dict(width=2.5), marker=dict(size=5),
                      textfont=dict(size=9, color=FC))
    styled(fig, xgrid=False, ygrid=True, legend_bottom=True,
           xaxis_title="Year", yaxis_title="Number of Titles", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ═══════════ SECTION 3 — Geography & Genre ════════════════════════════════════
st.markdown('<div class="pill">Geography &amp; Genre</div>', unsafe_allow_html=True)

c5, c6 = st.columns(2, gap="large")

with c5:
    st.markdown('<div class="chart-card"><h3>Top 10 Content-Producing Countries</h3>', unsafe_allow_html=True)
    cflat = fdf.assign(country=fdf["country"].str.split(", ")).explode("country")
    cc = cflat["country"].value_counts().head(10).reset_index(); cc.columns = ["Country","Count"]
    fig = px.bar(cc, x="Count", y="Country", orientation="h",
                 color="Count",
                 color_continuous_scale=["#2d0607","#6b0c10","#b00d15",RED],
                 text="Count")
    fig.update_traces(texttemplate="%{text:,}", textposition="outside",
                      textfont=dict(color=FC, size=10), cliponaxis=False)
    styled(fig, xgrid=False, ygrid=False,
           yaxis_categoryorder="total ascending",
           coloraxis_showscale=False, xaxis_title="", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c6:
    st.markdown('<div class="chart-card"><h3>Top 15 Genres / Categories</h3>', unsafe_allow_html=True)
    gflat = fdf.assign(genre=fdf["listed_in"].str.split(", ")).explode("genre")
    gc = gflat["genre"].value_counts().head(15).reset_index(); gc.columns = ["Genre","Count"]
    fig = px.bar(gc, x="Count", y="Genre", orientation="h",
                 color="Count",
                 color_continuous_scale=["#2d0607","#6b0c10","#b00d15",RED],
                 text="Count")
    fig.update_traces(texttemplate="%{text:,}", textposition="outside",
                      textfont=dict(color=FC, size=10), cliponaxis=False)
    styled(fig, xgrid=False, ygrid=False,
           yaxis_categoryorder="total ascending",
           coloraxis_showscale=False, xaxis_title="", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ═══════════ DATA EXPLORER ════════════════════════════════════════════════════
with st.expander("📋 Browse the Dataset", expanded=False):
    q = st.text_input("Search by title", placeholder="e.g. Stranger Things")
    cols = ["title","type","release_year","rating","duration","country","listed_in"]
    view = fdf[cols]
    if q:
        view = view[view["title"].str.contains(q, case=False, na=False)]
    st.dataframe(view, use_container_width=True, height=400, hide_index=True)
    st.caption(f"{len(view):,} titles shown.")

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown(
    "<div class='footer'>Built with ❤️ using <b>Streamlit</b> &amp; <b>Plotly</b>"
    " &nbsp;|&nbsp; Netflix Titles Dataset &nbsp;|&nbsp; © Ayush Sood</div>",
    unsafe_allow_html=True
)
