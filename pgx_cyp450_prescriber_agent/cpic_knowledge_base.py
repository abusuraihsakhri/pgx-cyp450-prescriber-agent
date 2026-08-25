"""
Clinical Pharmacogenomics Knowledge Base for PGx CYP450 Prescriber Agent.
Searchable database of CPIC, DPWG, and FDA pharmacogenomic guidelines
with recommendation summaries and evidence ratings.

Domain: Pharmacogenomics
Standards: CPIC, DPWG, FDA Table of Pharmacogenomic Biomarkers
Author: Dr. Abu Suraih Sakhri
"""
import datetime
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class GuidelineSource(str, Enum):
    CPIC = "CPIC"
    DPWG = "DPWG"
    FDA = "FDA"
    PHARMGKB = "PharmGKB"


class EvidenceLevel(str, Enum):
    LEVEL_1A = "1A"  # Guideline: genetic info should be used
    LEVEL_1B = "1B"  # Guideline: prescribing action recommended
    LEVEL_2A = "2A"  # Guideline: prescribing action suggested
    LEVEL_2B = "2B"  # Guideline: insufficient evidence
    LEVEL_3 = "3"    # Optional: informational
    LEVEL_4 = "4"    # Research only


class Actionability(str, Enum):
    HIGH = "HIGH"       # Clear prescribing action available
    MODERATE = "MODERATE"  # Some evidence for action
    LOW = "LOW"         # Informational only
    INSUFFICIENT = "INSUFFICIENT"


@dataclass
class GuidelineEntry:
    """Single pharmacogenomic guideline entry."""
    entry_id: str
    source: GuidelineSource
    gene: str
    drug: str
    evidence_level: EvidenceLevel
    actionability: Actionability
    summary: str
    recommendation: str
    phenotype_specific_actions: Dict[str, str]
    references: List[str]
    last_updated: str = ""
    version: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "source": self.source.value,
            "gene": self.gene,
            "drug": self.drug,
            "evidence_level": self.evidence_level.value,
            "actionability": self.actionability.value,
            "summary": self.summary,
            "recommendation": self.recommendation,
            "phenotype_specific_actions": self.phenotype_specific_actions,
            "references": self.references,
            "last_updated": self.last_updated,
            "version": self.version,
        }


