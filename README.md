# Blooming Essie — Business Intelligence Pipeline

ETL pipeline that pulls data from **Tienda Nube** and **Facebook Ads** into **Google BigQuery** daily.

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
│   ├── tienda_nube.py          # Tienda Nube extractor (orders, products, customers)
│   ├── facebook_ads.py         # Facebook Ads extractor (campaign insights)
│   └── bigquery_loader.py      # BigQuery loader + schema definitions
├── scheduler/
│   └── run_daily.sh            # Cron script for daily execution
└── logs/                       # Auto-created on first run
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
| `FACEBOOK_ACCESS_TOKEN` | Meta Business Suite > long-lived token |
| `FACEBOOK_AD_ACCOUNT_ID` | Meta Ads Manager > Account ID (format: `act_XXXXXXXXX`) |
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

### 5. Schedule daily runs (macOS cron)

```bash
crontab -e
```

Add this line to run every day at 6:00 AM:

```
0 6 * * * /bin/bash "/Users/juancruzcibran/Desktop/Blooming Essie/scheduler/run_daily.sh"
```

Logs are saved to `logs/pipeline.log`.

---

## BigQuery Tables

| Table | Source | Load mode |
|---|---|---|
| `orders` | Tienda Nube | Append (daily delta) |
| `products` | Tienda Nube | Full replace daily |
| `customers` | Tienda Nube | Full replace daily |
| `facebook_campaign_insights` | Facebook Ads | Append (daily delta) |

---

## Notes

- Orders and Facebook insights load only the **last 1 day** by default. Change `days_back` in `main.py` for backfills.
- All tables are auto-created on first run if they don't exist.
