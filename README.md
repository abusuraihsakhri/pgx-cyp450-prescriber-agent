# Pgx CYP450 Prescriber Agent

> **Domain:** Computational Pharmacogenomics & Clinical Decision Support
> **Reference Guidelines:** CPIC (Clinical Pharmacogenetics Implementation Consortium), PharmGKB, FDA Table of Pharmacogenomic Biomarkers

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## Overview

**Pgx CYP450 Prescriber Agent** is a clinical decision support platform implementing CPIC Gene-Drug Guidelines for CYP450 metabolizer phenotype interpretation and dosing recommendations. It maps star alleles to metabolizer phenotypes (PM, IM, NM, UM) and provides evidence-based dosing guidance.

---

## Key Features

### Core Analytical Engines

- **StarAlleleDiplotyperAgent**: Evaluates primary metric thresholds for pharmacogenomic variant calling
- **CPICDosingRuleEngineAgent**: Triggers safety interlocks based on critical flags and secondary parameters
- **AlternativeMedicationAdvisorAgent**: Detects phenotypic discordance and recommends confirmatory testing

### Enterprise Security

- **Zero-PHI Outbound Interceptor**: AST and regex inspection blocking SSNs, MRNs, phone numbers, emails, and patient identifiers
- **Tamper-Evident HMAC-SHA256 Audit Trail**: Chained, cryptographically signed logs for every evaluation
- **Input Path Validation**: Batch processing validates file existence and extension before processing

### Infrastructure

- **FastAPI REST API**: OpenAPI 3.1 endpoints for audit, chat, and metrics
- **Prometheus Telemetry**: Operational metrics at `/metrics`
- **Docker Support**: Containerized deployment with health checks
- **CLI Interface**: Interactive and parameterized command-line access

---

## Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/pgx-cyp450-prescriber-agent.git
cd pgx-cyp450-prescriber-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn pydantic pytest
```

---

## Usage

### CLI Commands

#### 1. Single Task Evaluation (Audit)
```bash
python cli.py audit --task-id TASK-001 --target KEY-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

#### 2. Supervisory Chat
```bash
python cli.py chat "What is the system status?"
```

#### 3. Batch CSV Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

#### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

#### 5. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### REST API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check and system metadata |
| GET | `/metrics` | Prometheus operational metrics |
| POST | `/api/audit` | Submit task for evaluation |
| POST | `/api/chat` | Query supervisory assistant |
| GET | `/api/audit/logs` | Retrieve and verify audit trail |

### Docker Deployment

```bash
docker build -t pgx-cyp450-prescriber-agent .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=your-secret-key pgx-cyp450-prescriber-agent
```

Or using docker-compose:

```bash
docker-compose up -d
```

---

## Input Data Schema

### Task Payload

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `task_id` | string | Unique task/case identifier | Yes |
| `target_identifier` | string | Entity or genomic target | Yes |
| `primary_metric` | float | Primary measurement/score | Yes |
| `secondary_metric` | float | Secondary kinetic/confidence score | No (default: 0.0) |
| `status_descriptor` | string | Status code or phenotype descriptor | No (default: "NOMINAL") |
| `is_critical_flag` | boolean | Emergency escalation trigger | No (default: false) |

### Batch CSV Format

```csv
case_id,patient_synthetic_id,metric_primary,metric_secondary,is_stat,status_flag
CASE-001,SYNTH-01,25.4,14.2,True,DISCORDANT
CASE-002,SYNTH-02,12.0,4.1,False,NORMAL
```

---

## Security Configuration

### Audit Secret Key

The HMAC-SHA256 audit trail requires a secret key for cryptographic signing. Set the `AUDIT_SECRET_KEY` environment variable for persistent audit integrity across restarts:

```bash
export AUDIT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
```

If not set, a random ephemeral key is generated (audit trail will not persist across restarts).

### PHI Protection

The Zero-PHI outbound guard automatically detects and blocks:
- Medical Record Numbers (MRN)
- Social Security Numbers (SSN)
- Phone numbers
- Email addresses
- Date of birth patterns
- Common patient name patterns

---

## Testing

```bash
# Run full test suite
pytest -v

# Run with coverage
pytest -v --cov=agents --cov-report=html

# Run security-focused tests only
pytest tests/test_security.py -v
```

### Test Coverage

- **PHI Guard Enforcement**: Validates detection of SSN, MRN, phone, email patterns
- **Worker Agents**: Tests threshold-based alert generation
- **Supervisor Consensus**: Validates multi-worker evaluation and audit signing
- **Audit Trail Integrity**: Tests cryptographic chain verification and tamper detection
- **Input Validation**: Tests file path validation for batch processing

---

## Project Structure

```
pgx-cyp450-prescriber-agent/
├── agents/                    # Core enterprise module
│   ├── __init__.py           # Package metadata
│   ├── api.py                # FastAPI REST server
│   ├── base.py               # Security, PHI guard, audit trail
│   ├── learning.py           # Bayesian calibration engine
│   ├── llm_factory.py        # LLM provider abstraction
│   ├── metrics.py            # Prometheus metrics collector
│   ├── models.py             # Pydantic data schemas
│   ├── streamer.py           # WebSocket telemetry broadcaster
│   ├── supervisor.py         # Master orchestrator
│   └── workers.py            # Specialized domain workers
├── tests/                    # Test suite
│   ├── test_pgx_cyp450_prescriber_agent.py
│   ├── test_pgx_prescriber.py
│   ├── test_enrichment.py
│   └── test_security.py
├── cli.py                    # Command-line interface
├── simulator.py              # High-throughput simulation
├── enrichment.py             # Domain enrichment engines
├── pgx_prescriber.py         # Standalone PGx module
├── web/                      # Web interface
├── Dockerfile                # Container build
├── docker-compose.yml        # Container orchestration
├── pyproject.toml            # Project metadata
├── sample.csv                # Sample batch input
├── sample_payload.json       # Sample API payload
└── benchmark_dataset.json    # Golden benchmark test cases
```

---

## License

MIT License - see [LICENSE](LICENSE) for details.
