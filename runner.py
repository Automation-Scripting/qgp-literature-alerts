#!/usr/bin/env python3
# arXiv → Discord runner (multi-topic YAML) with human-friendly logs
#
# Usage:
#   python runner.py topics/hep.yml
#
# Required per-topic env:
#   Each topic declares webhook_env, e.g. DISCORD_WEBHOOK_URL_QGP_ML
#   You must export it (or set it in GitHub Actions env).
#
# Optional env (global):
#   TIME_FRAME            = days back to include (default: 1) OR "all" to disable date filtering
#   MODE                  = "auto" | "per_paper" | "summary" (default: "auto")
#   REQUEST_TIMEOUT       = HTTP timeout seconds (default: 20)
#   POST_DELAY_SECONDS    = delay between per-paper posts (default: 0.4)
#   MAX_RETRIES_429       = max retries on Discord 429 (default: 8)
#   DISCORD_CHUNK_LIMIT   = summary chunk size (default: 1800)
#   MAX_POSTS_PER_TOPIC   = cap after time filter (default: 0 = no cap)
#
# Notes:
# - per_paper posts 1 message per paper (so one can react ⭐ per paper).
# - summary posts a compact list (auto chunked) to avoid rate limits.
# - It prints a clear report per topic: fetched, filtered, posted.
# - It fails loudly if arXiv returned zero entries for a topic (helps detect query/API issues).
# - It does not fail the run if some individual Discord posts fail; it reports them.

import os
import sys
import time
import yaml
import feedparser
import requests
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

# ========= COMMON (global) =========
TIME_FRAME_RAW = os.getenv("TIME_FRAME", "1").strip().lower()   # "1", "7", "30", "360", "all"
MODE = os.getenv("MODE", "auto").strip().lower()               # "auto" | "per_paper" | "summary"
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "20"))

POST_DELAY_SECONDS = float(os.getenv("POST_DELAY_SECONDS", "0.4"))
MAX_RETRIES_429 = int(os.getenv("MAX_RETRIES_429", "8"))
DISCORD_CHUNK_LIMIT = int(os.getenv("DISCORD_CHUNK_LIMIT", "1800"))

MAX_POSTS_PER_TOPIC = int(os.getenv("MAX_POSTS_PER_TOPIC", "0"))  # 0 = no cap after time filter


