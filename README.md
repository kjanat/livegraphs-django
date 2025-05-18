# Chat Analytics Dashboard

A Django application that creates an analytics dashboard for chat session data. The application allows different companies to have their own dashboards and view their own data.

## Features

- Multi-company support with user authentication
- CSV file upload and processing
- Interactive dashboard with charts and visualizations
- Detailed data views for chat sessions
- Search functionality to find specific chat sessions
- Admin interface for managing users and companies
- Responsive design using Bootstrap 5

## Requirements

- Python 3.13+
- Django 5.2+
- UV package manager (recommended)
- Other dependencies listed in [`pyproject.toml`](./pyproject.toml)

## Setup

### Local Development

1. Clone the repository:

   ```sh
   git clone <repository-url>
   cd LiveGraphsDjango
   ```

2. Install uv if you don't have it yet:

   ```sh
   # Install using pip
   pip install uv

   # Or with curl (Unix/macOS)
   curl -sSf https://install.pypa.io/get-uv.py | python3 -

   # Or on Windows with PowerShell
   irm https://install.pypa.io/get-uv.ps1 | iex
   ```

3. Create a virtual environment and activate it:

   ```sh
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

4. Install dependencies:

   ```sh
   # Install all dependencies including dev dependencies
   uv pip install -e ".[dev]"

   # Or just runtime dependencies
   uv pip install -e .
   ```

5. Run migrations:

   ```sh
   cd dashboard_project
   python manage.py makemigrations
   python manage.py migrate
   ```

6. Create a superuser:

   ```sh
   python manage.py createsuperuser
   ```

7. Set up environment variables:

   ```sh
   # Copy the sample .env file
   cp .env.sample .env

   # Edit the .env file with your credentials
   nano .env
   ```

   Be sure to update:

   - `EXTERNAL_API_USERNAME` and `EXTERNAL_API_PASSWORD` for the data integration API
   - `DJANGO_SECRET_KEY` for production environments
   - Redis URL if using a different configuration for Celery

8. Start Celery for background tasks:

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

9. Run the development server:

   ```sh
   python manage.py runserver
   ```

10. Access the application at <http://127.0.0.1:8000/>

### Development Workflow with UV

UV offers several advantages over traditional pip, including faster dependency resolution and installation:

1. Running linting and formatting:

   ```sh
   # Using the convenience script
   ./.scripts/lint.sh

   # Or directly
   uv run -m ruff check dashboard_project
   uv run -m ruff format dashboard_project
   uv run -m black dashboard_project
   ```

2. Running tests:

   ```sh
   # Using the convenience script
   ./.scripts/test.sh

   # Or directly
   uv run -m pytest
   ```

3. Adding new dependencies:

   ```sh
   # Add to project
   uv pip install package_name

   # Then update pyproject.toml manually
   # And update the lockfile
   uv pip freeze > requirements.lock
   ```

4. Updating the lockfile:

   ```sh
   uv pip compile pyproject.toml -o uv.lock
   ```

### Using Docker

1. Clone the repository:

   ```sh
   git clone <repository-url>
   cd dashboard_project
   ```

2. Build and run with Docker Compose:

   ```sh
   docker-compose up -d --build
   ```

3. Create a superuser:

   ```sh
   docker-compose exec web python manage.py createsuperuser
   ```

4. Access the application at <http://localhost/>

## Usage

1. Login as the superuser you created.
2. Go to the admin interface (<http://localhost/admin/>) and create companies and users.
3. Assign users to companies.
4. Upload CSV files for each company.
5. View the analytics dashboard.

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

## Future Enhancements

- API integration for real-time data
- More advanced visualizations
- Custom reports
- Export functionality
- Theme customization
- User access control with more granular permissions

## License

This project is unlicensed. Usage is restricted to personal and educational purposes only. For commercial use, please contact the author.
