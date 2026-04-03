-- Vista: Performance de productos
-- Página 3: Product Performance
CREATE OR REPLACE VIEW `blooming-essie.blooming_essie.v_product_performance` AS
SELECT
  product_name,
  sku,
  ROUND(price, 2) AS price,
  stock,
  published,
  CASE
    WHEN stock = 0 THEN 'Sin Stock'
    WHEN stock <= 5 THEN 'Stock Crítico'
    WHEN stock <= 15 THEN 'Stock Bajo'
    ELSE 'OK'
  END AS stock_status,
  ROUND(price * stock, 2) AS inventory_value
FROM `blooming-essie.blooming_essie.products`
WHERE published = TRUE
ORDER BY stock ASC
