#!/usr/bin/env python3
"""Download source data files specified in download.yaml and preprocess SQLite data."""

import sqlite3
import urllib.request
from pathlib import Path

import yaml


def download_files():
    """Download all files specified in download.yaml."""
    with open("download.yaml") as f:
        config = yaml.safe_load(f)

    downloads = config.get("downloads", [])
    if not downloads:
        print("No downloads configured in download.yaml")
        return

    for item in downloads:
        url = item["url"]
        local_name = item["local_name"]
        local_path = Path(local_name)

        # Create parent directories if needed
        local_path.parent.mkdir(parents=True, exist_ok=True)

        if local_path.exists():
            print(f"Skipping {local_name} (already exists)")
            continue

        print(f"Downloading {url} -> {local_name}")
        urllib.request.urlretrieve(url, local_path)
        print(f"  Downloaded {local_path.stat().st_size:,} bytes")


def extract_phenotype_mappings():
    """Extract phenotype name to ID mappings from ddpheno.db SQLite database."""
    db_path = Path("data/ddpheno.db")
    tsv_path = Path("data/ddpheno.tsv")

    if not db_path.exists():
        print(f"SQLite database {db_path} not found. Skipping phenotype mapping extraction.")
        return

    if tsv_path.exists():
        print(f"Skipping {tsv_path} (already exists)")
        return

    print(f"Extracting phenotype mappings from {db_path} -> {tsv_path}")

    # Query to extract DDPHENO term IDs and names from semantic SQL database
    query = """
        SELECT subject as id, value as name
        FROM rdfs_label_statement
        WHERE predicate = 'rdfs:label' AND subject LIKE 'DDPHENO:%'
    """

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()

        with open(tsv_path, 'w') as f:
            # Write header line
            f.write("id\tname\n")
            for row in rows:
                f.write(f"{row[0]}\t{row[1]}\n")

        print(f"  Extracted {len(rows)} phenotype mappings")
    except sqlite3.Error as e:
        print(f"Error extracting phenotype mappings: {e}")


if __name__ == "__main__":
    download_files()
    extract_phenotype_mappings()
