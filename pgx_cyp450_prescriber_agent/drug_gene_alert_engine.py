"""
Drug-Gene Interaction Alert Engine for PGx CYP450 Prescriber Agent.
Real-time clinical decision support alerts when prescribing medications
with pharmacogenomic implications based on CPIC guidelines.

Domain: Pharmacogenomics
Standard: CPIC Level A / FDA Table of Pharmacogenomic Biomarkers
Author: Dr. Abu Suraih Sakhri
"""
import datetime
import uuid
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class AlertSeverity(str, Enum):
    INFO = "INFO"
    ACTIONABLE = "ACTIONABLE"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class MetabolizerStatus(str, Enum):
    POOR = "PM"
    INTERMEDIATE = "IM"
    NORMAL = "NM"
    RAPID = "RM"
    ULTRARAPID = "UM"


class CPICLevel(str, Enum):
    LEVEL_A = "1A"  # Genetic information should be used to change prescribing
    LEVEL_B = "1B"  # Alternative therapies/dosing unclear
    LEVEL_C = "2C"  # Insufficient evidence


@dataclass
class DrugGeneInteraction:
    """Represents a single drug-gene interaction from CPIC/FDA guidelines."""
    drug_name: str
    gene: str
    cpic_level: CPICLevel
    affected_phenotypes: List[MetabolizerStatus]
    clinical_implication: str
    recommended_action: str
    alternative_drugs: List[str] = field(default_factory=list)
    dose_adjustment: Optional[str] = None
    fda_table_ref: Optional[str] = None
    evidence_sources: List[str] = field(default_factory=list)


@dataclass
class PrescribingAlert:
    """Alert generated when a prescription has PGx implications."""
    alert_id: str
    severity: AlertSeverity
    drug_name: str
    gene: str
    phenotype: MetabolizerStatus
    cpic_level: CPICLevel
    clinical_implication: str
    recommended_action: str
    alternative_drugs: List[str]
    dose_adjustment: Optional[str]
    timestamp: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "severity": self.severity.value,
            "drug_name": self.drug_name,
            "gene": self.gene,
            "phenotype": self.phenotype.value,
            "cpic_level": self.cpic_level.value,
            "clinical_implication": self.clinical_implication,
            "recommended_action": self.recommended_action,
            "alternative_drugs": self.alternative_drugs,
            "dose_adjustment": self.dose_adjustment,
            "timestamp": self.timestamp,
        }


