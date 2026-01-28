"""Tests for dictybase gene to phenotype transform."""

from typing import Dict

import pytest
from biolink_model.datamodel.pydanticmodel_v2 import GeneToPhenotypicFeatureAssociation
from koza import KozaTransform
from koza.io.writer.passthrough_writer import PassthroughWriter

from gene_to_phenotype import transform_record


@pytest.fixture
def phenotype_mapping_cache() -> Dict:
    """Mock phenotype name to ID mappings for Dictybase."""
    return {
        "decreased slug migration": {"id": "DDPHENO:0000225"},
        "aberrant spore morphology": {"id": "DDPHENO:0000163"},
        "delayed aggregation": {"id": "DDPHENO:0000156"},
        "increased cell-substrate adhesion": {"id": "DDPHENO:0000213"},
        "decreased cell motility": {"id": "DDPHENO:0000148"},
        "decreased cell-substrate adhesion": {"id": "DDPHENO:0000393"},
        "delayed development": {"id": "DDPHENO:0000162"},
        "increased growth rate": {"id": "DDPHENO:0000171"},
    }


@pytest.fixture
def test_row_1():
    """Test Dictybase Gene to Phenotype data row with two phenotypes."""
    return {
        "Systematic_Name": "DBS0235594",
        "Strain_Descriptor": "CHE10",
        "Associated gene(s)": "cbpC",
        "DDB_G_ID": "DDB_G0283613",
        "Phenotypes": " decreased slug migration | aberrant spore morphology ",
    }


@pytest.fixture
def test_row_2():
    """Test Dictybase Gene to Phenotype data row with three phenotypes."""
    return {
        "Systematic_Name": "DBS0351079",
        "Strain_Descriptor": "DDB_G0274679-",
        "Associated gene(s)": "DDB_G0274679",
        "DDB_G_ID": "DDB_G0283613",
        "Phenotypes": "delayed aggregation | increased cell-substrate adhesion | decreased cell motility",
    }


@pytest.fixture
def test_row_no_phenotypes():
    """Test row with empty phenotypes."""
    return {
        "Systematic_Name": "DBS0235594",
        "Strain_Descriptor": "CHE10",
        "Associated gene(s)": "cbpC",
        "DDB_G_ID": "DDB_G0283613",
        "Phenotypes": "",
    }


@pytest.fixture
def test_row_multiple_genes():
    """Test row with multiple genes (should be skipped)."""
    return {
        "Systematic_Name": "DBS0235594",
        "Strain_Descriptor": "CHE10",
        "Associated gene(s)": "cbpC|abc123",
        "DDB_G_ID": "DDB_G0283613|DDB_G0000001",
        "Phenotypes": "decreased slug migration",
    }


@pytest.fixture
def basic_dictybase_1(test_row_1, phenotype_mapping_cache):
    """Mock Koza run for Dictybase Gene to Phenotype ingest using KozaTransform."""
    koza_transform = KozaTransform(
        mappings={"dictybase_phenotype_names_to_ids": phenotype_mapping_cache},
        writer=PassthroughWriter(),
        extra_fields={},
    )
    return transform_record(koza_transform, test_row_1)


@pytest.fixture
def basic_dictybase_2(test_row_2, phenotype_mapping_cache):
    """Mock Koza run for second test row."""
    koza_transform = KozaTransform(
        mappings={"dictybase_phenotype_names_to_ids": phenotype_mapping_cache},
        writer=PassthroughWriter(),
        extra_fields={},
    )
    return transform_record(koza_transform, test_row_2)


@pytest.fixture
def result_no_phenotypes(test_row_no_phenotypes, phenotype_mapping_cache):
    """Mock Koza run for row with no phenotypes."""
    koza_transform = KozaTransform(
        mappings={"dictybase_phenotype_names_to_ids": phenotype_mapping_cache},
        writer=PassthroughWriter(),
        extra_fields={},
    )
    return transform_record(koza_transform, test_row_no_phenotypes)


