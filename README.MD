# Chess.com Play Style API

## Description

This API analyzes chess.com player styles using the chess.com API and Google's Gemini AI.

## Features

- API Key Management
- Player Profile Retrieval
- Play Style Analysis

## Technologies Used

- Flask
- Flask-SQLAlchemy
- Flask-Limiter
- Flask-Caching
- Chess.com API
- Google Gemini AI
- Swagger UI

## Setup

1.  Clone the repository.
2.  Set up a virtual environment.
3.  Install dependencies: `pip install -r requirements.txt`.
4.  Set environment variables: `SECRET_KEY` and `GOOGLE_API_KEY`.
5.  Initialize the database: `python run.py`.

## Running the Application

```bash
python run.py
```

## Database Setup

The application uses Flask-SQLAlchemy to manage the database. The database URI is configured using the `DATABASE_URI` environment variable. By default, it uses a SQLite database.

## API Endpoints

-   `/api/register` - Registers a new user.
-   `/api/login` - Logs in an existing user.
-   `/api/profile/<username>` - Retrieves the chess.com profile and play style analysis for a given username. Requires authentication.
-   `/api/admin/users` - Retrieves a list of all users (Admin only).

## API Documentation

The API documentation is available through Swagger UI. To access it, run the application and navigate to `/api/docs` in your browser.

## Contributing

Contributions are welcome! Please follow these steps:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Submit a pull request.