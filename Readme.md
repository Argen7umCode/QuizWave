# QuizMaster

QuizMaster is a web service for hosting and managing quizzes. It allows you to create and store quiz questions in a database and provides a REST API for retrieving questions from the database. This project includes instructions for building and running the service in a Docker container, as well as example API requests.

## Project Tasks

1. **Setup a Docker Container with a Database:**
   - Create a Docker container with an open-source database system (preferably PostgreSQL).
   - Provide scripts and configuration files (docker-compose) for container deployment.
   - Ensure data persistence by using volumes to store database files on the host machine.

2. **Implement a Python3 Web Service:**
   - Develop a web service using FastAPI or Flask to perform the following functions:
     - Accept POST requests with a "questions_num" parameter (an integer).
     - Request the specified number of random English quiz questions from a public API (e.g., https://jservice.io/api/random?count=1).
     - Store the received questions in the database, including information about the question, answer, and creation date.
     - Check for question uniqueness and make additional API requests until a unique question is obtained.
     - Respond to requests with saved quiz questions. In case of no saved questions, return an empty object.

3. **Instructions and Examples:**
   - Provide detailed instructions in the project repository for building the Docker image with the service, configuring it, and running it.
   - Include examples of API requests.

4. **Recommended Technologies:**
   - It's recommended to use docker-compose for managing containers, SQLAlchemy for interacting with the database, and type annotations for code readability.

## Project Timeline

The project should be completed by 23.10.2023.

## Getting Started

Follow these steps to get started with QuizMaster:

### Prerequisites

- Docker
- Python 3.10
- Your favorite code editor

### Building and Running the Service

1. Clone this repository to your local machine.

2. Navigate to the project directory.

3. Build the Docker image for the service:

4. Start the Docker containers:

5. The service will be accessible at `http://localhost:8000`.

### Example API Request

To retrieve a random quiz question, send a POST request to `http://localhost:8000/api/question` with the following JSON data:

```json
{
"questions_num": 1
}
```

### Contributors
- Artur Shatyrin (Argen7um)