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
time_frame = int(os.getenv("TIME_FRAME", "1"))
cutoff = datetime.now(timezone.utc) - timedelta(days=time_frame)

papers = []
for entry in feed.entries:
    published = datetime.strptime(
        entry.published,
        "%Y-%m-%dT%H:%M:%SZ"
    ).replace(tzinfo=timezone.utc)

    if published > cutoff:
        papers.append(entry)

if not papers:
    exit(0)

# ========= FORMAT MESSAGE AND SEND =========
for p in papers:
    title = p.title.replace("\n", " ")
    link = p.link
    published = p.published[:10]  # YYYY-MM-DD

    message = f"**{title}**\n {published}\n {link}"
    requests.post(WEBHOOK_URL, json={"content": message})