# ========= HELPERS =========
def _parse_published_utc(entry) -> datetime:
    # arXiv Atom 'published' is always like "YYYY-MM-DDTHH:MM:SSZ"
    return datetime.strptime(entry.published, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

def _short(s: str, n: int = 90) -> str:
    s = (s or "").replace("\n", " ").strip()
    return s if len(s) <= n else s[: n - 1] + "…"

def _get_cutoff() -> Optional[datetime]:
    if TIME_FRAME_RAW == "all":
        return None
    days = int(TIME_FRAME_RAW)
    return datetime.now(timezone.utc) - timedelta(days=days)

def _choose_mode(papers_count: int) -> str:
    if MODE in ("per_paper", "summary"):
        return MODE
    # auto: big windows / many papers -> summary to avoid 429 rate limit
    if TIME_FRAME_RAW == "all":
        return "summary"
    try:
        days = int(TIME_FRAME_RAW)
    except Exception:
        days = 1
    if days >= 30 or papers_count >= 30:
        return "summary"
    return "per_paper"

def _chunk_text(lines: List[str], limit: int) -> List[str]:
    chunks: List[str] = []
    cur: List[str] = []
    cur_len = 0

    for line in lines:
        add_len = len(line) + 1
        if cur and (cur_len + add_len > limit):
            chunks.append("\n".join(cur))
            cur = [line]
            cur_len = len(line) + 1
        else:
            cur.append(line)
            cur_len += add_len

    if cur:
        chunks.append("\n".join(cur))
    return chunks

def _post_with_rate_limit(session: requests.Session, webhook_url: str, content: str) -> Tuple[bool, int, str]:
    """
    Returns (ok, status_code, response_text).
    Handles Discord 429 by waiting retry_after and retrying.
    """
    payload = {"content": content}

    for attempt in range(MAX_RETRIES_429 + 1):
        r = session.post(webhook_url, json=payload, timeout=REQUEST_TIMEOUT)
        status = r.status_code
        body = (r.text or "").strip()

        if 200 <= status < 300:
            return True, status, body

        if status == 429:
            try:
                data = r.json()
                wait = float(data.get("retry_after", 1.0))
            except Exception:
                wait = 1.0
            wait = max(0.2, min(wait, 10.0))  # clamp for sanity
            print(f"  ⏳ Rate limited (429). Waiting {wait:.3f}s (attempt {attempt+1}/{MAX_RETRIES_429})...")
            time.sleep(wait)
            continue

        return False, status, body

    return False, 429, "Exceeded retry attempts for rate limit."

def _load_topics(yaml_path: str) -> List[Dict[str, Any]]:
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    topics = data.get("topics") or []
    if not isinstance(topics, list):
        raise ValueError("YAML must contain a top-level 'topics:' list.")

    # minimal schema validation
    for t in topics:
        for k in ("id", "title", "webhook_env", "arxiv_url"):
            if k not in t or not str(t[k]).strip():
                raise ValueError(f"Topic missing required field '{k}': {t}")

    return topics


# ========= CORE =========
def run_topic(session: requests.Session, topic: Dict[str, Any], cutoff: Optional[datetime]) -> None:
    topic_id = str(topic["id"]).strip()
    title = str(topic["title"]).strip()
    webhook_env = str(topic["webhook_env"]).strip()
    arxiv_url = str(topic["arxiv_url"]).strip()

    webhook_url = os.getenv(webhook_env, "").strip()

    print("\n===== Topic =====")
    print(f"ID               : {topic_id}")
    print(f"Title            : {title}")
    print(f"Webhook env      : {webhook_env}")

    if not webhook_url:
        print(f"  ⚠️  Skipping: env var '{webhook_env}' not set.")
        return

    # --- FETCH ---
    feed = feedparser.parse(arxiv_url)

    total_fetched = len(getattr(feed, "entries", []))
    total_available = (
        feed.feed.get("opensearch_totalresults")
        or feed.feed.get("opensearch:totalresults")
        or feed.feed.get("totalresults")
    )
    status = getattr(feed, "status", None)
    bozo = getattr(feed, "bozo", None)
    bozo_exc = getattr(feed, "bozo_exception", None) if bozo else None

    print("----- arXiv fetch -----")
    print(f"Query URL         : {arxiv_url}")
    print(f"TIME_FRAME        : {TIME_FRAME_RAW}")
    if cutoff is None:
        print("Cutoff (UTC)      : (no date filtering)")
    else:
        print(f"Cutoff (UTC)      : {cutoff.isoformat()}")
    print(f"HTTP status       : {status}")
    print(f"bozo              : {bozo}")
    if bozo_exc:
        print(f"bozo_exception    : {bozo_exc}")
    print(f"Fetched entries   : {total_fetched}")
    print(f"Total results on arXiv: {total_available}")

    # If arXiv returned no entries, something is likely wrong (query too strict / API issue / parsing)
    if total_fetched == 0:
        raise RuntimeError(
            f"[{topic_id}] arXiv returned 0 entries. This usually means the query is too strict, "
            "the API had an issue, or the response could not be parsed."
        )

    # --- FILTER ---
    papers: List[Tuple[Any, datetime]] = []
    skipped_bad_date = 0

    for entry in feed.entries:
        try:
            published_dt = _parse_published_utc(entry)
        except Exception as e:
            skipped_bad_date += 1
            print(f"  Skipping entry with unparsable date: {_short(getattr(entry, 'title', ''), 70)} | error={e}")
            continue

        if cutoff is None or published_dt > cutoff:
            papers.append((entry, published_dt))

    if MAX_POSTS_PER_TOPIC > 0 and len(papers) > MAX_POSTS_PER_TOPIC:
        papers = papers[:MAX_POSTS_PER_TOPIC]

    print("----- filtering -----")
    print(f"Entries after time filter: {len(papers)}")
    if skipped_bad_date:
        print(f"Skipped (bad dates)      : {skipped_bad_date}")

    if not papers:
        print("  No articles found in the selected time window. Nothing to post.")
        return

    # --- POST ---
    post_mode = _choose_mode(len(papers))
    print("----- posting -----")
    print(f"Posting mode      : {post_mode}")

    posted_ok = 0
    posted_fail = 0

    if post_mode == "summary":
        tf = "ALL (no date filter)" if cutoff is None else f"last {TIME_FRAME_RAW} days"
        lines = [
            f"**{title} — summary**",
            f"Time window: {tf}",
            f"Fetched: {total_fetched} | After filter: {len(papers)}",
            "",
        ]

        for i, (entry, published_dt) in enumerate(papers, 1):
            t = _short((entry.title or ""), 160)
            link = (entry.link or "").strip()
            date = published_dt.strftime("%Y-%m-%d")
            lines.append(f"{i}. **{t}** ({date})")
            lines.append(f"   {link}")

        chunks = _chunk_text(lines, DISCORD_CHUNK_LIMIT)

        for idx, chunk in enumerate(chunks, 1):
            ok, code, body = _post_with_rate_limit(session, webhook_url, chunk)
            if ok:
                posted_ok += 1
                print(f"  Posted chunk {idx}/{len(chunks)} ({code})")
            else:
                posted_fail += 1
                print(f"  Failed chunk {idx}/{len(chunks)} ({code})")
                if body:
                    print("    Response:", _short(body, 200))

    else:
        # per_paper: 1 paper = 1 message
        for entry, published_dt in papers:
            title_line = (entry.title or "").replace("\n", " ").strip()
            link = (entry.link or "").strip()
            published_str = published_dt.strftime("%Y-%m-%d")
            message = f"**{title_line}**\n🗓 {published_str}\n🔗 {link}"

            ok, code, body = _post_with_rate_limit(session, webhook_url, message)
            if ok:
                posted_ok += 1
                print(f"  Posted ({code}): {_short(title_line)}")
            else:
                posted_fail += 1
                print(f"  Failed ({code}): {_short(title_line)}")
                if body:
                    print("    Response:", _short(body, 200))

            time.sleep(POST_DELAY_SECONDS)

    # --- SUMMARY ---
    print("----- topic summary -----")
    print(f"Total results on arXiv    : {total_available}")
    print(f"Total fetched from arXiv  : {total_fetched}")
    print(f"Passed time filter        : {len(papers)}")
    print(f"Successfully posted       : {posted_ok}")
    print(f"Failed to post            : {posted_fail}")


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python runner.py topics/hep.yml")
        sys.exit(2)

    yaml_path = sys.argv[1]
    cutoff = _get_cutoff()
    topics = _load_topics(yaml_path)

    print("\n==============================")
    print("arXiv → Discord runner")
    print(f"Topics file      : {yaml_path}")
    print(f"TIME_FRAME       : {TIME_FRAME_RAW}")
    print(f"MODE             : {MODE}")
    print(f"MAX_POSTS_TOPIC  : {MAX_POSTS_PER_TOPIC if MAX_POSTS_PER_TOPIC else '(no limit)'}")
    print("==============================\n")

    with requests.Session() as session:
        for topic in topics:
            run_topic(session, topic, cutoff)


if __name__ == "__main__":
    main()