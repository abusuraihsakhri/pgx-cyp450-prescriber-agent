"""
Multi-Gene Pharmacogenomic Panel Interpreter for PGx CYP450 Prescriber Agent.
Guided step-by-step interpretation of multi-gene pharmacogenomic panels
with CPIC level evidence ratings and combined phenotype analysis.

Domain: Pharmacogenomics
Standard: CPIC Level A Gene-Drug Guidelines
Author: Dr. Abu Suraih Sakhri
"""
import datetime
import uuid
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class StarAlleleFunction(str, Enum):
    """Functional classification of CYP star alleles."""
    NO_FUNCTION = "NO_FUNCTION"
    DECREASED_FUNCTION = "DECREASED_FUNCTION"
    NORMAL_FUNCTION = "NORMAL_FUNCTION"
    INCREASED_FUNCTION = "INCREASED_FUNCTION"
    UNKNOWN = "UNKNOWN"


class MetabolizerPhenotype(str, Enum):
    POOR = "PM"
    INTERMEDIATE = "IM"
    NORMAL = "NM"
    RAPID = "RM"
    ULTRARAPID = "UM"
    INDETERMINATE = "INDETERMINATE"


@dataclass
class StarAllele:
    """Represents a single star allele with functional annotation."""
    allele_name: str  # e.g., "*1", "*2", "*4"
    gene: str
    function: StarAlleleFunction
    activity_score: float  # 0.0, 0.5, 1.0, 2.0
    population_frequency: Optional[float] = None
    notes: str = ""


@dataclass
class GeneResult:
    """Interpretation result for a single gene."""
    gene: str
    diplotype: str  # e.g., "*1/*4"
    allele_1: StarAllele
    allele_2: StarAllele
    activity_score: Optional[float]
    phenotype: MetabolizerPhenotype
    phenotype_detail: str
    confidence: str  # HIGH, MODERATE, LOW
    affected_drugs: List[str]
    clinical_significance: str


@dataclass
class PanelInterpretation:
    """Complete multi-gene panel interpretation result."""
    interpretation_id: str
    genes_tested: List[str]
    gene_results: Dict[str, GeneResult]
    combined_drug_alerts: List[Dict[str, Any]]
    panel_confidence: str
    summary: str
    timestamp: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "interpretation_id": self.interpretation_id,
            "genes_tested": self.genes_tested,
            "gene_results": {g: self._gr_to_dict(r) for g, r in self.gene_results.items()},
            "combined_drug_alerts": self.combined_drug_alerts,
            "panel_confidence": self.panel_confidence,
            "summary": self.summary,
            "timestamp": self.timestamp,
        }

    @staticmethod
    def _gr_to_dict(gr: GeneResult) -> Dict[str, Any]:
        return {
            "gene": gr.gene,
            "diplotype": gr.diplotype,
            "activity_score": gr.activity_score,
            "phenotype": gr.phenotype.value,
            "phenotype_detail": gr.phenotype_detail,
            "confidence": gr.confidence,
            "affected_drugs": gr.affected_drugs,
            "clinical_significance": gr.clinical_significance,
        }


