-- Batch 1 (comment line)
SELECT TOP (3) [Id], ISNULL([Name], 'N/A') AS Name
FROM [dbo].[Users]
WHERE [Active] = 1
ORDER BY [CreatedAt] DESC;
GO

/* Batch 2: CTE + window */
WITH AgentSales AS (
  SELECT a.[full_name], p.[city], SUM(t.[sale_price]) AS TotalSales
  FROM [dbo].[transactions] t
  JOIN [dbo].[agents] a ON a.[agent_id] = t.[agent_id]
  JOIN [dbo].[properties] p ON p.[property_id] = t.[property_id]
  WHERE t.[created_at] >= DATEADD(month, -3, GETDATE())
  GROUP BY a.[full_name], p.[city]
)
SELECT [city], [full_name], TotalSales,
       ROW_NUMBER() OVER (PARTITION BY [city] ORDER BY TotalSales DESC) AS rn
FROM AgentSales;
-- adam go   (random leftover)
