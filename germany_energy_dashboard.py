import pandas as pd
import dash
from dash import dcc, html, Input, Output, State, clientside_callback
import plotly.graph_objects as go

# LOAD & PREPARE DATA
df = pd.read_csv("opsd_germany_daily.csv")
df["Date"]      = pd.to_datetime(df["Date"])
df["Year"]      = df["Date"].dt.year.astype(int)
df["Month"]     = df["Date"].dt.month.astype(int)
df["MonthName"] = df["Date"].dt.strftime("%b")
df["Season"]    = df["Month"].map({
    12:"Winter",1:"Winter",2:"Winter",
    3:"Spring",4:"Spring",5:"Spring",
    6:"Summer",7:"Summer",8:"Summer",
    9:"Autumn",10:"Autumn",11:"Autumn",
})

MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
YEARS  = [int(y) for y in sorted(df["Year"].unique())]

yearly = (df.groupby("Year")[["Consumption","Wind","Solar","Wind+Solar"]]
            .mean().round(2).reset_index())
yearly["Year"] = yearly["Year"].astype(int)

monthly = (df.groupby("Month")[["Consumption","Wind","Solar","Wind+Solar"]]
             .mean().round(2).reset_index())
monthly["MonthName"] = monthly["Month"].apply(lambda x: MONTHS[x-1])

SEASON_ORDER = ["Spring","Summer","Autumn","Winter"]
seasonal = (df.groupby("Season")[["Consumption","Wind","Solar"]]
              .mean().round(2).reset_index())
seasonal["Season"] = pd.Categorical(seasonal["Season"], categories=SEASON_ORDER, ordered=True)
seasonal = seasonal.sort_values("Season").reset_index(drop=True)

KPI = {
    "avg_cons"  : round(float(df["Consumption"].mean()), 1),
    "max_cons"  : round(float(df["Consumption"].max()),  1),
    "avg_wind"  : round(float(df["Wind"].mean()),        1),
    "max_wind"  : round(float(df["Wind"].max()),         1),
    "avg_solar" : round(float(df["Solar"].mean()),       1),
    "max_solar" : round(float(df["Solar"].max()),        1),
    "year_start": int(df["Year"].min()),
    "year_end"  : int(df["Year"].max()),
    "total_days": int(len(df)),
}
AVG_MIX = {
    "Wind" : round(float(df["Wind"].mean()), 2),
    "Solar": round(float(df["Solar"].mean()), 2),
    "Other": max(0.0, round(float(df["Consumption"].mean())
                            - float(df["Wind"].mean())
                            - float(df["Solar"].mean()), 2)),
}

# ACCENT COLOURS  (same in both themes)
A1 = "#38bdf8"   # sky-blue   – Consumption
A2 = "#22c55e"   # emerald    – Wind
A3 = "#f97316"   # orange     – Solar
A4 = "#a78bfa"   # violet     – Wind+Solar

COLORS = {"Consumption":A1, "Wind":A2, "Solar":A3, "Wind+Solar":A4, "Other":"#64748b"}

FILL_DARK  = {"Consumption":"rgba(56,189,248,0.12)","Wind":"rgba(34,197,94,0.12)",
              "Solar":"rgba(249,115,22,0.12)","Wind+Solar":"rgba(167,139,250,0.12)"}
FILL_LIGHT = {"Consumption":"rgba(56,189,248,0.18)","Wind":"rgba(34,197,94,0.18)",
              "Solar":"rgba(249,115,22,0.18)","Wind+Solar":"rgba(167,139,250,0.18)"}

HEATMAP_DARK  = [[0.0,"#0c1220"],[0.3,"#1a3a5c"],[0.6,"#1a6496"],[0.85,A1],[1.0,"#7dd3fc"]]
HEATMAP_LIGHT = [[0.0,"#eff6ff"],[0.3,"#bfdbfe"],[0.6,"#60a5fa"],[0.85,"#2563eb"],[1.0,"#1e3a8a"]]