class AlleleFunctionDatabase:
    """Database of CYP star allele functional annotations."""

    ALLELE_DB: Dict[str, Dict[str, StarAllele]] = {
        "CYP2D6": {
            "*1": StarAllele("*1", "CYP2D6", StarAlleleFunction.NORMAL_FUNCTION, 1.0, 0.36, "Wild-type normal function"),
            "*2": StarAllele("*2", "CYP2D6", StarAlleleFunction.NORMAL_FUNCTION, 1.0, 0.28, "Normal function variant"),
            "*3": StarAllele("*3", "CYP2D6", StarAlleleFunction.NO_FUNCTION, 0.0, 0.02, "Frameshift; no enzyme activity"),
            "*4": StarAllele("*4", "CYP2D6", StarAlleleFunction.NO_FUNCTION, 0.0, 0.20, "Splice defect; most common PM allele in Europeans"),
            "*5": StarAllele("*5", "CYP2D6", StarAlleleFunction.NO_FUNCTION, 0.0, 0.04, "Gene deletion"),
            "*6": StarAllele("*6", "CYP2D6", StarAlleleFunction.NO_FUNCTION, 0.0, 0.01, "Frameshift; no enzyme activity"),
            "*10": StarAllele("*10", "CYP2D6", StarAlleleFunction.DECREASED_FUNCTION, 0.25, 0.04, "Unstable protein; common in East Asians"),
            "*17": StarAllele("*17", "CYP2D6", StarAlleleFunction.DECREASED_FUNCTION, 0.5, 0.04, "Decreased affinity for substrates"),
            "*41": StarAllele("*41", "CYP2D6", StarAlleleFunction.DECREASED_FUNCTION, 0.5, 0.09, "Splice defect; reduced expression"),
        },
        "CYP2C19": {
            "*1": StarAllele("*1", "CYP2C19", StarAlleleFunction.NORMAL_FUNCTION, 1.0, 0.60, "Wild-type normal function"),
            "*2": StarAllele("*2", "CYP2C19", StarAlleleFunction.NO_FUNCTION, 0.0, 0.15, "Splice defect; most common loss-of-function allele"),
            "*3": StarAllele("*3", "CYP2C19", StarAlleleFunction.NO_FUNCTION, 0.0, 0.05, "Premature stop codon; common in East Asians"),
            "*4": StarAllele("*4", "CYP2C19", StarAlleleFunction.NO_FUNCTION, 0.0, 0.01, "Initiation codon variant"),
            "*8": StarAllele("*8", "CYP2C19", StarAlleleFunction.NO_FUNCTION, 0.0, 0.01, "Decreased enzyme activity"),
            "*17": StarAllele("*17", "CYP2C19", StarAlleleFunction.INCREASED_FUNCTION, 2.0, 0.21, "Increased transcription; ultrarapid metabolism"),
        },
        "CYP2C9": {
            "*1": StarAllele("*1", "CYP2C9", StarAlleleFunction.NORMAL_FUNCTION, 1.0, 0.79, "Wild-type normal function"),
            "*2": StarAllele("*2", "CYP2C9", StarAlleleFunction.DECREASED_FUNCTION, 0.5, 0.12, "Decreased catalytic activity"),
            "*3": StarAllele("*3", "CYP2C9", StarAlleleFunction.DECREASED_FUNCTION, 0.5, 0.07, "Significantly decreased activity"),
            "*5": StarAllele("*5", "CYP2C9", StarAlleleFunction.DECREASED_FUNCTION, 0.5, 0.02, "Decreased activity; African ancestry"),
            "*6": StarAllele("*6", "CYP2C9", StarAlleleFunction.NO_FUNCTION, 0.0, 0.01, "Frameshift; no enzyme activity"),
        },
        "SLCO1B1": {
            "*1A": StarAllele("*1A", "SLCO1B1", StarAlleleFunction.NORMAL_FUNCTION, 1.0, 0.55, "Wild-type normal function"),
            "*1B": StarAllele("*1B", "SLCO1B1", StarAlleleFunction.NORMAL_FUNCTION, 1.0, 0.25, "Intron variant; normal function"),
            "*5": StarAllele("*5", "SLCO1B1", StarAlleleFunction.DECREASED_FUNCTION, 0.5, 0.15, "Decreased transport; increased statin levels"),
            "*15": StarAllele("*15", "SLCO1B1", StarAlleleFunction.DECREASED_FUNCTION, 0.5, 0.05, "Combined *1B + *5; decreased function"),
        },
        "CYP3A5": {
            "*1": StarAllele("*1", "CYP3A5", StarAlleleFunction.NORMAL_FUNCTION, 1.0, 0.35, "Expresser allele; functional CYP3A5"),
            "*3": StarAllele("*3", "CYP3A5", StarAlleleFunction.NO_FUNCTION, 0.0, 0.60, "Splice defect; non-expresser; most common in Europeans"),
            "*6": StarAllele("*6", "CYP3A5", StarAlleleFunction.NO_FUNCTION, 0.0, 0.10, "Frameshift; non-expresser; common in Africans"),
            "*7": StarAllele("*7", "CYP3A5", StarAlleleFunction.NO_FUNCTION, 0.0, 0.05, "Splice defect; non-expresser"),
        },
    }

    @classmethod
    def get_allele(cls, gene: str, allele_name: str) -> Optional[StarAllele]:
        gene_upper = gene.upper().strip()
        if gene_upper in cls.ALLELE_DB:
            return cls.ALLELE_DB[gene_upper].get(allele_name)
        return None

    @classmethod
    def get_gene_alleles(cls, gene: str) -> Dict[str, StarAllele]:
        return cls.ALLELE_DB.get(gene.upper().strip(), {})


