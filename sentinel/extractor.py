"""
SovereignSentinel Extractor: Basic entity & claim triplet parser.
"""

import re
from typing import Dict, List, Tuple


def parse_triplets(text: str) -> List[Tuple[str, str, str]]:
    """Extract simple Subject-Predicate-Object triplets from statements."""
    lines = text.strip().splitlines()
    triplets = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Look for copulas or action verbs: is, was, launched, acquired, hacked, reported
        match = re.search(r"^(.*?)\s+(is|was|are|were|launched|acquired|hacked|funded|claims|denies)\s+(.*)$", line, re.IGNORECASE)
        if match:
            s, p, o = match.groups()
            triplets.append((s.strip(), p.strip().lower(), o.strip()))
        else:
            triplets.append((line, "states", "unspecified"))

    return triplets