#CSS  — uses CSS variables + data-theme on body
CUSTOM_CSS = f"""
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&display=swap');

:root, [data-theme="dark"] {{
  --bg:        #060a10;
  --panel:     #0c1220;
  --panel2:    #111827;
  --border:    #1e2d45;
  --border-h:  #2a4a72;
  --grid:      #182235;
  --text:      #e2e8f0;
  --subtext:   #64748b;
  --shadow:    rgba(0,0,0,0.35);
  --panel-sh:  rgba(0,0,0,0.30);
  --toggle-bg: #0c1220;
}}
[data-theme="light"] {{
  --bg:        #f0f4f8;
  --panel:     #ffffff;
  --panel2:    #f8fafc;
  --border:    #e2e8f0;
  --border-h:  #93c5fd;
  --grid:      #e8edf2;
  --text:      #0f172a;
  --subtext:   #64748b;
  --shadow:    rgba(0,0,0,0.08);
  --panel-sh:  rgba(0,0,0,0.05);
  --toggle-bg: #ffffff;
}}

*, *::before, *::after {{ box-sizing: border-box; }}

body {{
  margin: 0;
  background: var(--bg) !important;
  transition: background 0.3s ease;
}}

::-webkit-scrollbar {{ width: 6px; background: var(--bg); }}
::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 3px; }}

.dash-graph {{ animation: fadeUp 0.4s cubic-bezier(0.16,1,0.3,1) both; }}
@keyframes fadeUp {{
  from {{ opacity:0; transform:translateY(10px); }}
  to   {{ opacity:1; transform:translateY(0); }}
}}

.kpi-card {{
  transition: transform 0.22s cubic-bezier(0.34,1.56,0.64,1),
              box-shadow 0.22s ease !important;
}}
.kpi-card:hover {{
  transform: translateY(-5px) scale(1.015) !important;
  box-shadow: 0 18px 44px var(--shadow) !important;
}}

.dash-panel {{ transition: border-color 0.2s ease, box-shadow 0.2s ease; }}
.dash-panel:hover {{
  border-color: var(--border-h) !important;
  box-shadow: 0 8px 32px rgba(56,189,248,0.07) !important;
}}

.section-title::after {{
  content: '';
  display: block;
  width: 30px; height: 2px;
  background: linear-gradient(90deg, {A1}, {A4});
  margin-top: 5px; border-radius: 2px;
}}

label, .form-check-label,
.dash-checklist label, .dash-radio-items label {{
  color: var(--text) !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 13px !important;
}}

input[type="radio"]    {{ accent-color: {A1}; cursor: pointer; }}
input[type="checkbox"] {{ accent-color: {A1}; cursor: pointer; }}

.rc-slider-rail  {{ background-color: var(--border) !important; height: 5px !important; }}
.rc-slider-track {{ background: linear-gradient(90deg,{A1},{A4}) !important; height:5px !important; }}
.rc-slider-handle {{
  background: {A1} !important; border: 2px solid {A1} !important;
  box-shadow: 0 0 10px {A1}88 !important;
  width:17px !important; height:17px !important;
  margin-top:-6px !important; opacity:1 !important;
}}
.rc-slider-handle:hover, .rc-slider-handle-dragging {{
  box-shadow: 0 0 16px {A1} !important; border-color:{A1} !important;
}}
.rc-slider-mark-text {{
  color: var(--subtext) !important; font-size:10px !important;
  font-family:'DM Sans',sans-serif !important; margin-top:4px;
}}
.rc-slider-tooltip-inner {{
  background: var(--panel2) !important; color: var(--text) !important;
  border: 1px solid var(--border-h) !important;
  font-family:'DM Sans',sans-serif !important; font-size:11px !important;
}}

.modebar-btn path {{ fill: var(--subtext) !important; }}
.modebar-btn:hover path {{ fill: var(--text) !important; }}
.modebar {{ background: transparent !important; }}

#theme-toggle-btn {{
  display: inline-flex; align-items: center; gap: 7px;
  background: var(--toggle-bg);
  border: 1.5px solid var(--border);
  border-radius: 30px; padding: 7px 16px;
  font-family: 'DM Sans', sans-serif;
  font-size: 12px; font-weight: 600; letter-spacing: 0.3px;
  color: var(--text); cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px var(--shadow);
}}
#theme-toggle-btn:hover {{
  background: var(--border);
  transform: translateY(-1px);
  box-shadow: 0 4px 14px var(--shadow);
}}

.header-title {{
  background: linear-gradient(90deg, {A1} 0%, {A4} 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}}

.data-badge {{
  background: linear-gradient(135deg,{A2}22,{A2}0a);
  border: 1px solid {A2}44; color: {A2};
  font-size: 10px; font-weight: 700; letter-spacing:1.5px;
  padding: 5px 14px; border-radius: 20px;
  font-family: 'DM Sans', sans-serif;
}}

.dashboard-footer {{
  border-top: 1px solid var(--border);
  padding: 16px 0 4px; text-align: center;
  color: var(--subtext); font-size: 11px;
  font-family: 'DM Sans', sans-serif;
}}
"""

