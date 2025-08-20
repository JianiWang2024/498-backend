# API Documentation

This document lists all backend APIs for the FAQ management system. Each API includes the endpoint path, HTTP method, purpose, and sample JSON input/output.

## FAQ Management APIs

### 1. Get all FAQs

- **Endpoint:** `/api/faqs`
- **Method:** `GET`
- **Description:** Retrieve all FAQ entries from the database.
- **Request Body:** *None*
- **Sample Response (200 OK):**

```json
[
  {
    "id": 1,
    "question": "How do I apply for leave?",
    "answer": "Use the HR portal under 'Leave Management'."
  },
  {
    "id": 2,
    "question": "How do I reset my password?",
    "answer": "Go to the IT self-service portal and click 'Reset Password'."
  }
]
```

### 2. Get FAQ by ID

- **Endpoint:** `/api/faqs/<id>`
- **Method:** `GET`
- **Description:** Retrieve a single FAQ by its ID.
- **Request Body:** None
- **Sample Response (200 OK):**

```json
{
  "id": 1,
  "question": "How do I apply for leave?",
  "answer": "Use the HR portal under 'Leave Management'."
}
```

- **Sample Error (404 Not Found):**

```json
{
  "error": "FAQ not found"
}
```

### 3. Add new FAQ

- **Endpoint:** `/api/faqs`
- **Method:** `POST`
- **Description:** Add a new FAQ entry to the database.
- **Sample Request Body:**

```json
{
  "question": "Where can I find the employee handbook?",
  "answer": "Download it from the internal HR SharePoint."
}
```

- **Sample Response (201 Created):**

```json
{
  "id": 3,
  "question": "Where can I find the employee handbook?",
  "answer": "Download it from the internal HR SharePoint."
}
```

- **Sample Error (400 Bad Request):**

```json
{
  "error": "Missing fields"
}
```

### 4. Update existing FAQ

- **Endpoint:** `/api/faqs/<id>`
- **Method:** `PUT`
- **Description:** Update an existing FAQ based on ID.
- **Sample Request Body:**

```json
{
  "question": "How do I request time off?",
  "answer": "Submit a request via the HR system."
}
```

- **Sample Response (200 OK):**

```json
{
  "id": 1,
  "question": "How do I request time off?",
  "answer": "Submit a request via the HR system."
}
```

- **Sample Error (404 Not Found):**

```json
{
  "error": "FAQ not found"
}
```

### 5. Delete FAQ

- **Endpoint:** `/api/faqs/<id>`
- **Method:** `DELETE`
- **Description:** Remove a specific FAQ from the database.
- **Request Body:** None
- **Sample Response (200 OK):**

```json
{
  "success": true
}
```

- **Sample Error (404 Not Found):**

```json
{
  "error": "FAQ not found"
}
```

## AI Chat APIs

### 6. Smart Chat

- **Endpoint:** `/api/chat`
- **Method:** `POST`
- **Description:** Process user questions using AI and return intelligent responses.
- **Sample Request Body:**

```json
{
  "question": "How do I reset my password?",
  "session_id": "session_123"
}
```

- **Sample Response (200 OK):**

```json
{
  "answer": "To reset your password, go to the IT self-service portal and click 'Reset Password'.",
  "confidence": 0.95,
  "source": "FAQ"
}
```

## Session Management APIs

### 7. Start Session

- **Endpoint:** `/api/session/start`
- **Method:** `POST`
- **Description:** Start a new conversation session.
- **Sample Request Body:**

```json
{
  "user_id": "user123"
}
```

- **Sample Response (201 Created):**

```json
{
  "session_id": "session_456",
  "start_time": "2024-01-15T10:30:00Z",
  "status": "active"
}
```

### 8. End Session

- **Endpoint:** `/api/session/end`
- **Method:** `POST`
- **Description:** End an active conversation session.
- **Sample Request Body:**

```json
{
  "session_id": "session_456"
}
```

- **Sample Response (200 OK):**

```json
{
  "success": true,
  "end_time": "2024-01-15T11:00:00Z"
}
```

### 9. Get Session Status

- **Endpoint:** `/api/session/status/<session_id>`
- **Method:** `GET`
- **Description:** Get the status of a specific session.
- **Request Body:** None
- **Sample Response (200 OK):**

```json
{
  "session_id": "session_456",
  "status": "active",
  "start_time": "2024-01-15T10:30:00Z",
  "last_activity": "2024-01-15T10:45:00Z"
}
```

### 10. Get Session Questions

- **Endpoint:** `/api/session/questions/<session_id>`
- **Method:** `GET`
- **Description:** Get all questions asked in a specific session.
- **Request Body:** None
- **Sample Response (200 OK):**

```json
{
  "session_id": "session_456",
  "questions": [
    {
      "question": "How do I reset my password?",
      "timestamp": "2024-01-15T10:35:00Z"
    },
    {
      "question": "Where is the employee handbook?",
      "timestamp": "2024-01-15T10:40:00Z"
    }
  ]
}
```

### 11. Get Session Statistics

