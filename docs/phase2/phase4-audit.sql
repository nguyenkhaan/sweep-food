-- Run manually on a test database or read-only clone before Phase 4 rollout.
-- This query is read-only and reports legacy meal-plan items needing review.
WITH session_counts AS (
    SELECT
        meal_plan_item_id,
        COUNT(*) AS session_count,
        COUNT(*) FILTER (WHERE status = 'COMPLETED') AS completed_session_count
    FROM cooking_sessions
    WHERE meal_plan_item_id IS NOT NULL
    GROUP BY meal_plan_item_id
)
SELECT
    meal_plan_items.id AS meal_plan_item_id,
    meal_plan_items.meal_plan_id,
    meal_plan_items.status AS meal_plan_item_status,
    COALESCE(session_counts.session_count, 0) AS session_count,
    COALESCE(session_counts.completed_session_count, 0) AS completed_session_count
FROM meal_plan_items
LEFT JOIN session_counts ON session_counts.meal_plan_item_id = meal_plan_items.id
WHERE COALESCE(session_counts.session_count, 0) > 1
   OR COALESCE(session_counts.completed_session_count, 0) > 1
   OR (
       meal_plan_items.status = 'PLANNED'
       AND COALESCE(session_counts.completed_session_count, 0) > 0
   )
ORDER BY meal_plan_items.id;
