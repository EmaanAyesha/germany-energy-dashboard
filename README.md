# ⚡ Germany Energy Dashboard

An interactive Dash + Plotly dashboard exploring Germany's daily electricity consumption, wind, and solar generation from 2006–2017, built on the [Open Power System Data (OPSD)](https://open-power-system-data.org/) dataset.

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Dash](https://img.shields.io/badge/dash-2.x-00d4aa)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

## Features

- **KPI cards** — average/peak daily consumption, wind, and solar output
- **Time series chart** — toggle between area, line, and bar views; filter by series and year range
- **Yearly & monthly aggregates** — bar and line charts of average output
- **Pie / donut / polar charts** — energy mix breakdown, renewables split, and a seasonal rose chart, all driven by a year selector
- **Seasonal breakdown** — grouped bar chart by Spring/Summer/Autumn/Winter
- **Consumption heatmap** — year × month grid
- **Distribution histogram** — daily value spread per series
- **Renewables growth** — stacked area chart of wind + solar over time

All charts are cross-filtered by a shared year-range slider and series checklist, and most run on Dash callbacks with no full-page reload.

## Demo

Run locally and open `http://127.0.0.1:8050` — see [Getting Started](#getting-started) below.

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/<your-username>/germany-energy-dashboard.git
cd germany-energy-dashboard
```

### 2. Set up a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add the dataset

Download `opsd_germany_daily.csv` from the [OPSD time series page](https://data.open-power-system-data.org/time_series/) and place it in the project root, alongside `germany_energy_dashboard.py`.

The CSV should contain at minimum these columns: `Date`, `Consumption`, `Wind`, `Solar` (a `Wind+Solar` column will be auto-computed if missing).

### 5. Run the app

```bash
python germany_energy_dashboard.py
```

Open **http://127.0.0.1:8050** in your browser.

## Project Structure

```
germany-energy-dashboard/
├── germany_energy_dashboard.py   # Main Dash app
├── requirements.txt              # Python dependencies
├── opsd_germany_daily.csv        # Dataset (not included — see step 4)
├── .gitignore
└── README.md
```

## Tech Stack

- [Dash](https://dash.plotly.com/) — web app framework
- [Plotly](https://plotly.com/python/) — interactive charting
- [Pandas](https://pandas.pydata.org/) — data wrangling

## Data Source

Open Power System Data, *Time series*. [https://open-power-system-data.org/](https://open-power-system-data.org/)

## License

MIT — see [LICENSE](LICENSE) for details.
