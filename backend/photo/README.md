# Photo Module

Photo storage and management service for PupMatch backend with support for local filesystem storage (development) and cloud storage (production).

## Features

- Photo upload with validation (JPEG, PNG, WebP; max 10MB)
- Photo deletion with automatic reordering
- Photo reordering (drag and drop support)
- Photo count constraints (2-6 photos per profile)
- Abstract storage interface (swap providers easily)
- Local filesystem storage (development)
- Ready for cloud storage (S3, GCS, Cloudflare R2)

---

## 🏗️ Architecture

### Storage Interface Pattern

We use an **abstract storage interface** that allows swapping storage providers without changing application code:

```
PhotoService
    ↓
StorageInterface (abstract)
    ↓
├── LocalStorage (development)
├── S3Storage (production - AWS)
├── GCSStorage (production - Google Cloud)
└── R2Storage (production - Cloudflare)
```

### Why This Pattern?

**Benefits:**
- ✅ **Flexible**: Swap storage providers by changing one line
- ✅ **Testable**: Use local storage for tests, no cloud account needed
- ✅ **Cost-effective**: Develop locally, deploy to cloud
- ✅ **Provider-agnostic**: Not locked into one cloud provider

---

## 📁 File Responsibilities

### **`storage_interface.py`** - Abstract Interface
**What it does:**
- Defines the contract all storage providers must implement
- Methods: `upload()`, `delete()`, `get_signed_url()`, `validate_file()`
- Allows swapping providers without changing PhotoService

### **`local_storage.py`** - Local Filesystem Implementation
**What it does:**
- Stores files on local filesystem (development)
- Validates file type (JPEG, PNG, WebP)
- Validates file size (max 10MB)
- Generates unique filenames (UUID)
- Returns URLs for accessing files

**File storage:**
```
backend/uploads/photos/
├── 550e8400-e29b-41d4-a716-446655440000.jpg
├── 6ba7b810-9dad-11d1-80b4-00c04fd430c8.png
└── 7c9e6679-7425-40de-944b-e07fc1f90ae7.webp
```

### **`photo_service.py`** - Business Logic
**What it does:**

**`upload_photo(user_id, file, filename, content_type, file_size)`:**
- Validates profile exists
- Checks photo count (max 6)
- Validates file (type, size)
- Uploads to storage
- Creates Photo record in database
- Returns Photo object

**`delete_photo(user_id, photo_id)`:**
- Validates profile and photo exist
- Checks photo count (min 2)
- Deletes from storage
- Deletes from database
- Reorders remaining photos

**`reorder_photos(user_id, photo_ids)`:**
- Validates all photo IDs match
- Updates order field for each photo
- Returns photos in new order

**`get_photos(user_id)`:**
- Returns all photos for profile
- Ordered by order field

### **`schemas.py`** - Data Validation
**What it does:**
- `PhotoResponse` - Photo data with URL and order
- `PhotoUploadResponse` - Upload success response
- `PhotoReorderRequest` - List of photo IDs (2-6)
- `PhotoReorderResponse` - Reordered photos

### **`routes.py`** - REST Endpoints
**What it does:**
- `POST /photos/upload` - Upload photo (multipart/form-data)
- `DELETE /photos/{photo_id}` - Delete photo
- `PUT /photos/reorder` - Reorder photos
- `GET /photos/` - Get all photos

**Why REST (not GraphQL)?**
- File uploads work better with multipart/form-data
- Standard pattern across all frameworks
- GraphQL is for data queries, not binary uploads

### **`exceptions.py`** - Error Types
**What it does:**
- `PhotoNotFoundError` - Photo doesn't exist
- `InvalidPhotoCountError` - Photo count constraints violated
- `ProfileNotFoundError` - Profile doesn't exist

---

## 📸 Photo Constraints

### Count Constraints
- **Minimum**: 2 photos required
- **Maximum**: 6 photos allowed
- **Enforced**: On upload and delete

### File Validation
- **Types**: JPEG, PNG, WebP only
- **Size**: Maximum 10MB per file
- **Extensions**: .jpg, .jpeg, .png, .webp

