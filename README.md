# ALAI Challenge

This repository contains a Flask application for the ALAI Challenge.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/alai-challenge.git
   cd alai-challenge
   ```

2. Create a virtual environment and activate it:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Create a `.env` file in the root directory with the following configuration:

```env
FIRECRAWL_API_KEY="YOUR_FIRECRAWL_KEY"
ALAI_API_KEY="YOUR_ALAI_API_KEY"
FLASK_SECRET_KEY="ANYTHING_OVER_HERE"
```

Replace the placeholder values with your actual configuration.

## Running the Application

To run the Flask application:

```bash
cd src
flask --app main run --debug --port 5500
```

The application will be available at `http://127.0.0.1:5500/`.

## API Documentation

Documentation for the API endpoints is available at `/docs` when the application is running.
