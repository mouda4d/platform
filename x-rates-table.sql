USE DE_SANDBOX;
GO
-- 1. Check and create schema
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'fin')
BEGIN
    EXEC('CREATE SCHEMA fin');
END
GO

-- 2. Check and create table
IF OBJECT_ID('fin.xrates', 'U') IS NULL
BEGIN
    CREATE TABLE fin.xrates (
        rate_date DATE NOT NULL,
        currency varchar(3) NOT NULL,
        bid DECIMAL(18, 4) NOT NULL,
        ask DECIMAL(18, 4),
        mid DECIMAL(18, 4),
        revision int NOT NULL DEFAULT 1,
        published_at datetimeOFFSET NULL,
        CONSTRAINT PK_xrates PRIMARY KEY (rate_date, currency)
    );
END
GO

SELECT * FROM fin.xrates;




USE qantara_uat;
GO
SELECT top 100 *
FROM fin.wallet w
INNER JOIN lkp.status_code sc 
  ON w.sts_cd = sc.STS_CD
  AND sc.entity = 'WLT'
  AND sc.DESC_en = 'ACTIVE'
--ORDER BY sc.entity DESC;

-- select * from lkp.status_code

select * from INFORMATION_SCHEMA.tables order by table_schema, table_name
select * from dbo.trx_mst;

select * from rem.partner;
select * from rem.corridor;

with cte as (
    select corridor_id, sum(payout_amount) as total_payout
    from rem.payout_instruction 
    where paid_at >= CAST(DATEADD(day, -1, getdate()) as date) 
    AND paid_at < cast(getdate() as date)
    group by corridor_id
)
select corridor_code, total_payout
from cte
LEFT JOIN rem.corridor c
ON cte.corridor_id = c.corridor_id
ORDER BY total_payout DESC;