- **Endpoint:** `/api/session/statistics`
- **Method:** `GET`
- **Description:** Get overall session statistics.
- **Request Body:** None
- **Sample Response (200 OK):**

```json
{
  "total_sessions": 150,
  "active_sessions": 5,
  "average_duration": 300,
  "total_questions": 450
}
```

## Analytics APIs

### 12. Get Top Questions

- **Endpoint:** `/api/top-questions`
- **Method:** `GET`
- **Description:** Get the most frequently asked questions.
- **Request Body:** None
- **Sample Response (200 OK):**

```json
[
  {
    "question": "How do I reset my password?",
    "count": 25,
    "category": "IT"
  },
  {
    "question": "How do I apply for leave?",
    "count": 20,
    "category": "HR"
  }
]
```

### 13. Get Category Details

- **Endpoint:** `/api/category-details/<category>`
- **Method:** `GET`
- **Description:** Get detailed information about a specific category.
- **Request Body:** None
- **Sample Response (200 OK):**

```json
{
  "category": "IT",
  "total_questions": 45,
  "top_questions": [
    "How do I reset my password?",
    "How do I access VPN?"
  ]
}
```

### 14. Get Categories

- **Endpoint:** `/api/categories`
- **Method:** `GET`
- **Description:** Get all available question categories.
- **Request Body:** None
- **Sample Response (200 OK):**

```json
[
  {
    "category": "HR",
    "count": 30
  },
  {
    "category": "IT",
    "count": 45
  },
  {
    "category": "Process",
    "count": 20
  }
]
```

### 15. Get Daily Question Counts

- **Endpoint:** `/api/daily-question-counts`
- **Method:** `GET`
- **Description:** Get daily question count statistics.
- **Request Body:** None
- **Sample Response (200 OK):**

```json
[
  {
    "date": "2024-01-15",
    "count": 25
  },
  {
    "date": "2024-01-14",
    "count": 30
  }
]
```

### 16. Get CSAT Scores

- **Endpoint:** `/api/csat`
- **Method:** `GET`
- **Description:** Get customer satisfaction scores.
- **Request Body:** None
- **Sample Response (200 OK):**

```json
{
  "average_score": 4.2,
  "total_responses": 150,
  "distribution": {
    "5": 60,
    "4": 45,
    "3": 30,
    "2": 10,
    "1": 5
  }
}
```

## User Management APIs

### 17. User Registration

- **Endpoint:** `/api/register`
- **Method:** `POST`
- **Description:** Register a new user account.
- **Sample Request Body:**

```json
{
  "username": "john_doe",
  "email": "john@company.com",
  "password": "securepassword123"
}
```

- **Sample Response (201 Created):**

```json
{
  "success": true,
  "message": "User registered successfully",
  "user_id": 123
}
```

### 18. User Login

- **Endpoint:** `/api/login`
- **Method:** `POST`
- **Description:** Authenticate user and create session.
- **Sample Request Body:**

```json
{
  "username": "john_doe",
  "password": "securepassword123"
}
```

- **Sample Response (200 OK):**

```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "id": 123,
    "username": "john_doe",
    "email": "john@company.com"
  }
}
```

### 19. User Logout

- **Endpoint:** `/api/logout`
- **Method:** `POST`
- **Description:** End user session and logout.
- **Request Body:** None
- **Sample Response (200 OK):**

```json
{
  "success": true,
  "message": "Logout successful"
}
```

### 20. Get Current User

- **Endpoint:** `/api/current-user`
- **Method:** `GET`
- **Description:** Get information about the currently logged-in user.
- **Request Body:** None
- **Sample Response (200 OK):**

```json
{
  "id": 123,
  "username": "john_doe",
  "email": "john@company.com",
  "login_time": "2024-01-15T09:00:00Z"
}
```

## Logging and Feedback APIs

### 21. Log Activity

- **Endpoint:** `/api/log`
- **Method:** `POST`
- **Description:** Log user activity and interactions.
- **Sample Request Body:**

```json
{
  "action": "question_asked",
  "question": "How do I reset my password?",
  "category": "IT",
  "session_id": "session_456"
}
```

- **Sample Response (200 OK):**

```json
{
  "success": true,
  "log_id": 789
}
```

### 22. Submit Feedback

- **Endpoint:** `/api/feedback`
- **Method:** `POST`
- **Description:** Submit user feedback and ratings.
- **Sample Request Body:**

```json
{
  "rating": 5,
  "comment": "Very helpful response!",
  "question_id": 123,
  "session_id": "session_456"
}
```

- **Sample Response (200 OK):**

```json
{
  "success": true,
  "feedback_id": 456
}
```

## Error Responses

All APIs may return the following common error responses:

- **400 Bad Request:** Invalid request format or missing required fields
- **401 Unauthorized:** Authentication required or invalid credentials
- **403 Forbidden:** Access denied
- **404 Not Found:** Resource not found
- **500 Internal Server Error:** Server error

Example error response:

```json
{
  "error": "Invalid request format",
  "message": "Missing required field: question"
}
```
