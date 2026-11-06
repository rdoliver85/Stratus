# Stratus - Veteran-Focused Technology Job Platform

A comprehensive job aggregation platform designed to connect veterans with technology career opportunities. This system integrates multiple job APIs to provide a unified search experience with veteran-specific features and preferences.

## Project Overview

Stratus is a Master's independent internship project developed for the Master of Science in Information Technology program at Arkansas Tech University. The platform addresses the unique challenges veterans face when transitioning to civilian technology careers by aggregating job listings from multiple sources and highlighting positions that value military experience, security clearances, and veteran benefits.

**Live Platform**: https://www.stratusjobs.com

## Current Metrics

- **Total Jobs**: 1,080 active listings
- **Companies**: 740 unique employers
- **API Sources**: Adzuna (approximately 700 jobs), USAJobs (approximately 380 jobs)
- **Database Tables**: 15 tables managing users, profiles, jobs, companies, and applications

## Technology Stack

### Backend Framework
- **Django**: 4.2.7
- **Python**: 3.11+
- **WSGI Server**: Gunicorn

### Database
- **PostgreSQL**: 15
- **Hosting**: Railway.app (turntable.proxy.rlwy.net:26138)

### Frontend
- **Template Engine**: Django Templates
- **UI Framework**: Bootstrap 5
- **Markup**: HTML5/CSS3

### External APIs
- **Adzuna API**: Job aggregation with app_id/key authentication
- **USAJobs API**: Government positions with header-based authentication
- **JSearch API**: Currently disabled

### Deployment & Infrastructure
- **Hosting Platform**: Railway.app
- **Version Control**: GitHub
- **CI/CD**: Automated deployment on push to main branch

### Security Features
- **Password Hashing**: PBKDF2-SHA256 (390,000 iterations)
- **Rate Limiting**: django-ratelimit (5 login attempts/min, 3 registrations/hr, 5 contact submissions/hr)
- **Session Management**: 2-hour timeout, HTTPS-only cookies
- **Security Headers**: HSTS, X-Frame-Options

## Core Features

### Job Aggregation
- Multi-source API integration with intelligent duplicate detection
- Automated job data normalization and standardization
- Company profile creation and management
- URL validation to identify expired listings

### Veteran-Specific Features
- Veteran-friendly job tagging based on keyword analysis
- Security clearance requirements highlighting
- Military Occupational Specialty (MOS) code mapping
- Military skills translation and recognition
- Veteran preference indicators
- Military benefits information

### User Management
- User authentication and profile management
- Veteran status and military service tracking
- Resume upload and storage
- Job application tracking
- Favorite jobs management

### Search Capabilities
- 14 technology-focused search terms
- Location-based filtering
- Salary range filtering
- Employment type categorization
- Experience level matching

## Database Architecture

The platform utilizes a relational database design with 15 tables:

**Core Tables**:
- `auth_user`: Django authentication (built-in)
- `user_profiles`: Extended user information including veteran status, military branch, years of service, MOS code, security clearance
- `companies`: Company information (740 records)
- `jobs`: Job listings with veteran-specific fields (1,080 records)
- `favorite_jobs`: User-saved jobs
- `job_applications`: Application tracking and status management
- `contact_contactmessage`: Contact form submissions

**System Tables**:
- Django migrations, sessions, admin logs, content types, rate limiting cache

## API Integration Pipeline

1. **Authentication**: API credentials validation (app_id/key for Adzuna, header authorization for USAJobs)
2. **Query Execution**: Systematic searches across 14 technology job categories and 3 government job codes
3. **Response Parsing**: JSON data extraction and field mapping
4. **Data Normalization**: Standardization of location, salary, and employment type fields
5. **Duplicate Detection**: Indexed lookup by title and company name
6. **Company Management**: Automatic company record creation or association
7. **Veteran Tagging**: Keyword-based analysis for military-relevant positions
8. **Database Insertion**: Atomic transaction processing
9. **URL Validation**: HTTP verification of application links
10. **Statistics Logging**: Aggregation metrics and error tracking

## Academic Context

**Institution**: Arkansas Tech University
**Program**: Master of Science in Information Technology
**Author**: Richard Oliver
**Submission Date**: December 2025

This independent internship project demonstrates practical application of advanced database design, API integration, web application security, and user-centered design principles for a specialized user demographic.

## Documentation

High-resolution diagrams for independent internship documentation are available in the `independent internship_diagrams/` directory:
- System Architecture Diagram
- Database Entity-Relationship Diagram
- API Integration Flow Diagram

## License

This project is submitted as academic work for Arkansas Tech University.
