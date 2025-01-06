# Slack Clone Application

This project is a Slack-like real-time communication platform built with a Python/FastAPI backend, PostgreSQL database, and Next.js frontend.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- Python 3.8 or higher
- Node.js 14 or higher
- PostgreSQL 12 or higher
- pip (Python package manager)
- npm (Node package manager)

## Backend Setup (Python/FastAPI)

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```
     source venv/bin/activate
     ```

4. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

5. Create a \`.env\` file in the backend directory and add your PostgreSQL database URL:
   ```
   DB_URL=postgresql://username:password@localhost/dbname
   ```

## Frontend Setup (Next.js)

1. Navigate to the project root directory.

2. Install the required Node.js packages:
   ```
   npm install
   ```

## Running the Application

1. Start the backend server:
   - Ensure you're in the backend directory and your virtual environment is activated.
   - Run the following command:
     ```
     uvicorn main:app --reload
     ```
   - The backend server should now be running on \`http://localhost:8000\`

2. Start the frontend development server:
   - Open a new terminal window/tab
   - Navigate to the project root directory
   - Run the following command:
     ```
     npm run dev
     ```
   - The frontend should now be accessible at \`http://localhost:3000\`

## Accessing the Application

Open your web browser and go to \`http://localhost:3000\` to view and interact with the Slack clone application.

## Additional Notes

- Ensure that your PostgreSQL server is running and that you've created a database for this application.
- If you encounter any issues with missing dependencies, make sure all required packages are installed for both the backend and frontend.
- For development purposes, both servers (backend and frontend) need to be running simultaneously.

## Troubleshooting

If you encounter any issues:
1. Ensure all prerequisites are correctly installed.
2. Check that all environment variables are properly set.
3. Verify that the PostgreSQL server is running and accessible.
4. Check the console output for both the backend and frontend servers for any error messages.

For more detailed information about the API endpoints and available features, refer to the backend documentation (accessible at \`http://localhost:8000/docs\` when the backend server is running).

