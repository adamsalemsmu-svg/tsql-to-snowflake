SELECT
  "Id",
  COALESCE("Name", 'N/A') AS "Name"
FROM "dbo"."Users"
WHERE
  "Active" = 1
ORDER BY
  "CreatedAt" DESC NULLS LAST
LIMIT 3;

WITH "AgentSales" AS (
  SELECT
    "a"."full_name",
    "p"."city",
    SUM("t"."sale_price") AS "TotalSales"
  FROM "dbo"."transactions" AS "t"
  JOIN "dbo"."agents" AS "a"
    ON "a"."agent_id" = "t"."agent_id"
  JOIN "dbo"."properties" AS "p"
    ON "p"."property_id" = "t"."property_id"
  WHERE
    "t"."created_at" >= DATEADD(MONTH, -3, CURRENT_TIMESTAMP())
  GROUP BY
    "a"."full_name",
    "p"."city"
)
SELECT
  "city",
  "full_name",
  "TotalSales",
  ROW_NUMBER() OVER (PARTITION BY "city" ORDER BY "TotalSales" DESC NULLS LAST) AS "rn"
FROM "AgentSales";