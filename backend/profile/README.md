# Profile Module

Profile management service for PupMatch backend with support for puppy profiles, prompts, preferences, and geolocation.

## Features

- Profile CRUD operations (Create, Read, Update, Delete)
- Prompt management (questions and answers)
- User preferences (age range, distance, activity level)
- Geolocation with PostGIS (latitude/longitude coordinates)
- Cascade deletion (deleting profile removes all associated data)

**Note:** Photo management (upload, delete, reorder) is handled by a separate photo storage service (Task 6).

---

## 🔄 Profile Management Flow

### Complete Flow: Create Profile → Update → Get → Delete

```
1. CREATE PROFILE
   Client: POST /profile {"name": "Buddy", "age": 2, "bio": "Loves fetch!"}
   ↓
   schemas.py: Validates ProfileInput (name length, age range, bio)
   ↓
   profile_service.py: Checks user doesn't already have profile
   ↓
   profile_service.py: Creates Profile with UUID
   ↓
   profile_service.py: Creates Prompts (if provided)
   ↓
   profile_service.py: Creates UserPreferences (if provided)
   ↓
   database: INSERT INTO profiles, prompts, user_preferences
   ↓
   Client: 201 {"id": "profile-123", "name": "Buddy", ...}

2. UPDATE PROFILE
   Client: PATCH /profile {"age": 3, "bio": "Updated bio"}
   ↓
   schemas.py: Validates ProfileUpdate (all fields optional)
   ↓
   profile_service.py: Finds existing profile by user_id
   ↓
   profile_service.py: Updates only provided fields
   ↓
   profile_service.py: Replaces prompts if provided
   ↓
   profile_service.py: Updates preferences if provided
   ↓
   database: UPDATE profiles, DELETE/INSERT prompts, UPDATE user_preferences
   ↓
   Client: 200 {"id": "profile-123", "age": 3, ...}

3. GET PROFILE
   Client: GET /profile
   ↓
   profile_service.py: Queries profile with relationships (photos, prompts, preferences)
   ↓
   profile_service.py: Converts PostGIS location to Coordinates
   ↓
   Client: 200 {"id": "profile-123", "photos": [...], "prompts": [...]}

4. DELETE PROFILE
   Client: DELETE /profile
   ↓
   profile_service.py: Finds profile by user_id
   ↓
   database: DELETE FROM profiles (CASCADE removes photos, prompts, preferences)
   ↓
   Client: 204 No Content
```

---

## 📁 File Responsibilities

### **`__init__.py`** - Module Interface
**What it does:**
- Exports public API of profile module
- Makes imports cleaner: `from profile import ProfileService`

### **`schemas.py`** - Data Validation
**What it does:**

**Input Schemas:**
- `Coordinates` - Validates latitude (-90 to 90) and longitude (-180 to 180)
- `PromptInput` - Validates question (1-500 chars), answer (1-1000 chars), order
- `UserPreferencesInput` - Validates age range (0-20), distance, activity level, units
- `ProfileInput` - Validates name (1-100 chars), age (0-20), bio (1-2000 chars)
- `ProfileUpdate` - All fields optional for partial updates

**Response Schemas:**
- `PhotoResponse` - Photo data with URL and order
- `PromptResponse` - Prompt with question and answer
- `UserPreferencesResponse` - User matching preferences
- `ProfileResponse` - Complete profile with nested photos, prompts, preferences

**Validation Features:**
- Field length constraints
- Numeric range validation
- Coordinate bounds checking
- Age range validation (max_age >= min_age)
- Uses Pydantic for automatic validation

### **`profile_service.py`** - Business Logic
**What it does:**

**`create_profile(user_id, data)`:**
- Checks if user already has profile → `ProfileAlreadyExistsError`
- Creates Profile with UUID
- Converts Coordinates to PostGIS WKT format
- Creates Prompts (if provided)
- Creates UserPreferences (if provided)
- Returns ProfileResponse

**`update_profile(user_id, data)`:**
- Finds existing profile → `ProfileNotFoundError` if missing
- Updates only provided fields (partial update)
- Replaces all prompts if provided
- Updates or creates preferences if provided
- Returns updated ProfileResponse

