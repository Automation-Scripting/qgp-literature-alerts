import os
import feedparser
import requests
from datetime import datetime, timedelta, timezone

# ========= CONFIG =========
WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL_QGP_BARYOGENESIS"]

ARXIV_URL = (
    "http://export.arxiv.org/api/query?"
    "search_query=("
        "cat:hep-ph+OR+cat:hep-th+OR+cat:astro-ph.CO+OR+cat:gr-qc"
    ")"
    "+AND+("
        "abs:baryogenesis"
        "+OR+abs:%22baryon+asymmetry%22"
        "+OR+abs:%22matter+antimatter+asymmetry%22"
        "+OR+abs:leptogenesis"
        "+OR+abs:%22Sakharov+conditions%22"
    ")"
    "&sortBy=submittedDate"
    "&sortOrder=descending"
    "&max_results=50"
)

# ========= FETCH =========
feed = feedparser.parse(ARXIV_URL)
time_frame = int(os.getenv("TIME_FRAME", "1"))
cutoff = datetime.utcnow() - timedelta(days=time_frame)

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

# ========= FORMAT MESSAGE =========
lines = ["**arXiv qgp-bayesian-inference — novos papers (últimas 24h) - Limitado a 20 resultados**\n"]

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