### Photo Order
- **Range**: 0-5 (6 photos max)
- **Automatic**: Order assigned on upload
- **Reorderable**: Drag and drop support
- **Auto-reorder**: After deletion, gaps are filled

---

## 🔄 Photo Operations Flow

### Upload Photo

```
1. Client uploads file
   POST /photos/upload
   Content-Type: multipart/form-data
   file: [binary data]
   ↓
2. routes.py validates authentication
   ↓
3. photo_service.py validates:
   - Profile exists
   - Photo count < 6
   - File type (JPEG/PNG/WebP)
   - File size < 10MB
   ↓
4. local_storage.py:
   - Generates unique filename (UUID)
   - Saves to uploads/photos/
   - Returns URL
   ↓
5. photo_service.py:
   - Creates Photo record
   - Sets order = current photo count
   - Saves to database
   ↓
6. Client receives response
   201 Created
   {
     "photo": {
       "id": "photo-123",
       "url": "http://localhost:8000/uploads/photos/uuid.jpg",
       "order": 2
     },
     "message": "Photo uploaded successfully"
   }
```

### Delete Photo

```
1. Client deletes photo
   DELETE /photos/photo-123
   ↓
2. photo_service.py validates:
   - Profile exists
   - Photo exists
   - Photo count > 2 (must keep at least 2)
   ↓
3. local_storage.py:
   - Deletes file from uploads/photos/
   ↓
4. photo_service.py:
   - Deletes Photo record
   - Reorders remaining photos (fills gap)
   ↓
5. Client receives response
   204 No Content
```

### Reorder Photos

```
1. Client reorders photos
   PUT /photos/reorder
   {
     "photo_ids": ["photo-3", "photo-1", "photo-2"]
   }
   ↓
2. photo_service.py validates:
   - All photo IDs exist
   - Count matches existing photos
   ↓
3. photo_service.py:
   - Updates order field for each photo
   - photo-3: order = 0
   - photo-1: order = 1
   - photo-2: order = 2
   ↓
4. Client receives response
   200 OK
   {
     "photos": [
       {"id": "photo-3", "order": 0},
       {"id": "photo-1", "order": 1},
       {"id": "photo-2", "order": 2}
     ],
     "message": "Photos reordered successfully"
   }
```

---

## 🔄 Swapping Storage Providers

### Current: Local Storage (Development)

```python
# photo/routes.py
def get_photo_service(db: AsyncSession = Depends(get_db)):
    storage = LocalStorage()  # ← Local filesystem
    return PhotoService(db, storage)
```

### Future: AWS S3 (Production)

```python
# photo/s3_storage.py (create this file)
class S3Storage(StorageService):
    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.bucket_name = os.getenv("S3_BUCKET_NAME")
    
    async def upload(self, file, filename, content_type):
        # Upload to S3
        key = f"photos/{uuid.uuid4()}{Path(filename).suffix}"
        self.s3_client.upload_fileobj(file, self.bucket_name, key)
        return f"https://{self.bucket_name}.s3.amazonaws.com/{key}"
    
    async def delete(self, file_url):
        # Extract key from URL and delete
        key = file_url.split('.com/')[-1]
        self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
    
    async def get_signed_url(self, file_url, expires_in=3600):
        # Generate pre-signed URL
        key = file_url.split('.com/')[-1]
        return self.s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket_name, 'Key': key},
            ExpiresIn=expires_in
        )

# photo/routes.py
def get_photo_service(db: AsyncSession = Depends(get_db)):
    storage = S3Storage()  # ← Just change this line!
    return PhotoService(db, storage)
```

### Future: Google Cloud Storage

```python
# photo/gcs_storage.py
class GCSStorage(StorageService):
    def __init__(self):
        self.client = storage.Client()
        self.bucket = self.client.bucket(os.getenv("GCS_BUCKET_NAME"))
    
    async def upload(self, file, filename, content_type):
        # Upload to GCS
        blob_name = f"photos/{uuid.uuid4()}{Path(filename).suffix}"
        blob = self.bucket.blob(blob_name)
        blob.upload_from_file(file, content_type=content_type)
        return blob.public_url
```

