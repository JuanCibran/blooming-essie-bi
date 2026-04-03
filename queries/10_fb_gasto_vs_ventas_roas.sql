-- ROAS: GASTO EN ADS VS VENTAS DEL MISMO DÍA
-- Return On Ad Spend — cuánto generás por cada peso invertido en Meta
-- ROAS > 3x se considera bueno para e-commerce de moda/bebé
SELECT
  f.date,
  ROUND(f.spend, 2) AS gasto_meta,
  ROUND(v.ingresos, 2) AS ventas_del_dia,
  ROUND(v.ingresos / NULLIF(f.spend, 0), 2) AS roas,
  v.ordenes
FROM (
  SELECT
    date,
    SUM(spend) AS spend
  FROM `blooming-essie.blooming_essie.facebook_campaign_insights`
  GROUP BY date
) f
LEFT JOIN (
  SELECT
    DATE(created_at) AS date,
    SUM(total) AS ingresos,
    COUNT(*) AS ordenes
  FROM `blooming-essie.blooming_essie.orders`
  WHERE payment_status = 'paid'
  GROUP BY date
) v ON f.date = v.date
ORDER BY f.date DESC
