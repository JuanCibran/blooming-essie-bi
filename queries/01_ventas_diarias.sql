-- VENTAS DIARIAS
-- Tendencia de ingresos, órdenes y ticket promedio por día
SELECT
  DATE(created_at) AS fecha,
  COUNT(*) AS total_ordenes,
  ROUND(SUM(total), 2) AS ingresos_totales,
  ROUND(AVG(total), 2) AS ticket_promedio,
  ROUND(SUM(discount), 2) AS descuentos_aplicados
FROM `blooming-essie.blooming_essie.orders`
WHERE payment_status = 'paid'
GROUP BY fecha
ORDER BY fecha DESC
