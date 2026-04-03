-- TOP 20 CLIENTES POR VALOR TOTAL GASTADO
SELECT
  name,
  email,
  orders_count AS cantidad_compras,
  ROUND(total_spent, 2) AS total_gastado,
  ROUND(total_spent / NULLIF(orders_count, 0), 2) AS ticket_promedio
FROM `blooming-essie.blooming_essie.customers`
ORDER BY total_spent DESC
LIMIT 20
