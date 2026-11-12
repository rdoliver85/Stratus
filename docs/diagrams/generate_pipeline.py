#!/usr/bin/env python3
"""Stratus job import pipeline, derived from import_jobs_advanced.py and the maintenance scripts."""
from pathlib import Path

from graphviz import Digraph

OUT = Path(__file__).resolve().parent
FONT = "DejaVu Sans"

g = Digraph("stratus_pipeline", format="png", engine="dot")
g.attr(rankdir="TB", splines="spline", nodesep="0.55", ranksep="0.7", bgcolor="white", dpi="200", pad="0.5",
       fontname=FONT, fontsize="22", labelloc="t", label="Stratus job import pipeline\n ")
g.attr("node", shape="box", style="rounded,filled", fontname=FONT, fontsize="14", margin="0.18,0.12",
       color="#455A64", fillcolor="white", penwidth="1.4")
g.attr("edge", fontname=FONT, fontsize="12", color="#37474F", penwidth="1.5")
g.attr("graph", fontname=FONT)

g.node("start", "python import_jobs_advanced.py\nrun manually; API credentials come from environment variables",
       shape="ellipse", fillcolor="#C8E6C9")

with g.subgraph(name="cluster_adzuna") as c:
    c.attr(label="Adzuna (enabled)", style="rounded,filled", fillcolor="#E3F2FD", color="#1565C0",
           fontsize="16", labeljust="l")
    c.node("a1", "14 search terms: software engineer, data analyst, cloud engineer,\n"
                 "devops engineer, cybersecurity analyst, network engineer,\n"
                 "full stack developer, backend developer, frontend developer,\n"
                 "machine learning engineer, data scientist, systems administrator,\n"
                 "database administrator, security engineer\n"
                 "up to 30 jobs per term, 50 results per page", fillcolor="#BBDEFB")
    c.node("a2", "GET api.adzuna.com/v1/api/jobs/us/search/{page}\n"
                 "auth: app_id and app_key as query parameters\n"
                 "0.5 s pause between pages, 2 s between terms", fillcolor="#BBDEFB")
    c.node("a3", "Duplicate check\nMD5 of title + company + location\ncompared with jobs.import_hash", fillcolor="#BBDEFB")
    c.node("a4", "Map fields: title, company, description, salary min/max,\nlatitude/longitude, redirect URL", fillcolor="#BBDEFB")

with g.subgraph(name="cluster_usajobs") as c:
    c.attr(label="USAJobs (enabled)", style="rounded,filled", fillcolor="#FFF3E0", color="#E65100",
           fontsize="16", labeljust="l")
    c.node("u1", "3 job-category codes\n2210 (IT management)\n1550 (computer science)\n0854 (computer engineering)\n"
                 "first 100 results for each code", fillcolor="#FFE0B2")
    c.node("u2", "GET data.usajobs.gov/api/search\n"
                 "auth: Authorization-Key header and User-Agent email\n1 s pause between codes", fillcolor="#FFE0B2")
    c.node("u3", "Duplicate check\nexisting job with the same title and company name", fillcolor="#FFE0B2")
    c.node("u4", "Map fields: title, organization, QualificationSummary as description,\n"
                 "location display, position URI\ndefaults: full time, mid level, state DC", fillcolor="#FFE0B2")

g.node("js", "JSearch (RapidAPI)\ncoded with 10 queries, switched off (enabled = False)",
       style="rounded,dashed,filled", fillcolor="#F5F5F5", color="#9E9E9E", fontcolor="#616161")

with g.subgraph(name="cluster_store") as c:
    c.attr(label="Shared normalize and store steps", style="rounded,filled", fillcolor="#E8F5E9",
           color="#2E7D32", fontsize="16", labeljust="l")
    c.node("n1", "Clean description\nstrip HTML tags and extra whitespace", fillcolor="#C8E6C9")
    c.node("n2", "Find or create company\nmatch on slugified company name", fillcolor="#C8E6C9")
    c.node("n3", "Build job record\nunique slug, employment type and experience level from keywords,\n"
                 "city and state split from location text, remote flag from keywords,\n"
                 "status = active, application URL kept", fillcolor="#C8E6C9")
    c.node("n4", "INSERT into jobs\nPostgreSQL through the Django ORM", fillcolor="#A5D6A7", penwidth="2")

g.node("skip", "Skip: already imported", shape="box", style="rounded,dashed,filled", fillcolor="#FFEBEE",
       color="#C62828")

with g.subgraph(name="cluster_maint") as c:
    c.attr(label="Maintenance scripts (run separately)", style="rounded,filled", fillcolor="#F3E5F5",
           color="#6A1B9A", fontsize="16", labeljust="l")
    c.node("m1", "validate_job_urls.py\nHTTP HEAD request to each active job URL (5 s timeout)\n"
                 "missing URL, non-200 response or error: status = expired", fillcolor="#E1BEE7")
    c.node("m2", "remove_duplicates.py\ngroup by title + company, keep the newest copy", fillcolor="#E1BEE7")
    c.node("m3", "clean_source_tags.py: remove 'Source: ... (ID: ...)' lines\n"
                 "check_truncated.py: flag short or truncated descriptions", fillcolor="#E1BEE7")
    c.node("m4", "archive/veteran_experiment/tag_veteran_jobs.py (archived, not part of the import)\n"
                 "keyword match (veteran, military, clearance, ...) sets is_veteran_friendly,\n"
                 "veteran_preference and security_clearance",
           style="rounded,dashed,filled", fillcolor="#F5F5F5", color="#9E9E9E", fontcolor="#616161")

g.node("db", "PostgreSQL 15\ncompanies and jobs tables", shape="cylinder", style="filled", fillcolor="#B3E5FC",
       color="#0277BD", fontsize="15")

g.edge("start", "a1")
g.edge("start", "u1")
g.edge("start", "js", style="dashed", color="#9E9E9E")
g.edge("a1", "a2")
g.edge("a2", "a3", label=" JSON results")
g.edge("a3", "a4", label=" new")
g.edge("a3", "skip", label=" exists", style="dashed", color="#C62828")
g.edge("u1", "u2")
g.edge("u2", "u3", label=" JSON results")
g.edge("u3", "u4", label=" new")
g.edge("u3", "skip", label=" exists", style="dashed", color="#C62828")
g.edge("a4", "n1")
g.edge("u4", "n1")
g.edge("n1", "n2")
g.edge("n2", "n3")
g.edge("n3", "n4")
g.edge("n4", "db")
for upper, lower in (("m1", "m2"), ("m2", "m3"), ("m3", "m4")):
    g.edge(upper, lower, style="invis")
for m in ("m1", "m2", "m3", "m4"):
    g.edge(m, "db", style="dotted", color="#6A1B9A", arrowhead="normal")

g.render(filename="03_import_pipeline", directory=str(OUT), cleanup=True)
print("wrote", OUT / "03_import_pipeline.png")
