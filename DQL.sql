


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