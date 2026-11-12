#!/usr/bin/env python3
"""Stratus system architecture as deployed in Dec 2025 (since decommissioned)."""
from pathlib import Path

from diagrams import Cluster, Diagram, Edge
from diagrams.onprem.client import Users
from diagrams.onprem.compute import Server
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.network import Gunicorn
from diagrams.onprem.vcs import Github
from diagrams.programming.framework import Django
from diagrams.programming.language import Python

OUT = Path(__file__).resolve().parent

title = (
    "Stratus system architecture as deployed (Dec 2025; since decommissioned)\n"
    "Security controls are those defined in the repository (production_settings.py: HTTPS-only cookies, 2-hour sessions, HSTS).\n"
    "wsgi.py defaults to settings.py unless the host sets DJANGO_SETTINGS_MODULE."
)

graph_attr = {"fontsize": "20", "bgcolor": "white", "dpi": "200", "pad": "0.6", "nodesep": "1.7",
              "ranksep": "1.2", "splines": "spline", "fontname": "DejaVu Sans"}
node_attr = {"fontsize": "15", "fontname": "DejaVu Sans"}
edge_attr = {"fontsize": "13", "fontname": "DejaVu Sans", "color": "#37474F", "penwidth": "1.6"}

with Diagram(title, filename=str(OUT / "01_system_architecture"), show=False, direction="TB",
             graph_attr=graph_attr, node_attr=node_attr, edge_attr=edge_attr, outformat="png"):
    visitors = Users("Job seekers\n(veterans and others)\nBootstrap 5 pages")

    with Cluster("Deployment"):
        repo = Github("GitHub\nmain branch")
        build = Server("Railway build (Nixpacks)\ncollectstatic, migrate,\ngunicorn")

    with Cluster("Railway hosting"):
        web = Gunicorn("Gunicorn\nWSGI server\nWhiteNoise static files")
        with Cluster("Django 4.2.7 project"):
            core = Django("URL routing\nand middleware")
            pages = Python("public_site\njob search and detail pages")
            jobs = Python("jobs and companies\nsaved jobs, application\ntracking")
            accounts = Python("accounts\nregister, login, profile")
            contact = Python("contact\nform with honeypot")
        with Cluster("Security controls"):
            limits = Server("django-ratelimit\nlogin 5/min, sign-up 3/hr,\ncontact 5/hr (per IP)")
            sessions = Server("Sessions and cookies\nHTTPS-only, HttpOnly,\n2 h timeout")
            hashing = Server("Password hashing\nPBKDF2-SHA256\n(Django default)")
            headers = Server("Security headers\nHSTS, X-Frame-Options\nCSP written, disabled")
        db = PostgreSQL("PostgreSQL 15\nRailway database")

    with Cluster("Offline import scripts (Django ORM)"):
        importer = Python("import_jobs_advanced.py\nvalidate_job_urls.py\nremove_duplicates.py")

    with Cluster("External job APIs"):
        adzuna = Server("Adzuna API\napp_id and app_key")
        usajobs = Server("USAJobs API\nAuthorization-Key header")
        jsearch = Server("JSearch (RapidAPI)\ndisabled")

    visitors >> Edge(label="HTTPS") >> web >> core
    core >> [pages, jobs, accounts, contact]
    web >> Edge(style="invis") >> [limits, sessions, hashing, headers]
    [pages, jobs, accounts, contact] >> Edge(label="ORM queries") >> db

    repo >> Edge(label="push") >> build >> Edge(label="deploy") >> web

    importer >> Edge(label="REST / JSON") >> [adzuna, usajobs]
    importer >> Edge(style="dashed", color="#9E9E9E") >> jsearch
    importer >> Edge(label="writes jobs and companies") >> db

print("wrote", OUT / "01_system_architecture.png")
