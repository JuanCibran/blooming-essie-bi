-- Vista: Ingresos mensuales
-- Página 1: Revenue & Sales
CREATE OR REPLACE VIEW `blooming-essie.blooming_essie.v_revenue_monthly` AS
SELECT
  FORMAT_DATE('%Y-%m', DATE(created_at)) AS month,
  COUNT(*) AS total_orders,
  ROUND(SUM(total), 2) AS revenue,
  ROUND(AVG(total), 2) AS avg_order_value,
  COUNT(DISTINCT customer_id) AS unique_customers,
  ROUND(SUM(discount), 2) AS total_discounts
FROM `blooming-essie.blooming_essie.orders`
WHERE payment_status = 'paid'
GROUP BY month
ORDER BY month DESC
