#standardSQL
SELECT
  SUM(twitter_shared) AS twitter_shared,
  SUM(twitter_likes) AS twitter_likes,
  SUM(pocket_count) AS pocket_count,
  SUM(hatena_bookmark) AS hatena_bookmark,
  SUM(hatena_comments) AS hatena_comments,
  SUM(hatena_star) AS hatena_star,
  SUM(hatena_colorstar) AS hatena_colorstar,
  SUM(facebook_share) AS facebook_share,
  SUM(analytics_last7days) AS analytics_last7days,
  SUM(analytics_last30days) AS analytics_last30days,
  SUM(analytics_total) AS analytics_total
FROM `${GCP_PROJECT_ID}.blog_data.summary`

