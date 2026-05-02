"""Upstream source version fetcher for dictybase-ingest.

DictyBase has no in-band versioning; use HTTP Last-Modified on the primary
gene_information.txt download as the release date proxy. The phenotype
SQLite (ddpheno.db) is a separate logical source from BBOP-SQLite.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from kozahub_metadata_schema import (
    now_iso,
    urls_from_download_yaml,
    version_from_http_last_modified,
)


INGEST_DIR = Path(__file__).resolve().parents[1]
DOWNLOAD_YAML = INGEST_DIR / "download.yaml"


def get_source_versions() -> list[dict[str, Any]]:
    dicty_urls = urls_from_download_yaml(DOWNLOAD_YAML, contains=["dictybase.org"])
    sqlite_urls = urls_from_download_yaml(DOWNLOAD_YAML, contains=["bbop-sqlite"])
    now = now_iso()

    sources: list[dict[str, Any]] = []

    if dicty_urls:
        ver, method = version_from_http_last_modified(dicty_urls[0])
        sources.append({
            "id": "infores:dictybase",
            "name": "dictyBase",
            "urls": dicty_urls,
            "version": ver,
            "version_method": method,
            "retrieved_at": now,
        })

    if sqlite_urls:
        ver, method = version_from_http_last_modified(sqlite_urls[0])
        sources.append({
            "id": "infores:ddpheno",
            "name": "Dicty Phenotype Ontology (BBOP SQLite)",
            "urls": sqlite_urls,
            "version": ver,
            "version_method": method,
            "retrieved_at": now,
        })

    return sources
