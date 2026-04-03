-- RENDIMIENTO DE CAMPAÑAS DE FACEBOOK ADS
-- Cuánto gastás, cuántos clicks, qué tan eficiente es cada campaña
SELECT
  date,
  campaign_name,
  impressions,
  clicks,
  spend,
  ROUND(ctr, 2) AS ctr_porcentaje,
  ROUND(cpc, 2) AS costo_por_click,
  ROUND(cpm, 2) AS costo_por_mil_impresiones
FROM `blooming-essie.blooming_essie.facebook_campaign_insights`
ORDER BY date DESC, spend DESC
