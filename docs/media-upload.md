# Media Upload API Documentation

This document covers the media upload endpoints for audio and image files in the IELTS system.

## Authentication

All upload endpoints require admin authentication. Include the JWT token in the Authorization header:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Base URL
All upload endpoints are prefixed with `/upload`

---

## Audio Upload

### POST /upload/audio
**Description**: Upload an audio file to Supabase storage

**Authentication**: Required (Admin JWT token)

**Request**:
- **Method**: POST
- **Content-Type**: multipart/form-data
- **Body**: Form data with file upload

**Supported Formats**: MP3, WAV, M4A, OGG, WebM  
**Maximum File Size**: 20MB

**Example Request**:
```bash
curl -X POST "http://localhost:8000/upload/audio" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@/path/to/audio.mp3"
```

**Success Response (200)**:
```json
{
  "message": "Audio file uploaded successfully",
  "data": {
    "success": true,
    "file_url": "https://bkvxbuidvwbqpqpxjwqf.supabase.co/storage/v1/object/public/uploads/audio/550e8400-e29b-41d4-a716-446655440000.mp3",
    "file_path": "audio/550e8400-e29b-41d4-a716-446655440000.mp3",
    "file_size": 1024576,
    "content_type": "audio/mpeg",
    "original_filename": "recording.mp3"
  }
}
```

**Error Responses**:

**400 Bad Request** - Invalid file format:
```json
{
  "detail": "Invalid audio format. Allowed: MP3, WAV, M4A, OGG, WebM"
}
```

**400 Bad Request** - No file provided:
```json
{
  "detail": "No file provided"
}
```

**413 Payload Too Large** - File size exceeds limit:
```json
{
  "detail": "File size exceeds 20MB limit"
}
```

---

## Image Upload

### POST /upload/image
**Description**: Upload an image file to Supabase storage

**Authentication**: Required (Admin JWT token)

**Request**:
- **Method**: POST
- **Content-Type**: multipart/form-data
- **Body**: Form data with file upload

**Supported Formats**: JPEG, PNG, WebP  
**Maximum File Size**: 10MB

**Example Request**:
```bash
curl -X POST "http://localhost:8000/upload/image" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@/path/to/image.jpg"
```

**Success Response (200)**:
```json
{
  "message": "Image file uploaded successfully",
  "data": {
    "success": true,
    "file_url": "https://bkvxbuidvwbqpxjwqf.supabase.co/storage/v1/object/public/uploads/images/550e8400-e29b-41d4-a716-446655440000.jpg",
    "file_path": "images/550e8400-e29b-41d4-a716-446655440000.jpg",
    "file_size": 204800,
    "content_type": "image/jpeg",
    "original_filename": "chart.jpg"
  }
}
```

**Error Responses**:

**400 Bad Request** - Invalid file format:
```json
{
  "detail": "Invalid image format. Allowed: JPEG, PNG, WebP"
}
```

**400 Bad Request** - Invalid or corrupted image:
```json
{
  "detail": "Invalid or corrupted image file"
}
```

**413 Payload Too Large** - File size exceeds limit:
```json
{
  "detail": "File size exceeds 10MB limit"
}
```

---

## File Deletion

### DELETE /upload/file/{file_path:path}
**Description**: Delete a file from Supabase storage

**Authentication**: Required (Admin JWT token)

**Path Parameters**:
- `file_path`: The full path of the file to delete (e.g., "audio/550e8400-e29b-41d4-a716-446655440000.mp3")

**Example Request**:
```bash
curl -X DELETE "http://localhost:8000/upload/file/audio/550e8400-e29b-41d4-a716-446655440000.mp3" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Success Response (200)**:
```json
{
  "message": "File deleted successfully",
  "data": {
    "success": true,
    "message": "File deleted successfully"
  }
}
```

**Error Responses**:

**401 Unauthorized** - Missing or invalid JWT token:
```json
{
  "detail": "Not authenticated"
}
```

**500 Internal Server Error** - Upload service issues:
```json
{
  "detail": "File deletion failed: Error message"
}
```

---

## Storage Configuration

- **Provider**: Supabase Storage
- **Bucket**: `uploads`
- **Folder Structure**:
  - Audio files: `audio/`
  - Image files: `images/`
- **File Naming**: UUID-based unique filenames with original extensions
- **Public Access**: All uploaded files are publicly accessible via generated URLs

## File Validation

### Image Files
- **Format Validation**: MIME type checking against allowed formats
- **Content Validation**: PIL (Pillow) verification to ensure valid image data
- **Size Limits**: 10MB maximum

### Audio Files
- **Format Validation**: MIME type checking against allowed formats
- **Size Limits**: 20MB maximum
- **No content validation** (assumes valid audio based on MIME type)

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200`: Success
- `400`: Bad Request (invalid format, no file, corrupted file)
- `401`: Unauthorized (missing/invalid JWT)
- `413`: Payload Too Large (file size exceeded)
- `500`: Internal Server Error (upload service issues)
- `503`: Service Unavailable (Supabase not configured)

## Environment Requirements

The upload service requires the following environment variable:
- `SUPABASE_ANON_KEY`: Supabase anonymous key for storage access

If not configured, upload endpoints will return 503 Service Unavailable.