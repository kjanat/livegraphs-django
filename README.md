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
- Django 5.0+
- PostgreSQL (optional, SQLite is fine for development)
- Other dependencies listed in [`pyproject.toml`](pyproject.toml)

## Setup

### Local Development

1. Clone the repository:

   ```sh
   git clone <repository-url>
   cd dashboard_project
   ```

2. Create a virtual environment and activate it:

    ```sh
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:

   ```sh
   uv pip install -r requirements.txt
   ```

4. Run migrations:

   ```sh
   uv run python manage.py makemigrations
   uv run python manage.py migrate
   ```

5. Create a superuser:

   ```sh
   uv run python manage.py createsuperuser
   ```

6. Run the development server:

   ```sh
   uv run python manage.py runserver
   ```

7. Access the application at <http://127.0.0.1:8000/>

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

- session_id: Unique identifier for the chat session
- start_time: When the session started (datetime)
- end_time: When the session ended (datetime)
- ip_address: IP address of the user
- country: Country of the user
- language: Language used in the conversation
- messages_sent: Number of messages in the conversation (integer)
- sentiment: Sentiment analysis of the conversation (string)
- escalated: Whether the conversation was escalated (boolean)
- forwarded_hr: Whether the conversation was forwarded to HR (boolean)
- full_transcript: Full transcript of the conversation (text)
- avg_response_time: Average response time in seconds (float)
- tokens: Total number of tokens used (integer)
- tokens_eur: Cost of tokens in EUR (float)
- category: Category of the conversation (string)
- initial_msg: First message from the user (text)
- user_rating: User rating of the conversation (string)

## Future Enhancements

- API integration for real-time data
- More advanced visualizations
- Custom reports
- Export functionality
- Theme customization
- User access control with more granular permissions

## License

This project is licensed under the MIT License - see the LICENSE file for details.
