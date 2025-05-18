# Instructions for Copilot

## General Instructions

-   Use clear and concise language.
-   Provide code examples where applicable.
-   Write clean code with Django best practices.
-   Use comments to explain complex logic.
-   Use packages and libraries where appropriate and possible to avoid reinventing the wheel.
-   Update [TODO](TODO.md), [README](README.md) as fits.

## uv

UV is a fast Python package and project manager written in Rust. Use UV to manage dependencies, virtual environments, and run Python scripts with improved performance.

### Running Python Scripts

-   Execute a Python script with uv:

  ```bash
  uv run python ${FILE}.py
  ```

-   Run a script with a specific Python version:

  ```bash
  uv run python3.8 ${FILE}.py
  ```

-   Run a script with arguments:

  ```bash
  uv run python ${FILE}.py --arg1 value1 --arg2 value2
  ```

-   Add dependencies to standalone scripts:

  ```bash
  uv add --script <package-name> ${FILE}.py
  ```

-   Remove dependencies from a script:

  ```bash
  uv remove --script <package-name> ${FILE}.py
  ```

### Package Management

-   Install packages:

  ```bash
  uv pip install <package-name>
  ```

-   Install from requirements file:

  ```bash
  uv pip install -r requirements.txt
  ```

-   Add a package to current project:

  ```bash
  uv add <package-name>
  ```

-   Remove a package:

  ```bash
  uv remove <package-name>
  ```

### Virtual Environment Management

-   Create and activate a virtual environment:

  ```bash
  uv venv .venv
  source .venv/bin/activate  # Linux/macOS
  ```

-   Install project dependencies into an environment:

  ```bash
  uv pip sync
  ```

-   Lock dependencies for reproducible environments:

  ```bash
  uv lock
  ```

### Project Management

-   Create a new Python project:

  ```bash
  uv init <project-name>
  ```

-   Build a project into distribution archives:

  ```bash
  uv build
  ```

-   View dependency tree:

  ```bash
  uv tree
  ```

-   Publish package to PyPI:

  ```bash
  uv publish
  ```

### Python Version Management

-   Install specific Python version:

  ```bash
  uv python install 3.11
  ```

-   List available Python versions:

  ```bash
  uv python list
  ```

-   Find installed Python version:

  ```bash
  uv python find
  ```

-   Pin project to specific Python version:

  ```bash
  uv python pin 3.11
  ```

### Performance Benefits

-   UV offers significantly faster package installations than pip
-   Built-in caching improves repeated operations
-   Compatible with existing Python tooling ecosystem
-   Reliable dependency resolution to avoid conflicts

## Project Structure

This section provides a comprehensive overview of the LiveGraphsDjango project structure and the function of each key file. Please update this section whenever there are noteworthy changes to the structure or to a file's function.

