-- RANKING DE CAMPAÑAS POR EFICIENCIA
-- Cuál campaña tiene mejor CTR y menor costo por click
SELECT
  campaign_name,
  SUM(impressions) AS impresiones_totales,
  SUM(clicks) AS clicks_totales,
  ROUND(SUM(spend), 2) AS gasto_total,
  ROUND(AVG(ctr), 2) AS ctr_promedio,
  ROUND(SUM(spend) / NULLIF(SUM(clicks), 0), 2) AS cpc_real,
  ROUND(SUM(spend) / NULLIF(SUM(impressions), 0) * 1000, 2) AS cpm_real
FROM `blooming-essie.blooming_essie.facebook_campaign_insights`
GROUP BY campaign_name
ORDER BY gasto_total DESC
