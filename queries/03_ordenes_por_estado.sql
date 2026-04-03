-- ÓRDENES POR ESTADO DE PAGO Y ENVÍO
-- Útil para ver cuánto está pendiente de cobro o envío
SELECT
  payment_status,
  shipping_status,
  COUNT(*) AS cantidad,
  ROUND(SUM(total), 2) AS valor_total
FROM `blooming-essie.blooming_essie.orders`
GROUP BY payment_status, shipping_status
ORDER BY cantidad DESC
