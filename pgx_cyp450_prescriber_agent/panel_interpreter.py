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
    activity_score: float
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
            "*10": StarAllele("*10", "CYP2D6", StarAlleleFunction.DECREASED_FUNCTION, 0.5, 0.04, "Unstable protein; common in East Asians"),
            "*17": StarAllele("*17", "CYP2D6", StarAlleleFunction.DECREASED_FUNCTION, 0.5, 0.04, "Decreased affinity for substrates"),
            "*41": StarAllele("*41", "CYP2D6", StarAlleleFunction.DECREASED_FUNCTION, 0.5, 0.09, "Splice defect; reduced expression"),
            "*xN": StarAllele("*xN", "CYP2D6", StarAlleleFunction.INCREASED_FUNCTION, 2.0, 0.02, "Gene duplication; ultrarapid metabolism"),
        },
        "CYP2C19": {
            "*1": StarAllele("*1", "CYP2C19", StarAlleleFunction.NORMAL_FUNCTION, 1.0, 0.60, "Wild-type normal function"),
            "*2": StarAllele("*2", "CYP2C19", StarAlleleFunction.NO_FUNCTION, 0.0, 0.15, "Splice defect; most common loss-of-function allele"),
            "*3": StarAllele("*3", "CYP2C19", StarAlleleFunction.NO_FUNCTION, 0.0, 0.05, "Premature stop codon; common in East Asians"),
            "*4": StarAllele("*4", "CYP2C19", StarAlleleFunction.NO_FUNCTION, 0.0, 0.01, "Initiation codon variant"),
            "*8": StarAllele("*8", "CYP2C19", StarAlleleFunction.DECREASED_FUNCTION, 0.5, 0.01, "Decreased enzyme activity"),
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

    # Activity score to phenotype mapping per CPIC
    PHENOTYPE_MAP = {
        0.0: MetabolizerPhenotype.POOR,
        0.25: MetabolizerPhenotype.INTERMEDIATE,
        0.5: MetabolizerPhenotype.INTERMEDIATE,
        1.0: MetabolizerPhenotype.INTERMEDIATE,
        1.25: MetabolizerPhenotype.NORMAL,
        1.5: MetabolizerPhenotype.NORMAL,
        2.0: MetabolizerPhenotype.NORMAL,
        2.5: MetabolizerPhenotype.RAPID,
        3.0: MetabolizerPhenotype.ULTRARAPID,
    }

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
        a1 = self.db.get_allele(gene, allele_1_name)
        a2 = self.db.get_allele(gene, allele_2_name)

        if a1 is None or a2 is None:
            return None

        activity_score = a1.activity_score + a2.activity_score

        # Map activity score to phenotype
        phenotype = self._score_to_phenotype(activity_score)

        # Determine confidence
        confidence = "HIGH"
        if a1.function == StarAlleleFunction.UNKNOWN or a2.function == StarAlleleFunction.UNKNOWN:
            confidence = "LOW"
        elif a1.function == StarAlleleFunction.DECREASED_FUNCTION or a2.function == StarAlleleFunction.DECREASED_FUNCTION:
            confidence = "MODERATE"

        # Get affected drugs
        affected_drugs = self.GENE_DRUG_MAP.get(gene.upper(), [])

        # Generate clinical significance
        significance = self._generate_significance(gene, phenotype, activity_score)

        return GeneResult(
            gene=gene.upper(),
            diplotype=f"{allele_1_name}/{allele_2_name}",
            allele_1=a1,
            allele_2=a2,
            activity_score=activity_score,
            phenotype=phenotype,
            phenotype_detail=f"{phenotype.value} (Activity Score: {activity_score:.1f})",
            confidence=confidence,
            affected_drugs=affected_drugs,
            clinical_significance=significance,
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
        gene_results = {}
        combined_alerts = []
        overall_confidence = "HIGH"

        for gene, (a1, a2) in panel.items():
            result = self.interpret_diplotype(gene, a1, a2)
            if result:
                gene_results[gene.upper()] = result
                if result.confidence == "LOW":
                    overall_confidence = "LOW"
                elif result.confidence == "MODERATE" and overall_confidence != "LOW":
                    overall_confidence = "MODERATE"

                # Generate alerts for actionable phenotypes
                if result.phenotype in [MetabolizerPhenotype.POOR, MetabolizerPhenotype.ULTRARAPID]:
                    for drug in result.affected_drugs:
                        combined_alerts.append({
                            "alert_id": str(uuid.uuid4())[:8],
                            "gene": gene.upper(),
                            "drug": drug,
                            "phenotype": result.phenotype.value,
                            "severity": "CRITICAL" if result.phenotype == MetabolizerPhenotype.POOR else "WARNING",
                            "message": f"{gene.upper()} {result.phenotype.value}: {result.clinical_significance}",
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

    def _score_to_phenotype(self, score: float) -> MetabolizerPhenotype:
        """Map activity score to metabolizer phenotype."""
        if score <= 0.0:
            return MetabolizerPhenotype.POOR
        elif score <= 1.0:
            return MetabolizerPhenotype.INTERMEDIATE
        elif score <= 2.0:
            return MetabolizerPhenotype.NORMAL
        elif score <= 2.5:
            return MetabolizerPhenotype.RAPID
        else:
            return MetabolizerPhenotype.ULTRARAPID

    @staticmethod
    def _generate_significance(gene: str, phenotype: MetabolizerPhenotype, score: float) -> str:
        """Generate clinical significance text."""
        if phenotype == MetabolizerPhenotype.POOR:
            return f"{gene} poor metabolizer (AS={score:.1f}): Significantly altered drug metabolism. Alternative therapy or dose adjustment required per CPIC guidelines."
        elif phenotype == MetabolizerPhenotype.INTERMEDIATE:
            return f"{gene} intermediate metabolizer (AS={score:.1f}): Moderately altered metabolism. Consider dose adjustment or monitoring."
        elif phenotype == MetabolizerPhenotype.NORMAL:
            return f"{gene} normal metabolizer (AS={score:.1f}): Standard drug metabolism expected."
        elif phenotype == MetabolizerPhenotype.RAPID:
            return f"{gene} rapid metabolizer (AS={score:.1f}): Increased metabolism. May require dose increase for prodrugs."
        elif phenotype == MetabolizerPhenotype.ULTRARAPID:
            return f"{gene} ultrarapid metabolizer (AS={score:.1f}): Markedly increased metabolism. Prodrug toxicity risk or reduced efficacy of active drugs."
        return f"{gene}: Indeterminate phenotype (AS={score:.1f})"

    @staticmethod
    def _generate_panel_summary(gene_results: Dict[str, GeneResult]) -> str:
        """Generate a human-readable panel summary."""
        lines = ["Pharmacogenomic Panel Interpretation Summary", "=" * 50]
        for gene, result in gene_results.items():
            lines.append(f"  {gene}: {result.diplotype} -> {result.phenotype.value} (AS={result.activity_score:.1f})")
            if result.phenotype in [MetabolizerPhenotype.POOR, MetabolizerPhenotype.ULTRARAPID]:
                lines.append(f"    ⚠ ACTIONABLE: {result.clinical_significance}")
        return "\n".join(lines)
