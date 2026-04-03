-- RESUMEN EJECUTIVO — KPIs PRINCIPALES
-- Una sola vista con los números más importantes
SELECT
  (SELECT COUNT(*) FROM `blooming-essie.blooming_essie.orders` WHERE payment_status = 'paid') AS total_ordenes_pagas,
  (SELECT ROUND(SUM(total), 2) FROM `blooming-essie.blooming_essie.orders` WHERE payment_status = 'paid') AS ingresos_totales,
  (SELECT ROUND(AVG(total), 2) FROM `blooming-essie.blooming_essie.orders` WHERE payment_status = 'paid') AS ticket_promedio,
  (SELECT COUNT(*) FROM `blooming-essie.blooming_essie.customers`) AS total_clientes,
  (SELECT COUNT(*) FROM `blooming-essie.blooming_essie.customers` WHERE orders_count >= 2) AS clientes_recurrentes,
  (SELECT COUNT(*) FROM `blooming-essie.blooming_essie.products` WHERE stock = 0 AND published = TRUE) AS productos_sin_stock,
  (SELECT COUNT(*) FROM `blooming-essie.blooming_essie.orders` WHERE payment_status = 'pending') AS ordenes_pendientes_cobro
