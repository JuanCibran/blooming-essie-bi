-- Vista: Top clientes por revenue
-- Página 2: Customer Analysis
CREATE OR REPLACE VIEW `blooming-essie.blooming_essie.v_top_customers` AS
SELECT
  name,
  email,
  orders_count,
  ROUND(total_spent, 2) AS total_spent,
  ROUND(total_spent / NULLIF(orders_count, 0), 2) AS avg_order_value,
  DATE(created_at) AS customer_since,
  CASE
    WHEN orders_count = 1 THEN 'Nuevo'
    WHEN orders_count BETWEEN 2 AND 3 THEN 'Recurrente'
    ELSE 'Fiel'
  END AS segment
FROM `blooming-essie.blooming_essie.customers`
ORDER BY total_spent DESC
