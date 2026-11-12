#!/usr/bin/env python3
"""Stratus database ERD, derived from the Django model definitions in this repository."""
from pathlib import Path

from graphviz import Digraph

OUT = Path(__file__).resolve().parent
FONT = "DejaVu Sans"
COLOR = {"PK": "#B71C1C", "FK": "#0D47A1", "UQ": "#4A148C", "": "#212121"}


def esc(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def table(title, rows, head="#1F3A5F", sub=None):
    html = '<<TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0" CELLPADDING="5" COLOR="#455A64" BGCOLOR="white">'
    html += (f'<TR><TD COLSPAN="3" BGCOLOR="{head}"><FONT COLOR="white" POINT-SIZE="17">'
             f'<B>{esc(title)}</B></FONT></TD></TR>')
    if sub:
        html += (f'<TR><TD COLSPAN="3" BGCOLOR="#ECEFF1"><FONT POINT-SIZE="11">'
                 f'<I>{esc(sub)}</I></FONT></TD></TR>')
    for row in rows:
        if row[0] == "--":
            html += (f'<TR><TD COLSPAN="3" BGCOLOR="#CFD8DC"><FONT POINT-SIZE="11">'
                     f'<B>{esc(row[1])}</B></FONT></TD></TR>')
            continue
        name, typ, flag = row
        color = COLOR[flag]
        bold = flag in ("PK", "FK")
        name_html = f"<B>{esc(name)}</B>" if bold else esc(name)
        tag = f"<B>{flag}</B>" if flag else "&nbsp;"
        html += (f'<TR><TD ALIGN="CENTER" WIDTH="34"><FONT COLOR="{color}" POINT-SIZE="11">{tag}</FONT></TD>'
                 f'<TD ALIGN="LEFT"><FONT COLOR="{color}" POINT-SIZE="13">{name_html}</FONT></TD>'
                 f'<TD ALIGN="LEFT"><FONT COLOR="#546E7A" POINT-SIZE="12">{esc(typ) or "&nbsp;"}</FONT></TD></TR>')
    return html + "</TABLE>>"


auth_user = [
    ("id", "bigint (auto)", "PK"), ("username", "varchar(150)", "UQ"), ("email", "varchar(254)", ""),
    ("password", "varchar(128), PBKDF2 hash", ""), ("first_name", "varchar(150)", ""),
    ("last_name", "varchar(150)", ""), ("is_active", "boolean", ""), ("is_staff", "boolean", ""),
    ("is_superuser", "boolean", ""), ("date_joined", "timestamp", ""), ("last_login", "timestamp", ""),
]

user_profiles = [
    ("profile_id", "uuid", "PK"), ("user_id", "int, one-to-one", "FK"), ("is_veteran", "boolean", ""),
    ("veteran_verified", "boolean", ""), ("military_branch", "varchar(20)", ""),
    ("years_of_service", "integer, null", ""), ("mos_code", "varchar(50)", ""),
    ("discharge_type", "varchar(50)", ""), ("current_clearance", "varchar(20)", ""),
    ("dd214_uploaded", "boolean", ""), ("verification_notes", "text", ""),
    ("created_at", "timestamp", ""), ("updated_at", "timestamp", ""),
]

companies = [
    ("company_id", "uuid", "PK"), ("name", "varchar(200)", ""), ("slug", "varchar(200)", "UQ"),
    ("description", "text", ""), ("website_url", "varchar(500)", ""), ("logo_url", "varchar(500)", ""),
    ("industry", "varchar(100)", ""), ("company_size", "varchar(50)", ""),
    ("headquarters_city", "varchar(100)", ""), ("headquarters_state", "varchar(50)", ""),
    ("is_verified", "boolean", ""), ("created_at", "timestamp", ""), ("updated_at", "timestamp", ""),
]

jobs = [
    ("--", "Listing"),
    ("job_id", "uuid", "PK"), ("company_id", "uuid", "FK"), ("title", "varchar(200)", ""),
    ("slug", "varchar(200)", ""), ("description", "text", ""), ("requirements", "text, null", ""),
    ("responsibilities", "text, null", ""), ("benefits", "text, null", ""),
    ("application_url", "varchar(500), null", ""), ("import_hash", "varchar(32), null, indexed", "UQ"),
    ("employment_type", "varchar(20)", ""), ("experience_level", "varchar(20)", ""),
    ("status", "varchar(20)", ""), ("views_count", "integer", ""), ("applications_count", "integer", ""),
    ("created_at", "timestamp", ""), ("updated_at", "timestamp", ""),
    ("--", "Salary and location"),
    ("salary_min", "integer, null", ""), ("salary_max", "integer, null", ""),
    ("salary_currency", "varchar(3)", ""), ("location_city", "varchar(100)", ""),
    ("location_state", "varchar(50)", ""), ("location_country", "varchar(50)", ""),
    ("latitude", "decimal(10,8), null", ""), ("longitude", "decimal(11,8), null", ""),
    ("is_remote", "boolean", ""), ("is_hybrid", "boolean", ""),
    ("--", "Veteran-specific fields"),
    ("is_veteran_friendly", "boolean", ""), ("veteran_preference", "boolean", ""),
    ("military_spouse_preference", "boolean", ""), ("security_clearance", "varchar(20)", ""),
    ("applicable_mos_codes", "text", ""), ("military_skills_valued", "text", ""),
    ("veteran_benefits", "text", ""), ("offers_transition_support", "boolean", ""),
]

favorite_jobs = [
    ("favorite_id", "uuid", "PK"), ("user_id", "int", "FK"), ("job_id", "uuid", "FK"),
    ("created_at", "timestamp", ""),
]

job_applications = [
    ("application_id", "uuid", "PK"), ("user_id", "int", "FK"), ("job_id", "uuid", "FK"),
    ("applied_date", "timestamp", ""), ("notes", "text", ""),
]

contact = [
    ("id", "bigint (auto)", "PK"), ("name", "varchar(100)", ""), ("email", "varchar(254)", ""),
    ("subject", "varchar(200)", ""), ("message", "text", ""), ("created_at", "timestamp", ""),
    ("ip_address", "inet, null", ""), ("user_agent", "varchar(255)", ""), ("is_read", "boolean", ""),
    ("is_spam", "boolean", ""), ("admin_notes", "text", ""), ("honeypot", "varchar(100)", ""),
]

framework = [
    ("auth_group", "", ""), ("auth_permission", "", ""), ("auth_group_permissions", "", ""),
    ("auth_user_groups", "", ""), ("auth_user_user_permissions", "", ""), ("django_admin_log", "", ""),
    ("django_content_type", "", ""), ("django_migrations", "", ""), ("django_session", "", ""),
    ("rate_limit_cache", "database cache table (production settings)", ""),
]

footnote = (
    "Derived from the Django models in this repository: 7 application tables plus 10 framework and cache tables.\n"
    "Unique constraints (user, job) on favorite_jobs and job_applications. All foreign keys use ON DELETE CASCADE.\n"
    "PK = primary key   FK = foreign key   UQ = unique   Crow's foot = many side of a one-to-many relationship.\n"
    "Not checked against the live database, which has been decommissioned."
)

g = Digraph("stratus_erd", format="png", engine="dot")
g.attr(rankdir="LR", splines="spline", nodesep="0.55", ranksep="1.7", bgcolor="white", dpi="200", pad="0.5",
       fontname=FONT, fontsize="15", labelloc="b", labeljust="l", label=footnote)
g.attr("node", shape="plain", fontname=FONT)
g.attr("edge", fontname=FONT, fontsize="13", color="#37474F", penwidth="2", dir="both",
       arrowtail="tee", arrowhead="crow", arrowsize="1.2")

g.node("companies", table("companies", companies, "#1F3A5F"))
g.node("jobs", table("jobs", jobs, "#1F3A5F"))
g.node("favorite_jobs", table("favorite_jobs", favorite_jobs, "#1F3A5F"))
g.node("job_applications", table("job_applications", job_applications, "#1F3A5F"))
g.node("auth_user", table("auth_user", auth_user, "#00695C", "Django built-in user table"))
g.node("user_profiles", table("user_profiles", user_profiles, "#00695C"))
g.node("contact", table("contact_contactmessage", contact, "#6D4C41", "no foreign keys"))
g.node("framework", table("Django framework tables", framework, "#546E7A", "no application foreign keys"))

g.edge("companies", "jobs", label="  company_id  ")
g.edge("jobs", "favorite_jobs", label="  job_id  ")
g.edge("jobs", "job_applications", label="  job_id  ")
g.edge("auth_user", "favorite_jobs", label="  user_id  ")
g.edge("auth_user", "job_applications", label="  user_id  ")
g.edge("auth_user", "user_profiles", label="  user_id (one-to-one)  ", arrowhead="tee")

with g.subgraph() as s:
    s.attr(rank="same")
    for n in ("companies", "auth_user", "contact", "framework"):
        s.node(n)

g.render(filename="02_database_erd", directory=str(OUT), cleanup=True)
print("wrote", OUT / "02_database_erd.png")
