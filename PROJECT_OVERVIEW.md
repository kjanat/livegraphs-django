# Chat Analytics Dashboard Project

## Overview

This Django project creates a multi-tenant dashboard application for analyzing chat session data. Companies can upload their chat data (in CSV format) and view analytics and metrics through an interactive dashboard. The application supports user authentication, role-based access control, and separate data isolation for different companies.

## Project Structure

The project consists of two main Django apps:

1. **accounts**: Handles user authentication, company management, and user roles
2. **dashboard**: Manages data sources, chat sessions, and dashboard visualization

## Key Features

- **Multi-company Support**: Each company has their own private dashboards and data
- **User Management**: Different user roles (admin, company admin, regular user)
- **CSV File Upload**: Upload and process CSV files containing chat session data
- **Interactive Dashboard**: Visualize chat data with charts and metrics
- **Search Functionality**: Find specific chat sessions based on various criteria
- **Data Exploration**: Drill down into individual chat sessions for detailed analysis

## Setup and Installation

### Requirements

- Python 3.8+
- Django 4.0+
- Other dependencies listed in `requirements.txt`

### Installation Steps

1. Clone the repository
2. Set up a virtual environment
3. Install dependencies with `pip install -r requirements.txt`
4. Run database migrations with `python manage.py migrate`
5. Create a superuser with `python manage.py createsuperuser`
6. Start the development server with `python manage.py runserver`

### Creating Sample Data

To quickly populate the application with sample data, run:

```sh
python manage.py create_sample_data
```

This will create:

- An admin user (username: admin, password: admin123)
- Three sample companies
- Company admin users for each company
- Regular users for each company
- Sample chat data for each company
- Default dashboards for each company

## Models

### Accounts App

- **CustomUser**: Extends Django's User model with company association and role
- **Company**: Represents a company with users and data sources

### Dashboard App

- **DataSource**: Represents an uploaded CSV file with chat data
- **ChatSession**: Stores individual chat session data parsed from CSV
- **Dashboard**: Allows configuration of custom dashboards with selected data sources

## Usage Flow

1. **Admin Setup**:
   - Admin creates companies
   - Admin creates users and assigns them to companies

2. **Company Admin**:
   - Uploads CSV files with chat data
   - Creates and configures dashboards
   - Manages company users

3. **Regular Users**:
   - View dashboards
   - Search and explore chat data
   - Analyze chat metrics

## CSV Format

The application expects CSV files with the following columns:

- **session_id**: Unique identifier for each chat session
- **start_time**: When the chat session started
- **end_time**: When the chat session ended
- **ip_address**: User's IP address
- **country**: User's country
- **language**: Language used in the chat
- **messages_sent**: Number of messages in the conversation
- **sentiment**: Sentiment analysis result (Positive, Neutral, Negative)
- **escalated**: Whether the chat was escalated
- **forwarded_hr**: Whether the chat was forwarded to HR
- **full_transcript**: Complete chat transcript
- **avg_response_time**: Average response time in seconds
- **tokens**: Number of tokens used (for AI chat systems)
- **tokens_eur**: Cost of tokens in EUR
- **category**: Chat category or topic
- **initial_msg**: First message from the user
- **user_rating**: User satisfaction rating

## Deployment

For production deployment, the project includes:

- **Dockerfile**: For containerizing the application
- **docker-compose.yml**: For orchestrating the application with PostgreSQL and Nginx
- **Nginx Configuration**: For serving the application and static files

## Future Enhancements

- **API Integration**: Direct integration with chat systems
- **Real-time Updates**: Live dashboard updates as new chats occur
- **Advanced Analytics**: More detailed and customizable metrics
- **Export Functionality**: Export reports and analysis
- **Customizable Themes**: Company-specific branding

## Support

For any issues or questions, please create an issue in the repository or contact the project maintainers.
