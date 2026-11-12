"""
SovereignSentinel Knowledge Graph: SQLite-backed verifiable provenance store.
Tracks entities, claims, evidence citations, and trust scores.
"""

import json
import os
import sqlite3
import time
from typing import Any, Dict, List, Optional, Tuple


class ProvenanceGraph:
    """Relational knowledge graph tracking verifiable claims and sources."""

    def __init__(self, db_path: str):
        self.db_path = os.path.abspath(db_path)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS sources (
                    source_id TEXT PRIMARY KEY,
                    url TEXT,
                    source_type TEXT,
                    title TEXT,
                    sha256_digest TEXT NOT NULL,
                    credibility_score REAL DEFAULT 0.5,
                    first_seen REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS entities (
                    entity_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    metadata_json TEXT
                );

                CREATE TABLE IF NOT EXISTS claims (
                    claim_id TEXT PRIMARY KEY,
                    subject TEXT NOT NULL,
                    predicate TEXT NOT NULL,
                    object TEXT NOT NULL,
                    verdict TEXT DEFAULT 'UNVERIFIED', -- VERIFIED, DISPUTED, DEBUNKED, UNVERIFIED
                    confidence REAL DEFAULT 0.5,
                    created_at REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS evidence_edges (
                    edge_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    claim_id TEXT NOT NULL,
                    source_id TEXT NOT NULL,
                    supports INTEGER NOT NULL, -- 1 for supports, 0 for refutes
                    quote_snippet TEXT,
                    FOREIGN KEY(claim_id) REFERENCES claims(claim_id),
                    FOREIGN KEY(source_id) REFERENCES sources(source_id)
                );
            """)

    def add_source(
        self,
        source_id: str,
        sha256_digest: str,
        url: str = "",
        source_type: str = "web",
        title: str = "",
        credibility: float = 0.5,
    ):
        with self._get_conn() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO sources 
                   (source_id, url, source_type, title, sha256_digest, credibility_score, first_seen)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (source_id, url, source_type, title, sha256_digest, credibility, time.time()),
            )

    def add_claim(
        self,
        claim_id: str,
        subject: str,
        predicate: str,
        obj: str,
        verdict: str = "UNVERIFIED",
        confidence: float = 0.5,
    ):
        with self._get_conn() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO claims 
                   (claim_id, subject, predicate, object, verdict, confidence, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (claim_id, subject, predicate, obj, verdict, confidence, time.time()),
            )

    def link_evidence(
        self,
        claim_id: str,
        source_id: str,
        supports: bool,
        quote_snippet: str = "",
    ):
        with self._get_conn() as conn:
            conn.execute(
                """INSERT INTO evidence_edges (claim_id, source_id, supports, quote_snippet)
                   VALUES (?, ?, ?, ?)""",
                (claim_id, source_id, 1 if supports else 0, quote_snippet),
            )

    def evaluate_claim(self, claim_id: str) -> Dict[str, Any]:
        """Calculates aggregate belief score for a claim based on linked evidence and source credibility."""
        with self._get_conn() as conn:
            claim = conn.execute("SELECT * FROM claims WHERE claim_id = ?", (claim_id,)).fetchone()
            if not claim:
                return {"error": "Claim not found"}

            edges = conn.execute(
                """SELECT e.supports, e.quote_snippet, s.source_id, s.credibility_score, s.url, s.sha256_digest
                   FROM evidence_edges e
                   JOIN sources s ON e.source_id = s.source_id
                   WHERE e.claim_id = ?""",
                (claim_id,),
            ).fetchall()

            supporting_weight = 0.0
            refuting_weight = 0.0

            citations = []
            for row in edges:
                cred = row["credibility_score"]
                if row["supports"] == 1:
                    supporting_weight += cred
                else:
                    refuting_weight += cred
                citations.append({
                    "source_id": row["source_id"],
                    "supports": bool(row["supports"]),
                    "credibility": cred,
                    "url": row["url"],
                    "sha256": row["sha256_digest"],
                    "quote": row["quote_snippet"],
                })

            total_weight = supporting_weight + refuting_weight
            if total_weight == 0:
                verdict = "UNVERIFIED"
                confidence = 0.0
            else:
                ratio = supporting_weight / total_weight
                confidence = round(abs(supporting_weight - refuting_weight) / total_weight, 3)
                if ratio > 0.65:
                    verdict = "VERIFIED"
                elif ratio < 0.35:
                    verdict = "DEBUNKED"
                else:
                    verdict = "DISPUTED"

            # Update claim state in DB
            conn.execute(
                "UPDATE claims SET verdict = ?, confidence = ? WHERE claim_id = ?",
                (verdict, confidence, claim_id),
            )

            return {
                "claim_id": claim_id,
                "statement": f"{claim['subject']} {claim['predicate']} {claim['object']}",
                "verdict": verdict,
                "confidence": confidence,
                "supporting_weight": round(supporting_weight, 3),
                "refuting_weight": round(refuting_weight, 3),
                "evidence_count": len(citations),
                "citations": citations,
            }
