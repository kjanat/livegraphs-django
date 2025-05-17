# Chat Analytics Dashboard: Quick Start Guide

## Getting Started

This guide will help you quickly set up and start using the Chat Analytics Dashboard.

### Installation

#### Option 1: Local Development

1. **Clone the repository**:

   ```sh
   git clone <repository-url>
   cd dashboard_project
   ```

2. **Set up a virtual environment**:

   ```sh
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**: # from pyproject.toml

   ```sh
   uv pip install -r requirements.txt
   ```

4. **Set up the database**:

   ```sh
   python manage.py migrate
   ```

5. **Create admin user**:

   ```sh
   python manage.py createsuperuser
   ```

6. **Start the development server**:

   ```sh
   python manage.py runserver
   ```

7. **Access the application**:
   Open your browser and go to <http://127.0.0.1:8000/>

#### Option 2: Docker Deployment

1. **Clone the repository**:

   ```sh
   git clone <repository-url>
   cd dashboard_project
   ```

2. **Build and start the containers**:

   ```sh
   docker-compose up -d --build
   ```

3. **Create admin user**:

   ```sh
   docker-compose exec web python manage.py createsuperuser
   ```

4. **Access the application**:
   Open your browser and go to <http://localhost/>

### Creating Sample Data (Optional)

To quickly populate the system with sample data:

```sh
python manage.py create_sample_data
```

This will create:

- Admin user (username: admin, password: admin123)
- Three companies with users
- Sample chat data and dashboards

## Basic Usage

### Admin Tasks

1. **Access Admin Panel**:

   - Go to <http://localhost/admin/>
   - Login with your admin credentials

2. **Create a Company**:

   - Go to Companies > Add Company
   - Fill in the company details and save

3. **Create Users**:
   - Go to Users > Add User
   - Fill in user details
   - Assign the user to a company
   - Set appropriate permissions (staff status, company admin)

### Company Admin Tasks

1. **Login to Dashboard**:

   - Go to <http://localhost/>
   - Login with your company admin credentials

2. **Upload Chat Data**:

   - Click on "Upload Data" in the sidebar
   - Fill in the data source details
   - Select a CSV file containing chat data
   - Click "Upload"

3. **Create a Dashboard**:
   - Click on "New Dashboard" in the sidebar
   - Fill in the dashboard details
   - Select data sources to include
   - Click "Create Dashboard"

### Regular User Tasks

1. **View Dashboard**:

   - Login with your user credentials
   - The dashboard will show automatically
   - Select different dashboards from the sidebar

2. **Search Chat Sessions**:

   - Click on "Search" in the top navigation
   - Enter search terms
   - Use filters to refine results

3. **View Session Details**:
   - In search results, click the eye icon for a session
   - View complete session information and transcript

## CSV Format

Your CSV files should include the following columns:

| Column              | Description                     | Type     |
| ------------------- | ------------------------------- | -------- |
| `session_id`        | Unique ID for the chat          | String   |
| `start_time`        | Session start time              | Datetime |
| `end_time`          | Session end time                | Datetime |
| `ip_address`        | User's IP address               | String   |
| `country`           | User's country                  | String   |
| `language`          | Chat language                   | String   |
| `messages_sent`     | Number of messages              | Integer  |
| `sentiment`         | Sentiment analysis result       | String   |
| `escalated`         | Whether chat was escalated      | Boolean  |
| `forwarded_hr`      | Whether chat was sent to HR     | Boolean  |
| `full_transcript`   | Complete chat text              | Text     |
| `avg_response_time` | Average response time (seconds) | Float    |
| `tokens`            | Number of tokens used           | Integer  |
| `tokens_eur`        | Cost in EUR                     | Float    |
| `category`          | Chat category                   | String   |
| `initial_msg`       | First user message              | Text     |
| `user_rating`       | User satisfaction rating        | String   |

Example CSV row:

```csv
acme_1,2023-05-01 10:30:00,2023-05-01 10:45:00,192.168.1.1,USA,English,10,Positive,FALSE,FALSE,"User: Hello\nAgent: Hi there!",2.5,500,0.01,Support,Hello I need help,Good
```

## Dashboard Features

### Overview Panel

The main dashboard shows:

- Total chat sessions
- Average response time
- Total tokens used
- Total cost

### Charts

The dashboard includes:

- **Sessions Over Time**: Line chart showing chat volume trends
- **Sentiment Analysis**: Pie chart of positive/negative/neutral chats
- **Top Countries**: Bar chart of user countries
- **Categories**: Distribution of chat categories

### Data Source Details

View details for each data source:

- Upload date and time
- Total sessions
- Source description
- List of all chat sessions from the source

### Session Details

For each chat session, you can view:

- Session metadata (time, location, etc.)
- Full chat transcript
- Performance metrics
- User sentiment and rating

## Troubleshooting

### CSV Upload Issues

If your CSV upload fails:

- Ensure all required columns are present
- Check date formats (should be YYYY-MM-DD HH:MM:SS)
- Verify boolean values (TRUE/FALSE, Yes/No, 1/0)
- Check for special characters in text fields

### Access Issues

If you can't access certain features:

- Verify your user role (admin, company admin, or regular user)
- Ensure you're assigned to the correct company
- Check if you're trying to access another company's data

### Empty Dashboard

If your dashboard is empty:

- Verify that data sources have been uploaded
- Check that the dashboard is configured to use those data sources
- Ensure the CSV was processed successfully

## Getting Help

If you encounter any issues:

- Check the documentation
- Contact your system administrator
- File an issue in the project repository
