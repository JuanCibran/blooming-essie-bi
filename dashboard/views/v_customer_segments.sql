-- Vista: Segmentación de clientes
-- Página 2: Customer Analysis
CREATE OR REPLACE VIEW `blooming-essie.blooming_essie.v_customer_segments` AS
SELECT
  CASE
    WHEN orders_count = 1 THEN '1 - Nuevo'
    WHEN orders_count BETWEEN 2 AND 3 THEN '2 - Recurrente'
    WHEN orders_count >= 4 THEN '3 - Fiel'
  END AS segment,
  COUNT(*) AS customer_count,
  ROUND(SUM(total_spent), 2) AS total_revenue,
  ROUND(AVG(total_spent), 2) AS avg_spent,
  ROUND(AVG(orders_count), 1) AS avg_orders
FROM `blooming-essie.blooming_essie.customers`
GROUP BY segment
ORDER BY segment
