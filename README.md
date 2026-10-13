# PGx CYP450 Prescriber Agent

Educational pharmacogenomics tools and synthetic metric-auditing demonstrations. The project includes a small static diplotype explorer, Python panel interpretation, a drug–gene example database, and older compatible CLI/API demonstrations.

**Clinical limitation:** This repository is **not validated for patient care, medication prescribing, dose calculation, or clinical triage**. Its curated guideline text is not automatically updated and must not substitute for current CPIC/DPWG recommendations, product labeling, clinical assessment, or institutional governance.

## Browser demonstration

The standalone application is in [web/index.html](web/index.html). Open that file in a modern browser. It requires no server and does not transmit or persist input. The page supports **a limited set of CYP2D6 and CYP2C19 alleles**; it excludes structural variation and does not provide drug or dosage recommendations.

A GitHub Pages deployment workflow is included, but a public live URL is not listed until Pages is enabled and the deployed application is verified. GitHub Pages hosts static files and cannot run the Python FastAPI endpoints. The browser demonstration therefore uses local JavaScript instead of loading Pyodide.

## Python setup

Python **3.10 or newer** is required.

```bash
git clone https://github.com/abusuraihsakhri/pgx-cyp450-prescriber-agent.git
cd pgx-cyp450-prescriber-agent
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[server,test]"
python -m pytest -q
```

Windows PowerShell activation: `.venv\Scripts\Activate.ps1`.

### Python phenotype examples

```python
from pgx_cyp450_prescriber_agent.panel_interpreter import PanelInterpreter

interpreter = PanelInterpreter()
result = interpreter.interpret_diplotype("CYP2D6", "*1", "*10")
print(result.phenotype.value, result.activity_score)  # NM 1.25

panel = interpreter.interpret_panel({
    "CYP2D6": ("*4", "*4"),
    "CYP2C19": ("*1", "*17"),
})
print(panel.to_dict())
```

Only CYP2D6 uses an additive activity score in this implementation. CYP2C19 uses function-based phenotype translation; CYP2C9, CYP3A5, and SLCO1B1 deliberately return `INDETERMINATE` pending properly validated gene-specific implementations. Alleles not in the small curated subset return no phenotype. Do not enter real patient identifiers.

### Legacy synthetic metric demonstrations

The existing metric-audit interfaces are retained for compatibility but **do not implement pharmacogenomic clinical rules**.

```bash
python cli.py audit --task-id SYN-001 --target SYNTH-01 --primary 28.5
python cli.py batch -i sample_platform.csv -o results.csv
python cli.py verify-audit
python cli.py serve --host 127.0.0.1 --port 8000
```

The top-level FastAPI interface at `http://127.0.0.1:8000` serves `/health`, `/metrics`, `/api/audit`, `/api/chat`, and `/api/audit/logs` for synthetic tasks. The separate `pgx_cyp450_prescriber_agent.cli` and `pgx_prescriber.py` programs remain available as legacy variants; `sample.csv` corresponds to the package CLI's field conventions. These interfaces should not be exposed to the public internet without authentication, rate limiting, and privacy review.

## Docker

```bash
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
docker compose up --build
```

The audit key is required by Compose; there is no repository-provided default. Audit signatures are chained in **volatile process memory**, not durable storage. Reopening the service does not restore previous audit records. Never enter actual health information or assume regular-expression identifier filtering guarantees HIPAA compliance.

## Tests, technology, privacy

- Python, Pydantic v2, FastAPI/Uvicorn, pytest; standalone HTML/CSS/JavaScript browser explorer.
- CI checks Python 3.10–3.12, unit tests, JavaScript syntax, and dependency vulnerabilities.
- HMAC-SHA256 provides in-process audit-chain tamper detection; it does not constitute a persistent, independently verified audit log.
- Browser demonstration runs entirely locally: no CDN, cookies, tracking, uploads, accounts, or API calls. Tested browser compatibility depends on current standards-supporting desktop/mobile browsers; a full cross-browser device matrix has not been verified.
- Source lists for formal clinical validation: [CPIC](https://cpicpgx.org/), [PharmGKB](https://www.pharmgkb.org/) and [PharmVar](https://www.pharmvar.org/). Always check current diplotype/function tables and drug-specific CPIC guidance.

## License

MIT — see [LICENSE](LICENSE).
