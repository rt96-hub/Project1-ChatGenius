# S3 File Storage Implementation Guide

## Setting up AWS S3 Instance and Configuration
- [x] Create an AWS account if you haven't already
- [x] Create a new S3 bucket
  - [x] Choose a unique bucket name (e.g., `chatgenius-files`)
  - [x] Select the appropriate region (preferably same as other AWS services)
  - [x] Configure bucket settings:
    - [x] Block all public access (recommended for security)
    - [x] Enable versioning (optional, for file version control)
    - [x] Enable server-side encryption (recommended)
- [x] Set up IAM credentials
  - [x] Create a new IAM user for the application
  - [x] Create an IAM policy with minimum required permissions:
    ```json
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:PutObject",
                    "s3:GetObject",
                    "s3:DeleteObject",
                    "s3:ListBucket"
                ],
                "Resource": [
                    "arn:aws:s3:::your-bucket-name",
                    "arn:aws:s3:::your-bucket-name/*"
                ]
            }
        ]
    }
    ```
  - [x] Generate and securely store AWS access key and secret key
- [x] Configure CORS policy for the bucket (if needed for frontend direct uploads)
  ```json
  {
      "CORSRules": [
          {
              "AllowedHeaders": ["*"],
              "AllowedMethods": ["PUT", "POST", "DELETE", "GET"],
              "AllowedOrigins": ["http://localhost:3000", "https://your-production-domain.com"],
              "ExposeHeaders": []
          }
      ]
  }
  ```

## Database Setup for File Storage
- [x] Create new `file_uploads` table with the following fields:
  - [x] id SERIAL PRIMARY KEY,
  - [x] message_id INTEGER REFERENCES messages(id) ON DELETE CASCADE,
  - [x] file_name VARCHAR(255) NOT NULL,  -- Original filename for display
  - [x] s3_key VARCHAR(512) NOT NULL,     -- Full path/key in S3 bucket
  - [x] content_type VARCHAR(100),        -- MIME type of the file
  - [x] file_size BIGINT,                -- Size in bytes
  - [x] uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  - [x] uploaded_by INTEGER REFERENCES users(id),
  - [x] is_deleted BOOLEAN DEFAULT FALSE

### Field Explanations:
- `id`: Unique identifier for each file upload
- `message_id`: Foreign key to the messages table
- `file_name`: Original name of the uploaded file (for display purposes)
- `s3_key`: The unique key/path where the file is stored in S3 (typically includes a UUID or timestamp to prevent collisions)
- `content_type`: MIME type of the file (useful for serving files with correct headers)
- `file_size`: Size of the file in bytes (useful for quota management)
- `uploaded_at`: Timestamp of upload
- `uploaded_by`: User who uploaded the file
- `is_deleted`: Soft delete flag

### Recommended Indexes:
- [x] Create the following indexes for optimal performance:
  ```sql
  CREATE INDEX idx_file_uploads_message_id ON file_uploads(message_id);
  CREATE INDEX idx_file_uploads_uploaded_by ON file_uploads(uploaded_by);
  CREATE INDEX idx_file_uploads_uploaded_at ON file_uploads(uploaded_at);
  ```

## Backend Implementation

### New Endpoints
- [x] POST `/files/upload`
  - [x] Should accept multipart/form-data with file and message_id
  - [x] Generate unique S3 key using UUID and original filename
  - [x] Upload file to S3
  - [x] Create file_uploads record
  - [x] Return file metadata including download URL
  - [x] Implement file size limits and allowed file types
  - [x] Broadcast WebSocket event for message update

- [x] GET `/files/download/{file_id}`
  - [x] Verify user has access to the channel containing the file
  - [x] Generate presigned S3 URL for secure download
  - [x] Add rate limiting for downloads
  - [x] Track download statistics