**`get_profile(user_id)`:**
- Queries profile with eager loading (photos, prompts, preferences)
- Converts PostGIS location to Coordinates
- Returns ProfileResponse

**`delete_profile(user_id)`:**
- Finds profile → `ProfileNotFoundError` if missing
- Deletes profile (cascade removes photos, prompts, preferences)
- Returns None

**Prompt Management:**
- `add_prompt(user_id, prompt_data)` - Add single prompt
- `update_prompt(user_id, prompt_id, prompt_data)` - Update existing prompt
- `delete_prompt(user_id, prompt_id)` - Delete single prompt

**Private Methods:**
- `_coordinates_to_wkt(coords)` - Convert Coordinates to PostGIS WKT
- `_wkt_to_coordinates(wkt)` - Convert PostGIS WKT to Coordinates
- `_profile_to_response(profile)` - Convert Profile model to ProfileResponse

### **`exceptions.py`** - Error Types
**What it does:**
- `ProfileNotFoundError` - Profile doesn't exist
- `ProfileAlreadyExistsError` - User already has profile
- `InvalidPhotoCountError` - Photo count constraints violated (2-6 photos)

**Why custom exceptions:**
- Clear error types for profile operations
- Easy to catch specific errors
- Better error messages
- Separates business errors from HTTP errors

---

## 🗺️ Geolocation with PostGIS

### What is PostGIS?

PostGIS is a PostgreSQL extension that adds support for geographic objects and spatial queries. It allows us to:
- Store latitude/longitude coordinates efficiently
- Calculate distances between points
- Find nearby profiles within a radius
- Use spatial indexes for fast queries

### Coordinate Storage

```python
# Client sends coordinates
{
  "location": {
    "latitude": 37.7749,   # San Francisco
    "longitude": -122.4194
  }
}

# Service converts to PostGIS WKT (Well-Known Text)
WKTElement('POINT(-122.4194 37.7749)', srid=4326)
# Note: PostGIS uses (longitude, latitude) order!
# SRID 4326 = WGS84 (standard GPS coordinates)

# Database stores as geometry
location: GEOMETRY(POINT, 4326)

# Service converts back to Coordinates for response
{
  "location": {
    "latitude": 37.7749,
    "longitude": -122.4194
  }
}
```

### Why PostGIS?

**Without PostGIS:**
```python
# Slow: Calculate distance in Python for every profile
for profile in all_profiles:
    distance = haversine(user_location, profile.location)
    if distance < max_distance:
        results.append(profile)
```

**With PostGIS:**
```sql
-- Fast: Database does spatial query with index
SELECT * FROM profiles
WHERE ST_DWithin(
    location,
    ST_MakePoint(-122.4194, 37.7749)::geography,
    25000  -- 25km in meters
);
```