#CHART HELPERS
def plot_colors(theme):
    if theme == "light":
        return dict(
            bg="#ffffff", bg2="#f8fafc", border="#e2e8f0", border_h="#93c5fd",
            grid="#e8edf2", text="#0f172a", subtext="#64748b",
            legend_bg="rgba(255,255,255,0.92)",
        )
    return dict(
        bg="#0c1220", bg2="#111827", border="#1e2d45", border_h="#2a4a72",
        grid="#182235", text="#e2e8f0", subtext="#64748b",
        legend_bg="rgba(12,18,32,0.88)",
    )


def base_layout(pc, **extra):
    layout = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor ="rgba(0,0,0,0)",
        font=dict(family="'DM Sans','Segoe UI',sans-serif", color=pc["text"], size=11),
        margin=dict(l=54, r=16, t=16, b=50),
        xaxis=dict(gridcolor=pc["grid"], linecolor=pc["border"], zerolinecolor=pc["grid"],
                   tickfont=dict(color=pc["subtext"])),
        yaxis=dict(gridcolor=pc["grid"], linecolor=pc["border"], zerolinecolor=pc["grid"],
                   tickfont=dict(color=pc["subtext"])),
        legend=dict(bgcolor=pc["legend_bg"], bordercolor=pc["border"],
                    borderwidth=1, font=dict(color=pc["text"], size=11)),
        hovermode="x unified",
        hoverlabel=dict(bgcolor=pc["bg2"], bordercolor=pc["border_h"],
                        font=dict(color=pc["text"], size=12)),
    )
    layout.update(extra)
    return layout

#UI HELPERS
def panel(children, style_extra=None):
    style = {
        "background": "var(--panel)",
        "border": "1px solid var(--border)",
        "borderRadius": "16px",
        "padding": "22px 24px",
        "boxShadow": "0 4px 24px var(--panel-sh)",
    }
    if style_extra:
        style.update(style_extra)
    return html.Div(children, className="dash-panel", style=style)


def ctrl_label(icon, text):
    return html.Div([html.Span(icon + "  "), html.Span(text)], style={
        "color":"var(--subtext)","fontSize":"10px","textTransform":"uppercase",
        "letterSpacing":"1.4px","fontWeight":"700",
        "fontFamily":"'DM Sans',sans-serif","marginBottom":"10px",
    })


def section_title(text):
    return html.H3(text, className="section-title", style={
        "margin":"0 0 14px","fontSize":"13px","fontWeight":"700",
        "color":"var(--text)","fontFamily":"'Syne',sans-serif","letterSpacing":"0.2px",
    })


