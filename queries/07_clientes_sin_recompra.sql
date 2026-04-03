-- CLIENTES QUE COMPRARON UNA VEZ Y NO VOLVIERON
-- Candidatos ideales para campañas de retargeting en Meta
SELECT
  name,
  email,
  ROUND(total_spent, 2) AS primera_compra,
  DATE(created_at) AS fecha_registro
FROM `blooming-essie.blooming_essie.customers`
WHERE orders_count = 1
ORDER BY total_spent DESC
