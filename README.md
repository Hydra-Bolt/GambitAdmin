# Gambit Admin API

## Overview

Gambit Admin API is a comprehensive Flask-based backend system designed to manage a sports content platform. This API provides administrative capabilities for managing users, sports leagues, teams, players, content, subscribers, and other aspects of the platform with proper security and role-based access controls.

## Table of Contents

- [System Architecture](#system-architecture)
- [Authentication & Authorization](#authentication--authorization)
- [API Endpoints](#api-endpoints)
- [Permission Types](#permission-types)
- [Data Models](#data-models)
- [Response Format](#response-format)
- [Authentication Flow](#authentication-flow)
- [Security Features](#security-features)
- [Setup & Installation](#setup--installation)
- [Environment Variables](#environment-variables)

## System Architecture

The Gambit Admin API is built with:
- **Framework**: Flask
- **Database**: SQLAlchemy ORM with SQLite (configurable)
- **Authentication**: JWT (JSON Web Token) + Flask-Login
- **Security**: Role-based access control

The system follows a modular architecture with components organized by feature into separate blueprints.

## Authentication & Authorization

- **JWT Authentication**: Bearer token authentication in the Authorization header
- **Token Expiration**: Access tokens expire after 1 hour
- **Refresh Tokens**: Valid for 30 days
- **Role-based Access**: Granular permission system with defined access types

## API Endpoints

### Authentication (/api/auth)

| Endpoint | Method | Description | Permission Required |
|----------|--------|-------------|---------------------|
| /api/auth/test | GET | Test if API is working | None |
| /api/auth/test-jwt | GET | Test JWT authentication | None |
| /api/auth/login | POST | Login with username and password | None |
| /api/auth/me | GET | Get current user profile | JWT Auth |
| /api/auth/change-password | POST | Change user's password | JWT Auth |

### Users Management (/api/users)

| Endpoint | Method | Description | Permission Required |
|----------|--------|-------------|---------------------|
| /api/users/ | GET | List all users with optional filtering | USERS |
| /api/users/<id> | GET | Get specific user by ID | USERS |
| /api/users/uuid/<uuid> | GET | Get specific user by UUID | USERS |
| /api/users/ | POST | Create a new user | USERS |
| /api/users/<id> | PUT | Update an existing user | USERS |
| /api/users/<id> | DELETE | Delete a user | USERS |
| /api/users/stats | GET | Get user statistics | USERS |
| /api/users/activity | GET | Get user activity data for charting | USERS |
| /api/users/profile/uuid/<uuid> | GET | Get detailed user profile with favorites | USERS |
| /api/users/profile/uuid/<uuid>/update-favorites | PUT | Update user's favorites | USERS |
| /api/users/profile/uuid/<uuid>/restrict | POST | Restrict a user (set status to suspended) | USERS |

### Teams Management (/api/teams)

| Endpoint | Method | Description | Permission Required |
|----------|--------|-------------|---------------------|
| /api/teams/ | GET | List all teams with optional filtering | LEAGUES |
| /api/teams/<id> | GET | Get specific team by ID | LEAGUES |
| /api/teams/ | POST | Create a new team | LEAGUES |
| /api/teams/<id> | PUT | Update an existing team | LEAGUES |
| /api/teams/<id> | DELETE | Delete a team | LEAGUES |
| /api/teams/popular | GET | Get most popular teams | LEAGUES |

### Roles Management (/api/roles)

| Endpoint | Method | Description | Permission Required |
|----------|--------|-------------|---------------------|
| /api/roles/ | GET | List all roles with pagination | ROLES |
| /api/roles/<id> | GET | Get specific role by ID | ROLES |
| /api/roles/ | POST | Create a new role | ROLES |
| /api/roles/<id> | PUT | Update an existing role | ROLES |
| /api/roles/<id> | DELETE | Delete a role | ROLES |
| /api/roles/permissions | GET | Get all available permissions | ROLES |
| /api/roles/admin-assignments | GET | Get all admin-role assignments | ROLES |
| /api/roles/assign | POST | Assign a role to an admin | ROLES |
| /api/roles/unassign | POST | Remove a role from an admin | ROLES |

### Reels Management (/api/reels)

| Endpoint | Method | Description | Permission Required |
|----------|--------|-------------|---------------------|
| /api/reels/ | GET | List all reels with optional filtering | REELS |
| /api/reels/<id> | GET | Get specific reel by ID with enriched data | REELS |
| /api/reels/popular | GET | Get most popular reels | REELS |
| /api/reels/with-player-details | GET | Get reels with player, team, league details | REELS |

### Players Management (/api/players)

| Endpoint | Method | Description | Permission Required |
|----------|--------|-------------|---------------------|
| /api/players/ | GET | List all players with optional filtering | JWT Auth |
| /api/players/<id> | GET | Get specific player by ID | JWT Auth |
| /api/players/popular | GET | Get most popular players | JWT Auth |

### Dashboard (/api/dashboard)

| Endpoint | Method | Description | Permission Required |
|----------|--------|-------------|---------------------|
| /api/dashboard/ | GET | Get all dashboard data | None |
| /api/dashboard/subscribers | GET | Get subscriber overview | None |
| /api/dashboard/users | GET | Get user statistics overview | None |
| /api/dashboard/popular | GET | Get most popular content | None |
| /api/dashboard/manage-leagues | GET | Serve the manage leagues page | None |

### Admins Management (/api/admins)

| Endpoint | Method | Description | Permission Required |
|----------|--------|-------------|---------------------|
| /api/admins/ | GET | List all admins with pagination | ROLES |
| /api/admins/<id> | GET | Get specific admin by ID | ROLES |
| /api/admins/ | POST | Create a new admin user | ROLES |
| /api/admins/<id> | PUT | Update an existing admin | ROLES |
| /api/admins/<id> | DELETE | Delete an admin | ROLES |
| /api/admins/<id>/toggle-status | PATCH | Toggle admin active status | ROLES |

### Leagues Management (/api/leagues)

| Endpoint | Method | Description | Permission Required |
|----------|--------|-------------|---------------------|
| /api/leagues/ | GET | List all leagues with optional filtering | LEAGUES |
| /api/leagues/<id> | GET | Get specific league by ID | LEAGUES |
| /api/leagues/ | POST | Create a new league | LEAGUES |
| /api/leagues/<id> | PUT | Update an existing league | LEAGUES |
| /api/leagues/<id> | DELETE | Delete a league | LEAGUES |

### Subscribers Management (/api/subscribers)

| Endpoint | Method | Description | Permission Required |
|----------|--------|-------------|---------------------|
| /api/subscribers/ | GET | List all subscribers with optional filtering | SUBSCRIBERS |
| /api/subscribers/<id> | GET | Get specific subscriber by ID | SUBSCRIBERS |
| /api/subscribers/stats | GET | Get subscriber statistics | SUBSCRIBERS |

### Content Management (/api/content)

| Endpoint | Method | Description | Permission Required |
|----------|--------|-------------|---------------------|
| /api/content/ | GET | List all content items | CONTENT |
| /api/content/<id> | GET | Get specific content item | CONTENT |
| /api/content/ | POST | Create new content | CONTENT |
| /api/content/<id> | PUT | Update content | CONTENT |
| /api/content/<id> | DELETE | Delete content | CONTENT |

### Notifications Management (/api/notifications)

| Endpoint | Method | Description | Permission Required |
|----------|--------|-------------|---------------------|
| /api/notifications/ | GET | List all notifications | NOTIFICATION |
| /api/notifications/<id> | GET | Get notification details | NOTIFICATION |
| /api/notifications/ | POST | Send new notification | NOTIFICATION |

## Permission Types

The system implements role-based access control with the following permission types:

| Permission | Description |
|------------|-------------|
| CONTENT | Content Management |
| NOTIFICATION | Notification Management |
| LEAGUES | Leagues Management |
| REELS | Reels Management |
| USERS | Users Management |
| SUBSCRIBERS | Subscribers Management |
| ROLES | Roles Management |
| ALL | All Permissions (Super Admin) |

## Data Models

The system includes several data models:
- **UserModel** - End users of the platform
- **AdminModel** - Administrative users
- **RoleModel** - Defines roles with permissions
- **TeamModel** - Sports teams
- **LeagueModel** - Sports leagues
- **PlayerModel** - Athletes
- **ReelModel** - Video content
- **UserActivityModel** - Tracks user engagement
- **SubscriberModel** - Paying subscribers

## Response Format

All API endpoints use a standardized response format:
- Success responses are formatted using `format_response()`
- Error responses are formatted using `format_error()`
- Consistent error handling with proper HTTP status codes

## Authentication Flow

1. Admin users authenticate via `/api/auth/login` with username/password
2. Upon successful authentication, the server returns a JWT token
3. Clients include this token in the Authorization header for subsequent requests
4. The `@jwt_required()` decorator ensures protection of secured endpoints
5. The `@require_permission()` decorator ensures proper role-based access

## Security Features

- Password hashing for admin accounts
- JWT expiration and refresh mechanism
- Role-based access control
- Input validation on all endpoints
- Error logging
- Protection against self-deactivation/deletion for admin accounts

## Setup & Installation

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv env
   ```
3. Activate the virtual environment:
   - Windows: `env\Scripts\activate`
   - Linux/Mac: `source env/bin/activate`
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Set up environment variables (see [Environment Variables](#environment-variables))
6. Initialize the database:
   ```
   python main.py
   ```
7. Run the application:
   ```
   python app.py
   ```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | Database connection string | sqlite:///instance/gambit.db |
| SESSION_SECRET | Secret key for session | dev_secret_key |
| JWT_SECRET_KEY | Secret key for JWT tokens | dev-key-123456 |
| FLASK_ENV | Flask environment | development |

## API Documentation

A Swagger UI for the API is available at `/api/docs` when the application is running.

---

© 2025 Gambit Admin API. All rights reserved.