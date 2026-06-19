# Kan Mind - Task Management System

A Django-based REST API for collaborative task management with boards, tasks, and team collaboration features.

## Features

- **Custom User Authentication** - Email-based authentication system
- **Collaborative Boards** - Create and share boards with team members
- **Task Management** - Create, assign, and track tasks with priority and status
- **Comments & Reviews** - Comment on tasks and assign reviewers
- **REST API** - Full REST API for seamless integration

## Requirements

- Python 3.8 or higher
- Django 6.0.6
- Django REST Framework 3.17.1

## Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd kan_mind
```

### 2. Create a Virtual Environment

#### On Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### On Windows (Command Prompt):
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

#### On macOS/Linux:
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Database Setup

### 1. Run Migrations

```bash
python manage.py migrate
```

This will create the SQLite database (`db.sqlite3`) and initialize all tables.

### 2. Create a Superuser (Admin Account)

```bash
python manage.py createsuperuser
```

You'll be prompted to enter:
- **Email**: Your admin email address
- **Fullname**: Your full name
- **Password**: A secure password

**Note:** Use the admin account to manage the application through the Django admin interface.

### 3. Load Initial Data (Optional)

If there are any initial data fixtures, load them with:
```bash
python manage.py loaddata <fixture_name>
```

## Running the Application

### Start the Development Server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

To run on a different host/port:
```bash
python manage.py runserver 0.0.0.0:8000
```

### Access the Admin Panel

- **URL**: `http://127.0.0.1:8000/admin/`
- **Login**: Use the superuser credentials you created

## Project Structure

```
kan_mind/
├── authentication/        # User authentication and custom user model
├── boards/               # Board management and collaboration
├── tasks/                # Task, comment, and review management
├── kan_mind/             # Main project settings
├── manage.py             # Django management script
└── requirements.txt      # Python dependencies
```

## API Endpoints

The project includes REST API endpoints for:

- **Authentication**: 
    /api/registration/, 
    /api/login/

- **Boards**: 
    /api/boards/, 
    /api/boards/{board_id}/, 
    /api/email-check

- **Tasks**:
    /api/tasks/, 
    /api/tasks/{task_id}/, 
    /api/tasks/{task_id}/comments/, 
    /api/tasks/{task_id}/comments/{comment_id}/, 
    /api/tasks/assigend-to-me/,
    /api/tasks/reviewing/


## Troubleshooting

### Port Already in Use

If port 8000 is already in use:
```bash
python manage.py runserver 8000
```
Or specify a different port:
```bash
python manage.py runserver 8080
```

### Database Issues

To reset the database and start fresh:
```bash
del db.sqlite3  # Remove the database file
python manage.py migrate
python manage.py createsuperuser
```
