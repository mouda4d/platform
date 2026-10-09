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

-- SELECT * FROM fin.xrates;

