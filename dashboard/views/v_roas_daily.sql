-- Vista: ROAS diario (Gasto en Ads vs Ventas)
-- Página 4: Ads Performance
CREATE OR REPLACE VIEW `blooming-essie.blooming_essie.v_roas_daily` AS
SELECT
  f.date,
  ROUND(f.spend, 2) AS ad_spend,
  ROUND(COALESCE(v.revenue, 0), 2) AS revenue,
  ROUND(COALESCE(v.revenue, 0) / NULLIF(f.spend, 0), 2) AS roas,
  COALESCE(v.total_orders, 0) AS orders,
  ROUND(COALESCE(v.revenue, 0) / NULLIF(v.total_orders, 0), 2) AS avg_order_value
FROM (
  SELECT date, ROUND(SUM(spend), 2) AS spend
  FROM `blooming-essie.blooming_essie.facebook_campaign_insights`
  GROUP BY date
) f
LEFT JOIN (
  SELECT
    DATE(created_at) AS date,
    SUM(total) AS revenue,
    COUNT(*) AS total_orders
  FROM `blooming-essie.blooming_essie.orders`
  WHERE payment_status = 'paid'
  GROUP BY date
) v ON f.date = v.date
ORDER BY f.date DESC
