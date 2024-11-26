# Task Management API

This is a simple task management API built with FastAPI, PostgreSQL, and Redis.

## Prerequisites

- Docker
- Docker Compose

## Installation and Setup

1. Clone the repository:git clone https://github.com/yourusername/task-management-api.git cd task-management-api
2. Create a `.env` file in the root directory with the following content:SECRET_KEY=your_secret_key_here ALGORITHM=HS256 ACCESS_TOKEN_EXPIRE_MINUTES=30 REFRESH_TOKEN_EXPIRE_DAYS=7docker-compose up --build
3. Build and run the Docker containers:
4. The API will be available at `http://localhost:8000`.

## API Documentation

Once the application is running, you can access the interactive API documentation at `http://localhost:8000/docs`.

## Endpoints

- POST /auth/register - Register a new user
- POST /auth/login - Login and get access and refresh tokens
- POST /auth/refresh - Refresh the access token
- POST /tasks - Create a new task
- GET /tasks - Get all tasks (with optional status filter)
- PUT /tasks/{task_id} - Update a task
- DELETE /tasks/{task_id} - Delete a task

## Testing

To run the tests, use the following command:docker-compose run web pytest


## Stopping the Application

To stop the application and remove the containers, use:docker-compose down

If you want to remove the volumes as well, use:docker-compose down -v



