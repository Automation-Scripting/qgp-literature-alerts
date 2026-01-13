#!/usr/bin/env python3
# arXiv → Discord (1 paper = 1 message) with human-friendly logs
#
# Required env:
#   DISCORD_WEBHOOK_URL_QGP_DKL   (or change the name below)
#
# Optional env:
#   TIME_FRAME    = days back to include (default: 1)
#   MAX_RESULTS   = how many items to fetch from arXiv (default: 50)
#
# Notes:
# - This script POSTS one Discord message per paper (so you can react ⭐ per paper).
# - It prints a clear report: fetched count, filtered count, posted count.
# - It fails loudly if arXiv returned zero entries (often means query/API problem).
# - It does not fail the run if some individual Discord posts fail; it reports them.

import os
import sys
import feedparser
import requests
from datetime import datetime, timedelta, timezone

# ========= COMMON =========
TIME_FRAME = int(os.getenv("TIME_FRAME", "1"))          # days
MAX_RESULTS = int(os.getenv("MAX_RESULTS", "50"))       # arXiv API fetch size
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "20"))

# ========= CONFIG =========
WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL_QGP_ML"]

ARXIV_URL = (
    "https://export.arxiv.org/api/query?"
    "search_query=("
        "cat:hep-ph+OR+cat:hep-lat+OR+cat:nucl-th+OR+cat:nucl-ex"
    ")"
    "+AND+("
        "abs:%22machine+learning%22"
        "+OR+abs:ML"
        "+OR+abs:emulator"
        "+OR+abs:%22surrogate+model%22"
        "+OR+abs:%22Gaussian+process%22"    
    ")"
    "+AND+("
        "abs:%22quark+gluon+plasma%22"
        "+OR+abs:QGP"
        "+OR+abs:%22heavy+ion%22"
    ")"
    "&sortBy=submittedDate"
    "&sortOrder=descending"
    "&max_results=200"
)

# ========= HELPERS =========
def _parse_published_utc(entry) -> datetime:
    # arXiv Atom 'published' is always like "YYYY-MM-DDTHH:MM:SSZ"
    return datetime.strptime(entry.published, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

def _short(s: str, n: int = 90) -> str:
    s = (s or "").replace("\n", " ").strip()
    return s if len(s) <= n else s[: n - 1] + "…"

# ========= FETCH =========
cutoff = datetime.now(timezone.utc) - timedelta(days=TIME_FRAME)

feed = feedparser.parse(ARXIV_URL)

total_entries = len(getattr(feed, "entries", []))
total_available = feed.feed.get("opensearch_totalresults")
status = getattr(feed, "status", None)
bozo = getattr(feed, "bozo", None)
bozo_exc = getattr(feed, "bozo_exception", None) if bozo else None

print("\n===== arXiv → Discord Report =====")
print(f"Query URL         : {ARXIV_URL}")
print(f"TIME_FRAME (days) : {TIME_FRAME}")
print(f"Cutoff (UTC)      : {cutoff.isoformat()}")
print(f"HTTP status       : {status}")
print(f"bozo              : {bozo}")
if bozo_exc:
    print(f"bozo_exception    : {bozo_exc}")
print(f"Fetched entries   : {total_entries}")
print(f"Total results available on arXiv: {total_available}")

# If arXiv returned no entries, something is likely wrong (query too strict or API issue).
if total_entries == 0:
    raise RuntimeError(
        "arXiv returned 0 entries. This usually means the query is too strict, "
        "the API had an issue, or the response could not be parsed."
    )

# ========= FILTER =========
papers = []
for entry in feed.entries:
    try:
        published_dt = _parse_published_utc(entry)
    except Exception as e:
        print(f"  Skipping entry with unparsable date: {_short(getattr(entry, 'title', ''), 70)} | error={e}")
        continue

    if published_dt > cutoff:
        papers.append((entry, published_dt))

print(f"Entries after time filter: {len(papers)}")

if not papers:
    print("  No articles found in the selected time window. Nothing to post.\n")
    sys.exit(0)

# ========= POST (1 paper = 1 message) =========
posted_ok = 0
posted_fail = 0

for entry, published_dt in papers:
    title = (entry.title or "").replace("\n", " ").strip()
    link = (entry.link or "").strip()
    published_str = published_dt.strftime("%Y-%m-%d")

    # Message format: title + published date + link
    message = f"**{title}**\n🗓 {published_str}\n🔗 {link}"

    try:
        r = requests.post(WEBHOOK_URL, json={"content": message}, timeout=REQUEST_TIMEOUT)
        if 200 <= r.status_code < 300:
            posted_ok += 1
            print(f" Posted ({r.status_code}): {_short(title)}")
        else:
            posted_fail += 1
            print(f" Failed ({r.status_code}): {_short(title)}")
            # Print a bit of body for debugging (Discord often returns JSON)
            body = (r.text or "").strip()
            if body:
                print("   Response:", _short(body, 200))
    except Exception as e:
        posted_fail += 1
        print(f" Exception posting: {_short(title)}")
        print("   Error:", str(e))

# ========= SUMMARY =========
print("\n===== Summary =====")
print(f"Fetched from arXiv        : {total_entries}")
print(f"Passed time filter        : {len(papers)}")
print(f"Successfully posted       : {posted_ok}")
print(f"Failed to post            : {posted_fail}")

if posted_ok == 0:
    print("  WARNING: No messages were posted successfully.")
else:
    print(" Done. Posts delivered successfully.")

print("================================\n")