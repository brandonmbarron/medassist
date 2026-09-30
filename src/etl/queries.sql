-- Week 1, Block 4 practice: run these with spark.sql() after registering
-- the curated claims as a temp view:
--   spark.read.parquet("data/curated/claims").createOrReplaceTempView("claims")

-- 1. Denial rate by plan
-- TODO: SELECT plan_id, share of claims with status = 'DENIED'

-- 2. Average days to process, paid vs denied
-- TODO

-- 3. Top 3 denial reasons per plan (hint: ROW_NUMBER() OVER (PARTITION BY ...))
-- TODO
