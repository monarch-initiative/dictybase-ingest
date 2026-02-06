#!/bin/sh

echo "Running \"scripts/after_download.sh\"."

if [ -f data/ddpheno.db ]; then
  # Make an id, name map of DDPHENO terms
  sqlite3 -cmd ".mode tabs" -cmd ".headers on" data/ddpheno.db "select subject as id, value as name from rdfs_label_statement where predicate = 'rdfs:label' and subject like 'DDPHENO:%'" > data/ddpheno.tsv
  echo "\"data/ddpheno.tsv\" created from \"data/ddpheno.db\"."
else
  echo "\"data/ddpheno.db\" does not exist. Skipping creation of \"data/ddpheno.tsv\"."
fi
