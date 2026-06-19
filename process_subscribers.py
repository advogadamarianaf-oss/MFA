"""
Reads 5 pages of subscriber data from the Atende Direito API,
finds phone numbers present in both Comercial 1 (f175863) and Comercial 2 (f270363),
and writes the matches to matches.json.
"""

import json
import os

BASE = r"C:\Users\Thiag\.claude\projects\C--Users-Thiag-OneDrive--rea-de-Trabalho-Analise-de-Mensagens\1c338e98-e80f-4af9-b54c-57bce6e90964\tool-results"

FILES = [
    os.path.join(BASE, "mcp-atende-direito-execute_request-1781811696328.txt"),
    os.path.join(BASE, "mcp-atende-direito-execute_request-1781811699440.txt"),
    os.path.join(BASE, "mcp-atende-direito-execute_request-1781811702676.txt"),
    os.path.join(BASE, "mcp-atende-direito-execute_request-1781811707284.txt"),
    os.path.join(BASE, "mcp-atende-direito-execute_request-1781811710617.txt"),
]

OUTPUT = r"C:\Users\Thiag\OneDrive\Área de Trabalho\Analise de Mensagens\matches.json"


def load_subscribers(files):
    """Load all subscriber objects from the given JSON files."""
    all_subs = []
    for fpath in files:
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
        subs = data.get("data", [])
        all_subs.extend(subs)
        print(f"  Loaded {len(subs)} subscribers from {os.path.basename(fpath)}")
    return all_subs


def separate_by_flow(subscribers):
    """Separate subscribers into Comercial 1 and Comercial 2 by user_ns prefix."""
    comercial1 = {}  # phone -> subscriber
    comercial2 = {}  # phone -> subscriber

    for sub in subscribers:
        user_ns = sub.get("user_ns", "")
        phone = sub.get("phone", "")
        if not phone:
            continue

        if user_ns.startswith("f175863"):
            # If duplicate phone in same flow, keep the one with more recent activity
            if phone not in comercial1:
                comercial1[phone] = sub
        elif user_ns.startswith("f270363"):
            if phone not in comercial2:
                comercial2[phone] = sub

    return comercial1, comercial2


def format_labels(labels):
    """Extract label names as comma-separated string."""
    if not labels:
        return ""
    return ", ".join(lbl.get("name", "") for lbl in labels if lbl.get("name"))


def find_matches(comercial1, comercial2):
    """Find phones present in both flows and build match records."""
    common_phones = set(comercial1.keys()) & set(comercial2.keys())
    matches = []

    for phone in sorted(common_phones):
        c1 = comercial1[phone]
        c2 = comercial2[phone]
        matches.append({
            "phone": phone,
            "name_comercial1": c1.get("name", ""),
            "name_comercial2": c2.get("name", ""),
            "labels_comercial1": format_labels(c1.get("labels", [])),
            "labels_comercial2": format_labels(c2.get("labels", [])),
            "user_ns_comercial1": c1.get("user_ns", ""),
            "user_ns_comercial2": c2.get("user_ns", ""),
            "status_comercial1": c1.get("status", ""),
            "status_comercial2": c2.get("status", ""),
        })

    return matches


def main():
    print("Loading subscriber data...")
    all_subs = load_subscribers(FILES)
    print(f"\nTotal subscribers loaded: {len(all_subs)}")

    print("\nSeparating by flow...")
    comercial1, comercial2 = separate_by_flow(all_subs)
    print(f"  Comercial 1 (f175863): {len(comercial1)} unique phones")
    print(f"  Comercial 2 (f270363): {len(comercial2)} unique phones")

    print("\nFinding matches...")
    matches = find_matches(comercial1, comercial2)
    print(f"  Found {len(matches)} phone numbers in BOTH flows")

    # Write output
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(matches, f, ensure_ascii=False, indent=2)
    print(f"\nResults written to: {OUTPUT}")

    # Print summary
    if matches:
        print(f"\n{'='*80}")
        print(f"MATCHES FOUND: {len(matches)}")
        print(f"{'='*80}")
        for i, m in enumerate(matches, 1):
            print(f"\n--- Match {i} ---")
            print(f"  Phone:           {m['phone']}")
            print(f"  Name (Com1):     {m['name_comercial1']}")
            print(f"  Name (Com2):     {m['name_comercial2']}")
            print(f"  Labels (Com1):   {m['labels_comercial1'] or '(none)'}")
            print(f"  Labels (Com2):   {m['labels_comercial2'] or '(none)'}")
            print(f"  user_ns (Com1):  {m['user_ns_comercial1']}")
            print(f"  user_ns (Com2):  {m['user_ns_comercial2']}")
            print(f"  Status (Com1):   {m['status_comercial1']}")
            print(f"  Status (Com2):   {m['status_comercial2']}")
    else:
        print("\nNo matches found.")


if __name__ == "__main__":
    main()
