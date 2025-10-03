SELECT
  a.full_name          AS agent_name,
  COUNT(t.transaction_id) AS deals,
  SUM(t.sale_price)       AS total_sales,
  SUM(t.commission)       AS total_commission,
  ROUND(AVG(t.sale_price), 2) AS avg_deal
FROM agents a
JOIN transactions t
  ON t.agent_id = a.agent_id
GROUP BY a.full_name
ORDER BY total_sales DESC
LIMIT 5;


SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'agents';

SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'transactions';
