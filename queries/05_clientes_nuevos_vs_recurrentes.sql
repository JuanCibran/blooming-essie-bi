-- CLIENTES NUEVOS VS RECURRENTES
SELECT
  CASE
    WHEN orders_count = 1 THEN 'Nuevo (1 compra)'
    WHEN orders_count BETWEEN 2 AND 3 THEN 'Recurrente (2-3 compras)'
    WHEN orders_count >= 4 THEN 'Fiel (4+ compras)'
  END AS segmento,
  COUNT(*) AS cantidad_clientes,
  ROUND(AVG(total_spent), 2) AS gasto_promedio,
  ROUND(SUM(total_spent), 2) AS gasto_total
FROM `blooming-essie.blooming_essie.customers`
GROUP BY segmento
ORDER BY gasto_total DESC
