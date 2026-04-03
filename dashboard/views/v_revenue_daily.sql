-- Vista: Ingresos diarios
-- Página 1: Revenue & Sales
CREATE OR REPLACE VIEW `blooming-essie.blooming_essie.v_revenue_daily` AS
SELECT
  DATE(created_at) AS date,
  COUNT(*) AS total_orders,
  ROUND(SUM(total), 2) AS revenue,
  ROUND(AVG(total), 2) AS avg_order_value,
  ROUND(SUM(discount), 2) AS total_discounts,
  COUNT(DISTINCT customer_id) AS unique_customers
FROM `blooming-essie.blooming_essie.orders`
WHERE payment_status = 'paid'
GROUP BY date
ORDER BY date DESC