@pytest.fixture
def result_multiple_genes(test_row_multiple_genes, phenotype_mapping_cache):
    """Mock Koza run for row with multiple genes."""
    koza_transform = KozaTransform(
        mappings={"dictybase_phenotype_names_to_ids": phenotype_mapping_cache},
        writer=PassthroughWriter(),
        extra_fields={},
    )
    return transform_record(koza_transform, test_row_multiple_genes)


def test_association_count_two_phenotypes(basic_dictybase_1):
    """Test that two associations are created for two phenotypes."""
    associations = [a for a in basic_dictybase_1 if isinstance(a, GeneToPhenotypicFeatureAssociation)]
    assert len(associations) == 2


def test_association_count_three_phenotypes(basic_dictybase_2):
    """Test that three associations are created for three phenotypes."""
    associations = [a for a in basic_dictybase_2 if isinstance(a, GeneToPhenotypicFeatureAssociation)]
    assert len(associations) == 3


def test_association_subject(basic_dictybase_1):
    """Test association subject (gene ID)."""
    associations = [a for a in basic_dictybase_1 if isinstance(a, GeneToPhenotypicFeatureAssociation)]
    for association in associations:
        assert association.subject == "dictyBase:DDB_G0283613"


def test_association_predicate(basic_dictybase_1):
    """Test association predicate."""
    associations = [a for a in basic_dictybase_1 if isinstance(a, GeneToPhenotypicFeatureAssociation)]
    for association in associations:
        assert association.predicate == "biolink:has_phenotype"


def test_association_objects(basic_dictybase_1):
    """Test association objects (phenotype IDs)."""
    associations = [a for a in basic_dictybase_1 if isinstance(a, GeneToPhenotypicFeatureAssociation)]
    objects = [a.object for a in associations]
    assert "DDPHENO:0000225" in objects
    assert "DDPHENO:0000163" in objects


def test_association_knowledge_source(basic_dictybase_1):
    """Test association knowledge source."""
    associations = [a for a in basic_dictybase_1 if isinstance(a, GeneToPhenotypicFeatureAssociation)]
    for association in associations:
        assert association.primary_knowledge_source == "infores:dictybase"
        assert "infores:monarchinitiative" in association.aggregator_knowledge_source


def test_no_phenotypes_empty_result(result_no_phenotypes):
    """Test that rows with no phenotypes return empty list."""
    assert result_no_phenotypes == []


def test_multiple_genes_skipped(result_multiple_genes):
    """Test that rows with multiple genes are skipped."""
    assert result_multiple_genes == []


# Real data test
@pytest.fixture
def real_data_row():
    """Real example from all-mutants-ddb_g.txt file."""
    return {
        "Systematic_Name": "DBS0235412",
        "Strain_Descriptor": "1C7",
        "Associated gene(s)": "gp130",
        "DDB_G_ID": "DDB_G0279921",
        "Phenotypes": "decreased cell-substrate adhesion | delayed development | increased growth rate",
    }


@pytest.fixture
def real_data_associations(real_data_row, phenotype_mapping_cache):
    """Mock Koza run with real data."""
    koza_transform = KozaTransform(
        mappings={"dictybase_phenotype_names_to_ids": phenotype_mapping_cache},
        writer=PassthroughWriter(),
        extra_fields={},
    )
    return transform_record(koza_transform, real_data_row)


def test_real_data_association_count(real_data_associations):
    """Test with actual data from all-mutants-ddb_g.txt."""
    associations = [a for a in real_data_associations if isinstance(a, GeneToPhenotypicFeatureAssociation)]
    assert len(associations) == 3


def test_real_data_subject(real_data_associations):
    """Test real data subject."""
    associations = [a for a in real_data_associations if isinstance(a, GeneToPhenotypicFeatureAssociation)]
    for association in associations:
        assert association.subject == "dictyBase:DDB_G0279921"


def test_real_data_objects(real_data_associations):
    """Test real data phenotype objects."""
    associations = [a for a in real_data_associations if isinstance(a, GeneToPhenotypicFeatureAssociation)]
    objects = [a.object for a in associations]
    assert "DDPHENO:0000393" in objects
    assert "DDPHENO:0000162" in objects
    assert "DDPHENO:0000171" in objects
