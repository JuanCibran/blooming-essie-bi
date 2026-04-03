-- Vista: Performance de campañas Facebook Ads
-- Página 4: Ads Performance
CREATE OR REPLACE VIEW `blooming-essie.blooming_essie.v_ads_performance` AS
SELECT
  date,
  campaign_name,
  adset_name,
  impressions,
  clicks,
  ROUND(spend, 2) AS spend,
  reach,
  ROUND(ctr, 2) AS ctr,
  ROUND(cpc, 2) AS cpc,
  ROUND(cpm, 2) AS cpm
FROM `blooming-essie.blooming_essie.facebook_campaign_insights`
ORDER BY date DESC, spend DESC