def kpi_card(label, value, unit, color, icon="", badge=""):
    return html.Div([
        html.Div([
            html.Span(icon, style={"fontSize":"22px",
                                   "filter":f"drop-shadow(0 0 8px {color}88)"}),
            html.Span(badge, style={
                "fontSize":"10px","padding":"2px 8px","borderRadius":"10px",
                "fontWeight":"600","fontFamily":"'DM Sans',sans-serif",
                "background":f"{color}18","color":color,"marginLeft":"auto",
            }),
        ], style={"display":"flex","alignItems":"center",
                  "justifyContent":"space-between","marginBottom":"10px"}),
        html.P(label, style={
            "color":"var(--subtext)","fontSize":"10px","margin":"0 0 5px",
            "textTransform":"uppercase","letterSpacing":"1.1px",
            "fontWeight":"600","fontFamily":"'DM Sans',sans-serif",
        }),
        html.H2(f"{value:,.1f}", style={
            "color":color,"margin":"0","fontSize":"28px",
            "fontWeight":"800","letterSpacing":"-0.8px",
            "textShadow":f"0 0 20px {color}44",
            "fontFamily":"'Syne',sans-serif",
        }),
        html.P(unit, style={
            "color":"var(--subtext)","fontSize":"10px","margin":"5px 0 0",
            "fontFamily":"'DM Sans',sans-serif",
        }),
        html.Div(style={
            "position":"absolute","bottom":"0","left":"0","right":"0","height":"2px",
            "background":f"linear-gradient(90deg, {color}88, transparent)",
            "borderRadius":"0 0 14px 14px",
        }),
    ], className="kpi-card", style={
        "background":"var(--panel)","border":"1px solid var(--border)",
        "borderRadius":"14px","padding":"18px 20px",
        "flex":"1","minWidth":"150px","position":"relative","overflow":"hidden",
        "boxShadow":f"0 2px 16px {color}12",
    })

#APP
app = dash.Dash(__name__, title="⚡ Germany Energy Dashboard",
                suppress_callback_exceptions=True)

app.index_string = (
    "<!DOCTYPE html><html><head>"
    "{%metas%}<title>{%title%}</title>{%favicon%}{%css%}"
    f"<style>{CUSTOM_CSS}</style>"
    "</head>"
    "<body data-theme='dark' style='margin:0'>"
    "{%app_entry%}"
    "<footer>{%config%}{%scripts%}{%renderer%}</footer>"
    "</body></html>"
)

