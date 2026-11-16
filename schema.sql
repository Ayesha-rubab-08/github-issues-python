CREATE TABLE IF NOT EXISTS issues (
  id BIGINT PRIMARY KEY,
  number INTEGER NOT NULL,
  title TEXT NOT NULL,
  author TEXT,
  is_pull_request BOOLEAN NOT NULL DEFAULT false
);

CREATE INDEX IF NOT EXISTS idx_issues_author ON issues (author);