class CPICKnowledgeBase:
    """
    Searchable database of pharmacogenomic guidelines from CPIC, DPWG, and FDA.
    Supports querying by gene, drug, evidence level, and source.
    """

    def __init__(self):
        self._entries: List[GuidelineEntry] = self._load_default_guidelines()

    def _load_default_guidelines(self) -> List[GuidelineEntry]:
        """Load curated guideline entries from CPIC, DPWG, and FDA."""
        return [
            GuidelineEntry(
                entry_id="CPIC-CYP2C19-CLOPIDOGREL-001",
                source=GuidelineSource.CPIC,
                gene="CYP2C19",
                drug="clopidogrel",
                evidence_level=EvidenceLevel.LEVEL_1A,
                actionability=Actionability.HIGH,
                summary="CYP2C19 poor metabolizers have reduced clopidogrel activation leading to decreased antiplatelet effect and increased cardiovascular event risk.",
                recommendation="For CYP2C19 poor and intermediate metabolizers, use an alternative antiplatelet agent (prasugrel or ticagrelor) when available.",
                phenotype_specific_actions={
                    "PM": "Use prasugrel or ticagrelor. Clopidogrel is contraindicated.",
                    "IM": "Consider alternative antiplatelet. If clopidogrel used, monitor closely.",
                    "NM": "Standard dosing appropriate.",
                    "RM": "Standard dosing appropriate.",
                    "UM": "Standard dosing appropriate.",
                },
                references=[
                    "CPIC Guideline for CYP2C19 and Clopidogrel (2022)",
                    "Scott SA et al. Clin Pharmacol Ther. 2022;111(3):571-585",
                    "FDA Drug Safety Communication: Reduced effectiveness of clopidogrel (2010)",
                ],
                last_updated="2022-03-15",
                version="2.0",
            ),
            GuidelineEntry(
                entry_id="CPIC-CYP2D6-CODEINE-002",
                source=GuidelineSource.CPIC,
                gene="CYP2D6",
                drug="codeine",
                evidence_level=EvidenceLevel.LEVEL_1A,
                actionability=Actionability.HIGH,
                summary="CYP2D6 converts codeine to morphine. Poor metabolizers get no analgesic effect; ultrarapid metabolizers risk fatal respiratory depression.",
                recommendation="Avoid codeine in CYP2D6 poor and ultrarapid metabolizers. Use alternative analgesic.",
                phenotype_specific_actions={
                    "PM": "No analgesic effect expected. Use morphine or non-opioid alternative.",
                    "IM": "Reduced efficacy possible. Consider dose increase or alternative.",
                    "NM": "Standard dosing appropriate.",
                    "RM": "Standard dosing appropriate.",
                    "UM": "CONTRAINDICATED. Risk of fatal respiratory depression. Use non-codeine analgesic.",
                },
                references=[
                    "CPIC Guideline for CYP2D6 and Codeine (2019)",
                    "Crews KR et al. Clin Pharmacol Ther. 2021;110(4):888-896",
                    "FDA Drug Safety Communication: Codeine use in children (2017)",
                ],
                last_updated="2021-08-20",
                version="2.1",
            ),
            GuidelineEntry(
                entry_id="CPIC-SLCO1B1-SIMVASTATIN-003",
                source=GuidelineSource.CPIC,
                gene="SLCO1B1",
                drug="simvastatin",
                evidence_level=EvidenceLevel.LEVEL_1A,
                actionability=Actionability.HIGH,
                summary="SLCO1B1 poor function variants increase simvastatin plasma concentration, elevating myopathy risk especially at higher doses.",
                recommendation="For SLCO1B1 poor function carriers, prescribe lower simvastatin dose (20mg) or use alternative statin.",
                phenotype_specific_actions={
                    "PM": "Max 20mg/day simvastatin. Consider rosuvastatin, pravastatin, or atorvastatin.",
                    "IM": "Max 40mg/day simvastatin. Monitor for myopathy symptoms.",
                    "NM": "Standard dosing appropriate.",
                    "UM": "Standard dosing appropriate.",
                },
                references=[
                    "CPIC Guideline for SLCO1B1, ABCG2, and Statins (2022)",
                    "Ramsey LB et al. Clin Pharmacol Ther. 2022;111(5):1007-1021",
                ],
                last_updated="2022-06-01",
                version="1.1",
            ),
            GuidelineEntry(
                entry_id="FDA-CYP2C9-WARFARIN-004",
                source=GuidelineSource.FDA,
                gene="CYP2C9",
                drug="warfarin",
                evidence_level=EvidenceLevel.LEVEL_1A,
                actionability=Actionability.HIGH,
                summary="CYP2C9 variants affect warfarin metabolism. Poor metabolizers have decreased clearance and increased bleeding risk.",
                recommendation="Consider CYP2C9 and VKORC1 genotype when initiating warfarin. Use pharmacogenomic dosing algorithms.",
                phenotype_specific_actions={
                    "PM": "Reduce initial dose by 25-50%. Increase INR monitoring frequency.",
                    "IM": "Reduce initial dose by 15-25%. Monitor INR closely.",
                    "NM": "Standard dosing with routine INR monitoring.",
                    "UM": "May require higher doses. Monitor INR closely.",
                },
                references=[
                    "FDA Table of Pharmacogenomic Biomarkers in Drug Labeling",
                    "Johnson JA et al. Clin Pharmacol Ther. 2017;102(3):377-380",
                ],
                last_updated="2023-01-10",
                version="5.0",
            ),
            GuidelineEntry(
                entry_id="DPWG-CYP2D6-TAMOXIFEN-005",
                source=GuidelineSource.DPWG,
                gene="CYP2D6",
                drug="tamoxifen",
                evidence_level=EvidenceLevel.LEVEL_1A,
                actionability=Actionability.HIGH,
                summary="CYP2D6 converts tamoxifen to active metabolite endoxifen. Poor metabolizers have reduced endoxifen levels and potentially decreased efficacy.",
                recommendation="Consider alternative endocrine therapy for CYP2D6 poor metabolizers (aromatase inhibitor if postmenopausal).",
                phenotype_specific_actions={
                    "PM": "Consider aromatase inhibitor (postmenopausal) or increased tamoxifen dose.",
                    "IM": "Monitor for treatment response. Consider dose adjustment.",
                    "NM": "Standard tamoxifen dosing.",
                    "RM": "Standard tamoxifen dosing.",
                    "UM": "Standard tamoxifen dosing.",
                },
                references=[
                    "DPWG Guideline: CYP2D6 and Tamoxifen (2023)",
                    "Province MA et al. J Clin Oncol. 2022;40(15):1652-1662",
                ],
                last_updated="2023-04-15",
                version="3.0",
            ),
            GuidelineEntry(
                entry_id="CPIC-CYP3A5-TACROLIMUS-006",
                source=GuidelineSource.CPIC,
                gene="CYP3A5",
                drug="tacrolimus",
                evidence_level=EvidenceLevel.LEVEL_1A,
                actionability=Actionability.HIGH,
                summary="CYP3A5 expressers metabolize tacrolimus faster, requiring higher doses to achieve target trough concentrations.",
                recommendation="CYP3A5 expressers should receive 1.5-2x standard starting dose with therapeutic drug monitoring.",
                phenotype_specific_actions={
                    "PM": "Standard dose: 0.1 mg/kg/day. Target trough 8-12 ng/mL.",
                    "IM": "Intermediate dose: 0.15 mg/kg/day. Monitor trough levels.",
                    "NM": "Higher dose: 0.2 mg/kg/day. Frequent trough monitoring.",
                    "RM": "Higher dose: 0.2 mg/kg/day. Frequent trough monitoring.",
                },
                references=[
                    "CPIC Guideline for CYP3A5 and Tacrolimus (2022)",
                    "Birdwell KA et al. Clin Pharmacol Ther. 2022;111(5):1022-1034",
                ],
                last_updated="2022-09-01",
                version="1.0",
            ),
        ]

    def search_by_gene(self, gene: str) -> List[GuidelineEntry]:
        """Search guidelines by gene name."""
        gene_upper = gene.upper().strip()
        return [e for e in self._entries if e.gene.upper() == gene_upper]

    def search_by_drug(self, drug: str) -> List[GuidelineEntry]:
        """Search guidelines by drug name."""
        drug_lower = drug.lower().strip()
        return [e for e in self._entries if e.drug.lower() == drug_lower]

    def search_by_source(self, source: GuidelineSource) -> List[GuidelineEntry]:
        """Search guidelines by source (CPIC, DPWG, FDA)."""
        return [e for e in self._entries if e.source == source]

    def search_by_evidence_level(self, level: EvidenceLevel) -> List[GuidelineEntry]:
        """Search guidelines by evidence level."""
        return [e for e in self._entries if e.evidence_level == level]

    def search_by_actionability(self, actionability: Actionability) -> List[GuidelineEntry]:
        """Search guidelines by actionability rating."""
        return [e for e in self._entries if e.actionability == actionability]

    def full_text_search(self, query: str) -> List[GuidelineEntry]:
        """Full-text search across summary, recommendation, and references."""
        query_lower = query.lower().strip()
        results = []
        for entry in self._entries:
            searchable = " ".join([
                entry.summary.lower(),
                entry.recommendation.lower(),
                entry.gene.lower(),
                entry.drug.lower(),
                " ".join(entry.references).lower(),
            ])
            if query_lower in searchable:
                results.append(entry)
        return results

    def get_gene_drug_matrix(self) -> Dict[str, List[str]]:
        """Get a matrix of all genes and their associated drugs."""
        matrix: Dict[str, List[str]] = {}
        for entry in self._entries:
            if entry.gene not in matrix:
                matrix[entry.gene] = []
            if entry.drug not in matrix[entry.gene]:
                matrix[entry.gene].append(entry.drug)
        return matrix

    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge base statistics."""
        return {
            "total_entries": len(self._entries),
            "by_source": {s.value: len([e for e in self._entries if e.source == s]) for s in GuidelineSource},
            "by_evidence_level": {l.value: len([e for e in self._entries if e.evidence_level == l]) for l in EvidenceLevel},
            "by_actionability": {a.value: len([e for e in self._entries if e.actionability == a]) for a in Actionability},
            "unique_genes": len(set(e.gene for e in self._entries)),
            "unique_drugs": len(set(e.drug for e in self._entries)),
        }

    def add_entry(self, entry: GuidelineEntry) -> None:
        """Add a new guideline entry to the knowledge base."""
        self._entries.append(entry)

    def export_json(self) -> str:
        """Export entire knowledge base as JSON."""
        return json.dumps([e.to_dict() for e in self._entries], indent=2)