#LAYOUT
app.layout = html.Div(
    style={
        "background":"var(--bg)","minHeight":"100vh",
        "fontFamily":"'DM Sans','Segoe UI',sans-serif",
        "color":"var(--text)","padding":"32px 36px","lineHeight":"1.5",
        "transition":"background 0.3s ease, color 0.3s ease",
    },
    children=[
        dcc.Store(id="theme-store", data="dark"),

        # Header
        html.Div([
            html.Div([
                html.H1("⚡ Germany Energy Dashboard",
                        className="header-title",
                        style={"margin":"0","fontSize":"28px","fontWeight":"800",
                               "letterSpacing":"-0.8px","fontFamily":"'Syne',sans-serif"}),
                html.P(
                    f"Open Power System Data  ·  {KPI['year_start']}–{KPI['year_end']}"
                    f"  ·  {KPI['total_days']:,} daily records",
                    style={"margin":"6px 0 0","color":"var(--subtext)","fontSize":"13px",
                           "fontFamily":"'DM Sans',sans-serif"}),
            ]),
            html.Div([
                html.Span("OPSD 2006–2017", className="data-badge"),
                html.Button(
                    id="theme-toggle-btn",
                    n_clicks=0,
                    children="☀️  Light Mode",
                ),
            ], style={"display":"flex","alignItems":"center","gap":"14px"}),
        ], style={"display":"flex","justifyContent":"space-between",
                  "alignItems":"center","marginBottom":"28px"}),

        # KPI Row
        html.Div([
            kpi_card("Avg Daily Consumption", KPI["avg_cons"], "GWh / day", A1, "🔋", "AVG"),
            kpi_card("Peak Consumption",      KPI["max_cons"], "GWh",       A1, "⚡", "MAX"),
            kpi_card("Avg Wind Output",        KPI["avg_wind"], "GWh / day", A2, "🌬️","AVG"),
            kpi_card("Peak Wind Output",       KPI["max_wind"], "GWh",       A2, "💨", "MAX"),
            kpi_card("Avg Solar Output",       KPI["avg_solar"],"GWh / day", A3, "☀️", "AVG"),
            kpi_card("Peak Solar Output",      KPI["max_solar"],"GWh",       A3, "🌞", "MAX"),
        ], style={"display":"flex","gap":"14px","flexWrap":"wrap","marginBottom":"24px"}),

        # Controls
        panel([
            html.Div([
                html.Div([
                    ctrl_label("📅","Date Range"),
                    dcc.RangeSlider(
                        id="year-slider",
                        min=YEARS[0], max=YEARS[-1],
                        value=[YEARS[0],YEARS[-1]], step=1,
                        marks={y:{"label":str(y),
                                  "style":{"color":"var(--subtext)","fontSize":"10px",
                                           "fontFamily":"'DM Sans',sans-serif"}}
                               for y in YEARS},
                        tooltip={"placement":"bottom","always_visible":False},
                    ),
                ], style={"flex":"3","minWidth":"260px"}),
                html.Div(style={"width":"1px","background":"var(--border)",
                                "alignSelf":"stretch","margin":"0 4px"}),
                html.Div([
                    ctrl_label("📊","Chart Style"),
                    dcc.RadioItems(
                        id="chart-type",
                        options=[
                            {"label":"  Lines","value":"line"},
                            {"label":"  Area", "value":"area"},
                        ],
                        value="area",
                        inputStyle={"accentColor":A1,"cursor":"pointer",
                                    "width":"14px","height":"14px"},
                        labelStyle={"display":"flex","alignItems":"center",
                                    "marginBottom":"10px","cursor":"pointer",
                                    "fontFamily":"'DM Sans',sans-serif","fontSize":"13px"},
                    ),
                ], style={"flex":"1","minWidth":"130px"}),
                html.Div(style={"width":"1px","background":"var(--border)",
                                "alignSelf":"stretch","margin":"0 4px"}),
                html.Div([
                    ctrl_label("🔍","Show Series"),
                    dcc.Checklist(
                        id="series-select",
                        options=[
                            {"label":"  ● Consumption","value":"Consumption"},
                            {"label":"  ● Wind",       "value":"Wind"},
                            {"label":"  ● Solar",      "value":"Solar"},
                            {"label":"  ● Wind+Solar", "value":"Wind+Solar"},
                        ],
                        value=["Consumption","Wind","Solar"],
                        inline=True,
                        inputStyle={"accentColor":A1,"cursor":"pointer",
                                    "width":"14px","height":"14px","marginRight":"4px"},
                        labelStyle={"display":"inline-flex","alignItems":"center",
                                    "marginRight":"20px","marginBottom":"6px",
                                    "cursor":"pointer","fontFamily":"'DM Sans',sans-serif",
                                    "fontSize":"13px"},
                    ),
                ], style={"flex":"2","minWidth":"280px"}),
            ], style={"display":"flex","gap":"28px","alignItems":"flex-start","flexWrap":"wrap"}),
        ], style_extra={"marginBottom":"22px"}),

        # Time Series
        panel([
            section_title("Time Series — Daily Energy Output (GWh)"),
            dcc.Graph(id="timeseries-chart", style={"height":"320px"},
                      config={"displayModeBar":True,"scrollZoom":True,
                              "modeBarButtonsToRemove":["lasso2d","select2d"]}),
        ], style_extra={"marginBottom":"22px"}),

        # Row 2
        html.Div([
            panel([section_title("Yearly Averages"),
                   dcc.Graph(id="yearly-chart",  style={"height":"260px"},
                             config={"displayModeBar":False})],
                  style_extra={"flex":"1","minWidth":"300px"}),
            panel([section_title("Monthly Patterns (All Years)"),
                   dcc.Graph(id="monthly-chart", style={"height":"260px"},
                             config={"displayModeBar":False})],
                  style_extra={"flex":"1","minWidth":"300px"}),
        ], style={"display":"flex","gap":"22px","marginBottom":"22px","flexWrap":"wrap"}),

        # Row 3
        html.Div([
            panel([section_title("Seasonal Breakdown"),
                   dcc.Graph(id="seasonal-chart", style={"height":"260px"},
                             config={"displayModeBar":False})],
                  style_extra={"flex":"1","minWidth":"300px"}),
            panel([section_title("Consumption Heatmap  (Year × Month)"),
                   dcc.Graph(id="heatmap-chart",  style={"height":"260px"},
                             config={"displayModeBar":False})],
                  style_extra={"flex":"1","minWidth":"300px"}),
        ], style={"display":"flex","gap":"22px","marginBottom":"22px","flexWrap":"wrap"}),

        # Row 4
        html.Div([
            panel([section_title("Energy Distribution (Histogram)"),
                   dcc.Graph(id="hist-chart",       style={"height":"260px"},
                             config={"displayModeBar":False})],
                  style_extra={"flex":"1","minWidth":"300px"}),
            panel([section_title("Renewables Growth Over Years"),
                   dcc.Graph(id="renewables-chart", style={"height":"260px"},
                             config={"displayModeBar":False})],
                  style_extra={"flex":"1","minWidth":"300px"}),
        ], style={"display":"flex","gap":"22px","marginBottom":"22px","flexWrap":"wrap"}),

        # Row 5 – Pies
        html.Div([
            panel([
                section_title("⚡ Average Energy Mix"),
                html.P("Share of Wind, Solar & other sources in avg daily consumption",
                       style={"color":"var(--subtext)","fontSize":"11px","margin":"0 0 10px",
                              "fontFamily":"'DM Sans',sans-serif"}),
                dcc.Graph(id="pie-mix-chart", style={"height":"280px"},
                          config={"displayModeBar":False}),
            ], style_extra={"flex":"1","minWidth":"300px"}),
            panel([
                section_title("🌿 Wind vs Solar Split  (Selected Range)"),
                html.P("Proportional contribution of wind vs solar in filtered date range",
                       style={"color":"var(--subtext)","fontSize":"11px","margin":"0 0 10px",
                              "fontFamily":"'DM Sans',sans-serif"}),
                dcc.Graph(id="pie-ws-chart",  style={"height":"280px"},
                          config={"displayModeBar":False}),
            ], style_extra={"flex":"1","minWidth":"300px"}),
        ], style={"display":"flex","gap":"22px","marginBottom":"22px","flexWrap":"wrap"}),

        # Footer
        html.Div(
            html.P("Data: Open Power System Data (OPSD)  ·  Germany Daily Energy 2006–2017"),
            className="dashboard-footer",
        ),
    ]
)

