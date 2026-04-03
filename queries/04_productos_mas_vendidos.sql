-- PRODUCTOS MÁS VENDIDOS POR STOCK RESTANTE
-- Identifica tus bestsellers y los que necesitan reposición urgente
SELECT
  product_name,
  sku,
  price,
  stock,
  CASE
    WHEN stock = 0 THEN 'SIN STOCK'
    WHEN stock <= 5 THEN 'STOCK CRÍTICO'
    WHEN stock <= 15 THEN 'STOCK BAJO'
    ELSE 'OK'
  END AS estado_stock
FROM `blooming-essie.blooming_essie.products`
WHERE published = TRUE
ORDER BY stock ASC
