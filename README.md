# Flask RBAC

This project is a Flask application that implements Role-Based Access Control (RBAC) using Flask, Flask-RESTx, Flask-JWT-Extended, and SQLAlchemy. The application allows users to perform CRUD (Create, Read, Update, Delete) operations on users, roles, and permissions, and manage access control through roles and permissions.

## Requirements

To run this application, you will need:

- Python 3.6 or higher
- Flask
- Flask-RESTx
- Flask-JWT-Extended
- Flask-SQLAlchemy
- MySQL

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/djharshit/flask-rbac
   ```
2. Navigate to the project directory:
   ```sh
   cd flask-rbac
   ```
3. Create a virtual environment:
   ```sh
   python3 -m venv env
   ```
4. Activate the virtual environment:
   ```sh
   source env/bin/activate
   ```
5. Install the required packages:
   ```sh
   pip install -r requirements.txt
   ```
6. Set the environment variables for MySQL URI and JWT secret key:
   ```sh
   export MYSQL_URI="mysql://username:password@localhost/dbname"
   export JWT_SECRET="your_jwt_secret_key"
   ```
7. Start the application:
   ```sh
   python server.py
   ```

## Usage

Once the application is running, you can access the REST API endpoints using Postman or any other HTTP client.

### Available Endpoints

- **Health Check**

  - `GET /health`: Returns the health status of the application.

- **Login Management**

  - `POST /login`: Authenticates a user and returns a JWT access token.

- **User Management**

  - `GET /users`: Returns a list of all users.
  - `POST /users`: Creates a new user.

- **Role Management**

  - `GET /roles`: Returns a list of all roles.
  - `POST /roles`: Creates a new role.
  - `GET /role/<int:roleid>`: Returns the permissions of a specific role.

- **Permission Management**

  - `GET /permissions`: Returns a list of all permissions.
  - `POST /permissions`: Creates a new permission.

- **Role Assignment**

  - `POST /assignrole`: Assigns a role to a user.
  - `POST /assignperm`: Assigns a permission to a role.

- **Access Validation**

  - `POST /validate`: Validates if a user has access to a specific action and resource.

- **Logs**
  - `GET /logs/<int:hours>`: Retrieves logs for the past N hours (admin only).

## Logging

The application uses a custom logging setup to log important events. Logs are stored in [logs.log](./logs.log) and can be retrieved using the `/logs/<int:hours>` endpoint.

## Models

The application uses SQLAlchemy models to define the database schema for users, roles, and permissions. The models are defined in [models.py](./models.py).

## Author

Harshit Mehra
