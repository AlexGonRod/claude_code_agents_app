# Invoice Processing App

A mobile-first web application for capturing invoice images, extracting data via OCR, verifying information, and saving to Excel in Google Drive.

## Features

- Capture images via camera or file picker
- Extract invoice information using OCR (Google Vision API or Azure Form Recognizer)
- Verify and edit extracted data
- Save invoices to Excel file in Google Drive
- Google OAuth 2.0 authentication
- Responsive design for mobile devices

## Tech Stack

- **Frontend**: Astro.js + Svelte
- **Backend**: FastAPI (Python)
- **Authentication**: Google OAuth 2.0
- **OCR**: Google Vision API (or Azure Form Recognizer)
- **Storage**: Google Drive API
- **Package Manager**: pnpm

## Getting Started

### Prerequisites

- Node.js (v16+)
- Python (v3.9+)
- Google Cloud account with Vision API and Drive API enabled
- Azure subscription (if using Azure Form Recognizer)

### Installation

1. Clone the repository
2. Install frontend dependencies:
   ```bash
   cd frontend
   pnpm install
   ```
3. Install backend dependencies:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

### Configuration

1. Create a `.env` file in the backend directory based on `.env.example`:
   ```env
   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_CLIENT_SECRET=your_google_client_secret
   GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
   GOOGLE_VISION_API_KEY=your_google_vision_api_key
   ```

2. For Azure Form Recognizer (alternative to Google Vision):
   ```env
   AZURE_FORM_RECOGNIZER_ENDPOINT=your_azure_endpoint
   AZURE_FORM_RECOGNIZER_KEY=your_azure_key
   ```

### Running the Application

1. Start the backend server:
   ```bash
   cd backend
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   uvicorn main:app --reload
   ```

2. Start the frontend development server:
   ```bash
   cd frontend
   pnpm dev
   ```

3. Open your browser and navigate to `http://localhost:3000`

### Docker Deployment

1. Build and run with Docker Compose:
   ```bash
   docker-compose up --build
   ```

2. The application will be available at:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

## API Endpoints

- `GET /` - Health check
- `GET /auth/google` - Google OAuth login URL
- `GET /auth/google/callback` - Google OAuth callback
- `POST /ocr` - Process image with OCR
- `POST /drive/save` - Save invoice data to Google Drive

## Project Structure

```
invoice-processing-app/
├── backend/
│   ├── main.py          # FastAPI application
│   ├── auth.py          # Authentication endpoints
│   ├── models.py        # Pydantic models
│   ├── ocr.py           # OCR processing endpoints
│   ├── drive.py         # Google Drive integration
│   ├── requirements.txt # Python dependencies
│   └── Dockerfile       # Docker configuration
├── frontend/
│   ├── src/
│   │   ├── components/  # Svelte components
│   │   ├── pages/       # Astro pages
│   │   ├── stores/      # State management stores
│   │   ├── layout.astro # Main layout
│   │   └── ...          # Other frontend files
│   ├── package.json     # Frontend dependencies
│   └── ...              # Other frontend config
├── docker-compose.yml   # Docker Compose configuration
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
pnpm test
```

## Future Enhancements

- Multi-language OCR support
- Batch processing of multiple invoices
- Expense categorization and reporting
- Integration with accounting software (QuickBooks, Xero)
- Offline-first capability with service workers
- Biometric authentication (Face ID/Touch ID)

## License

MIT