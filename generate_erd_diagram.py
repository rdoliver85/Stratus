#!/usr/bin/env python3
"""
Generate Database ERD for Stratus Platform
High-resolution Entity-Relationship Diagram for Master's thesis
"""

from graphviz import Digraph
import os

output_dir = "/mnt/user-data/outputs"
os.makedirs(output_dir, exist_ok=True)

# Create high-resolution graph
dot = Digraph('StratusERD', format='png')
dot.attr(rankdir='TB', splines='ortho', nodesep='1.2', ranksep='1.5',
         bgcolor='white', dpi='300', size='20,16!', fontsize='14')

# Define table style
def create_table(name, fields, records=""):
    """Create a table node with fields"""
    label = f'<<TABLE BORDER="2" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8" BGCOLOR="lightblue">'
    label += f'<TR><TD COLSPAN="2" BGCOLOR="darkblue"><FONT COLOR="white" POINT-SIZE="16"><B>{name}</B></FONT></TD></TR>'
    if records:
        label += f'<TR><TD COLSPAN="2" BGCOLOR="lightgray"><FONT POINT-SIZE="12"><I>{records}</I></FONT></TD></TR>'

    for field in fields:
        field_parts = field.split('|')
        field_name = field_parts[0]
        field_type = field_parts[1] if len(field_parts) > 1 else ""

        # Check for primary key
        if 'PK' in field_name:
            label += f'<TR><TD ALIGN="LEFT"><FONT COLOR="red" POINT-SIZE="13"><B>{field_name}</B></FONT></TD><TD ALIGN="LEFT"><FONT POINT-SIZE="12">{field_type}</FONT></TD></TR>'
        # Check for foreign key
        elif 'FK' in field_name or '_id' in field_name:
            label += f'<TR><TD ALIGN="LEFT"><FONT COLOR="blue" POINT-SIZE="13"><B>{field_name}</B></FONT></TD><TD ALIGN="LEFT"><FONT POINT-SIZE="12">{field_type}</FONT></TD></TR>'
        else:
            label += f'<TR><TD ALIGN="LEFT"><FONT POINT-SIZE="13">{field_name}</FONT></TD><TD ALIGN="LEFT"><FONT POINT-SIZE="12">{field_type}</FONT></TD></TR>'

    label += '</TABLE>>'
    return label

# Core Tables
auth_user_fields = [
    "id (PK)|BigAutoField",
    "username|VARCHAR(150)",
    "email|EmailField",
    "password|VARCHAR(128)",
    "first_name|VARCHAR(150)",
    "last_name|VARCHAR(150)",
    "is_active|Boolean",
    "is_staff|Boolean",
    "is_superuser|Boolean",
    "date_joined|DateTime",
    "last_login|DateTime"
]

user_profiles_fields = [
    "id (PK)|BigAutoField",
    "user_id (FK)|OneToOne",
    "is_veteran|Boolean",
    "military_branch|VARCHAR(50)",
    "years_of_service|Integer",
    "mos_code|VARCHAR(20)",
    "current_clearance|VARCHAR(50)",
    "resume|FileField",
    "created_at|DateTime",
    "updated_at|DateTime"
]

companies_fields = [
    "id (PK)|BigAutoField",
    "name|VARCHAR(200)",
    "website|URLField",
    "location|VARCHAR(200)",
    "created_at|DateTime",
    "updated_at|DateTime"
]

jobs_fields = [
    "id (PK)|BigAutoField",
    "company_id (FK)|ForeignKey",
    "title|VARCHAR(200)",
    "description|TextField",
    "location|VARCHAR(200)",
    "salary_min|DecimalField",
    "salary_max|DecimalField",
    "employment_type|VARCHAR(50)",
    "experience_level|VARCHAR(50)",
    "status|VARCHAR(20)",
    "posted_date|DateField",
    "application_url|URLField",
    "source_api|VARCHAR(50)",
    "is_veteran_friendly|Boolean",
    "veteran_preference|Boolean",
    "security_clearance|VARCHAR(100)",
    "applicable_mos_codes|TextField",
    "military_skills_valued|TextField",
    "veteran_benefits|TextField",
    "created_at|DateTime",
    "updated_at|DateTime"
]

favorite_jobs_fields = [
    "id (PK)|BigAutoField",
    "user_id (FK)|ForeignKey",
    "job_id (FK)|ForeignKey",
    "created_at|DateTime"
]

job_applications_fields = [
    "id (PK)|BigAutoField",
    "user_id (FK)|ForeignKey",
    "job_id (FK)|ForeignKey",
    "applied_at|DateTime",
    "status|VARCHAR(50)",
    "notes|TextField"
]

contact_fields = [
    "id (PK)|BigAutoField",
    "name|VARCHAR(200)",
    "email|EmailField",
    "message|TextField",
    "created_at|DateTime"
]

# Django system tables
django_migrations_fields = [
    "id (PK)|BigAutoField",
    "app|VARCHAR(255)",
    "name|VARCHAR(255)",
    "applied|DateTime"
]

django_session_fields = [
    "session_key (PK)|VARCHAR(40)",
    "session_data|TextField",
    "expire_date|DateTime"
]