**Benefits:**
- ✅ **Fast**: Spatial indexes make queries 100x faster
- ✅ **Accurate**: Uses proper geodesic calculations (accounts for Earth's curvature)
- ✅ **Scalable**: Database handles millions of locations efficiently
- ✅ **Standard**: WGS84 (SRID 4326) is the GPS standard

### Coordinate Validation

```python
# Coordinates schema validates bounds
class Coordinates(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)      # -90° to 90°
    longitude: float = Field(..., ge=-180, le=180)   # -180° to 180°

# Invalid coordinates are rejected
{"latitude": 100, "longitude": 200}  # ❌ ValidationError
{"latitude": 37.7749, "longitude": -122.4194}  # ✅ Valid
```

### Location Updates

```python
# Update profile location
PATCH /profile
{
  "location": {
    "latitude": 40.7128,   # New York
    "longitude": -74.0060
  }
}

# Service updates PostGIS geometry
profile.location = WKTElement('POINT(-74.0060 40.7128)', srid=4326)
```

### Future Geolocation Features

The geolocation service (Task 8) will add:
- Distance calculation between profiles
- Nearby profile search within radius
- Distance unit conversion (miles/kilometers)
- Haversine formula for accurate distances

---

## 🎯 Prompts and Answers

### What are Prompts?

Prompts are questions that users answer to showcase their puppy's personality. Examples:
- "My puppy's favorite activity is..."
- "The best thing about my puppy is..."
- "My puppy's superpower is..."

### Prompt Structure

```python
{
  "question": "My puppy's favorite activity is...",
  "answer": "Chasing squirrels in the park!",
  "order": 0
}
```

### Prompt Operations

```python
# Add prompt during profile creation
POST /profile
{
  "name": "Buddy",
  "age": 2,
  "bio": "Loves fetch!",
  "prompts": [
    {
      "question": "My puppy's favorite activity is...",
      "answer": "Chasing squirrels!",
      "order": 0
    }
  ]
}

# Update all prompts
PATCH /profile
{
  "prompts": [
    {
      "question": "New question",
      "answer": "New answer",
      "order": 0
    }
  ]
}
# Note: This replaces ALL existing prompts

# Add single prompt
POST /profile/prompts
{
  "question": "My puppy's superpower is...",
  "answer": "Making everyone smile!",
  "order": 1
}

# Update single prompt
PATCH /profile/prompts/prompt-123
{
  "question": "Updated question",
  "answer": "Updated answer",
  "order": 0
}

# Delete single prompt
DELETE /profile/prompts/prompt-123
```

---

## ⚙️ User Preferences

### Preference Fields

```python
{
  "min_age": 0,              # Minimum puppy age (0-20)
  "max_age": 5,              # Maximum puppy age (0-20)
  "max_distance": 25.0,      # Maximum distance in miles/km
  "activity_level": "medium", # low, medium, high
  "distance_unit": "miles"   # miles or kilometers
}
```

### Activity Levels

- **low**: Calm puppies, short walks, indoor play
- **medium**: Moderate energy, regular walks, some outdoor play
- **high**: Very active, long runs, lots of outdoor time

### Distance Units

- **miles**: Imperial system (US)
- **kilometers**: Metric system (International)

### Preference Validation

```python
# Age range validation
min_age: 0-20
max_age: 0-20
max_age >= min_age  # Enforced by validator

# Distance validation
max_distance > 0  # Must be positive

# Activity level validation
activity_level in ['low', 'medium', 'high']

# Distance unit validation
distance_unit in ['miles', 'kilometers']
```

### Preference Operations

```python
# Set preferences during profile creation
POST /profile
{
  "name": "Buddy",
  "preferences": {
    "min_age": 1,
    "max_age": 5,
    "max_distance": 25.0,
    "activity_level": "high",
    "distance_unit": "miles"
  }
}

# Update preferences
PATCH /profile
{
  "preferences": {
    "max_distance": 50.0,
    "activity_level": "medium"
  }
}
```

---

## 🔄 Cascade Deletion

### What is Cascade Deletion?

When a profile is deleted, all associated data is automatically deleted:

```
DELETE Profile
    ↓
Automatically deletes:
    ├── Photos (all photos for this profile)
    ├── Prompts (all prompts for this profile)
    ├── UserPreferences (preferences for this profile)
    └── Playgrounds (favorite playgrounds for this profile)
```

### Why Cascade Deletion?

- **Data Integrity**: No orphaned records in database
- **Simplicity**: One delete operation removes everything
- **Performance**: Database handles deletion efficiently
- **Safety**: Configured at database level (can't forget to delete)

### Database Configuration

```python
# In Profile model
photos: Mapped[list["Photo"]] = relationship(
    "Photo",
    back_populates="profile",
    cascade="all, delete-orphan"  # ← Cascade deletion
)

# In database migration
sa.ForeignKeyConstraint(
    ['profile_id'],
    ['profiles.id'],
    ondelete='CASCADE'  # ← Database-level cascade
)
```

### Deletion Flow

```python
# 1. User deletes profile
DELETE /profile

# 2. Service finds profile
profile = await db.get(Profile, user_id)

# 3. Service deletes profile
await db.delete(profile)
await db.commit()

# 4. Database automatically deletes:
# - All photos where profile_id = profile.id
# - All prompts where profile_id = profile.id
# - All preferences where profile_id = profile.id
# - All playgrounds where user_id = user.id
```

---

## 🎯 How Files Work Together

### Create Profile Example

```python
# 1. Client sends request
POST /profile
{
  "name": "Buddy",
  "age": 2,
  "bio": "Loves fetch!",
  "location": {"latitude": 37.7749, "longitude": -122.4194},
  "prompts": [
    {"question": "Favorite activity?", "answer": "Fetch!", "order": 0}
  ],
  "preferences": {
    "min_age": 1,
    "max_age": 5,
    "max_distance": 25.0,
    "activity_level": "high"
  }
}

# 2. schemas.py validates input
ProfileInput(
    name="Buddy",           # ✓ 1-100 chars
    age=2,                  # ✓ 0-20
    bio="Loves fetch!",     # ✓ 1-2000 chars
    location=Coordinates(   # ✓ Valid coordinates
        latitude=37.7749,   # ✓ -90 to 90
        longitude=-122.4194 # ✓ -180 to 180
    ),
    prompts=[...],          # ✓ Valid prompts
    preferences={...}       # ✓ Valid preferences
)

# 3. profile_service.py processes it
async def create_profile(user_id, data):
    # Check if profile exists
    existing = await db.query(Profile).filter_by(user_id=user_id).first()
    if existing:
        raise ProfileAlreadyExistsError()
    
    # Create profile
    profile = Profile(
        id=str(uuid.uuid4()),
        user_id=user_id,
        name=data.name,
        age=data.age,
        bio=data.bio,
        location=WKTElement('POINT(-122.4194 37.7749)', srid=4326)
    )
    db.add(profile)
    await db.flush()  # Get profile.id for relationships
    
    # Create prompts
    for prompt_data in data.prompts:
        prompt = Prompt(
            id=str(uuid.uuid4()),
            profile_id=profile.id,
            question=prompt_data.question,
            answer=prompt_data.answer,
            order=prompt_data.order
        )
        db.add(prompt)
    
    # Create preferences
    preferences = UserPreferences(
        id=str(uuid.uuid4()),
        profile_id=profile.id,
        min_age=data.preferences.min_age,
        max_age=data.preferences.max_age,
        max_distance=data.preferences.max_distance,
        activity_level=data.preferences.activity_level,
        distance_unit=data.preferences.distance_unit
    )
    db.add(preferences)
    
    await db.commit()
    return await get_profile(user_id)

# 4. Client receives response
201 Created
{
  "id": "profile-123",
  "user_id": "user-456",
  "name": "Buddy",
  "age": 2,
  "bio": "Loves fetch!",
  "location": {"latitude": 37.7749, "longitude": -122.4194},
  "photos": [],
  "prompts": [
    {
      "id": "prompt-789",
      "question": "Favorite activity?",
      "answer": "Fetch!",
      "order": 0
    }
  ],
  "preferences": {
    "id": "pref-012",
    "min_age": 1,
    "max_age": 5,
    "max_distance": 25.0,
    "activity_level": "high",
    "distance_unit": "miles"
  },
  "created_at": "2024-12-26T...",
  "updated_at": "2024-12-26T..."
}
```

### Update Profile Example

```python
# 1. Client sends partial update
PATCH /profile
{
  "age": 3,
  "bio": "Updated bio"
}

# 2. schemas.py validates (all fields optional)
ProfileUpdate(
    age=3,              # ✓ 0-20
    bio="Updated bio"   # ✓ 1-2000 chars
)

# 3. profile_service.py updates only provided fields
async def update_profile(user_id, data):
    profile = await db.query(Profile).filter_by(user_id=user_id).first()
    
    if not profile:
        raise ProfileNotFoundError()
    
    # Update only provided fields
    if data.age is not None:
        profile.age = data.age
    if data.bio is not None:
        profile.bio = data.bio
    
    await db.commit()
    return await get_profile(user_id)

# 4. Client receives updated profile
200 OK
{
  "id": "profile-123",
  "age": 3,              # ← Updated
  "bio": "Updated bio",  # ← Updated
  "name": "Buddy",       # ← Unchanged
  ...
}
```

---

## Structure

```
profile/
├── __init__.py          # Module exports
├── profile_service.py   # ProfileService implementation
├── schemas.py           # Pydantic request/response models
├── exceptions.py        # Custom exceptions
└── README.md            # This file
```

## Usage

### Create Profile

```python
POST /profile
{
  "name": "Buddy",
  "age": 2,
  "bio": "Loves fetch and long walks!",
  "location": {
    "latitude": 37.7749,
    "longitude": -122.4194
  },
  "prompts": [
    {
      "question": "My puppy's favorite activity is...",
      "answer": "Chasing squirrels in the park!",
      "order": 0
    }
  ],
  "preferences": {
    "min_age": 1,
    "max_age": 5,
    "max_distance": 25.0,
    "activity_level": "high",
    "distance_unit": "miles"
  }
}

Response: 201 Created
{
  "id": "profile-123",
  "user_id": "user-456",
  "name": "Buddy",
  "age": 2,
  "bio": "Loves fetch and long walks!",
  "location": {"latitude": 37.7749, "longitude": -122.4194},
  "photos": [],
  "prompts": [...],
  "preferences": {...},
  "created_at": "2024-12-26T...",
  "updated_at": "2024-12-26T..."
}
```

### Update Profile

```python
PATCH /profile
{
  "age": 3,
  "bio": "Updated bio"
}

Response: 200 OK
{
  "id": "profile-123",
  "age": 3,
  "bio": "Updated bio",
  ...
}
```

### Get Profile

```python
GET /profile

Response: 200 OK
{
  "id": "profile-123",
  "user_id": "user-456",
  "name": "Buddy",
  "age": 2,
  "photos": [...],
  "prompts": [...],
  "preferences": {...}
}
```

### Delete Profile

```python
DELETE /profile

Response: 204 No Content
```

## Implementation Details

### Geolocation

- **Storage**: PostGIS GEOMETRY(POINT, 4326)
- **Format**: WGS84 (standard GPS coordinates)
- **Conversion**: Coordinates ↔ WKT (Well-Known Text)
- **Validation**: Latitude (-90 to 90), Longitude (-180 to 180)

### Relationships

- **Photos**: One-to-many (profile has many photos)
- **Prompts**: One-to-many (profile has many prompts)
- **Preferences**: One-to-one (profile has one preferences)
- **Cascade**: Deleting profile removes all related data

### Validation

- **Name**: 1-100 characters
- **Age**: 0-20 years
- **Bio**: 1-2000 characters
- **Prompts**: Question (1-500 chars), Answer (1-1000 chars)
- **Preferences**: Age range (0-20), Distance (> 0)

## Error Handling

### Custom Exceptions

- `ProfileNotFoundError` - Profile doesn't exist
- `ProfileAlreadyExistsError` - User already has profile
- `InvalidPhotoCountError` - Photo count constraints violated

### HTTP Status Codes

- `201` - Profile created successfully
- `200` - Profile updated/retrieved successfully
- `204` - Profile deleted successfully
- `404` - Profile not found
- `409` - Profile already exists
- `400` - Validation error

## Testing

See Task 5.3 for property-based tests validating:
- **Property 3**: Profile Photo Count Constraints (2-6 photos) - *Note: This will be tested in the photo storage service (Task 6)*
- **Property 17**: Photo Order Preservation - *Note: This will be tested in the photo storage service (Task 6)*

## Requirements Validated

✅ **Requirement 2.1** - Profile creation with name, age, bio, location
✅ **Requirement 2.2** - Profile updates persist immediately
✅ **Requirement 2.5** - Prompts and answers stored with profile
✅ **Requirement 2.6** - Profile retrieval with all data
✅ **Requirement 2.7** - Profile deletion removes all associated data

**Note:** Photo-related requirements (2.4, 3.x) are handled by the photo storage service (Task 6)

## Future Enhancements

- Geolocation service (Task 8) - Distance calculations and nearby profile search
- Photo storage service (Task 6) - Photo upload, validation, and management
