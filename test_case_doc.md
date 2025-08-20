# Test Case Document & API Testing Results

## Test Case Summary

### FAQ Management APIs

| Test Case ID | Endpoint              | Method | Description                         | Expected Result                  | 
|--------------|-----------------------|--------|-------------------------------------|----------------------------------|
| TC001        | `/api/faqs`           | GET    | Retrieve all FAQs                   | 200 + list of FAQ items          | 
| TC002        | `/api/faqs`           | POST   | Add a new FAQ                       | 201 + new FAQ JSON               | 
| TC003        | `/api/faqs/1`         | GET    | Retrieve FAQ with ID = 1           | 200 + corresponding FAQ JSON     | 
| TC004        | `/api/faqs/999`       | GET    | Retrieve non-existent FAQ          | 404 + error message              | 
| TC005        | `/api/faqs/1`         | PUT    | Update FAQ with ID = 1             | 200 + updated FAQ JSON           | 
| TC006        | `/api/faqs/999`       | PUT    | Update non-existent FAQ            | 404 + error message              | 
| TC007        | `/api/faqs/1`         | DELETE | Delete FAQ with ID = 1             | 200 + success message            | 
| TC008        | `/api/faqs/999`       | DELETE | Delete non-existent FAQ            | 404 + error message              | 

### AI Chat APIs

| Test Case ID | Endpoint              | Method | Description                         | Expected Result                  |
|--------------|-----------------------|--------|-------------------------------------|----------------------------------|
| TC009        | `/api/chat`           | POST   | Send question to AI chat            | 200 + AI response with metadata  |
| TC010        | `/api/chat`           | POST   | Send empty question                 | 400 + error message              |
| TC011        | `/api/chat`           | POST   | Send question with session ID       | 200 + AI response with session   |

### Session Management APIs

| Test Case ID | Endpoint                        | Method | Description                         | Expected Result                  |
|--------------|--------------------------------|--------|-------------------------------------|----------------------------------|
| TC012        | `/api/session/start`           | POST   | Start new session                   | 201 + session info               |
| TC013        | `/api/session/start`           | POST   | Start session with user ID         | 201 + session with user info     |
| TC014        | `/api/session/end`             | POST   | End existing session               | 200 + success message            |
| TC015        | `/api/session/end`             | POST   | End non-existent session          | 404 + error message              |
| TC016        | `/api/session/status/<id>`     | GET    | Get session status                 | 200 + session status             |
| TC017        | `/api/session/status/999`      | GET    | Get non-existent session status   | 404 + error message              |
| TC018        | `/api/session/questions/<id>`  | GET    | Get session questions              | 200 + questions list             |
| TC019        | `/api/session/questions/999`   | GET    | Get questions from invalid session | 404 + error message              |
| TC020        | `/api/session/statistics`      | GET    | Get session statistics             | 200 + statistics data            |

### Analytics APIs

| Test Case ID | Endpoint                        | Method | Description                         | Expected Result                  |
|--------------|--------------------------------|--------|-------------------------------------|----------------------------------|
| TC021        | `/api/top-questions`           | GET    | Get top questions                   | 200 + questions with counts      |
| TC022        | `/api/categories`              | GET    | Get question categories             | 200 + categories with counts     |
| TC023        | `/api/category-details/<cat>`  | GET    | Get category details               | 200 + detailed questions         |
| TC024        | `/api/category-details/invalid`| GET    | Get invalid category details       | 404 + error message              |
| TC025        | `/api/daily-question-counts`   | GET    | Get daily question counts          | 200 + daily statistics           |
| TC026        | `/api/csat`                    | GET    | Get CSAT score                     | 200 + satisfaction metrics       |

### User Management APIs

| Test Case ID | Endpoint              | Method | Description                         | Expected Result                  |
|--------------|-----------------------|--------|-------------------------------------|----------------------------------|
| TC027        | `/api/register`       | POST   | Register new user                   | 201 + user info                  |
| TC028        | `/api/register`       | POST   | Register with missing fields       | 400 + error message              |
| TC029        | `/api/register`       | POST   | Register with existing username     | 400 + error message              |
| TC030        | `/api/login`          | POST   | User login with valid credentials   | 200 + login success              |
| TC031        | `/api/login`          | POST   | User login with invalid credentials | 401 + error message              |
| TC032        | `/api/logout`         | POST   | User logout                         | 200 + logout success             |
| TC033        | `/api/current-user`   | GET    | Get current user info              | 200 + user information           |
| TC034        | `/api/current-user`   | GET    | Get user info when not logged in   | 401 + error message              |

### Logging and Feedback APIs