#CALLBACKS

# Toggle theme via clientside callback – sets body[data-theme], no layout rebuild
clientside_callback(
    """
    function(n, current) {
        var next = (current === 'dark') ? 'light' : 'dark';
        document.body.setAttribute('data-theme', next);
        return next;
    }
    """,
    Output("theme-store", "data"),
    Input("theme-toggle-btn", "n_clicks"),
    State("theme-store", "data"),
    prevent_initial_call=True,
)

@app.callback(
    Output("theme-toggle-btn", "children"),
    Input("theme-store", "data"),
)
def update_toggle_label(theme):
    return "🌙  Dark Mode" if theme == "light" else "☀️  Light Mode"


def get_pc(theme): return plot_colors(theme or "dark")


@app.callback(
    Output("timeseries-chart", "figure"),
    Input("year-slider","value"), Input("series-select","value"),
    Input("chart-type","value"),  Input("theme-store","data"),
)
def update_timeseries(year_range, series, chart_type, theme):
    pc   = get_pc(theme)
    FILL = FILL_LIGHT if theme=="light" else FILL_DARK
    series = series or []
    mask = (df["Year"]>=year_range[0]) & (df["Year"]<=year_range[1])
    dff  = df[mask]
    fig  = go.Figure()
    for col in series:
        kw = dict(x=dff["Date"], y=dff[col], name=col, mode="lines",
                  line=dict(color=COLORS[col], width=1.5 if chart_type=="area" else 1.9),
                  hovertemplate=f"<b>{col}</b>: %{{y:.1f}} GWh<extra></extra>")
        if chart_type == "area":
            fig.add_trace(go.Scatter(**kw, fill="tozeroy", fillcolor=FILL[col]))
        else:
            fig.add_trace(go.Scatter(**kw))
    fig.update_layout(**base_layout(pc, xaxis_title="Date", yaxis_title="GWh"))
    return fig


@app.callback(
    Output("yearly-chart","figure"),
    Input("series-select","value"), Input("theme-store","data"),
)
def update_yearly(series, theme):
    pc = get_pc(theme); series = series or []
    fig = go.Figure()
    for col in series:
        fig.add_trace(go.Bar(
            x=yearly["Year"], y=yearly[col], name=col,
            marker=dict(color=COLORS[col], line=dict(width=0), opacity=0.85),
            hovertemplate=f"<b>{col}</b>: %{{y:.1f}} GWh<extra></extra>"))
    fig.update_layout(**base_layout(pc, barmode="group", xaxis_title="Year",
                                    yaxis_title="Avg GWh / day", bargap=0.2, bargroupgap=0.05))
    return fig


