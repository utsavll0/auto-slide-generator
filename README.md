# Automatic Presentation Creator

This repository contains a Flask application for creating automated slides by crawling the web.

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

Documentation for the API endpoints is available at `/apidocs` when the application is running.

## How to use

1. Once the backend is running the first order of business is to login. The endpoint is a HTTP Post at URI `auth/login`

```json
{
  "username": "alai_email",
  "password": "alai_password"
}
```

This will authenticate the user in the backend and for all further calls user doesnt have to worry about authentication.

2. To create presentation hit the API at `presentation/create` endpoint using the following json

```json
{
  "url": "https://example.com",
  "instructions": "System prompt for the AI to create a slide on.",
  "num_of_slides": 3,
  "tone": "SOME_TONE",
  "verbosity": 3
}
```

`num_of_slides`, `tone` and `verbosity` are optional, default values are 1, 'DEFAULT' and 3 respectively.

ALSO `TONE` currently only supports the values from the ALAI's website and giving a custom tone might lead to unexpected behavior. Best to use something like `PROFESSIONAL`,`CASUAL`, etc.
