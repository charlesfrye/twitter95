UPDATE tweets t
SET quotes = (
    SELECT COUNT(*)
    FROM tweets q
    WHERE q.quoted = t.tweet_id
)