class PanelInterpreter:
    """
    Guided step-by-step interpreter for multi-gene pharmacogenomic panels.
    Processes diplotypes for multiple genes and generates combined interpretation.
    """

    # Gene-drug associations
    GENE_DRUG_MAP = {
        "CYP2D6": ["codeine", "tramadol", "tamoxifen", "amitriptyline", "nortriptyline", "fluoxetine", "paroxetine", "metoprolol", "ondansetron"],
        "CYP2C19": ["clopidogrel", "voriconazole", "escitalopram", "citalopram", "sertraline", "omeprazole", "pantoprazole"],
        "CYP2C9": ["warfarin", "phenytoin", "celecoxib", "losartan", "fluvastatin"],
        "SLCO1B1": ["simvastatin", "atorvastatin", "rosuvastatin", "pravastatin"],
        "CYP3A5": ["tacrolimus", "sirolimus", "everolimus"],
    }

    def __init__(self):
        self.db = AlleleFunctionDatabase()

    def interpret_diplotype(self, gene: str, allele_1_name: str, allele_2_name: str) -> Optional[GeneResult]:
        """
        Interpret a single gene diplotype.

        Args:
            gene: Gene name (e.g., "CYP2D6")
            allele_1_name: First allele (e.g., "*1")
            allele_2_name: Second allele (e.g., "*4")

        Returns:
            GeneResult with phenotype interpretation, or None if alleles not found
        """
        gene = gene.upper().strip()
        allele_1_name = allele_1_name.strip()
        allele_2_name = allele_2_name.strip()
        a1 = self.db.get_allele(gene, allele_1_name)
        a2 = self.db.get_allele(gene, allele_2_name)
        if a1 is None or a2 is None:
            return None

        # Only CYP2D6 has a validated additive activity-score convention here.
        # Other CYPs and transporters require gene-specific translation tables.
        activity_score = a1.activity_score + a2.activity_score if gene == "CYP2D6" else None
        phenotype = self._interpret_gene(gene, a1, a2, activity_score)
        confidence = "LOW" if phenotype == MetabolizerPhenotype.INDETERMINATE else (
            "MODERATE" if StarAlleleFunction.DECREASED_FUNCTION in (a1.function, a2.function) else "HIGH"
        )
        detail = (
            f"{phenotype.value} (CYP2D6 activity score: {activity_score:g})"
            if activity_score is not None else
            f"{phenotype.value} (gene-specific function classification; no additive activity score)"
        )
        return GeneResult(
            gene=gene,
            diplotype=f"{allele_1_name}/{allele_2_name}",
            allele_1=a1,
            allele_2=a2,
            activity_score=activity_score,
            phenotype=phenotype,
            phenotype_detail=detail,
            confidence=confidence,
            affected_drugs=list(self.GENE_DRUG_MAP.get(gene, [])),
            clinical_significance=self._generate_significance(gene, phenotype, activity_score),
        )

    def interpret_panel(
        self,
        panel: Dict[str, Tuple[str, str]],
    ) -> PanelInterpretation:
        """
        Interpret a multi-gene pharmacogenomic panel.

        Args:
            panel: Dict mapping gene names to (allele_1, allele_2) tuples
                e.g., {"CYP2D6": ("*1", "*4"), "CYP2C19": ("*1", "*1")}

        Returns:
            PanelInterpretation with combined results
        """
        # This is a limited, educational interaction flagger. It must never
        # extrapolate from phenotype alone to a prescribing instruction.
        from .drug_gene_alert_engine import DrugGeneInteractionDatabase, MetabolizerStatus
        interactions = DrugGeneInteractionDatabase()
        phenotype_codes = {
            MetabolizerPhenotype.POOR: MetabolizerStatus.POOR,
            MetabolizerPhenotype.INTERMEDIATE: MetabolizerStatus.INTERMEDIATE,
            MetabolizerPhenotype.NORMAL: MetabolizerStatus.NORMAL,
            MetabolizerPhenotype.RAPID: MetabolizerStatus.RAPID,
            MetabolizerPhenotype.ULTRARAPID: MetabolizerStatus.ULTRARAPID,
        }
        gene_results = {}
        combined_alerts = []
        overall_confidence = "HIGH"

        for gene, (a1, a2) in panel.items():
            result = self.interpret_diplotype(gene, a1, a2)
            if result is None:
                overall_confidence = "LOW"
                combined_alerts.append({
                    "gene": str(gene).upper(),
                    "severity": "REVIEW",
                    "message": "Unsupported allele or gene; phenotype was not assigned.",
                })
                continue
            gene_results[result.gene] = result
            if result.confidence == "LOW":
                overall_confidence = "LOW"
            elif result.confidence == "MODERATE" and overall_confidence != "LOW":
                overall_confidence = "MODERATE"

            status = phenotype_codes.get(result.phenotype)
            if result.gene not in ("CYP2D6", "CYP2C19") or status is None:
                continue
            for drug in result.affected_drugs:
                for interaction in interactions.lookup_by_drug(drug):
                    if interaction.gene != result.gene or status not in interaction.affected_phenotypes:
                        continue
                    combined_alerts.append({
                        "alert_id": str(uuid.uuid4())[:8],
                        "gene": result.gene,
                        "drug": drug,
                        "phenotype": result.phenotype.value,
                        "severity": "REVIEW",
                        "message": "Potential gene-drug interaction: verify the latest gene-drug-specific guideline with a qualified clinician. No dose is determined.",
                    })

        genes_tested = list(gene_results.keys())
        summary = self._generate_panel_summary(gene_results)

        return PanelInterpretation(
            interpretation_id=str(uuid.uuid4())[:8],
            genes_tested=genes_tested,
            gene_results=gene_results,
            combined_drug_alerts=combined_alerts,
            panel_confidence=overall_confidence,
            summary=summary,
        )

    @staticmethod
    def _interpret_gene(
        gene: str, a1: StarAllele, a2: StarAllele, score: Optional[float],
    ) -> MetabolizerPhenotype:
        if gene == "CYP2D6":
            if score == 0:
                return MetabolizerPhenotype.POOR
            if score < 1.25:
                return MetabolizerPhenotype.INTERMEDIATE
            if score <= 2.25:
                return MetabolizerPhenotype.NORMAL
            return MetabolizerPhenotype.ULTRARAPID
        if gene == "CYP2C19":
            functions = (a1.function, a2.function)
            no = functions.count(StarAlleleFunction.NO_FUNCTION)
            increased = functions.count(StarAlleleFunction.INCREASED_FUNCTION)
            normal = functions.count(StarAlleleFunction.NORMAL_FUNCTION)
            if no == 2:
                return MetabolizerPhenotype.POOR
            if no == 1:
                return MetabolizerPhenotype.INTERMEDIATE
            if increased == 2:
                return MetabolizerPhenotype.ULTRARAPID
            if increased == 1 and normal == 1:
                return MetabolizerPhenotype.RAPID
            if normal == 2:
                return MetabolizerPhenotype.NORMAL
        # CYP2C9, CYP3A5 and SLCO1B1 do not share CYP2D6
        # metabolizer-score thresholds; fail closed instead of misclassifying.
        return MetabolizerPhenotype.INDETERMINATE

    @staticmethod
    def _generate_significance(
        gene: str, phenotype: MetabolizerPhenotype, score: Optional[float],
    ) -> str:
        if phenotype == MetabolizerPhenotype.INDETERMINATE:
            return (
                f"{gene}: No validated translation implemented for this diplotype. "
                "Consult a current gene-specific interpretation; do not infer dosing."
            )
        return (
            f"{gene} predicted {phenotype.value} phenotype. "
            "Interpretation is limited to the listed alleles and does not account "
            "for structural variation, phenoconversion, or laboratory assay limitations. "
            "Confirm any gene-drug prescribing action against current guidance."
        )

    @staticmethod
    def _generate_panel_summary(gene_results: Dict[str, GeneResult]) -> str:
        """Generate a human-readable panel summary."""
        lines = ["Pharmacogenomic Panel Interpretation Summary", "=" * 50]
        for gene, result in gene_results.items():
            lines.append(f"  {gene}: {result.diplotype} -> {result.phenotype.value}" + (f" (AS={result.activity_score:g})" if result.activity_score is not None else " (score not applicable)"))
            if result.phenotype == MetabolizerPhenotype.INDETERMINATE:
                lines.append(f"    REVIEW REQUIRED: {result.clinical_significance}")
        return "\n".join(lines)
