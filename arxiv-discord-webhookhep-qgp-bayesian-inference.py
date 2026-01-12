import os
import feedparser
import requests
from datetime import datetime, timedelta, timezone

# ========= CONFIG =========
WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL_BAYESIAN_QGP"]

ARXIV_URL = (
    "http://export.arxiv.org/api/query?"
    "search_query=("
        "cat:hep-ph+OR+cat:hep-lat+OR+cat:nucl-th"
    ")"
    "+AND+("
        "abs:bayesian"
        "+OR+abs:%22Bayesian+inference%22"
        "+OR+abs:%22Bayesian+analysis%22"
    ")"
    "+AND+("
        "abs:%22quark+gluon+plasma%22"
        "+OR+abs:QGP"
    ")"
    "&sortBy=submittedDate"
    "&sortOrder=descending"
    "&max_results=20"
)

# ========= FETCH =========
feed = feedparser.parse(ARXIV_URL)
yesterday = datetime.utcnow() - timedelta(days=1)

papers = []
for entry in feed.entries:
    published = datetime.strptime(entry.published, "%Y-%m-%dT%H:%M:%SZ")
    if published > yesterday:
        papers.append(entry)

if not papers:
    exit(0)

# ========= FORMAT MESSAGE =========
lines = ["**arXiv qgp-bayesian-inference — novos papers (últimas 24h)**\n"]

for p in papers:
    title = p.title.replace("\n", " ")
    link = p.link
    lines.append(f"• **{title}**\n  {link}")

message = "\n".join(lines)

# ========= SEND =========
requests.post(
    WEBHOOK_URL,
    json={"content": message}
)
