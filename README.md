# Chat Analytics Dashboard

A Django application that creates an analytics dashboard for chat session data. The application allows different companies to have their own dashboards and view their own data.

## Project Overview

This Django project creates a multi-tenant dashboard application for analyzing chat session data. Companies can upload their chat data (in CSV format) and view analytics and metrics through an interactive dashboard. The application supports user authentication, role-based access control, and separate data isolation for different companies.

### Project Structure

The project consists of two main Django apps:

1.  **accounts**: Handles user authentication, company management, and user roles
2.  **dashboard**: Manages data sources, chat sessions, and dashboard visualization
3.  **data_integration**: Handles external API data integration

### Key Features

-   **Multi-company Support**: Each company has their own private dashboards and data
-   **User Management**: Different user roles (admin, company admin, regular user)
-   **CSV File Upload**: Upload and process CSV files containing chat session data
-   **Interactive Dashboard**: Visualize chat data with charts and metrics
-   **Search Functionality**: Find specific chat sessions based on various criteria
-   **Data Export**: Export data in CSV, JSON, and Excel formats
-   **Data Exploration**: Drill down into individual chat sessions for detailed analysis
-   **Responsive Design**: Mobile-friendly interface using Bootstrap 5

## Requirements

-   Python 3.13+
-   Django 5.2+
-   UV package manager (recommended)
-   Other dependencies listed in [`pyproject.toml`](./pyproject.toml)

## Setup

### Local Development

1.  Clone the repository:

    ```sh
    git clone <repository-url>
    cd LiveGraphsDjango
    ```

2.  Install uv if you don't have it yet:

    ```sh
    # Install using pip
    pip install uv

    # Or with curl (Unix/macOS)
    curl -sSf https://install.pypa.io/get-uv.py | python3 -

    # Or on Windows with PowerShell
    irm https://install.pypa.io/get-uv.ps1 | iex
    ```

3.  Create a virtual environment and activate it:

    ```sh
    uv venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

4.  Install dependencies:

    ```sh
    # Install all dependencies including dev dependencies
    uv pip install -e ".[dev]"

    # Or just runtime dependencies
    uv pip install -e .
    ```

5.  Run migrations:

    ```sh
    cd dashboard_project
    python manage.py makemigrations
    python manage.py migrate
    ```

6.  Create a superuser:

    ```sh
    python manage.py createsuperuser
    ```

7.  Set up environment variables:

    ```sh
    # Copy the sample .env file
    cp .env.sample .env

    # Edit the .env file with your credentials
    nano .env
    ```

    Be sure to update:

    -   `EXTERNAL_API_USERNAME` and `EXTERNAL_API_PASSWORD` for the data integration API
    -   `DJANGO_SECRET_KEY` for production environments
    -   Redis URL if using a different configuration for Celery

8.  Start Celery for background tasks:

    ```sh
    # In a separate terminal
    cd dashboard_project
    celery -A dashboard_project worker --loglevel=info

    # Start the Celery Beat scheduler in another terminal
    cd dashboard_project
    celery -A dashboard_project beat --scheduler django_celery_beat.schedulers:DatabaseScheduler
    ```

    Alternative without Redis (using SQLite):

    ```sh
    # Set environment variables to use SQLite instead of Redis
    export CELERY_BROKER_URL=sqla+sqlite:///celery.sqlite
    export CELERY_RESULT_BACKEND=db+sqlite:///results.sqlite

    # In a separate terminal
    cd dashboard_project
    celery -A dashboard_project worker --loglevel=info

    # Start the Celery Beat scheduler in another terminal with the same env vars
    cd dashboard_project
    celery -A dashboard_project beat --scheduler django_celery_beat.schedulers:DatabaseScheduler
    ```

9.  Run the development server:

    ```sh
    python manage.py runserver
    ```

10.  Access the application at <http://127.0.0.1:8000/>

### Development Workflow with UV

UV offers several advantages over traditional pip, including faster dependency resolution and installation:

1.  Running linting and formatting:

    ```sh
    # Using the convenience script
    ./.scripts/lint.sh

    # Or directly
    uv run -m ruff check dashboard_project
    uv run -m ruff format dashboard_project
    uv run -m black dashboard_project
    ```

2.  Running tests:

    ```sh
    # Using the convenience script
    ./.scripts/test.sh

    # Or directly
    uv run -m pytest
    ```

3.  Adding new dependencies:

    ```sh
    # Add to project
    uv pip install package_name

    # Then update pyproject.toml manually
    # And update the lockfile
    uv pip freeze > requirements.lock
    ```

4.  Updating the lockfile:

    ```sh
    uv pip compile pyproject.toml -o uv.lock
    ```

### Using Docker

1.  Clone the repository:

    ```sh
    git clone <repository-url>
    cd dashboard_project
    ```

2.  Build and run with Docker Compose:

    ```sh
    docker-compose up -d --build
    ```

3.  Create a superuser:

```sh
docker-compose exec web python manage.py createsuperuser
```

4.  Access the application at <http://localhost/>

## Development Tools

### Prettier for Django Templates

This project uses Prettier with the `prettier-plugin-django-annotations` plugin to format HTML templates with Django template syntax.

#### Prettier Configuration

The project is already configured with Prettier integration in pre-commit hooks. The configuration includes:

1.  `.prettierrc` - Configuration file with Django HTML support
2.  `.prettierignore` - Files to exclude from formatting
3.  Pre-commit hook for automatic formatting on commits

#### Manual Installation

To use Prettier locally (outside of pre-commit hooks), you'll need to install the dependencies:

```bash
# Using npm
npm install