class DrugGeneInteractionDatabase:
    """Knowledge base of CPIC and FDA drug-gene interactions."""

    def __init__(self):
        self._interactions: List[DrugGeneInteraction] = self._load_default_interactions()

    def _load_default_interactions(self) -> List[DrugGeneInteraction]:
        """Load curated CPIC Level A drug-gene interactions."""
        return [
            DrugGeneInteraction(
                drug_name="clopidogrel",
                gene="CYP2C19",
                cpic_level=CPICLevel.LEVEL_A,
                affected_phenotypes=[MetabolizerStatus.POOR, MetabolizerStatus.INTERMEDIATE],
                clinical_implication="Reduced conversion to active metabolite; decreased platelet inhibition",
                recommended_action="Use alternative antiplatelet agent (prasugrel, ticagrelor)",
                alternative_drugs=["prasugrel", "ticagrelor"],
                fda_table_ref="FDA Table - Clopidogrel/CYP2C19",
                evidence_sources=["CPIC 2022 Guideline", "FDA Black Box Warning"],
            ),
            DrugGeneInteraction(
                drug_name="codeine",
                gene="CYP2D6",
                cpic_level=CPICLevel.LEVEL_A,
                affected_phenotypes=[MetabolizerStatus.POOR, MetabolizerStatus.ULTRARAPID],
                clinical_implication="PM: No analgesic effect; UM: Risk of toxicity (respiratory depression)",
                recommended_action="PM: Use alternative analgesic; UM: Use non-codeine opioid or non-opioid",
                alternative_drugs=["morphine", "acetaminophen"],
                dose_adjustment="PM: No dose effective; UM: Avoid codeine entirely",
                fda_table_ref="FDA Table - Codeine/CYP2D6",
                evidence_sources=["CPIC 2019 Guideline", "FDA Contraindication"],
            ),
            DrugGeneInteraction(
                drug_name="warfarin",
                gene="CYP2C9",
                cpic_level=CPICLevel.LEVEL_A,
                affected_phenotypes=[MetabolizerStatus.POOR, MetabolizerStatus.INTERMEDIATE],
                clinical_implication="Decreased warfarin clearance; increased bleeding risk",
                recommended_action="Consider lower starting dose; increase INR monitoring frequency",
                alternative_drugs=["apixaban", "rivaroxaban", "edoxaban"],
                dose_adjustment="No dose can be calculated from CYP2C9 phenotype alone; use a validated multigene algorithm and INR monitoring.",
                fda_table_ref="FDA Table - Warfarin/CYP2C9+VKORC1",
                evidence_sources=["CPIC 2017 Guideline", "FDA Label Update"],
            ),
            DrugGeneInteraction(
                drug_name="simvastatin",
                gene="SLCO1B1",
                cpic_level=CPICLevel.LEVEL_A,
                affected_phenotypes=[MetabolizerStatus.POOR],
                clinical_implication="Increased plasma concentration; elevated myopathy risk",
                recommended_action="Prescribe lower dose (20mg) or use alternative statin",
                alternative_drugs=["rosuvastatin", "pravastatin", "atorvastatin"],
                dose_adjustment="Use current SLCO1B1 function-based statin recommendations; CYP metabolizer labels do not apply.",
                fda_table_ref="FDA Table - Simvastatin/SLCO1B1",
                evidence_sources=["CPIC 2022 Guideline"],
            ),
            DrugGeneInteraction(
                drug_name="amitriptyline",
                gene="CYP2D6",
                cpic_level=CPICLevel.LEVEL_A,
                affected_phenotypes=[MetabolizerStatus.POOR, MetabolizerStatus.ULTRARAPID],
                clinical_implication="PM: Elevated drug levels, increased side effects; UM: Subtherapeutic levels",
                recommended_action="PM: Reduce dose 50% or use alternative; UM: Increase dose or use alternative",
                alternative_drugs=["desipramine", "nortriptyline", "escitalopram"],
                dose_adjustment="Consult current CYP2D6/CYP2C19 tricyclic antidepressant guidance and drug monitoring.",
                evidence_sources=["CPIC 2016 Guideline"],
            ),
            DrugGeneInteraction(
                drug_name="tacrolimus",
                gene="CYP3A5",
                cpic_level=CPICLevel.LEVEL_A,
                affected_phenotypes=[MetabolizerStatus.NORMAL, MetabolizerStatus.RAPID],
                clinical_implication="Expressers require higher doses to achieve target trough levels",
                recommended_action="CYP3A5 expressers: 1.5-2x standard starting dose",
                alternative_drugs=["cyclosporine", "sirolimus", "everolimus"],
                dose_adjustment="Consider genotype-guided initial dosing only within an appropriate protocol and therapeutic drug monitoring.",
                evidence_sources=["CPIC 2022 Guideline"],
            ),
        ]

    def get_all_interactions(self) -> List[DrugGeneInteraction]:
        return self._interactions

    def lookup_by_drug(self, drug_name: str) -> List[DrugGeneInteraction]:
        drug_lower = drug_name.lower().strip()
        return [i for i in self._interactions if i.drug_name.lower() == drug_lower]

    def lookup_by_gene(self, gene: str) -> List[DrugGeneInteraction]:
        gene_upper = gene.upper().strip()
        return [i for i in self._interactions if i.gene.upper() == gene_upper]

    def add_interaction(self, interaction: DrugGeneInteraction) -> None:
        self._interactions.append(interaction)