@app.callback(
    Output("monthly-chart","figure"),
    Input("series-select","value"), Input("theme-store","data"),
)
def update_monthly(series, theme):
    pc = get_pc(theme); series = series or []
    fig = go.Figure()
    for col in series:
        fig.add_trace(go.Scatter(
            x=monthly["MonthName"], y=monthly[col], name=col,
            mode="lines+markers",
            line=dict(color=COLORS[col], width=2.5),
            marker=dict(size=7, color=COLORS[col], line=dict(color=pc["bg"], width=1.5)),
            hovertemplate=f"<b>{col}</b>: %{{y:.1f}} GWh<extra></extra>"))
    layout = base_layout(pc, yaxis_title="Avg GWh / day")
    layout["xaxis"] = dict(title=dict(text="Month", font=dict(color=pc["subtext"])),
                           categoryorder="array", categoryarray=MONTHS,
                           gridcolor=pc["grid"], linecolor=pc["border"],
                           zerolinecolor=pc["grid"], tickfont=dict(color=pc["subtext"]))
    fig.update_layout(**layout)
    return fig


@app.callback(
    Output("seasonal-chart","figure"),
    Input("year-slider","value"), Input("theme-store","data"),
)
def update_seasonal(_, theme):
    pc = get_pc(theme)
    fig = go.Figure()
    for col in ["Consumption","Wind","Solar"]:
        fig.add_trace(go.Bar(
            x=seasonal["Season"].astype(str), y=seasonal[col], name=col,
            marker=dict(color=COLORS[col], line=dict(width=0), opacity=0.85),
            hovertemplate=f"<b>{col}</b>: %{{y:.1f}} GWh<extra></extra>"))
    fig.update_layout(**base_layout(pc, barmode="group", xaxis_title="Season",
                                    yaxis_title="Avg GWh / day", bargap=0.25))
    return fig


@app.callback(
    Output("heatmap-chart","figure"),
    Input("year-slider","value"), Input("theme-store","data"),
)
def update_heatmap(year_range, theme):
    pc = get_pc(theme)
    colorscale = HEATMAP_LIGHT if theme=="light" else HEATMAP_DARK
    mask  = (df["Year"]>=year_range[0]) & (df["Year"]<=year_range[1])
    pivot = df[mask].groupby(["Year","Month"])["Consumption"].mean().unstack()
    pivot.columns = [MONTHS[c-1] for c in pivot.columns]
    fig = go.Figure(go.Heatmap(
        z=pivot.values.tolist(), x=pivot.columns.tolist(),
        y=[int(y) for y in pivot.index],
        colorscale=colorscale, hoverongaps=False,
        hovertemplate="Year: %{y}<br>Month: %{x}<br>Avg: %{z:.1f} GWh<extra></extra>",
        colorbar=dict(tickfont=dict(color=pc["text"],size=10),
                      outlinecolor=pc["border"],outlinewidth=1,thickness=12)))
    layout = base_layout(pc, yaxis_title="Year")
    layout["xaxis"] = dict(title=dict(text="Month",font=dict(color=pc["subtext"])),
                           gridcolor=pc["grid"],linecolor=pc["border"],
                           tickfont=dict(color=pc["subtext"]))
    fig.update_layout(**layout)
    return fig


@app.callback(
    Output("hist-chart","figure"),
    Input("year-slider","value"), Input("series-select","value"),
    Input("theme-store","data"),
)
def update_hist(year_range, series, theme):
    pc = get_pc(theme); series = series or []
    mask = (df["Year"]>=year_range[0]) & (df["Year"]<=year_range[1])
    dff  = df[mask]; fig = go.Figure()
    for col in series:
        fig.add_trace(go.Histogram(
            x=dff[col].dropna(), name=col,
            marker=dict(color=COLORS[col],opacity=0.75,line=dict(color="rgba(0,0,0,0)",width=0)),
            nbinsx=40,
            hovertemplate=f"<b>{col}</b>: %{{x:.0f}} GWh  Count: %{{y}}<extra></extra>"))
    fig.update_layout(**base_layout(pc, barmode="overlay",
                                    xaxis_title="GWh", yaxis_title="Days"))
    return fig


