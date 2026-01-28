"""Tests for dictybase gene transform."""

import pytest
from biolink_model.datamodel.pydanticmodel_v2 import Gene

from gene import transform_record


@pytest.fixture
def basic_gene_row():
    """Test Dictybase Gene ingest with mock data."""
    row = {"GENE ID": "DDB_G0269222", "Gene Name": "gefB", "Synonyms": "RasGEFB, RasGEF"}
    return transform_record(None, row)


@pytest.fixture
def gene_no_synonyms():
    """Test Dictybase Gene ingest with no synonyms."""
    row = {"GENE ID": "DDB_G0267364", "Gene Name": "DDB_G0267364_RTE", "Synonyms": ""}
    return transform_record(None, row)


def test_gene_count(basic_gene_row):
    genes = [entity for entity in basic_gene_row if isinstance(entity, Gene)]
    assert len(genes) == 1


def test_gene_id(basic_gene_row):
    gene = basic_gene_row[0]
    assert gene.id == "dictyBase:DDB_G0269222"


def test_gene_symbol(basic_gene_row):
    gene = basic_gene_row[0]
    assert gene.symbol == "gefB"


def test_gene_name(basic_gene_row):
    gene = basic_gene_row[0]
    assert gene.name == "gefB"


def test_gene_synonyms(basic_gene_row):
    gene = basic_gene_row[0]
    assert "RasGEFB" in gene.synonym
    assert "RasGEF" in gene.synonym


def test_gene_no_synonyms(gene_no_synonyms):
    gene = gene_no_synonyms[0]
    assert gene.synonym == []


def test_gene_taxon(basic_gene_row):
    gene = basic_gene_row[0]
    assert "NCBITaxon:44689" in gene.in_taxon
    assert gene.in_taxon_label == "Dictyostelium discoideum"


def test_gene_provided_by(basic_gene_row):
    gene = basic_gene_row[0]
    assert "infores:dictybase" in gene.provided_by
