"""Entity Mappers for Gastric Domain Models
Handles CSV/JSON serialization and deserialization for gastric entities.
"""

import json
from datetime import datetime
from typing import Any

import pandas as pd

from apps.surge.core.models.medical import (
    GastricSystem,
    IndependentCellEntity,
    TumorUnit,
)


class GastricEntityMapper:
    """Mapper for converting gastric entities to/from CSV and JSON formats."""

    @staticmethod
    def gastric_system_to_dict(entity: GastricSystem) -> dict[str, Any]:
        """Convert GastricSystem to dictionary."""
        return {
            "system_id": entity.system_id,
            "patient_id": entity.patient_id,
            "primary_region": entity.primary_region,
            "involved_regions": entity.involved_regions,
            "functional_status": entity.functional_status,
            "gastric_emptying_time": entity.gastric_emptying_time,
            "acid_production_level": entity.acid_production_level,
            "wall_thickness_mm": entity.wall_thickness_mm,
            "mucosal_integrity": entity.mucosal_integrity,
            "vascular_supply": entity.vascular_supply,
            "prior_interventions": entity.prior_interventions,
            "anatomical_variants": entity.anatomical_variants,
            "assessment_date": entity.assessment_date.isoformat()
            if entity.assessment_date
            else None,
            "assessed_by": entity.assessed_by,
        }

    @staticmethod
    def dict_to_gastric_system(data: dict[str, Any]) -> GastricSystem:
        """Convert dictionary to GastricSystem."""
        # Handle date conversion
        assessment_date = None
        if data.get("assessment_date"):
            if isinstance(data["assessment_date"], str):
                assessment_date = datetime.fromisoformat(
                    data["assessment_date"].replace("Z", "+00:00")
                )
            else:
                assessment_date = data["assessment_date"]

        # Handle list fields that might be strings
        involved_regions = data.get("involved_regions", [])
        if isinstance(involved_regions, str):
            try:
                involved_regions = json.loads(involved_regions)
            except json.JSONDecodeError:
                involved_regions = [
                    r.strip() for r in involved_regions.split(",") if r.strip()
                ]

        prior_interventions = data.get("prior_interventions", [])
        if isinstance(prior_interventions, str):
            try:
                prior_interventions = json.loads(prior_interventions)
            except json.JSONDecodeError:
                prior_interventions = [
                    i.strip() for i in prior_interventions.split(",") if i.strip()
                ]

        anatomical_variants = data.get("anatomical_variants", [])
        if isinstance(anatomical_variants, str):
            try:
                anatomical_variants = json.loads(anatomical_variants)
            except json.JSONDecodeError:
                anatomical_variants = [
                    v.strip() for v in anatomical_variants.split(",") if v.strip()
                ]

        return GastricSystem(
            system_id=data["system_id"],
            patient_id=data["patient_id"],
            primary_region=data["primary_region"],
            involved_regions=involved_regions,
            functional_status=data["functional_status"],
            gastric_emptying_time=data.get("gastric_emptying_time"),
            acid_production_level=data.get("acid_production_level"),
            wall_thickness_mm=data.get("wall_thickness_mm"),
            mucosal_integrity=data.get("mucosal_integrity"),
            vascular_supply=data.get("vascular_supply"),
            prior_interventions=prior_interventions,
            anatomical_variants=anatomical_variants,
            assessment_date=assessment_date or datetime.now(),
            assessed_by=data.get("assessed_by"),
        )

    @staticmethod
    def tumor_unit_to_dict(entity: TumorUnit) -> dict[str, Any]:
        """Convert TumorUnit to dictionary."""
        return {
            "tumor_id": entity.tumor_id,
            "case_id": entity.case_id,
            "patient_id": entity.patient_id,
            "t_stage": entity.t_stage,
            "n_stage": entity.n_stage,
            "m_stage": entity.m_stage,
            "overall_stage": entity.overall_stage,
            "histology_type": entity.histology_type,
            "tumor_grade": entity.tumor_grade,
            "primary_location": entity.primary_location,
            "tumor_size_cm": entity.tumor_size_cm,
            "depth_of_invasion": entity.depth_of_invasion,
            "lymph_nodes_examined": entity.lymph_nodes_examined,
            "lymph_nodes_positive": entity.lymph_nodes_positive,
            "resection_margin": entity.resection_margin,
            "proximal_margin_cm": entity.proximal_margin_cm,
            "distal_margin_cm": entity.distal_margin_cm,
            "circumferential_margin_mm": entity.circumferential_margin_mm,
            "her2_status": entity.her2_status,
            "her2_score": entity.her2_score,
            "msi_status": entity.msi_status,
            "pdl1_expression": entity.pdl1_expression,
            "ebv_status": entity.ebv_status,
            "molecular_subtype": entity.molecular_subtype,
            "genetic_alterations": entity.genetic_alterations,
            "mutation_burden": entity.mutation_burden,
            "radiological_size_cm": entity.radiological_size_cm,
            "imaging_features": entity.imaging_features,
            "pathology_date": entity.pathology_date.isoformat()
            if entity.pathology_date
            else None,
            "pathologist": entity.pathologist,
            "specimen_type": entity.specimen_type,
        }

    @staticmethod
    def dict_to_tumor_unit(data: dict[str, Any]) -> TumorUnit:
        """Convert dictionary to TumorUnit."""
        # Handle date conversion
        pathology_date = None
        if data.get("pathology_date"):
            if isinstance(data["pathology_date"], str):
                pathology_date = datetime.fromisoformat(
                    data["pathology_date"].replace("Z", "+00:00")
                )
            else:
                pathology_date = data["pathology_date"]

        # Handle list fields
        genetic_alterations = data.get("genetic_alterations", [])
        if isinstance(genetic_alterations, str):
            try:
                genetic_alterations = json.loads(genetic_alterations)
            except json.JSONDecodeError:
                genetic_alterations = [
                    g.strip() for g in genetic_alterations.split(",") if g.strip()
                ]

        imaging_features = data.get("imaging_features", [])
        if isinstance(imaging_features, str):
            try:
                imaging_features = json.loads(imaging_features)
            except json.JSONDecodeError:
                imaging_features = [
                    f.strip() for f in imaging_features.split(",") if f.strip()
                ]

        return TumorUnit(
            tumor_id=data["tumor_id"],
            case_id=data["case_id"],
            patient_id=data["patient_id"],
            t_stage=data["t_stage"],
            n_stage=data["n_stage"],
            m_stage=data["m_stage"],
            overall_stage=data.get("overall_stage"),
            histology_type=data["histology_type"],
            tumor_grade=data["tumor_grade"],
            primary_location=data["primary_location"],
            tumor_size_cm=data.get("tumor_size_cm"),
            depth_of_invasion=data.get("depth_of_invasion"),
            lymph_nodes_examined=data.get("lymph_nodes_examined"),
            lymph_nodes_positive=data.get("lymph_nodes_positive"),
            resection_margin=data.get("resection_margin"),
            proximal_margin_cm=data.get("proximal_margin_cm"),
            distal_margin_cm=data.get("distal_margin_cm"),
            circumferential_margin_mm=data.get("circumferential_margin_mm"),
            her2_status=data.get("her2_status"),
            her2_score=data.get("her2_score"),
            msi_status=data.get("msi_status"),
            pdl1_expression=data.get("pdl1_expression"),
            ebv_status=data.get("ebv_status"),
            molecular_subtype=data.get("molecular_subtype"),
            genetic_alterations=genetic_alterations,
            mutation_burden=data.get("mutation_burden"),
            radiological_size_cm=data.get("radiological_size_cm"),
            imaging_features=imaging_features,
            pathology_date=pathology_date,
            pathologist=data.get("pathologist"),
            specimen_type=data.get("specimen_type"),
        )

    @staticmethod
    def cell_entity_to_dict(entity: IndependentCellEntity) -> dict[str, Any]:
        """Convert IndependentCellEntity to dictionary."""
        return {
            "cell_entity_id": entity.cell_entity_id,
            "tumor_id": entity.tumor_id,
            "sample_id": entity.sample_id,
            "her2_expression": entity.her2_expression,
            "her2_gene_amplification": entity.her2_gene_amplification,
            "her2_fish_ratio": entity.her2_fish_ratio,
            "ki67_percentage": entity.ki67_percentage,
            "mitotic_rate": entity.mitotic_rate,
            "mlh1_expression": entity.mlh1_expression,
            "msh2_expression": entity.msh2_expression,
            "msh6_expression": entity.msh6_expression,
            "pms2_expression": entity.pms2_expression,
            "msi_status": entity.msi_status,
            "pdl1_expression": entity.pdl1_expression,
            "pdl1_cps_score": entity.pdl1_cps_score,
            "cd8_til_density": entity.cd8_til_density,
            "p53_expression": entity.p53_expression,
            "p53_mutation_status": entity.p53_mutation_status,
            "e_cadherin_expression": entity.e_cadherin_expression,
            "beta_catenin_pattern": entity.beta_catenin_pattern,
            "cyclin_d1_expression": entity.cyclin_d1_expression,
            "rb_expression": entity.rb_expression,
            "cell_morphology": entity.cell_morphology,
            "tissue_architecture": entity.tissue_architecture,
            "stromal_reaction": entity.stromal_reaction,
            "staining_method": entity.staining_method,
            "antibody_clone": entity.antibody_clone,
            "analysis_date": entity.analysis_date.isoformat()
            if entity.analysis_date
            else None,
            "analyzed_by": entity.analyzed_by,
            "tissue_quality": entity.tissue_quality,
            "fixation_time": entity.fixation_time,
            "processing_protocol": entity.processing_protocol,
        }

    @staticmethod
    def dict_to_cell_entity(data: dict[str, Any]) -> IndependentCellEntity:
        """Convert dictionary to IndependentCellEntity."""
        # Handle date conversion
        analysis_date = None
        if data.get("analysis_date"):
            if isinstance(data["analysis_date"], str):
                analysis_date = datetime.fromisoformat(
                    data["analysis_date"].replace("Z", "+00:00")
                )
            else:
                analysis_date = data["analysis_date"]

        return IndependentCellEntity(
            cell_entity_id=data["cell_entity_id"],
            tumor_id=data["tumor_id"],
            sample_id=data.get("sample_id"),
            her2_expression=data.get("her2_expression"),
            her2_gene_amplification=data.get("her2_gene_amplification"),
            her2_fish_ratio=data.get("her2_fish_ratio"),
            ki67_percentage=data.get("ki67_percentage"),
            mitotic_rate=data.get("mitotic_rate"),
            mlh1_expression=data.get("mlh1_expression"),
            msh2_expression=data.get("msh2_expression"),
            msh6_expression=data.get("msh6_expression"),
            pms2_expression=data.get("pms2_expression"),
            msi_status=data.get("msi_status"),
            pdl1_expression=data.get("pdl1_expression"),
            pdl1_cps_score=data.get("pdl1_cps_score"),
            cd8_til_density=data.get("cd8_til_density"),
            p53_expression=data.get("p53_expression"),
            p53_mutation_status=data.get("p53_mutation_status"),
            e_cadherin_expression=data.get("e_cadherin_expression"),
            beta_catenin_pattern=data.get("beta_catenin_pattern"),
            cyclin_d1_expression=data.get("cyclin_d1_expression"),
            rb_expression=data.get("rb_expression"),
            cell_morphology=data.get("cell_morphology"),
            tissue_architecture=data.get("tissue_architecture"),
            stromal_reaction=data.get("stromal_reaction"),
            staining_method=data.get("staining_method"),
            antibody_clone=data.get("antibody_clone"),
            analysis_date=analysis_date or datetime.now(),
            analyzed_by=data.get("analyzed_by"),
            tissue_quality=data.get("tissue_quality"),
            fixation_time=data.get("fixation_time"),
            processing_protocol=data.get("processing_protocol"),
        )

    @classmethod
    def entities_to_csv(
        cls,
        entities: list[GastricSystem | TumorUnit | IndependentCellEntity],
        filepath: str,
    ) -> None:
        """Export entities to CSV file."""
        if not entities:
            return

        entity_type = type(entities[0])

        if entity_type == GastricSystem:
            data = [cls.gastric_system_to_dict(entity) for entity in entities]
        elif entity_type == TumorUnit:
            data = [cls.tumor_unit_to_dict(entity) for entity in entities]
        elif entity_type == IndependentCellEntity:
            data = [cls.cell_entity_to_dict(entity) for entity in entities]
        else:
            msg = f"Unsupported entity type: {entity_type}"
            raise ValueError(msg)

        df = pd.DataFrame(data)

        # Convert list columns to JSON strings for CSV compatibility
        for col in df.columns:
            if df[col].dtype == "object":
                df[col] = df[col].apply(
                    lambda x: json.dumps(x) if isinstance(x, list) else x
                )

        df.to_csv(filepath, index=False)

    @classmethod
    def csv_to_entities(
        cls, filepath: str, entity_type: str
    ) -> list[GastricSystem | TumorUnit | IndependentCellEntity]:
        """Import entities from CSV file."""
        df = pd.read_csv(filepath)
        data = df.fillna("").to_dict("records")

        if entity_type.lower() == "gastric_system":
            return [cls.dict_to_gastric_system(row) for row in data]
        if entity_type.lower() == "tumor_unit":
            return [cls.dict_to_tumor_unit(row) for row in data]
        if entity_type.lower() == "cell_entity":
            return [cls.dict_to_cell_entity(row) for row in data]
        msg = f"Unsupported entity type: {entity_type}"
        raise ValueError(msg)

    @classmethod
    def entities_to_json(
        cls,
        entities: list[GastricSystem | TumorUnit | IndependentCellEntity],
        filepath: str,
    ) -> None:
        """Export entities to JSON file."""
        if not entities:
            return

        entity_type = type(entities[0])

        if entity_type == GastricSystem:
            data = [cls.gastric_system_to_dict(entity) for entity in entities]
        elif entity_type == TumorUnit:
            data = [cls.tumor_unit_to_dict(entity) for entity in entities]
        elif entity_type == IndependentCellEntity:
            data = [cls.cell_entity_to_dict(entity) for entity in entities]
        else:
            msg = f"Unsupported entity type: {entity_type}"
            raise ValueError(msg)

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2, default=str)

    @classmethod
    def json_to_entities(
        cls, filepath: str, entity_type: str
    ) -> list[GastricSystem | TumorUnit | IndependentCellEntity]:
        """Import entities from JSON file."""
        with open(filepath) as f:
            data = json.load(f)

        if entity_type.lower() == "gastric_system":
            return [cls.dict_to_gastric_system(row) for row in data]
        if entity_type.lower() == "tumor_unit":
            return [cls.dict_to_tumor_unit(row) for row in data]
        if entity_type.lower() == "cell_entity":
            return [cls.dict_to_cell_entity(row) for row in data]
        msg = f"Unsupported entity type: {entity_type}"
        raise ValueError(msg)
