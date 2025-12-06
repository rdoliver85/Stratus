#!/usr/bin/env python3
"""
Generate API Integration Flow Diagram for Stratus Platform
High-resolution flow diagram showing API integration pipeline for Master's thesis
"""

from graphviz import Digraph
import os

output_dir = "/mnt/user-data/outputs"
os.makedirs(output_dir, exist_ok=True)

# Create high-resolution graph
dot = Digraph('StratusAPIFlow', format='png')
dot.attr(rankdir='TB', splines='spline', nodesep='0.8', ranksep='1.2',
         bgcolor='white', dpi='300', size='18,24!', fontsize='14')

# Define node styles
dot.attr('node', shape='box', style='rounded,filled', fontsize='13', width='2.8', height='0.8')

# Start Node
dot.node('start', 'Start Job Aggregation\nCron Job / Manual Trigger',
         fillcolor='lightgreen', shape='ellipse', width='3', height='1.2', fontsize='14')

# API Authentication Phase
with dot.subgraph(name='cluster_auth') as c:
    c.attr(label='Authentication Phase', style='rounded', bgcolor='#E3F2FD', fontsize='16', color='blue', penwidth='2')
    c.node('auth_adzuna', 'Adzuna API Auth\napp_id: ADZUNA_APP_ID\napp_key: ADZUNA_API_KEY', fillcolor='#BBDEFB')
    c.node('auth_usajobs', 'USAJobs API Auth\nHeader: Authorization-Key\nUser-Agent: email@domain.com', fillcolor='#BBDEFB')
    c.node('auth_jsearch', 'JSearch API\n(DISABLED)', fillcolor='#FFCDD2', style='rounded,filled,dashed')

# Search Query Phase
with dot.subgraph(name='cluster_search') as c:
    c.attr(label='Search Query Execution', style='rounded', bgcolor='#FFF3E0', fontsize='16', color='orange', penwidth='2')
    c.node('search_adzuna', 'Execute Adzuna Searches\n14 search terms:\n• software engineer\n• data analyst\n• cloud engineer\n• cybersecurity\n• IT support\n• network admin\n• devops\n• systems admin\n• database admin\n• web developer\n• full stack\n• QA engineer\n• project manager\n• scrum master', fillcolor='#FFE0B2', height='3.5')
    c.node('search_usajobs', 'Execute USAJobs Searches\nJob codes:\n• 2210 (IT Management)\n• 1550 (Computer Science)\n• 0854 (Computer Engineering)', fillcolor='#FFE0B2', height='2')

# Response Parsing Phase
with dot.subgraph(name='cluster_parse') as c:
    c.attr(label='Response Parsing', style='rounded', bgcolor='#F3E5F5', fontsize='16', color='purple', penwidth='2')
    c.node('parse_adzuna', 'Parse Adzuna JSON\nExtract:\n• title, company, location\n• salary_min, salary_max\n• description (500 char)\n• application_url\n• posted_date', fillcolor='#E1BEE7', height='2')
    c.node('parse_usajobs', 'Parse USAJobs JSON\nExtract:\n• title, company, location\n• job_code, grade\n• full description\n• application_url\n• posted_date', fillcolor='#E1BEE7', height='2')

# Data Normalization Phase
with dot.subgraph(name='cluster_normalize') as c:
    c.attr(label='Data Normalization & Processing', style='rounded', bgcolor='#E8F5E9', fontsize='16', color='green', penwidth='2')
    c.node('normalize', 'Normalize Data Fields\n• Standardize location format\n• Convert salary to decimal\n• Clean description text\n• Parse employment type\n• Determine experience level', fillcolor='#C8E6C9', height='2.2')
    c.node('duplicate', 'Duplicate Detection\nIndexed lookup:\ntitle + company_name\nCheck existing jobs table', fillcolor='#C8E6C9', height='1.5')

# Company Processing Phase
with dot.subgraph(name='cluster_company') as c:
    c.attr(label='Company Management', style='rounded', bgcolor='#FCE4EC', fontsize='16', color='pink', penwidth='2')
    c.node('company_lookup', 'Company Lookup\nSearch by name', fillcolor='#F8BBD0')
    c.node('company_create', 'Create Company?\nIf not exists', fillcolor='#F8BBD0', shape='diamond', width='2.5')
    c.node('company_save', 'Save Company Record\nname, website, location', fillcolor='#F8BBD0')

# Veteran Tagging Phase
with dot.subgraph(name='cluster_veteran') as c:
    c.attr(label='Veteran-Specific Tagging', style='rounded', bgcolor='#FFF9C4', fontsize='16', color='#F9A825', penwidth='2')
    c.node('veteran_tag', 'Keyword-Based Tagging\nSearch for:\n• "veteran"\n• "clearance"\n• "security clearance"\n• "military"\n• "TS/SCI", "Secret"\n• MOS codes\n• "transition"', fillcolor='#FFF59D', height='2.5')
    c.node('veteran_fields', 'Set Veteran Fields\n• is_veteran_friendly\n• veteran_preference\n• security_clearance\n• applicable_mos_codes\n• military_skills_valued\n• veteran_benefits', fillcolor='#FFF59D', height='2.2')