### Configuration-Based (Best Practice)

```python
# photo/storage_factory.py
def get_storage_service() -> StorageService:
    provider = os.getenv("STORAGE_PROVIDER", "local")
    
    if provider == "s3":
        return S3Storage()
    elif provider == "gcs":
        return GCSStorage()
    elif provider == "r2":
        return R2Storage()
    else:
        return LocalStorage()

# .env
STORAGE_PROVIDER=local  # Change to "s3" for production
```

---

## 🎯 Usage Examples

### Upload Photo

```bash
curl -X POST http://localhost:8000/photos/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@puppy.jpg"

# Response:
{
  "photo": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "profile_id": "profile-123",
    "url": "http://localhost:8000/uploads/photos/550e8400-e29b-41d4-a716-446655440000.jpg",
    "order": 0,
    "created_at": "2024-12-28T10:30:00Z"
  },
  "message": "Photo uploaded successfully"
}
```

### Delete Photo

```bash
curl -X DELETE http://localhost:8000/photos/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer <token>"

# Response: 204 No Content
```

### Reorder Photos

```bash
curl -X PUT http://localhost:8000/photos/reorder \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "photo_ids": [
      "photo-3",
      "photo-1",
      "photo-2"
    ]
  }'

# Response:
{
  "photos": [
    {"id": "photo-3", "order": 0, ...},
    {"id": "photo-1", "order": 1, ...},
    {"id": "photo-2", "order": 2, ...}
  ],
  "message": "Photos reordered successfully"
}
```

### Get All Photos

```bash
curl -X GET http://localhost:8000/photos/ \
  -H "Authorization: Bearer <token>"

# Response:
[
  {
    "id": "photo-1",
    "profile_id": "profile-123",
    "url": "http://localhost:8000/uploads/photos/uuid1.jpg",
    "order": 0,
    "created_at": "2024-12-28T10:30:00Z"
  },
  {
    "id": "photo-2",
    "profile_id": "profile-123",
    "url": "http://localhost:8000/uploads/photos/uuid2.jpg",
    "order": 1,
    "created_at": "2024-12-28T10:31:00Z"
  }
]
```

---

## Structure

```
photo/
├── __init__.py              # Module exports
├── storage_interface.py     # Abstract storage interface
├── local_storage.py         # Local filesystem implementation
├── photo_service.py         # PhotoService implementation
├── schemas.py               # Pydantic request/response models
├── routes.py                # FastAPI REST endpoints
├── exceptions.py            # Custom exceptions
└── README.md                # This file
```

---

## Error Handling

### Custom Exceptions

- `PhotoNotFoundError` - Photo doesn't exist (404)
- `InvalidPhotoCountError` - Photo count constraints violated (400)
- `ProfileNotFoundError` - Profile doesn't exist (404)
- `ValueError` - File validation failed (400)

### HTTP Status Codes

- `201` - Photo uploaded successfully
- `204` - Photo deleted successfully
- `200` - Photos reordered successfully
- `400` - Validation error (file type, size, count)
- `404` - Photo or profile not found

---

## Testing

See Task 6.3 for property-based tests validating:
- **Property 4**: Photo Upload Validation
- **Validates: Requirements 3.2, 3.3**

---

## Requirements Validated

✅ **Requirement 3.1** - Photo upload with URL return
✅ **Requirement 3.2** - File type validation (JPEG, PNG, WebP)
✅ **Requirement 3.3** - File size validation (max 10MB)
✅ **Requirement 3.4** - Photo deletion from storage
✅ **Requirement 3.5** - Photo reordering
✅ **Requirement 2.4** - Photo count constraints (2-6 photos)

---

## Future Enhancements

- S3 storage implementation (AWS)
- GCS storage implementation (Google Cloud)
- R2 storage implementation (Cloudflare)
- Image optimization (resize, compress)
- CDN integration
- Thumbnail generation
