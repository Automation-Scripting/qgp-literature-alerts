import os
import feedparser
import requests
from datetime import datetime, timedelta, timezone

# ========= CONFIG =========
WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL_HEPPH"]

ARXIV_URL = (
    "http://export.arxiv.org/api/query?"
    "search_query=cat:hep-ph"
    "&sortBy=submittedDate"
    "&sortOrder=descending"
    "&max_results=50"
)

# ========= FETCH =========
feed = feedparser.parse(ARXIV_URL)
yesterday = datetime.now(timezone.utc) - timedelta(days=1)

papers = []
for entry in feed.entries:
    published = datetime.strptime(
        entry.published,
        "%Y-%m-%dT%H:%M:%SZ"
    ).replace(tzinfo=timezone.utc)

    if published > yesterday:
        papers.append(entry)

if not papers:
    exit(0)

# ========= FORMAT MESSAGE =========
lines = ["**arXiv hep-ph — novos papers (últimas 24h)**\n"]

for p in papers:
    title = p.title.replace("\n", " ")
    link = p.link
    lines.append(f"• **{title}**\n  {link}")

# ========= SEND =========
requests.post(
    WEBHOOK_URL,
    json={"content": "\n".join(lines)}
)