# Database Insertion Phase
with dot.subgraph(name='cluster_db') as c:
    c.attr(label='Database Operations', style='rounded', bgcolor='#E0F2F1', fontsize='16', color='teal', penwidth='2')
    c.node('db_insert', 'Insert Job Record\nPostgreSQL 15\njobs table', fillcolor='#B2DFDB')
    c.node('url_validate', 'URL Validation\nHTTP HEAD request\nMark expired if 404', fillcolor='#B2DFDB', height='1.2')

# Results Phase
with dot.subgraph(name='cluster_results') as c:
    c.attr(label='Results & Logging', style='rounded', bgcolor='#EFEBE9', fontsize='16', color='brown', penwidth='2')
    c.node('stats', 'Generate Statistics\n• Total jobs fetched\n• New jobs added\n• Duplicates skipped\n• Companies created\n• Veteran jobs tagged', fillcolor='#D7CCC8', height='2')
    c.node('log', 'Log Results\nDjango logger\nTimestamp, counts, errors', fillcolor='#D7CCC8')

# End Node
dot.node('end', 'Job Aggregation Complete\nDatabase Updated',
         fillcolor='lightcoral', shape='ellipse', width='3', height='1.2', fontsize='14')

# Define flow connections
dot.edge('start', 'auth_adzuna')
dot.edge('start', 'auth_usajobs')
dot.edge('start', 'auth_jsearch', style='dashed', color='gray')

dot.edge('auth_adzuna', 'search_adzuna', label='Authenticated', fontsize='11')
dot.edge('auth_usajobs', 'search_usajobs', label='Authenticated', fontsize='11')

dot.edge('search_adzuna', 'parse_adzuna', label='~700 results', fontsize='11', color='darkblue')
dot.edge('search_usajobs', 'parse_usajobs', label='~380 results', fontsize='11', color='darkblue')

dot.edge('parse_adzuna', 'normalize')
dot.edge('parse_usajobs', 'normalize')

dot.edge('normalize', 'duplicate', label='For each job', fontsize='11')

# Duplicate check flow
dot.edge('duplicate', 'company_lookup', label='Not duplicate', fontsize='11', color='green')
dot.edge('duplicate', 'stats', label='Is duplicate\n(skip)', fontsize='11', color='red', style='dashed')

dot.edge('company_lookup', 'company_create')
dot.edge('company_create', 'company_save', label='No', fontsize='11')
dot.edge('company_create', 'veteran_tag', label='Yes\n(exists)', fontsize='11', color='green')
dot.edge('company_save', 'veteran_tag')

dot.edge('veteran_tag', 'veteran_fields', label='Keywords found', fontsize='11')
dot.edge('veteran_fields', 'db_insert')
dot.edge('veteran_tag', 'db_insert', label='No keywords', fontsize='11', style='dashed')

dot.edge('db_insert', 'url_validate')
dot.edge('url_validate', 'stats')

dot.edge('stats', 'log')
dot.edge('log', 'end')

# Add summary box
summary = '''<<TABLE BORDER="2" CELLBORDER="0" CELLSPACING="4" CELLPADDING="8" BGCOLOR="lightyellow">
<TR><TD COLSPAN="2" BGCOLOR="gold"><FONT POINT-SIZE="16"><B>Pipeline Summary</B></FONT></TD></TR>
<TR><TD ALIGN="LEFT"><B>Total Jobs Aggregated:</B></TD><TD ALIGN="LEFT">~1,080</TD></TR>
<TR><TD ALIGN="LEFT"><B>Adzuna Contribution:</B></TD><TD ALIGN="LEFT">~700 jobs</TD></TR>
<TR><TD ALIGN="LEFT"><B>USAJobs Contribution:</B></TD><TD ALIGN="LEFT">~380 jobs</TD></TR>
<TR><TD ALIGN="LEFT"><B>Total Companies:</B></TD><TD ALIGN="LEFT">740</TD></TR>
<TR><TD ALIGN="LEFT"><B>Security Features:</B></TD><TD ALIGN="LEFT">PBKDF2-SHA256 (390k iterations)<BR/>Rate limiting (5/min login)<BR/>Session timeout (2 hours)</TD></TR>
<TR><TD ALIGN="LEFT"><B>Database:</B></TD><TD ALIGN="LEFT">PostgreSQL 15 (Railway.app)</TD></TR>
</TABLE>>'''

dot.node('summary', summary, shape='plaintext')

# Render the diagram
output_file = f"{output_dir}/03_api_integration_flow"
dot.render(output_file, cleanup=True)

print(f"✓ API Integration Flow Diagram saved to {output_file}.png")
