DROP TABLE IF EXISTS meta;
CREATE TABLE meta (
  key text primary key,
  value text not null,
  comment text
);
INSERT INTO meta (key, value, comment) VALUES ('first-run', '0', 'Whether or not the control panel has run a first time');