class DrugGeneAlertEngine:
    """
    Real-time clinical decision support engine that generates alerts
    when prescribing medications with pharmacogenomic implications.
    """

    def __init__(self, db: Optional[DrugGeneInteractionDatabase] = None):
        self.db = db or DrugGeneInteractionDatabase()
        self.alert_history: List[PrescribingAlert] = []

    @staticmethod
    def _normalise_phenotypes(
        patient_phenotypes: Dict[str, MetabolizerStatus],
    ) -> Dict[str, MetabolizerStatus]:
        """Normalize gene names and validate enum/string phenotype codes."""
        normalized = {}
        for gene, value in patient_phenotypes.items():
            normalized[str(gene).upper().strip()] = (
                value if isinstance(value, MetabolizerStatus)
                else MetabolizerStatus(str(value).upper().strip())
            )
        return normalized

    def check_prescription(
        self,
        drug_name: str,
        patient_phenotypes: Dict[str, MetabolizerStatus],
    ) -> List[PrescribingAlert]:
        """
        Check a drug prescription against patient's pharmacogenomic profile.

        Args:
            drug_name: The medication being prescribed
            patient_phenotypes: Dict mapping gene names to metabolizer status
                e.g., {"CYP2D6": MetabolizerStatus.POOR, "CYP2C19": MetabolizerStatus.NORMAL}

        Returns:
            List of PrescribingAlert objects for any matching interactions
        """
        alerts = []
        patient_phenotypes = self._normalise_phenotypes(patient_phenotypes)
        interactions = self.db.lookup_by_drug(drug_name)

        for interaction in interactions:
            gene = interaction.gene
            if gene not in patient_phenotypes:
                continue

            phenotype = patient_phenotypes[gene]
            if phenotype not in interaction.affected_phenotypes:
                continue

            severity = self._determine_severity(interaction, phenotype)

            alert = PrescribingAlert(
                alert_id=str(uuid.uuid4())[:8],
                severity=severity,
                drug_name=drug_name,
                gene=gene,
                phenotype=phenotype,
                cpic_level=interaction.cpic_level,
                clinical_implication=interaction.clinical_implication,
                recommended_action=interaction.recommended_action,
                alternative_drugs=interaction.alternative_drugs,
                dose_adjustment=interaction.dose_adjustment,
            )
            alerts.append(alert)
            self.alert_history.append(alert)

        return alerts

    def check_medication_list(
        self,
        medications: List[str],
        patient_phenotypes: Dict[str, MetabolizerStatus],
    ) -> Dict[str, List[PrescribingAlert]]:
        """
        Check an entire medication list against patient's PGx profile.

        Returns:
            Dict mapping drug names to their alerts (only drugs with alerts)
        """
        results = {}
        for drug in medications:
            drug_alerts = self.check_prescription(drug, patient_phenotypes)
            if drug_alerts:
                results[drug] = drug_alerts
        return results

    def get_safe_alternatives(
        self,
        drug_name: str,
        patient_phenotypes: Dict[str, MetabolizerStatus],
    ) -> List[str]:
        """Return candidate alternatives; NOT a safety or suitability assessment.

        These static examples are not screened for comorbidities, other gene-drug
        interactions, interactions with current therapy, or contraindications.
        """
        patient_phenotypes = self._normalise_phenotypes(patient_phenotypes)
        interactions = self.db.lookup_by_drug(drug_name)
        alternatives = set()
        for interaction in interactions:
            gene = interaction.gene
            if gene in patient_phenotypes:
                phenotype = patient_phenotypes[gene]
                if phenotype in interaction.affected_phenotypes:
                    alternatives.update(interaction.alternative_drugs)
        return sorted(alternatives)

    def get_alert_summary(self) -> Dict[str, Any]:
        """Get summary statistics of all alerts generated."""
        total = len(self.alert_history)
        by_severity = {}
        by_gene = {}
        by_drug = {}

        for alert in self.alert_history:
            by_severity[alert.severity.value] = by_severity.get(alert.severity.value, 0) + 1
            by_gene[alert.gene] = by_gene.get(alert.gene, 0) + 1
            by_drug[alert.drug_name] = by_drug.get(alert.drug_name, 0) + 1

        return {
            "total_alerts": total,
            "by_severity": by_severity,
            "by_gene": by_gene,
            "by_drug": by_drug,
        }

    @staticmethod
    def _determine_severity(interaction: DrugGeneInteraction, phenotype: MetabolizerStatus) -> AlertSeverity:
        """Determine alert severity based on interaction and phenotype."""
        if interaction.cpic_level == CPICLevel.LEVEL_A:
            # A phenotype alone cannot establish a clinical emergency.
            # Only this specific well-known toxicity scenario is distinguished.
            if interaction.drug_name == "codeine" and phenotype == MetabolizerStatus.ULTRARAPID:
                return AlertSeverity.CRITICAL
            return AlertSeverity.WARNING
        elif interaction.cpic_level == CPICLevel.LEVEL_B:
            return AlertSeverity.ACTIONABLE
        return AlertSeverity.INFO
