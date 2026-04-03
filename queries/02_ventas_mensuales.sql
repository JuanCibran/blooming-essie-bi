-- VENTAS MENSUALES + COMPARACIÓN MES ANTERIOR
SELECT
  FORMAT_DATE('%Y-%m', DATE(created_at)) AS mes,
  COUNT(*) AS total_ordenes,
  ROUND(SUM(total), 2) AS ingresos,
  ROUND(AVG(total), 2) AS ticket_promedio,
  COUNT(DISTINCT customer_id) AS clientes_unicos
FROM `blooming-essie.blooming_essie.orders`
WHERE payment_status = 'paid'
GROUP BY mes
ORDER BY mes DESC
