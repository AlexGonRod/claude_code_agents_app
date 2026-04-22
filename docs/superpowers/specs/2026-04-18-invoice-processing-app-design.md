# Invoice Processing App Design Document

## Overview
A mobile-first web application that allows users to capture invoice images via camera or file picker, extract invoice information using third-party OCR APIs, verify the extracted data, and save it to an Excel file in their Google Drive.

**Primary Purpose**: Personal expense tracking
**Stack**: Astro.js + Svelte frontend, FastAPI backend, pnpm package manager
**Authentication**: Google OAuth 2.0 (user login)
**Image Input**: Both camera and file picker
**OCR Approach**: Third-party OCR/API (e.g., Google Vision, Azure Form Recognizer)
**Storage**: Save to Excel file in user's Google Drive

## Architecture

### High-Level Architecture
```
Frontend (Astro.js + Svelte)  <--->  Backend (FastAPI)  <--->  Third-Party Services
                                                                     |
                                                                     v
                                                      Google Drive API
```

### Technology Choices
- **Frontend**: Astro.js for static site generation and routing, Svelte for reactive UI components
- **Backend**: FastAPI for high-performance async API endpoints
- **Authentication**: Google OAuth 2.0 via FastAPI endpoints
- **OCR**: Third-party API (Google Vision API or Azure Form Recognizer)
- **File Storage**: Temporary storage on backend for OCR processing (automatically cleaned up)
- **Package Manager**: pnpm for frontend and backend dependencies
- **Deployment**: Backend deployable to VPS/cloud services (Render, Fly.io, etc.)
- **Excel Format**: Single sheet with columns: Date, Vendor, Amount, Tax, Line Items Count, Notes, Created At

### Why This Architecture
1. **Separation of Concerns**: Clear division between UI, business logic, and external services
2. **Mobile-First**: Astro + Svelte provides excellent performance and responsiveness on mobile
3. **Flexibility**: Easy to swap OCR providers or storage backends
4. **Control**: Full control over authentication flow and data handling
5. **Scalability**: FastAPI handles async operations well for API calls to OCR and Drive

## Components

### Frontend Components (Astro.js + Svelte)
1. **ImageInput.svelte**
   - Camera access using `navigator.mediaDevices.getUserMedia()`
   - File picker input for existing images/PDFs
   - Returns image as base64 or File object

2. **ImagePreview.svelte**
   - Displays selected/captured image
   - Basic controls: rotate, zoom, reset
   - Shows loading state during OCR processing

3. **Auth.svelte**
   - Handles Google OAuth login flow
   - Redirects to `/login/google` on backend
   - Stores JWT token in localStorage after successful auth
   - Provides logout functionality

4. **InvoiceForm.svelte**
   - Displays extracted OCR data in editable form fields
   - Fields: Vendor, Date, Amount, Tax, Line Items (dynamic), Notes
   - Validation: Required fields, numeric validation for amounts
   - Reset/form clear functionality

5. **SaveButton.svelte**
   - Triggers save to Google Drive
   - Shows loading state during save operation
   - Displays success/error messages

6. **Layout.astro**
   - Mobile-first responsive layout
   - Bottom navigation bar for easy thumb access
   - Header with app title and user profile
   - Main content area for component routing

### Backend Components (FastAPI)
1. **auth.py**
   - `/login/google`: Initiates Google OAuth 2.0 flow
   - `/auth/google/callback`: Handles OAuth redirect, exchanges code for tokens
   - Creates JWT token for user session
   - Securely stores Google OAuth tokens (encrypted) associated with JWT

2. **ocr.py**
   - `/ocr`: POST endpoint for image upload
   - Accepts multipart/form-data with image file
   - Validates file type (JPEG, PNG, PDF) and size
   - Calls third-party OCR API with image
   - Parses and normalizes OCR response into structured InvoiceData
   - Returns JSON with extracted data or error details

3. **drive.py**
   - `/drive/save`: POST endpoint to save invoice data
   - Accepts verified InvoiceData JSON
   - Retrieves user's Google OAuth token from session
   - Uses Google Drive API to:
     - Find/create target Excel file in user's Drive
     - Append new row with invoice data to Excel sheet
   - Returns success confirmation

4. **main.py**
   - FastAPI application instance
   - Configures CORS middleware for Astro frontend
   - Includes all API routers
   - Health check endpoint
   - Error handlers

5. **models.py**
   - Pydantic models for data validation:
     - `InvoiceData`: vendor (str), date (date), amount (float), tax (float), line_items (List[LineItem]), notes (str)
     - `LineItem`: description (str), quantity (float), unit_price (float), amount (float)
     - `OCRResponse`: Raw OCR API response handling
     - `TokenData`: Google OAuth token storage model

### Data Flow Details

#### 1. Authentication Flow
```
User → Frontend: Click Login
Frontend → Backend: GET /login/google
Backend → Google: Redirect to OAuth consent
Google → User: OAuth consent screen
User → Google: Grant permissions
Google → Backend: Redirect to /auth/google/callback with code
Backend → Google: Exchange code for tokens
Backend → Frontend: Return JWT token
Frontend → LocalStorage: Store JWT token
```

