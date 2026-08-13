-- ================================================================
-- Amazon Web Traffic Analysis - SQL Business Analysis
-- Database: MySQL
-- Table: web_traffic (from amazon_traffic_clean.csv)
-- ================================================================

CREATE TABLE IF NOT EXISTS web_traffic (
    session_id                 VARCHAR(20),
    timestamp                  DATETIME,
    country                    VARCHAR(50),
    device_category            VARCHAR(20),
    source                     VARCHAR(30),
    page_path                  VARCHAR(50),
    avg_session_duration_sec   DECIMAL(8,1),
    bounce_rate                DECIMAL(5,3),
    conversions                TINYINT,
    new_user                   VARCHAR(3),
    page_views                 INT,
    unique_page_views          INT
);

-- 1. Overall traffic & conversion summary
SELECT
    COUNT(*)                                   AS total_sessions,
    SUM(conversions)                           AS total_conversions,
    ROUND(SUM(conversions) * 100.0 / COUNT(*), 2) AS conversion_rate_pct,
    ROUND(AVG(bounce_rate) * 100, 1)           AS avg_bounce_rate_pct,
    ROUND(AVG(avg_session_duration_sec), 1)    AS avg_session_duration_sec
FROM web_traffic;

-- 2. Traffic source performance (window function for % share)
SELECT
    source,
    COUNT(*) AS sessions,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct_of_traffic,
    ROUND(SUM(conversions) * 100.0 / COUNT(*), 2) AS conversion_rate_pct,
    ROUND(AVG(bounce_rate) * 100, 1) AS avg_bounce_rate_pct
FROM web_traffic
GROUP BY source
ORDER BY sessions DESC;

-- 3. New vs returning users
SELECT
    new_user,
    COUNT(*) AS sessions,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct_of_sessions,
    ROUND(SUM(conversions) * 100.0 / COUNT(*), 2) AS conversion_rate_pct
FROM web_traffic
GROUP BY new_user;

-- 4. Traffic & bounce rate by device category
SELECT
    device_category,
    COUNT(*) AS sessions,
    ROUND(AVG(bounce_rate) * 100, 1) AS avg_bounce_rate_pct,
    ROUND(SUM(conversions) * 100.0 / COUNT(*), 2) AS conversion_rate_pct
FROM web_traffic
GROUP BY device_category
ORDER BY sessions DESC;

-- 5. Top 10 countries by traffic
SELECT
    country,
    COUNT(*) AS sessions,
    ROUND(SUM(conversions) * 100.0 / COUNT(*), 2) AS conversion_rate_pct
FROM web_traffic
GROUP BY country
ORDER BY sessions DESC
LIMIT 10;

-- 6. Top 10 pages by page views
SELECT
    page_path,
    SUM(page_views) AS total_page_views,
    SUM(unique_page_views) AS total_unique_page_views,
    RANK() OVER (ORDER BY SUM(page_views) DESC) AS page_rank
FROM web_traffic
GROUP BY page_path
ORDER BY total_page_views DESC
LIMIT 10;

-- 7. Traffic by hour of day
SELECT
    HOUR(timestamp) AS hour_of_day,
    COUNT(*) AS sessions,
    ROUND(AVG(bounce_rate) * 100, 1) AS avg_bounce_rate_pct
FROM web_traffic
GROUP BY hour_of_day
ORDER BY hour_of_day;

-- 8. Traffic by day of week
SELECT
    DAYNAME(timestamp) AS day_of_week,
    COUNT(*) AS sessions,
    SUM(conversions) AS conversions
FROM web_traffic
GROUP BY day_of_week
ORDER BY FIELD(day_of_week, 'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday');

-- 9. Monthly traffic trend (window function: month-over-month growth)
SELECT
    traffic_month,
    monthly_sessions,
    ROUND(
        (monthly_sessions - LAG(monthly_sessions) OVER (ORDER BY traffic_month))
        / LAG(monthly_sessions) OVER (ORDER BY traffic_month) * 100, 1
    ) AS mom_growth_pct
FROM (
    SELECT DATE_FORMAT(timestamp, '%Y-%m') AS traffic_month,
           COUNT(*) AS monthly_sessions
    FROM web_traffic
    GROUP BY traffic_month
) monthly
ORDER BY traffic_month;

-- 10. High-bounce, low-conversion sources (CTE - optimization targets)
WITH source_perf AS (
    SELECT
        source,
        ROUND(AVG(bounce_rate) * 100, 1) AS avg_bounce_rate_pct,
        ROUND(SUM(conversions) * 100.0 / COUNT(*), 2) AS conversion_rate_pct
    FROM web_traffic
    GROUP BY source
)
SELECT *
FROM source_perf
WHERE avg_bounce_rate_pct > 45 AND conversion_rate_pct < 3
ORDER BY avg_bounce_rate_pct DESC;