django_admin_log_fields = [
    "id (PK)|BigAutoField",
    "user_id (FK)|ForeignKey",
    "content_type_id (FK)|ForeignKey",
    "object_id|TextField",
    "action_flag|SmallInt",
    "change_message|TextField",
    "action_time|DateTime"
]

django_content_type_fields = [
    "id (PK)|BigAutoField",
    "app_label|VARCHAR(100)",
    "model|VARCHAR(100)"
]

rate_limit_fields = [
    "id (PK)|BigAutoField",
    "cache_key|VARCHAR(255)",
    "count|Integer",
    "expires|DateTime"
]

# Create nodes with clusters
with dot.subgraph(name='cluster_core') as c:
    c.attr(label='Core Application Tables', style='rounded', bgcolor='#E8F4F8', fontsize='18', color='darkblue', penwidth='3')
    c.node('auth_user', create_table('auth_user', auth_user_fields), shape='plaintext')
    c.node('user_profiles', create_table('user_profiles', user_profiles_fields), shape='plaintext')
    c.node('companies', create_table('companies', companies_fields, "740 records"), shape='plaintext')
    c.node('jobs', create_table('jobs', jobs_fields, "1,080 records"), shape='plaintext')
    c.node('favorite_jobs', create_table('favorite_jobs', favorite_jobs_fields), shape='plaintext')
    c.node('job_applications', create_table('job_applications', job_applications_fields), shape='plaintext')
    c.node('contact', create_table('contact_contactmessage', contact_fields), shape='plaintext')

with dot.subgraph(name='cluster_django') as c:
    c.attr(label='Django System Tables', style='rounded', bgcolor='#FFF4E6', fontsize='18', color='darkgreen', penwidth='3')
    c.node('django_migrations', create_table('django_migrations', django_migrations_fields), shape='plaintext')
    c.node('django_session', create_table('django_session', django_session_fields), shape='plaintext')
    c.node('django_admin_log', create_table('django_admin_log', django_admin_log_fields), shape='plaintext')
    c.node('django_content_type', create_table('django_content_type', django_content_type_fields), shape='plaintext')
    c.node('rate_limit_cache', create_table('rate_limit_cache', rate_limit_fields), shape='plaintext')

# Define relationships with labels
# OneToOne relationship
dot.edge('auth_user', 'user_profiles', label='1:1\nOneToOne', color='red', penwidth='3', fontsize='12', style='bold')

# OneToMany relationships from auth_user
dot.edge('auth_user', 'favorite_jobs', label='1:N\nOneToMany', color='blue', penwidth='2', fontsize='12')
dot.edge('auth_user', 'job_applications', label='1:N\nOneToMany', color='blue', penwidth='2', fontsize='12')
dot.edge('auth_user', 'django_admin_log', label='1:N\nOneToMany', color='darkgreen', penwidth='1.5', fontsize='11', style='dashed')

# OneToMany from companies
dot.edge('companies', 'jobs', label='1:N\nOneToMany', color='blue', penwidth='2', fontsize='12')

# ManyToOne from favorites and applications to jobs
dot.edge('jobs', 'favorite_jobs', label='1:N\nOneToMany', color='blue', penwidth='2', fontsize='12')
dot.edge('jobs', 'job_applications', label='1:N\nOneToMany', color='blue', penwidth='2', fontsize='12')

# Django admin relationships
dot.edge('django_content_type', 'django_admin_log', label='1:N\nOneToMany', color='darkgreen', penwidth='1.5', fontsize='11', style='dashed')

# Add legend
legend = '''<<TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0" CELLPADDING="6" BGCOLOR="white">
<TR><TD COLSPAN="2" BGCOLOR="gray"><FONT POINT-SIZE="14"><B>Legend</B></FONT></TD></TR>
<TR><TD ALIGN="LEFT"><FONT COLOR="red" POINT-SIZE="12"><B>Red Text</B></FONT></TD><TD ALIGN="LEFT">Primary Key (PK)</TD></TR>
<TR><TD ALIGN="LEFT"><FONT COLOR="blue" POINT-SIZE="12"><B>Blue Text</B></FONT></TD><TD ALIGN="LEFT">Foreign Key (FK)</TD></TR>
<TR><TD ALIGN="LEFT"><FONT POINT-SIZE="12">Red Line (Bold)</FONT></TD><TD ALIGN="LEFT">OneToOne Relationship</TD></TR>
<TR><TD ALIGN="LEFT"><FONT POINT-SIZE="12">Blue Line</FONT></TD><TD ALIGN="LEFT">OneToMany Relationship</TD></TR>
<TR><TD ALIGN="LEFT"><FONT POINT-SIZE="12">Green Line (Dashed)</FONT></TD><TD ALIGN="LEFT">Django System Relationship</TD></TR>
</TABLE>>'''

dot.node('legend', legend, shape='plaintext')

# Render the diagram
output_file = f"{output_dir}/02_database_erd"
dot.render(output_file, cleanup=True)

print(f"✓ Database ERD Diagram saved to {output_file}.png")