```tree
LiveGraphsDjango/
├── dashboard_project/               # Main Django project directory
│   ├── __init__.py                  # Python package declaration
│   ├── __main__.py                  # Entry point for running module as script
│   ├── asgi.py                      # ASGI configuration for async web servers
│   ├── manage.py                    # Django command-line utility
│   ├── wsgi.py                      # WSGI configuration for web servers
│   ├── accounts/                    # User authentication and company management
│   │   ├── admin.py                 # Admin interface for accounts
│   │   ├── forms.py                 # User registration and login forms
│   │   ├── models.py                # User and Company models
│   │   ├── urls.py                  # URL routing for accounts
│   │   └── views.py                 # View functions for user authentication
│   ├── dashboard/                   # Core dashboard functionality
│   │   ├── admin.py                 # Admin interface for dashboard components
│   │   ├── forms.py                 # Dashboard configuration forms
│   │   ├── models.py                # Dashboard, DataSource models
│   │   ├── signals.py               # Signal handlers for dashboard events
│   │   ├── urls.py                  # URL routing for dashboard
│   │   ├── utils.py                 # Utility functions for dashboard
│   │   ├── views.py                 # Main dashboard view functions
│   │   ├── views_export.py          # Data export views (CSV, JSON, Excel)
│   │   ├── management/              # Custom management commands
│   │   │   └── commands/            # Django management commands
│   │   ├── migrations/              # Database migrations
│   │   └── templatetags/            # Custom template tags
│   ├── dashboard_project/           # Project settings and configuration
│   │   ├── settings.py              # Django settings
│   │   ├── urls.py                  # Main URL configuration
│   │   └── celery.py                # Celery configuration for async tasks
│   ├── data_integration/            # External data integration
│   │   ├── admin.py                 # Admin interface for data sources
│   │   ├── models.py                # ExternalDataSource, ChatSession models
│   │   ├── tasks.py                 # Celery tasks for data fetching
│   │   ├── urls.py                  # URL routing for data integration
│   │   ├── utils.py                 # Data fetching and transformation utilities
│   │   └── views.py                 # Views for data source management
│   ├── media/                       # User-uploaded files
│   │   └── data_sources/            # Uploaded CSV data sources
│   ├── scripts/                     # Utility scripts
│   │   ├── cleanup_duplicates.py    # Script to remove duplicate data
│   │   └── fix_dashboard_data.py    # Script to fix corrupt dashboard data
│   ├── static/                      # Static assets (CSS, JS, images)
│   │   ├── css/                     # Stylesheets
│   │   ├── img/                     # Images
│   │   └── js/                      # JavaScript files
│   └── templates/                   # HTML templates
│       ├── base.html                # Base template with common layout
│       ├── accounts/                # Account-related templates
│       └── dashboard/               # Dashboard-related templates
├── docs/                            # Project documentation
│   ├── CELERY_REDIS.md              # Celery and Redis setup guide
│   └── TROUBLESHOOTING.md           # Common issues and solutions
├── examples/                        # Example data files
│   ├── 132f3a8c-3ba5-4d89-ae04-cd83f1bc5272.txt  # Sample transcript
│   ├── jumbo.csv                    # Sample chat data
│   ├── sample.csv                   # Generic sample data
│   └── sessions.csv                 # Sample session data
├── nginx/                           # Nginx configuration
│   └── conf.d/                      # Nginx site configs
├── .github/                         # GitHub-specific files
│   └── copilot-instructions.md      # Instructions for GitHub Copilot (this file)
├── dev.sh                           # Development environment setup script
├── docker-compose.yml               # Docker Compose configuration
├── Dockerfile                       # Docker image definition
├── IMPLEMENTATION_SUMMARY.md        # Implementation details and status
├── Makefile                         # Common commands for the project
├── Procfile                         # Heroku deployment configuration
├── PROJECT_OVERVIEW.md              # Project overview and architecture
├── pyproject.toml                   # Python project configuration
├── QUICK_START_GUIDE.md             # Getting started guide
├── README.md                        # Project introduction and overview
├── requirements.txt                 # Python dependencies
├── start.sh                         # Production startup script
└── TODO.md                          # Pending tasks and features
```

### Key Component Relationships

1.  **Multi-Tenant Architecture**:

-   Companies are the top-level organizational unit
-   Users belong to Companies and have different permission levels
-   DataSources are owned by Companies
-   Dashboards display analytics based on DataSources

2.  **Data Integration Flow**:

-   External APIs are configured via ExternalDataSource models
-   Data is fetched, parsed, and stored as ChatSessions and ChatMessages
-   Dashboard views aggregate and visualize this data

3.  **Export Functionality**:

-   Export available in CSV, JSON, and Excel formats
-   Filtering options to customize exported data

### Important Note

**Please update this section whenever:**

1.  New files or directories are added to the project
2.  The function of existing files changes significantly
3.  New relationships between components are established
4.  The architecture of the application changes

This ensures that anyone working with GitHub Copilot has an up-to-date understanding of the project structure.