#### 2. Image Processing Flow
```
User → Frontend: Capture/select image
Frontend → Backend: POST /ocr (image + JWT)
Backend → Validation: Check file type/size
Backend → OCR API: Send image for processing
OCR API → Backend: Return extracted text/data
Backend → Processing: Normalize to InvoiceData model
Backend → Frontend: Return JSON with extracted data
Frontend → InvoiceForm: Display data for verification
```

#### 3. Verification & Save Flow
```
User → Frontend: Review/edit data in form
User → Frontend: Click Save
Frontend → Backend: POST /drive/save (InvoiceData + JWT)
Backend → Auth: Validate JWT, get Google token
Backend → Drive API: Locate/create Excel file
Backend → Drive API: Append row to Excel sheet
Backend → Frontend: Return success response
Frontend → User: Show success message
```

### Error Handling

#### Frontend Error Handling
- **Network Errors**: Show retry button with exponential backoff (1s, 2s, 4s, max 8s)
- **Validation Errors**: Field-level validation with inline error messages
- **Camera Access**: If denied, show fallback message and disable camera button
- **OCR Processing**: Show loading spinner, timeout after 30s
- **Save Errors**: Retry failed saves up to 3 times with user notification
- **Toast Notifications**: Non-intrusive messages for transient errors/success

#### Backend Error Handling
- **400 Bad Request**: Missing file, invalid file type, oversized file
- **401 Unauthorized**: Missing/expired JWT → clear localStorage, redirect to login
- **401 Google Token**: Expired Google OAuth token → trigger refresh or re-auth
- **429 Too Many Requests**: Rate limiting from OCR/Drive APIs → retry with delay
- **500 Internal Server Error**: Log detailed traceback, return generic error message
- **OCR API Errors**: Handle service unavailable, timeouts, invalid image, quota exceeded
- **Drive API Errors**: Handle permission denied, file not found, quota exceeded, service unavailable

#### Recovery Strategies
- **Token Refresh**: Automatically refresh Google OAuth tokens before expiry (55 min)
- **Queued Retries**: Failed Drive saves queued for retry with user notification
- **Local Fallback**: If Drive save fails permanently, save verified data to localStorage
- **Cleanup**: Remove temporary OCR images after processing or on error
- **Circuit Breaker**: Temporary backend failure detection for external API outages

### Testing Approach

#### Unit Testing
- **Frontend (Vitest/Jest)**:
  - ImageInput: Test camera simulation, file picker, state management
  - ImagePreview: Test image display, zoom/rotate controls
  - InvoiceForm: Test field validation, data binding, reset functionality
  - Auth: Test login/logout flow, token storage
  - SaveButton: Test loading states, click handlers

- **Backend (Pytest)**:
  - auth.py: Test OAuth flow, JWT creation/validation, token storage
  - ocr.py: Test file validation, OCR API integration, data normalization
  - drive.py: Test Google Drive API integration, Excel manipulation
  - models.py: Test Pydantic model validation, serialization
  - main.py: Test CORS configuration, health check, error handlers

#### Integration Testing
- **Frontend-Backend Contracts**:
  - Mock backend endpoints for frontend development/testing
  - Test API request/response formats match expectations
  
- **External API Mocks**:
  - Mock OCR API responses (various formats, error cases)
  - Mock Google Drive API responses (success, errors, edge cases)
  
- **Full Flow Tests**:
  - Image → OCR → Verification → Save flow with mocked services
  - Authentication → OCR → Save flow
  - Error recovery flows (network failure, token expiry, etc.)

#### End-to-End Testing
- **Playwright/Cypress Scenarios**:
  1. Happy path: Login → capture image → verify OCR data → save to Drive
  2. File picker path: Login → select file → verify → save
  3. Error case: Login → invalid image → show error → retry with valid image
  4. Error case: Login → valid image → OCR failure → retry → success
  5. Auth expiry: Login → wait for token expiry → attempt save → re-auth prompt
  
- **Mobile Testing**:
  - Test on iOS/Android emulators and real devices
  - Verify camera access works on mobile browsers
  - Test responsive breakpoints (320px, 375px, 425px, 768px)
  - Test touch targets and gesture support

#### Testing Strategy
- **Coverage Goals**: 80%+ unit test coverage on backend business logic
- **Contract Testing**: Verify API contracts between frontend and backend
- **CI/CD**: GitHub Actions to run tests on pull requests and pushes
- **Manual Testing Checklist**:
  - Camera permissions on iOS Safari, Android Chrome
  - File picker functionality across browsers
  - OCR accuracy with various invoice formats/languages
  - Excel file creation and appending in Google Drive
  - Offline behavior and retry mechanisms
  - Performance testing (image upload times, OCR latency)

## Design Decisions Summary

### Chosen Approach: Traditional Full-Stack
Selected over serverless and BaaS alternatives for:
- Full control over authentication and OCR integration
- Easier debugging and error handling
- Predictable performance and costs
- Simpler deployment for initial version

### Key Trade-offs Accepted
- **Server Management**: Accepting responsibility for backend server maintenance
- **Cold Start Avoidance**: Choosing persistent server over serverless for consistent performance
- **Vendor Flexibility**: Using pnpm allows easy switching of frontend/backend hosts

### Future Enhancements (Out of Scope for V1)
- Multi-language OCR support
- Batch processing of multiple invoices
- Expense categorization and reporting
- Integration with accounting software (QuickBooks, Xero)
- Offline-first capability with service workers
- Biometric authentication (Face ID/Touch ID)

---
*Design completed and approved on 2026-04-18*