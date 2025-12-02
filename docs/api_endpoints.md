# IELTS System API Endpoints

## Authentication

### POST /auth/admin/login
**Description**: Admin login with pass key to get JWT token
**Request Body**:
```json
{
  "admin_pass_key": "your-admin-password"
}
```
**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```
**Error Response (401)**:
```json
{
  "detail": "Invalid admin pass key"
}
```

**Note**: All endpoints except GET requests require admin authentication. Include the token in the Authorization header:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Test Endpoints

### POST /tests/
**Description**: Create a new IELTS test
**Request Body**:
```json
{
  "title": "IELTS Academic Practice Test 1",
  "image": "https://example.com/test-image.jpg",
  "description": "Complete IELTS academic practice test covering all four skills"
}
```
**Response**:
```json
{
  "id": 1,
  "title": "IELTS Academic Practice Test 1",
  "image": "https://example.com/test-image.jpg",
  "description": "Complete IELTS academic practice test covering all four skills"
}
```

### GET /tests/
**Description**: Get all IELTS tests
**Response**:
```json
[
  {
    "id": 1,
    "title": "IELTS Academic Practice Test 1",
    "image": "https://example.com/test-image.jpg",
    "description": "Complete IELTS academic practice test covering all four skills"
  }
]
```

### GET /tests/{test_id}
**Description**: Get a specific test by ID
**Response**:
```json
{
  "id": 1,
  "title": "IELTS Academic Practice Test 1",
  "image": "https://example.com/test-image.jpg",
  "description": "Complete IELTS academic practice test covering all four skills"
}
```

### PUT /tests/{test_id}
**Description**: Update a test
**Request Body**: Same as POST
**Response**: Same as POST

### DELETE /tests/{test_id}
**Description**: Delete a test
**Response**: `204 No Content`

---

## Listening Endpoints

### POST /listening/
**Description**: Create listening section for a test
**Request Body**:
```json
{
  "test_id": 1,
  "text1": "# Listening Section 1\n\nYou will hear a conversation...",
  "text2": "# Listening Section 2\n\nYou will hear a monologue...",
  "text3": "# Listening Section 3\n\nYou will hear a discussion...",
  "text4": "# Listening Section 4\n\nYou will hear a lecture...",
  "audio_url1": "https://example.com/audio1.mp3",
  "audio_url2": "https://example.com/audio2.mp3",
  "audio_url3": "https://example.com/audio3.mp3",
  "audio_url4": "https://example.com/audio4.mp3",
  "answer_sheet1": {1: "A", 2: "Animal", 3: "London", 4: "B"},
  "answer_sheet2": {1: "C", 2: "Doctor", 3: "Tuesday", 4: "A"},
  "answer_sheet3": {1: "B", 2: "Library", 3: "15", 4: "D"},
  "answer_sheet4": {1: "D", 2: "Swimming", 3: "Morning", 4: "C"}
}
```
**Response**:
```json
{
  "id": 1,
  "test_id": 1,
  "text1": "# Listening Section 1...",
  "text2": "# Listening Section 2...",
  "text3": "# Listening Section 3...",
  "text4": "# Listening Section 4...",
  "audio_url1": "https://example.com/audio1.mp3",
  "audio_url2": "https://example.com/audio2.mp3",
  "audio_url3": "https://example.com/audio3.mp3",
  "audio_url4": "https://example.com/audio4.mp3",
  "answer_sheet1": {1: "A", 2: "Animal", 3: "London", 4: "B"},
  "answer_sheet2": {1: "C", 2: "Doctor", 3: "Tuesday", 4: "A"},
  "answer_sheet3": {1: "B", 2: "Library", 3: "15", 4: "D"},
  "answer_sheet4": {1: "D", 2: "Swimming", 3: "Morning", 4: "C"}
}
```

### GET /listening/test/{test_id}
**Description**: Get listening section by test ID
**Response**: Same as POST response

### PUT /listening/{listening_id}
**Description**: Update listening section
**Request Body**: Same as POST
**Response**: Same as POST

### DELETE /listening/{listening_id}
**Description**: Delete listening section
**Response**: `204 No Content`

---

## Reading Endpoints

### POST /reading/
**Description**: Create reading section for a test
**Request Body**:
```json
{
  "test_id": 1,
  "text1": "# Reading Passage 1\n\nClimate change is one of...",
  "text2": "# Reading Passage 2\n\nTechnology has revolutionized...",
  "text3": "# Reading Passage 3\n\nEducation systems worldwide...",
  "text4": "# Reading Passage 4\n\nEnvironmental conservation...",
  "answer_sheet1": {1: "A", 2: "TRUE", 3: "Climate change", 4: "B"},
  "answer_sheet2": {1: "C", 2: "FALSE", 3: "Technology", 4: "D"},
  "answer_sheet3": {1: "B", 2: "NOT GIVEN", 3: "Education", 4: "A"},
  "answer_sheet4": {1: "D", 2: "TRUE", 3: "Environment", 4: "C"}
}
```
**Response**:
```json
{
  "id": 1,
  "test_id": 1,
  "text1": "# Reading Passage 1...",
  "text2": "# Reading Passage 2...",
  "text3": "# Reading Passage 3...",
  "text4": "# Reading Passage 4...",
  "answer_sheet1": {1: "A", 2: "TRUE", 3: "Climate change", 4: "B"},
  "answer_sheet2": {1: "C", 2: "FALSE", 3: "Technology", 4: "D"},
  "answer_sheet3": {1: "B", 2: "NOT GIVEN", 3: "Education", 4: "A"},
  "answer_sheet4": {1: "D", 2: "TRUE", 3: "Environment", 4: "C"}
}
```

### GET /reading/test/{test_id}
**Description**: Get reading section by test ID
**Response**: Same as POST response

### PUT /reading/{reading_id}
**Description**: Update reading section
**Request Body**: Same as POST
**Response**: Same as POST

### DELETE /reading/{reading_id}
**Description**: Delete reading section
**Response**: `204 No Content`

---

## Speaking Endpoints

### POST /speaking/
**Description**: Create speaking section for a test
**Request Body**:
```json
{
  "test_id": 1,
  "questions": [
    "Tell me about your hometown",
    "Describe your favorite hobby",
    "What are your future plans?",
    "How do you think technology will change education?"
  ],
  "instruction_ai": "Evaluate the candidate's fluency, coherence, vocabulary range, grammatical accuracy, and pronunciation. Provide scores for each criterion on a scale of 1-9 and overall band score."
}
```
**Response**:
```json
{
  "id": 1,
  "test_id": 1,
  "questions": [
    "Tell me about your hometown",
    "Describe your favorite hobby",
    "What are your future plans?",
    "How do you think technology will change education?"
  ],
  "instruction_ai": "Evaluate the candidate's fluency, coherence, vocabulary range..."
}
```

### GET /speaking/test/{test_id}
**Description**: Get speaking section by test ID
**Response**: Same as POST response

### PUT /speaking/{speaking_id}
**Description**: Update speaking section
**Request Body**: Same as POST
**Response**: Same as POST

### DELETE /speaking/{speaking_id}
**Description**: Delete speaking section
**Response**: `204 No Content`

---

## Writing Endpoints

### POST /writing/
**Description**: Create writing section for a test
**Request Body**:
```json
{
  "test_id": 1,
  "task_1_text": "The chart below shows the percentage of households in owned and rented accommodation in England and Wales between 1918 and 2011.",
  "task_2_text": "Some people think that universities should provide graduates with the knowledge and skills needed in the workplace. Others think that the true function of a university should be to give access to knowledge for its own sake, regardless of whether the course is useful to an employer. What, in your opinion, are the main functions of a university?",
  "task_1_image_url": "https://example.com/chart.png",
  "task_2_image_url": null,
  "task_1_instruction": "Summarize the information by selecting and reporting the main features, and make comparisons where relevant. Write at least 150 words.",
  "task_2_instruction": "Give reasons for your answer and include any relevant examples from your own knowledge or experience. Write at least 250 words.",
  "task_1_ai_prompt": "Evaluate Task 1 response for: Task Achievement, Coherence and Cohesion, Lexical Resource, Grammatical Range and Accuracy. Check if main features are identified, data is accurate, and word count is met.",
  "task_2_ai_prompt": "Evaluate Task 2 response for: Task Response, Coherence and Cohesion, Lexical Resource, Grammatical Range and Accuracy. Check if question is fully addressed, position is clear, arguments are developed, and word count is met."
}
```
**Response**:
```json
{
  "id": 1,
  "test_id": 1,
  "task_1_text": "The chart below shows the percentage...",
  "task_2_text": "Some people think that universities...",
  "task_1_image_url": "https://example.com/chart.png",
  "task_2_image_url": null,
  "task_1_instruction": "Summarize the information...",
  "task_2_instruction": "Give reasons for your answer...",
  "task_1_ai_prompt": "Evaluate Task 1 response for...",
  "task_2_ai_prompt": "Evaluate Task 2 response for..."
}
```

### GET /writing/test/{test_id}
**Description**: Get writing section by test ID
**Response**: Same as POST response

### PUT /writing/{writing_id}
**Description**: Update writing section
**Request Body**: Same as POST
**Response**: Same as POST

### DELETE /writing/{writing_id}
**Description**: Delete writing section
**Response**: `204 No Content`

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Validation error message"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```