#!/usr/bin/env python3
"""Flag the day a listed rate stops appearing on the vendor page it came from.

    python3 check_prices.py            # check every entry that has a source URL
    python3 check_prices.py --offline  # arithmetic only: recompute derived rows

A rate that disappears from its page is not proof of a price change -- pages get
rewritten, numbers get moved into scripts. It is the signal to open the page and
read it, which is the job this script cannot do.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
UA = {"User-Agent": "Mozilla/5.0 (compatible; pricing-check/1.0)"}


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def money_patterns(amount: float) -> list[str]:
    """The ways a page might print this number."""
    whole = amount if amount == int(amount) else amount
    forms = {f"${whole:g}", f"{whole:g} credits", f"{whole:g}"}
    if amount >= 1000:
        forms |= {f"${amount:,.0f}", f"{amount:,.0f}"}
    return sorted(forms)


def derived_rows(p: dict) -> list[tuple[str, str]]:
    rows = []
    ac = p["kortix"]["agent_computer"]
    cpu, ram, store = ac["cpu_usd_per_vcpu_hour"], ac["ram_usd_per_gb_hour"], ac["storage_usd_per_gb_month"]
    hourly_usd = 2 * cpu + 4 * ram
    hourly_credits = hourly_usd / p["kortix"]["credit_usd"]
    rows.append(("kortix 2 vCPU / 4 GB hourly cost",
                 f"${hourly_usd:.4f}/hour = {hourly_credits:.1f} credits/hour "
                 f"(the page prints {ac['default_machine_credits_per_hour']})"))
    rows.append(("kortix 100 agent-computer hours",
                 f"{hourly_credits * 100:.0f} credits = ${hourly_usd * 100:.2f} "
                 f"against a free tier of {p['kortix']['free_tier']['credits_month']} credits"))
    rows.append(("perplexity 300 tasks at 100 credits",
                 f"{300 * 100 / p['perplexity']['credits_per_usd']:.2f} USD of credits"))
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--offline", action="store_true")
    args = ap.parse_args()
    p = json.loads((HERE / "data" / "pricing.json").read_text())

    for label, value in derived_rows(p):
        print(f"derived  {label:38} {value}")

    if args.offline:
        return

    checks: list[tuple[str, str, float]] = []
    for plan in p["perplexity"]["plans"]:
        checks.append((f"perplexity {plan['name']} monthly", plan["source"], plan["price_usd_month"]))
    checks.append(("kortix cpu rate", p["kortix"]["source"], p["kortix"]["agent_computer"]["cpu_usd_per_vcpu_hour"]))
    checks.append(("kortix ram rate", p["kortix"]["source"], p["kortix"]["agent_computer"]["ram_usd_per_gb_hour"]))
    checks.append(("kortix storage rate", p["kortix"]["source"], p["kortix"]["agent_computer"]["storage_usd_per_gb_month"]))

    pages: dict[str, str] = {}
    changed = 0
    for label, url, amount in checks:
        if url not in pages:
            try:
                pages[url] = fetch(url)
            except Exception as exc:  # noqa: BLE001 - a blocked page is a finding, not a crash
                pages[url] = ""
                print(f"unreachable {label}: {url} ({exc})")
                changed += 1
                continue
        body = pages[url]
        hit = any(re.search(re.escape(f), body) for f in money_patterns(amount))
        print(f"{'ok      ' if hit else 'CHECK   '} {label:38} {amount} {url}")
        changed += 0 if hit else 1
    print(f"\n{changed} row(s) need a human read.")


if __name__ == "__main__":
    main()