@app.callback(
    Output("renewables-chart","figure"),
    Input("year-slider","value"), Input("theme-store","data"),
)
def update_renewables(year_range, theme):
    pc = get_pc(theme)
    mask = (df["Year"]>=year_range[0]) & (df["Year"]<=year_range[1])
    dff  = (df[mask].groupby("Year")[["Wind","Solar"]]
            .mean().round(2).dropna(subset=["Wind"]).reset_index())
    dff["Year"] = dff["Year"].astype(int)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dff["Year"],y=dff["Solar"],name="Solar",
        mode="lines",stackgroup="one",line=dict(color=A3,width=0),
        fillcolor="rgba(249,115,22,0.65)",
        hovertemplate="Solar: %{y:.1f} GWh<extra></extra>"))
    fig.add_trace(go.Scatter(x=dff["Year"],y=dff["Wind"],name="Wind",
        mode="lines",stackgroup="one",line=dict(color=A2,width=0),
        fillcolor="rgba(34,197,94,0.65)",
        hovertemplate="Wind: %{y:.1f} GWh<extra></extra>"))
    fig.update_layout(**base_layout(pc, xaxis_title="Year", yaxis_title="Avg GWh / day"))
    return fig


@app.callback(
    Output("pie-mix-chart","figure"),
    Input("year-slider","value"), Input("theme-store","data"),
)
def update_pie_mix(_, theme):
    pc = get_pc(theme)
    labels = ["Wind","Solar","Other"]
    values = [AVG_MIX["Wind"],AVG_MIX["Solar"],AVG_MIX["Other"]]
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.58,
        marker=dict(colors=[A2,A3,pc["subtext"]], line=dict(color=pc["bg"],width=3)),
        textinfo="label+percent", textfont=dict(color=pc["text"],size=11),
        hovertemplate="<b>%{label}</b><br>Avg: %{value:.1f} GWh/day<br>%{percent}<extra></extra>",
        pull=[0.04,0.04,0], rotation=30))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20,r=20,t=10,b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(color=pc["text"],size=11),
                    orientation="h",y=-0.05),
        font=dict(family="'DM Sans',sans-serif",color=pc["text"]),
        annotations=[dict(text=f"<b>{KPI['avg_cons']:.0f}</b><br>GWh/day",
                          x=0.5,y=0.5,showarrow=False,
                          font=dict(size=14,color=pc["text"],family="'DM Sans',sans-serif"))])
    return fig


@app.callback(
    Output("pie-ws-chart","figure"),
    Input("year-slider","value"), Input("theme-store","data"),
)
def update_pie_ws(year_range, theme):
    pc    = get_pc(theme)
    mask  = (df["Year"]>=year_range[0]) & (df["Year"]<=year_range[1])
    dff   = df[mask]
    avg_w = round(float(dff["Wind"].mean()),2)
    avg_s = round(float(dff["Solar"].mean()),2)
    total = avg_w + avg_s
    fig = go.Figure(go.Pie(
        labels=["Wind","Solar"], values=[avg_w,avg_s], hole=0.58,
        marker=dict(colors=[A2,A3], line=dict(color=pc["bg"],width=3)),
        textinfo="label+percent", textfont=dict(color=pc["text"],size=11),
        hovertemplate="<b>%{label}</b><br>Avg: %{value:.1f} GWh/day<br>%{percent}<extra></extra>",
        pull=[0.05,0.05], rotation=45))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20,r=20,t=10,b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(color=pc["text"],size=11),
                    orientation="h",y=-0.05),
        font=dict(family="'DM Sans',sans-serif",color=pc["text"]),
        annotations=[dict(text=f"<b>{total:.1f}</b><br>GWh/day",
                          x=0.5,y=0.5,showarrow=False,
                          font=dict(size=14,color=pc["text"],family="'DM Sans',sans-serif"))])
    return fig


#RUN
if __name__ == "__main__":
    print("Germany Energy Dashboard")
    print("   Open http://127.0.0.1:8050")
    app.run(debug=False, port=8050)