#!/usr/bin/env python3
"""
Generate System Architecture Diagram for Stratus Platform
High-resolution diagram for Master's thesis
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import Client
from diagrams.onprem.network import Nginx
from diagrams.onprem.compute import Server
from diagrams.programming.framework import Django
from diagrams.onprem.database import PostgreSQL
from diagrams.programming.language import Python
from diagrams.saas.cdn import Cloudflare
from diagrams.onprem.vcs import Github
from diagrams.custom import Custom
import os

# High-resolution settings
graph_attr = {
    "fontsize": "20",
    "bgcolor": "white",
    "dpi": "300",
    "size": "16,12!",
    "ratio": "auto",
    "splines": "ortho",
    "nodesep": "1.0",
    "ranksep": "1.5",
    "pad": "1.0",
}

node_attr = {
    "fontsize": "14",
    "width": "2.5",
    "height": "2.5",
}

edge_attr = {
    "fontsize": "12",
}

output_dir = "/mnt/user-data/outputs"
os.makedirs(output_dir, exist_ok=True)

with Diagram(
    "Stratus System Architecture",
    filename=f"{output_dir}/01_system_architecture",
    show=False,
    direction="TB",
    graph_attr=graph_attr,
    node_attr=node_attr,
    edge_attr=edge_attr,
    outformat="png",
):
    # User Layer
    with Cluster("Users"):
        veterans = Client("Veterans")
        employers = Client("Employers")
        users = [veterans, employers]

    # Frontend/Application Layer
    with Cluster("Frontend Layer"):
        with Cluster("Django Templates"):
            html_templates = Server("HTML/CSS\nTemplates")
            bootstrap = Server("Bootstrap 5\nUI Framework")

    # Application Server Layer
    with Cluster("Application Layer (Railway.app)"):
        with Cluster("Web Server"):
            gunicorn = Server("Gunicorn\nWSGI Server")

        with Cluster("Django 4.2.7 Framework"):
            django_app = Django("Django Core")
            views = Python("Views Layer")
            models = Python("Models/ORM")
            middleware = Python("Middleware")

        with Cluster("Security Components"):
            auth = Server("Authentication\nPBKDF2-SHA256\n390k iterations")
            rate_limit = Server("Rate Limiting\ndjango-ratelimit")
            session = Server("Session Mgmt\n2hr timeout\nHTTPS cookies")
            security_headers = Server("Security Headers\nHSTS\nX-Frame-Options")

    # Database Layer
    with Cluster("Database Layer (Railway.app)"):
        db = PostgreSQL("PostgreSQL 15\nturntable.proxy.rlwy.net:26138\n15 Tables\n1,080 Jobs\n740 Companies")

    # External APIs
    with Cluster("External Job APIs"):
        adzuna = Server("Adzuna API\napp_id/key auth\n~700 jobs")
        usajobs = Server("USAJobs API\nHeader auth\n~380 jobs")
        jsearch = Server("JSearch API\n(Disabled)")

    # Deployment Pipeline
    with Cluster("CI/CD Pipeline"):
        github = Github("GitHub\nRepository")
        railway = Server("Railway.app\nAuto-Deploy")

    # Define connections
    # User to Frontend
    users >> Edge(label="HTTPS") >> html_templates
    html_templates >> bootstrap

    # Frontend to Application
    html_templates >> Edge(label="HTTP Request") >> gunicorn

    # Gunicorn to Django
    gunicorn >> django_app

    # Django internal flow
    django_app >> views
    views >> models
    django_app >> middleware

    # Security flow
    middleware >> auth
    middleware >> rate_limit
    middleware >> session
    middleware >> security_headers

    # Database connections
    models >> Edge(label="ORM Queries") >> db

    # External API connections
    django_app >> Edge(label="API Calls") >> adzuna
    django_app >> Edge(label="API Calls") >> usajobs

    # Deployment pipeline
    github >> Edge(label="Git Push") >> railway
    railway >> Edge(label="Deploy") >> gunicorn

print(f"✓ System Architecture Diagram saved to {output_dir}/01_system_architecture.png")