# Or install just the required packages
npm install --save-dev prettier prettier-plugin-django-annotations
```

#### Usage

##### With Pre-commit

Prettier will automatically run as part of the pre-commit hooks when you commit changes.

To manually run the pre-commit hooks on all files:

```bash
pre-commit run prettier --all-files
```

##### Using npm Scripts

The package.json includes npm scripts for formatting:

```bash
# Format all static files
npm run format

# Check formatting without modifying files
npm run format:check
```

##### Command Line

You can also run Prettier directly:

```bash
# Format a specific file
npx prettier --write path/to/template.html

# Format all HTML files
npx prettier --write "dashboard_project/templates/**/*.html"
```

#### VSCode Integration

For VSCode users, install the Prettier extension and add these settings to your `.vscode/settings.json`:

```json
{
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "[html]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "editor.formatOnSave": true
  },
  "prettier.requireConfig": true
}
```

#### Ignoring Parts of Templates

If you need to prevent Prettier from formatting a section of your template:

```html
{# prettier-ignore #}
<div>This section will not be formatted by Prettier.</div>

<!-- prettier-ignore -->
<div>
    This works too.
</div>
```

#### Django Template Support

The `prettier-plugin-django-annotations` plugin provides special handling for Django templates, including:

-   Proper formatting of Django template tags (`{% %}`)
-   Support for Django template comments (`{# #}`)
-   Preservation of Django template variable output (`{{ }}`)
-   Special handling for Django template syntax inside HTML attributes

## Basic Usage Instructions

1.  Login as the superuser you created.
2.  Go to the admin interface (<http://localhost/admin/>) and create companies and users.
3.  Assign users to companies.
4.  Upload CSV files for each company.
5.  View the analytics dashboard.

## Quick Start Guide

### Creating Sample Data (Optional)

To quickly populate the system with sample data:

```sh
python manage.py create_sample_data
```

This will create:

-   Admin user (username: admin, password: admin123)
-   Three companies with users
-   Sample chat data and dashboards

### Admin Tasks

1.  **Access Admin Panel**:

    -   Go to <http://localhost/admin/>
    -   Login with your admin credentials

2.  **Create a Company**:

    -   Go to Companies > Add Company
    -   Fill in the company details and save

3.  **Create Users**:
    -   Go to Users > Add User
    -   Fill in user details
    -   Assign the user to a company
    -   Set appropriate permissions (staff status, company admin)

### Company Admin Tasks

1.  **Login to Dashboard**:

    -   Go to <http://localhost/>
    -   Login with your company admin credentials

2.  **Upload Chat Data**:

    -   Click on "Upload Data" in the sidebar
    -   Fill in the data source details
    -   Select a CSV file containing chat data
    -   Click "Upload"

3.  **Create a Dashboard**:
    -   Click on "New Dashboard" in the sidebar
    -   Fill in the dashboard details
    -   Select data sources to include
    -   Click "Create Dashboard"

### Regular User Tasks

1.  **View Dashboard**:

    -   Login with your user credentials
    -   The dashboard will show automatically
    -   Select different dashboards from the sidebar

2.  **Search Chat Sessions**:

    -   Click on "Search" in the top navigation
    -   Enter search terms
    -   Use filters to refine results

3.  **View Session Details**:
    -   In search results, click the eye icon for a session
    -   View complete session information and transcript

### Dashboard Features

The dashboard includes:

-   **Sessions Over Time**: Line chart showing chat volume trends
-   **Sentiment Analysis**: Pie chart of positive/negative/neutral chats
-   **Top Countries**: Bar chart of user countries
-   **Categories**: Distribution of chat categories

### Data Source Details

View details for each data source:

-   Upload date and time
-   Total sessions
-   Source description
-   List of all chat sessions from the source

### Troubleshooting

#### CSV Upload Issues

If your CSV upload fails:

-   Ensure all required columns are present
-   Check date formats (should be YYYY-MM-DD HH:MM:SS)
-   Verify boolean values (TRUE/FALSE, Yes/No, 1/0)
-   Check for special characters in text fields

#### Access Issues

If you can't access certain features:

-   Verify your user role (admin, company admin, or regular user)
-   Ensure you're assigned to the correct company
-   Check if you're trying to access another company's data

#### Empty Dashboard

If your dashboard is empty:

-   Verify that data sources have been uploaded
-   Check that the dashboard is configured to use those data sources
-   Ensure the CSV was processed successfully

## CSV File Format

The CSV file should contain the following columns:

| Column              | Description                                            |
| ------------------- | ------------------------------------------------------ |
| `session_id`        | Unique identifier for the chat session                 |
| `start_time`        | When the session started (datetime)                    |
| `end_time`          | When the session ended (datetime)                      |
| `ip_address`        | IP address of the user                                 |
| `country`           | Country of the user                                    |
| `language`          | Language used in the conversation                      |
| `messages_sent`     | Number of messages in the conversation (integer)       |
| `sentiment`         | Sentiment analysis of the conversation (string)        |
| `escalated`         | Whether the conversation was escalated (boolean)       |
| `forwarded_hr`      | Whether the conversation was forwarded to HR (boolean) |
| `full_transcript`   | Full transcript of the conversation (text)             |
| `avg_response_time` | Average response time in seconds (float)               |
| `tokens`            | Total number of tokens used (integer)                  |
| `tokens_eur`        | Cost of tokens in EUR (float)                          |
| `category`          | Category of the conversation (string)                  |
| `initial_msg`       | First message from the user (text)                     |
| `user_rating`       | User rating of the conversation (string)               |

Example CSV row:

```csv
acme_1,2023-05-01 10:30:00,2023-05-01 10:45:00,192.168.1.1,USA,English,10,Positive,FALSE,FALSE,"User: Hello\nAgent: Hi there!",2.5,500,0.01,Support,Hello I need help,Good
```

## Implementation Details

### Core Features Implemented

1.  **Multi-Tenant Architecture**:

    -   Companies have isolated data and user access
    -   Users belong to specific companies
    -   Role-based permissions (admin, company admin, regular user)

2.  **Data Management**:

    -   CSV file upload and processing
    -   Data source management
    -   Chat session records with comprehensive metadata

3.  **Dashboard Visualization**:

    -   Interactive charts using Plotly.js
    -   Key metrics and KPIs
    -   Time-series analysis
    -   Geographic distribution
    -   Sentiment analysis
    -   Category distribution

4.  **Search and Analysis**:

    -   Full-text search across chat sessions
    -   Filtering by various attributes
    -   Detailed view of individual chat sessions
    -   Transcript viewing

5.  **User Management**:

    -   User registration and authentication
    -   Profile management
    -   Password change functionality
    -   Role assignment

6.  **Admin Interface**:

    -   Company management
    -   User administration
    -   Data source oversight
    -   System-wide configuration

7.  **Responsive Design**:
    -   Mobile-friendly interface using Bootstrap 5
    -   Consistent layout and navigation
    -   Accessible UI components

### Technical Implementation

#### Backend (Django)

-   **Custom User Model**: Extended for company association and roles
-   **Database Models**: Structured for efficient data storage and queries
-   **View Logic**: Separation of concerns with dedicated view functions
-   **Form Handling**: Validated data input and file uploads
-   **Data Processing**: CSV parsing and structured storage
-   **Template Context**: Prepared data for frontend rendering
-   **URL Routing**: Clean URL structure
-   **Access Control**: Permission checks throughout

#### Frontend

-   **Bootstrap 5**: For responsive layout and UI components
-   **Plotly.js**: For interactive charts and visualizations
-   **jQuery**: For AJAX functionality
-   **Font Awesome**: For icons
-   **Custom CSS**: For styling enhancements

#### Data Flow

1.  **Upload Process**:

    -   File validation
    -   CSV parsing
    -   Data normalization
    -   Record creation
    -   Association with company

2.  **Dashboard Generation**:

    -   Data aggregation
    -   Statistical calculations
    -   Chart data preparation
    -   JSON serialization for frontend

3.  **User Authentication**:
    -   Login/registration handling
    -   Session management
    -   Permission checks
    -   Access control based on company

#### Deployment Configuration

-   **Docker**: Containerization for consistent deployment
-   **Docker Compose**: Multi-container orchestration
-   **Nginx**: Web server and static file serving
-   **PostgreSQL**: Production-ready database
-   **Gunicorn**: WSGI HTTP server

### Models

#### Accounts App

-   **CustomUser**: Extends Django's User model with company association and role
-   **Company**: Represents a company with users and data sources

#### Dashboard App

-   **DataSource**: Represents an uploaded CSV file with chat data
-   **ChatSession**: Stores individual chat session data parsed from CSV
-   **Dashboard**: Allows configuration of custom dashboards with selected data sources

### Usage Flow

1.  **Admin Setup**:

    -   Admin creates companies
    -   Admin creates users and assigns them to companies

2.  **Company Admin**:

    -   Uploads CSV files with chat data
    -   Creates and configures dashboards
    -   Manages company users

3.  **Regular Users**:
    -   View dashboards
    -   Search and explore chat data
    -   Analyze chat metrics

## Future Enhancements

-   API integration for real-time data
-   More advanced visualizations
-   Custom reports
-   Export to additional formats (XML, HTML, PDF)
-   Theme customization
-   User access control with more granular permissions
-   Direct integration with chat platforms via API
-   Real-time dashboard updates using WebSockets
-   Advanced analytics with machine learning
-   Customizable reports and scheduling
-   Enhanced visualization options

## License

This project is unlicensed. Usage is restricted to personal and educational purposes only. For commercial use, please contact the author.
