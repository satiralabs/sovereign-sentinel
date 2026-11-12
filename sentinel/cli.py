"""
SovereignSentinel CLI: Command-line interface for the verification knowledge graph.
"""

import argparse
import hashlib
import json
import os
import sys
from .graph import ProvenanceGraph
from .receipt import generate_provenance_receipt


def get_default_db_path() -> str:
    home = os.path.expanduser("~")
    return os.path.join(home, ".sovereign-sentinel", "sentinel_graph.db")


def cmd_add_source(args):
    db_path = args.db or get_default_db_path()
    graph = ProvenanceGraph(db_path)
    digest = hashlib.sha256(args.url.encode("utf-8")).hexdigest()
    graph.add_source(
        source_id=args.source_id,
        sha256_digest=digest,
        url=args.url,
        title=args.title or args.source_id,
        credibility=args.credibility,
    )
    print(f"Recorded source: {args.source_id} (Credibility: {args.credibility})")


def cmd_add_claim(args):
    db_path = args.db or get_default_db_path()
    graph = ProvenanceGraph(db_path)
    graph.add_claim(
        claim_id=args.claim_id,
        subject=args.subject,
        predicate=args.predicate,
        obj=args.object,
    )
    print(f"Created claim: {args.claim_id} [{args.subject} -> {args.predicate} -> {args.object}]")


def cmd_link_evidence(args):
    db_path = args.db or get_default_db_path()
    graph = ProvenanceGraph(db_path)
    supports = args.verdict.lower() in ["supports", "true", "1", "yes"]
    graph.link_evidence(
        claim_id=args.claim_id,
        source_id=args.source_id,
        supports=supports,
        quote_snippet=args.quote or "",
    )
    print(f"Linked evidence: {args.source_id} {'supports' if supports else 'refutes'} {args.claim_id}")


def cmd_verify(args):
    db_path = args.db or get_default_db_path()
    graph = ProvenanceGraph(db_path)
    result = graph.evaluate_claim(args.claim_id)
    receipt = generate_provenance_receipt(result)
    result["receipt"] = receipt
    print(json.dumps(result, indent=2))


def main():
    parser = argparse.ArgumentParser(
        prog="sovereign-sentinel",
        description="SovereignSentinel: Verifiable OSINT & Counter-Disinformation Graph",
    )
    parser.add_argument("--db", help="Path to SQLite graph database")

    subparsers = parser.add_subparsers(dest="command")

    p_src = subparsers.add_parser("add-source", help="Register a verified evidence source")
    p_src.add_argument("--source-id", required=True)
    p_src.add_argument("--url", required=True)
    p_src.add_argument("--title", default="")
    p_src.add_argument("--credibility", type=float, default=0.7)
    p_src.set_defaults(func=cmd_add_source)

    p_clm = subparsers.add_parser("add-claim", help="Register a claim for verification")
    p_clm.add_argument("--claim-id", required=True)
    p_clm.add_argument("--subject", required=True)
    p_clm.add_argument("--predicate", required=True)
    p_clm.add_argument("--object", required=True)
    p_clm.set_defaults(func=cmd_add_claim)

    p_ev = subparsers.add_parser("link-evidence", help="Link source evidence to a claim")
    p_ev.add_argument("--claim-id", required=True)
    p_ev.add_argument("--source-id", required=True)
    p_ev.add_argument("--verdict", default="supports", choices=["supports", "refutes"])
    p_ev.add_argument("--quote", default="")
    p_ev.set_defaults(func=cmd_link_evidence)

    p_vfy = subparsers.add_parser("verify", help="Evaluate claim validity and produce cryptographic receipt")
    p_vfy.add_argument("--claim-id", required=True)
    p_vfy.set_defaults(func=cmd_verify)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
