# Beacons - Google Sheet Visualization App

A Streamlit application that visualizes data from a Google Sheet.

## Setup Instructions

### Prerequisites

- Python 3.12
- uv package manager

### Installation

1. Clone the repository
2. Install dependencies using uv:
   ```bash
   uv pip install --upgrade -e .
   ```

### Google Sheets API Setup

To connect to the Google Sheet, you need to set up a Google Cloud service account:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API
4. Create a service account and download the JSON key file
5. Share your Google Sheet with the service account email (viewer access is sufficient)

### Streamlit Secrets Setup

1. Update the `.streamlit/secrets.toml` file with your service account credentials:
   ```toml
   [gcp_service_account]
   # Copy the contents of your service account JSON file here
   type = "service_account"
   project_id = "your-project-id"
   private_key_id = "your-private-key-id"
   private_key = "-----BEGIN PRIVATE KEY-----\nyour-private-key-content\n-----END PRIVATE KEY-----\n"
   client_email = "your-service-account-email@your-project-id.iam.gserviceaccount.com"
   client_id = "your-client-id"
   auth_uri = "https://accounts.google.com/o/oauth2/auth"
   token_uri = "https://oauth2.googleapis.com/token"
   auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
   client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account-email%40your-project-id.iam.gserviceaccount.com"

   [connections.gsheets]
   spreadsheet = "https://docs.google.com/spreadsheets/d/1aZvvNwm5l0HoqTFY5XFnXMVnfog_1DXdwySpsmcNc4w/edit?gid=0#gid=0"
   ```

## Running the App

To run the Streamlit app:

```bash
streamlit run app.py
```

The app will be available at http://localhost:8501

## Features

- Data preview with table display
- Summary statistics
- Multiple visualization options:
  - Bar charts
  - Line charts
  - Scatter plots
  - Histograms
  - Box plots
  - Correlation heatmaps
- Interactive controls via sidebar