| Test Case ID | Endpoint              | Method | Description                         | Expected Result                  |
|--------------|-----------------------|--------|-------------------------------------|----------------------------------|
| TC035        | `/api/log`            | POST   | Log user activity                   | 200 + log confirmation           |
| TC036        | `/api/log`            | POST   | Log with missing fields            | 400 + error message              |
| TC037        | `/api/feedback`       | POST   | Submit user feedback               | 200 + feedback confirmation      |
| TC038        | `/api/feedback`       | POST   | Submit feedback with missing data  | 400 + error message              |

## Sample Request Bodies

### Add FAQ (TC002)
```json
{
  "question": "How do I access the company VPN?",
  "answer": "Download the VPN client from the IT portal and use your domain credentials."
}
```

### Update FAQ (TC005)
```json
{
  "question": "How do I request vacation time?",
  "answer": "Submit a request through the HR self-service portal at least 2 weeks in advance."
}
```

### AI Chat (TC009)
```json
{
  "question": "How do I reset my password?",
  "session_id": "session_123"
}
```

### Start Session (TC012)
```json
{
  "user_id": "user123"
}
```

### End Session (TC014)
```json
{
  "session_id": "session_456"
}
```

### User Registration (TC027)
```json
{
  "username": "john_doe",
  "email": "john@company.com",
  "password": "securepassword123"
}
```

### User Login (TC030)
```json
{
  "username": "john_doe",
  "password": "securepassword123"
}
```

### Log Activity (TC035)
```json
{
  "action": "question_asked",
  "question": "How do I reset my password?",
  "category": "IT",
  "session_id": "session_456"
}
```

### Submit Feedback (TC037)
```json
{
  "rating": 5,
  "comment": "Very helpful response!",
  "question_id": 123,
  "session_id": "session_456"
}
```

## Sample Response Bodies

### Get All FAQs (TC001)
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

### Add FAQ Response (TC002)
```json
{
  "id": 3,
  "question": "How do I access the company VPN?",
  "answer": "Download the VPN client from the IT portal and use your domain credentials."
}
```

### AI Chat Response (TC009)
```json
{
  "answer": "To reset your password, go to the IT self-service portal and click 'Reset Password'.",
  "confidence": 0.95,
  "source": "FAQ"
}
```

### Start Session Response (TC012)
```json
{
  "session_id": "session_456",
  "start_time": "2024-01-15T10:30:00Z",
  "status": "active"
}
```

### Session Status Response (TC016)
```json
{
  "session_id": "session_456",
  "status": "active",
  "start_time": "2024-01-15T10:30:00Z",
  "last_activity": "2024-01-15T10:45:00Z"
}
```

### Top Questions Response (TC021)
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

### User Registration Response (TC027)
```json
{
  "success": true,
  "message": "User registered successfully",
  "user_id": 123
}
```

### Login Response (TC030)
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

## Error Response Examples

### FAQ Not Found (TC004, TC006, TC008)
```json
{
  "error": "FAQ not found"
}
```

### Missing Fields (TC010, TC028, TC036, TC038)
```json
{
  "error": "Missing required fields",
  "message": "Question and answer are required"
}
```

### Session Not Found (TC015, TC017, TC019)
```json
{
  "error": "Session not found",
  "message": "Invalid session ID"
}
```

### Unauthorized Access (TC031, TC034)
```json
{
  "error": "Unauthorized",
  "message": "Invalid credentials"
}
```

### User Already Exists (TC029)
```json
{
  "error": "User already exists",
  "message": "Username is already taken"
}
```

## Testing Notes

- All timestamps are in ISO 8601 format (UTC)
- Session IDs are generated as UUIDs
- Authentication is session-based using Flask sessions
- All POST requests expect JSON content type
- Error responses follow a consistent format with "error" and "message" fields
- Rate limiting may apply to prevent abuse
- Database operations are transactional
- All endpoints support CORS for frontend integration

## Test Environment Setup

1. Ensure Flask application is running on `http://localhost:5000`
2. Database should be initialized with sample data
3. All required environment variables should be set
4. Test with both authenticated and unauthenticated requests where applicable
5. Verify proper error handling for edge cases
6. Test concurrent session management
7. Validate data persistence across requests

## Performance Considerations

- Response times should be under 200ms for simple queries
- Database queries should be optimized with proper indexing
- Session management should handle concurrent users
- Memory usage should remain stable during extended testing
- API should handle at least 100 concurrent requests

## Security Testing

- Validate input sanitization for all endpoints
- Test SQL injection prevention
- Verify session security and timeout handling
- Test authentication bypass attempts
- Validate CORS configuration
- Check for sensitive data exposure in error messages