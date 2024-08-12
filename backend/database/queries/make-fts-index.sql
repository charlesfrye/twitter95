alter table
  tweets
add column
  text_fts tsvector generated always as (to_tsvector('english', text)) stored;

create index tweets_text_fts on tweets using gin (text_fts);
