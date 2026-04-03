import os
from dotenv import load_dotenv

load_dotenv()

# Tienda Nube
TIENDANUBE_USER_ID = os.getenv("TIENDANUBE_USER_ID")
TIENDANUBE_ACCESS_TOKEN = os.getenv("TIENDANUBE_ACCESS_TOKEN")
TIENDANUBE_BASE_URL = f"https://api.tiendanube.com/v1/{TIENDANUBE_USER_ID}"
TIENDANUBE_HEADERS = {
    "Authentication": f"bearer {TIENDANUBE_ACCESS_TOKEN}",
    "User-Agent": "Blooming Essie BI (bloomingessie@email.com)",
}

# Facebook Ads
FACEBOOK_APP_ID = os.getenv("FACEBOOK_APP_ID")
FACEBOOK_APP_SECRET = os.getenv("FACEBOOK_APP_SECRET")
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")
FACEBOOK_AD_ACCOUNT_ID = os.getenv("FACEBOOK_AD_ACCOUNT_ID")

# BigQuery
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
BIGQUERY_PROJECT_ID = os.getenv("BIGQUERY_PROJECT_ID")
BIGQUERY_DATASET_ID = os.getenv("BIGQUERY_DATASET_ID", "blooming_essie")
