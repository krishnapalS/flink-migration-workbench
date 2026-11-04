SELECT `id` AS `id`, `amount` AS `amount`, `region` AS `region`
FROM `orders`
WHERE `amount` >= CAST('100.00' AS DECIMAL(18,2));
