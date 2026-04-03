import pandas as pd
from datetime import datetime, timedelta
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adsinsights import AdsInsights
from config.settings import (
    FACEBOOK_APP_ID,
    FACEBOOK_APP_SECRET,
    FACEBOOK_ACCESS_TOKEN,
    FACEBOOK_AD_ACCOUNT_ID,
)


def init_facebook_api():
    FacebookAdsApi.init(
        app_id=FACEBOOK_APP_ID,
        app_secret=FACEBOOK_APP_SECRET,
        access_token=FACEBOOK_ACCESS_TOKEN,
    )


def extract_campaign_insights(days_back: int = 1) -> pd.DataFrame:
    """Pull campaign-level ad insights for the last N days."""
    init_facebook_api()

    account = AdAccount(FACEBOOK_AD_ACCOUNT_ID)
    since = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    until = datetime.utcnow().strftime("%Y-%m-%d")

    fields = [
        AdsInsights.Field.campaign_id,
        AdsInsights.Field.campaign_name,
        AdsInsights.Field.adset_name,
        AdsInsights.Field.impressions,
        AdsInsights.Field.clicks,
        AdsInsights.Field.spend,
        AdsInsights.Field.reach,
        AdsInsights.Field.cpc,
        AdsInsights.Field.cpm,
        AdsInsights.Field.ctr,
        AdsInsights.Field.date_start,
        AdsInsights.Field.date_stop,
    ]

    params = {
        "time_range": {"since": since, "until": until},
        "level": "campaign",
        "time_increment": 1,
    }

    insights = account.get_insights(fields=fields, params=params)

    rows = []
    for insight in insights:
        rows.append(
            {
                "campaign_id": insight.get("campaign_id", ""),
                "campaign_name": insight.get("campaign_name", ""),
                "adset_name": insight.get("adset_name", ""),
                "date": insight.get("date_start", ""),
                "impressions": int(insight.get("impressions", 0)),
                "clicks": int(insight.get("clicks", 0)),
                "spend": float(insight.get("spend", 0)),
                "reach": int(insight.get("reach", 0)),
                "cpc": float(insight.get("cpc", 0) or 0),
                "cpm": float(insight.get("cpm", 0) or 0),
                "ctr": float(insight.get("ctr", 0) or 0),
            }
        )

    return pd.DataFrame(rows)
