# SovereignSentinel

> **Verifiable OSINT & Counter-Disinformation Knowledge Graph.**  
> *Tamper-proof source lineage, weighted belief graphs, and cryptographic evidence receipts for open-source intelligence.*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/downloads/)
[![Zero-Dependency](https://img.shields.io/badge/dependencies-zero-brightgreen.svg)]()

---

## 🎯 Abstract

Information disorder, algorithmic synthetic media, and coordinated narrative manipulation threaten digital civic integrity. Standard fact-checking systems rely on centralized opaque trust lists that can be manipulated or dismissed as biased.

**SovereignSentinel** is a lightweight, local-first knowledge graph and evidence reconciliation engine that mathematically grounds claims against verifiable, hash-indexed source documents. It produces cryptographic provenance receipts proving how a verdict was reached.

---

## ⚡ Core Architecture

- **SQLite WAL Relational Knowledge Graph**: Zero-maintenance embedded graph database linking entities, claims, and citation edges.
- **Weighted Belief Propagation**: Evaluates claims by weighting supporting vs refuting citations based on calibrated source credibility.
- **Cryptographic Provenance Receipts**: Produces SHA-256 receipts encapsulating the exact citation state at the time of verification.
- **Standard Library Core**: Zero heavy graph dependencies (no Neo4j server, no heavy JVM runtime required).

---

## 🚀 Quickstart

```bash
git clone https://github.com/abenih/sovereign-sentinel.git
cd sovereign-sentinel
./bin/sovereign-sentinel --help
```

---

## 📄 License
MIT License. Created by [Susan (Abenezer)](https://satiralabs.com) at SatiraLabs.
