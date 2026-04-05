# Blooming Essie — Business Intelligence Pipeline

ETL pipeline that pulls data from **Tienda Nube** and **Facebook Ads** into **Google BigQuery**, with a **Streamlit dashboard** for analysis.

---

## Project Structure

```
Blooming Essie/
├── main.py                     # Pipeline entry point
├── requirements.txt
├── .env.example                # Copy to .env and fill in credentials
├── config/
│   └── settings.py             # Loads env vars
├── etl/
│   ├── tienda_nube.py          # Tienda Nube extractor (orders, products, customers, abandoned carts)
│   ├── facebook_ads.py         # Facebook Ads extractor (campaign insights)
│   ├── meta_capi.py            # Meta Conversions API (purchase events)
│   └── bigquery_loader.py      # BigQuery loader + schema definitions
├── dashboard/
│   ├── data.py                 # BigQuery queries for the dashboard
│   └── filters.py              # Date filter component
├── Resumen.py                  # Dashboard home page
├── pages/
│   ├── 1_Revenue_Sales.py
│   ├── 2_Customer_Analysis.py
│   ├── 3_Product_Performance.py
│   └── 4_Ads_Performance.py
└── .github/workflows/
    └── daily_pipeline.yml      # GitHub Actions — runs every 4 hours
```

---

## Setup Instructions

### 1. Install dependencies

```bash
cd "Blooming Essie"
pip3 install -r requirements.txt
```

### 2. Configure credentials

```bash
cp .env.example .env
```

Open `.env` and fill in:

| Variable | Where to find it |
|---|---|
| `TIENDANUBE_USER_ID` | Tienda Nube Partners > App credentials |
| `TIENDANUBE_ACCESS_TOKEN` | Tienda Nube API OAuth token |
| `FACEBOOK_APP_ID` | Meta for Developers > Your App |
| `FACEBOOK_APP_SECRET` | Meta for Developers > Your App > Settings |
| `FACEBOOK_ACCESS_TOKEN` | Meta Business Suite > long-lived token (~60 days) |
| `FACEBOOK_AD_ACCOUNT_ID` | Meta Ads Manager > Account ID (format: `act_XXXXXXXXX`) |
| `FACEBOOK_PIXEL_ID` | Meta Events Manager > Pixel ID |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to GCP service account JSON key |
| `BIGQUERY_PROJECT_ID` | Google Cloud Console > Project ID |
| `BIGQUERY_DATASET_ID` | Leave as `blooming_essie` or rename |

### 3. Set up Google Cloud

1. Create a project at [console.cloud.google.com](https://console.cloud.google.com)
2. Enable the **BigQuery API**
3. Create a **Service Account** with the `BigQuery Data Editor` role
4. Download the JSON key and set its path in `GOOGLE_APPLICATION_CREDENTIALS`

### 4. Run manually

```bash
python3 main.py
```

### 5. Automated runs

The pipeline runs automatically every 4 hours via **GitHub Actions** (`.github/workflows/daily_pipeline.yml`). No local cron needed.

Credentials are stored as **GitHub Secrets** (`TIENDANUBE_USER_ID`, `TIENDANUBE_ACCESS_TOKEN`, `FACEBOOK_ACCESS_TOKEN`, etc.) and as a `GCP_SERVICE_ACCOUNT_JSON` secret for BigQuery auth.

---

## BigQuery Tables

| Table | Source | Load mode |
|---|---|---|
| `orders` | Tienda Nube | Full replace daily |
| `products` | Tienda Nube | Full replace daily |
| `customers` | Tienda Nube | Full replace daily |
| `abandoned_carts` | Tienda Nube | Full replace daily |
| `facebook_campaign_insights` | Facebook Ads | Append (last 7 days) |

---

## Dashboard (Streamlit)

Deployed on **Streamlit Cloud**. BigQuery credentials are stored in Streamlit Secrets as a `[gcp_service_account]` TOML section.

| Page | Content |
|---|---|
| Resumen | KPIs, monthly revenue chart, alerts |
| Revenue & Sales | Daily/monthly revenue by period |
| Customer Analysis | Segments, top customers, campaign list (unconverted + abandoned carts) |
| Product Performance | Stock by variant/size, low stock alerts |
| Ads Performance | Facebook campaigns, CTR, CPC, ROAS |

---

## Notes

- Meta CAPI only sends purchase events from the **last 7 days** (Meta rejects older events).
- Facebook Access Token is a long-lived token (~60 days). Rotate before expiry.
- All BigQuery tables are auto-created on first run if they don't exist.