- [x] DELETE `/files/{file_id}`
  - [x] Verify user is file owner
  - [x] Soft delete in database (update is_deleted flag)
  - [x] Optionally delete from S3 (or implement periodic cleanup)
  - [x] Broadcast WebSocket event for message update

### Message Schema Updates
- [x] Update Message Pydantic schema (`schemas.py`)
  - [x] Add files field to include associated file uploads
  - [x] Include download URLs in the response

### CRUD Operations Updates
- [x] Modify message retrieval functions in `crud.py`
  - [x] Include file uploads when fetching messages
  - [x] Join with file_uploads table where needed
  - [x] Filter out soft-deleted files

### WebSocket Events
- [x] Add new WebSocket event types:
  - [x] `file_upload_complete`
  - [x] `file_deleted`
  - [x] Update existing message events to include file data

### Environment Variables
- [x] Add new environment variables:
  - [x] `AWS_ACCESS_KEY_ID`
  - [x] `AWS_SECRET_ACCESS_KEY`
  - [x] `AWS_S3_BUCKET_NAME`
  - [x] `AWS_S3_REGION`
  - [x] `MAX_FILE_SIZE_MB`
  - [x] `ALLOWED_FILE_TYPES`

### Dependencies
- [x] Add new Python packages to requirements.txt:
  - [x] boto3 for AWS S3 integration
  - [x] python-multipart for file upload handling
  - [x] python-magic for file type detection

### Error Handling
- [x] Implement specific error handlers for:
  - [x] File size exceeded
  - [x] Invalid file type
  - [x] S3 upload/download failures
  - [x] Permission denied scenarios
  - [x] Rate limit exceeded

## Frontend Implementation

### New Components
- [ ] FileUploadButton Component
  - Paperclip icon button positioned left of message input
  - Hidden file input element
  - Handle file selection and validation
  - Show loading state during upload
  - Display selected filename before sending

- [ ] FilePreview Component
  - Small preview below message input
  - Show selected file name and size
  - Option to remove file before sending
  - Progress indicator during upload

- [ ] MessageAttachment Component
  - Renders in ChatMessage component
  - Shows file name, size, and type icon
  - Download button/link
  - Loading state for download
  - Error state handling

- [ ] FileUploadProgress Component
  - Progress bar for large file uploads
  - Cancel upload option
  - Error state with retry option

### UI/UX Considerations
- [ ] File upload indicators:
  - Drag and drop zone highlighting
  - Upload progress feedback
  - Success/error notifications
  - File size/type validation messages

- [ ] Message display updates:
  - Attachment preview in message composition
  - File thumbnails for image attachments
  - Consistent file type icons
  - Clear download buttons/links

### State Management Updates
- [ ] Add to message composition state:
  - Currently selected file
  - Upload progress
  - Upload error state

- [ ] Add to message display state:
  - File download status
  - Download error state
  - File preview state

### API Integration
- [ ] Implement file upload logic:
  - Option 1: Single endpoint approach
    - Send multipart request with both message and file
    - Handle as single transaction
    - Pros: Atomic operation, simpler error handling
    - Cons: Longer initial request time

  - Option 2: Separate requests approach
    - Upload file first, get file_id
    - Create message with file_id reference
    - Pros: Better progress tracking, faster message sending
    - Cons: Need to handle partial failures

- [ ] Add download handling:
  - Fetch presigned URL
  - Handle download through browser
  - Track download progress
  - Error handling and retries

### Error Handling
- [ ] Implement user feedback for:
  - File size limits
  - Unsupported file types
  - Upload failures
  - Download failures
  - Network issues

### Accessibility
- [ ] Ensure file interactions are keyboard accessible
- [ ] Add proper ARIA labels
- [ ] Screen reader friendly error messages
- [ ] Focus management during upload/download

## Next Steps
The following sections will be added as we progress:
1. Backend Integration
2. Frontend Implementation
3. Security Considerations
4. Testing Procedures
5. Deployment Instructions

Note: This is a living document and will be updated as we implement each part of the file storage system. 