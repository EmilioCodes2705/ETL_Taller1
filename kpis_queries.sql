-- hires_by_technology
SELECT dt.technology, SUM(f.hired) AS hires
FROM fact_application f
JOIN dim_technology dt ON dt.technology_key = f.technology_key
GROUP BY dt.technology
ORDER BY hires DESC;

-- hires_by_year
SELECT d.year, SUM(f.hired) AS hires
FROM fact_application f
JOIN dim_date d ON d.date_key = f.date_key
GROUP BY d.year
ORDER BY d.year;

-- hires_by_seniority
SELECT s.seniority, SUM(f.hired) AS hires
FROM fact_application f
JOIN dim_seniority s ON s.seniority_key = f.seniority_key
GROUP BY s.seniority
ORDER BY hires DESC;

-- hires_by_country_over_years (focus: USA, Brazil, Colombia, Ecuador)
SELECT c.country, d.year, SUM(f.hired) AS hires
FROM fact_application f
JOIN dim_country c ON c.country_key = f.country_key
JOIN dim_date d ON d.date_key = f.date_key
WHERE c.country IN ('United States of America','Brazil','Colombia','Ecuador')
GROUP BY c.country, d.year
ORDER BY c.country, d.year;

-- overall_hire_rate
SELECT ROUND(100.0 * SUM(f.hired) / COUNT(1), 2) AS hire_rate_percent
FROM fact_application f;

-- hires_by_experience_and_avg_scores
SELECT e.experience_range,
       SUM(f.hired) AS hires,
       ROUND(AVG(f.code_challenge_score),2) AS avg_code_challenge,
       ROUND(AVG(f.technical_interview_score),2) AS avg_technical_interview
FROM fact_application f
JOIN dim_experience e ON e.experience_key = f.experience_key
GROUP BY e.experience_range
ORDER BY e.experience_range;
