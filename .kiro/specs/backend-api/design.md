# Design Document: Backend API

## Overview

This design document describes the backend architecture for PupMatch, a puppy dating application. The backend will provide authentication, profile management, real-time messaging, geolocation, and playground mapping features.

After evaluating multiple technology options (detailed below), we've selected **Python with FastAPI** and a **GraphQL + WebSocket** hybrid API architecture. This combination provides excellent developer experience, strong typing, async performance, and flexible data querying.

## Technology Selection

### Framework Comparison

We evaluated three primary backend frameworks:

#### Option 1: Node.js with TypeScript

**Pros:**
- Excellent for real-time applications (event-driven, non-blocking I/O)
- Large ecosystem (npm) with extensive libraries
- JavaScript/TypeScript shared with React Native frontend
- Strong async/await support
- Great WebSocket support (Socket.io)
- Fast development with hot reloading

**Cons:**
- Single-threaded (CPU-intensive tasks can block)
- Callback hell potential (though mitigated by async/await)
- Less mature for data science/ML if needed later
- Type safety requires TypeScript discipline

**Best for:** Real-time apps, microservices, I/O-heavy workloads

#### Option 2: Python with FastAPI

**Pros:**
- Modern async framework (comparable to Node.js performance)
- Excellent type hints with Pydantic validation
- Auto-generated OpenAPI/GraphQL documentation
- Strong data science ecosystem (if ML matching needed)
- Clean, readable syntax
- Great ORM options (SQLAlchemy)
- Built-in dependency injection
- Excellent testing support (pytest)

**Cons:**
- Slightly slower than Node.js for pure I/O
- GIL (Global Interpreter Lock) for CPU-bound tasks
- Smaller ecosystem than Node.js
- Less common for real-time apps (though FastAPI WebSockets work well)

**Best for:** API-first applications, data-heavy apps, ML integration

#### Option 3: Java with Spring Boot

**Pros:**
- Enterprise-grade stability and performance
- Strong type safety (compile-time checking)
- Excellent for large-scale systems
- Mature ecosystem with battle-tested libraries
- Great for microservices architecture
- Strong concurrency support

**Cons:**
- Verbose syntax (more boilerplate)
- Slower development velocity
- Heavier resource usage
- Steeper learning curve
- Longer build times

**Best for:** Enterprise applications, large teams, long-term maintenance

#### Decision: Python with FastAPI

**Rationale:**
1. **Type Safety**: Pydantic provides excellent runtime validation and type hints
2. **Performance**: Async support makes it competitive with Node.js for I/O operations
3. **Developer Experience**: Clean syntax, auto-documentation, fast development
4. **Future-Proofing**: Easy to add ML-based matching algorithms later
5. **Modern Stack**: FastAPI is cutting-edge with growing adoption
6. **Testing**: pytest is superior for property-based testing (Hypothesis library)

### API Architecture Comparison

We evaluated three API architectural styles:

#### Option 1: RESTful API

**Pros:**
- Industry standard, well-understood
- Stateless, cacheable
- Simple to implement and debug
- Great tooling (Postman, Swagger)
- HTTP status codes provide clear semantics
- Works well with CDNs

**Cons:**
- Over-fetching (getting more data than needed)
- Under-fetching (multiple requests for related data)
- Versioning challenges (v1, v2 endpoints)
- No built-in real-time support
- Rigid endpoint structure

**Best for:** Simple CRUD apps, public APIs, caching-heavy workloads

#### Option 2: GraphQL

**Pros:**
- Client specifies exact data needs (no over/under-fetching)
- Single endpoint (no versioning issues)
- Strong typing with schema
- Excellent developer tools (GraphQL Playground)
- Efficient for complex, nested data
- Built-in introspection
- Great for mobile apps (reduces bandwidth)

**Cons:**
- More complex to implement
- Caching is harder (no HTTP caching)
- Can expose too much data if not careful
- Query complexity can cause performance issues
- Learning curve for clients

**Best for:** Complex data models, mobile apps, flexible client needs

#### Option 3: gRPC

**Pros:**
- Extremely fast (Protocol Buffers binary format)
- Strong typing with .proto files
- Bi-directional streaming
- Great for microservices communication
- Efficient bandwidth usage
- Code generation for multiple languages

**Cons:**
- Not browser-friendly (requires gRPC-Web)
- Harder to debug (binary format)
- Less human-readable
- Smaller ecosystem than REST/GraphQL
- Steeper learning curve

**Best for:** Microservices, high-performance internal APIs, streaming

#### Option 4: tRPC

**Pros:**
- End-to-end type safety (TypeScript only)
- No code generation needed
- Simple to implement
- Great developer experience
- Automatic client generation

**Cons:**
- TypeScript only (not suitable for Python backend)
- Smaller ecosystem
- Less mature than alternatives

**Best for:** Full-stack TypeScript applications

#### Decision: GraphQL + WebSocket Hybrid

**Rationale:**
1. **Flexible Data Fetching**: Mobile app can request exactly what it needs
2. **Single Endpoint**: Simplifies API management and versioning
3. **Strong Typing**: GraphQL schema provides type safety
4. **Real-Time Support**: WebSocket for chat, GraphQL for everything else
5. **Mobile-Optimized**: Reduces bandwidth usage for React Native app
6. **Developer Experience**: Strawberry GraphQL integrates beautifully with FastAPI

**Hybrid Approach:**
- **GraphQL**: For queries (profiles, matches, playgrounds) and mutations (like, update profile)
- **WebSocket**: For real-time messaging (chat messages, match notifications)
- **REST**: For file uploads (photos) - multipart/form-data works better with REST

## Architecture

### Technology Stack

- **Runtime**: Python 3.11+
- **API Framework**: FastAPI with Strawberry GraphQL
- **Real-time**: FastAPI WebSockets
- **Database**: PostgreSQL with PostGIS extension (geospatial queries)
- **Cache**: Redis (session management, rate limiting, recommendations)
- **Background Jobs**: Celery with Redis broker (recommendation refresh)
- **File Storage**: AWS S3 or compatible object storage (boto3)
- **Authentication**: JWT (JSON Web Tokens) with python-jose
- **ORM**: SQLAlchemy 2.0 with async support
- **Validation**: Pydantic v2

### System Components

```
┌─────────────┐
│   Client    │
│  (React     │
│   Native)   │
└──────┬──────┘
       │
       ├─────────────────┐
       │                 │
       ▼                 ▼
┌─────────────┐   ┌─────────────┐
│   GraphQL   │   │  WebSocket  │
│   (Strawb.) │   │  (FastAPI)  │
└──────┬──────┘   └──────┬──────┘
       │                 │
       ├─────────────────┤
       │                 │
       ▼                 ▼
┌─────────────────────────────┐
│     Business Logic Layer    │
│  (Services & Controllers)   │
└──────────────┬──────────────┘
               │
       ┌───────┴───────┐
       │               │
       ▼               ▼
┌─────────────┐ ┌─────────────┐
│  PostgreSQL │ │    Redis    │
│  + PostGIS  │ │             │
└─────────────┘ └─────────────┘
       │
       ▼
┌─────────────┐
│   AWS S3    │
│  (Photos)   │
└─────────────┘
```

### Architecture Layers

1. **API Layer**: Strawberry GraphQL resolvers and FastAPI WebSocket handlers
2. **Service Layer**: Business logic for authentication, matching, messaging, etc.
3. **Data Access Layer**: SQLAlchemy ORM for database operations
4. **Storage Layer**: PostgreSQL database and S3 object storage

## Components and Interfaces

### 1. Authentication Service

**Responsibilities:**
- User registration and login
- Password hashing (bcrypt)
- JWT token generation and validation
- Password reset flow

**Key Methods:**
```python
from typing import Protocol
from datetime import datetime

class AuthService(Protocol):
    async def register(self, email: str, password: str) -> User:
        ...
    
    async def login(self, email: str, password: str) -> AuthToken:
        ...
    
    async def validate_token(self, token: str) -> User:
        ...
    
    async def request_password_reset(self, email: str) -> None:
        ...
    
    async def reset_password(self, token: str, new_password: str) -> None:
        ...
```

### 2. Profile Service

**Responsibilities:**
- Profile CRUD operations
- Photo management
- Prompt management
- Profile validation

**Key Methods:**
```python
from typing import Protocol, Optional

class ProfileService(Protocol):
    async def create_profile(self, user_id: str, data: ProfileInput) -> Profile:
        ...
    
    async def update_profile(self, user_id: str, data: ProfileInput) -> Profile:
        ...
    
    async def get_profile(self, user_id: str) -> Profile:
        ...
    
    async def delete_profile(self, user_id: str) -> None:
        ...
    
    async def add_photo(self, user_id: str, file: bytes) -> Photo:
        ...
    
    async def delete_photo(self, user_id: str, photo_id: str) -> None:
        ...
    
    async def reorder_photos(self, user_id: str, photo_ids: list[str]) -> None:
        ...
```

### 3. Photo Storage Service

**Responsibilities:**
- Upload photos to S3
- Generate signed URLs
- Validate file types and sizes
- Delete photos from storage

**Key Methods:**
```python
class PhotoStorageService(Protocol):
    async def upload_photo(self, file: bytes, user_id: str) -> str:
        ...
    
    async def delete_photo(self, photo_url: str) -> None:
        ...
    
    async def get_signed_url(self, photo_url: str) -> str:
        ...
    
    async def validate_photo(self, file: bytes) -> bool:
        ...
```

### 4. Matching Service

**Responsibilities:**
- Calculate compatibility scores
- Filter profiles by preferences
- Exclude already-seen profiles
- Order profiles by relevance

**Key Methods:**
```python
class MatchingService(Protocol):
    async def get_recommendations(self, user_id: str, limit: int) -> list[Profile]:
        ...
    
    def calculate_compatibility(self, user1: Profile, user2: Profile) -> float:
        ...
    
    def filter_by_preferences(
        self, profiles: list[Profile], preferences: UserPreferences
    ) -> list[Profile]:
        ...
```

### 5. Like/Pass Service

**Responsibilities:**
- Record like and pass actions
- Detect mutual matches
- Trigger match notifications
- Manage match state

**Key Methods:**
```python
from dataclasses import dataclass

@dataclass
class LikeResult:
    is_match: bool
    match: Optional[Match] = None

class LikePassService(Protocol):
    async def like_profile(self, user_id: str, target_id: str) -> LikeResult:
        ...
    
    async def pass_profile(self, user_id: str, target_id: str) -> None:
        ...
    
    async def unlike_profile(self, user_id: str, target_id: str) -> None:
        ...
    
    async def get_matches(self, user_id: str) -> list[Match]:
        ...
    
    async def unmatch(self, user_id: str, match_id: str) -> None:
        ...
```

### 6. Messaging Service

**Responsibilities:**
- Send and receive messages
- Store message history
- Deliver real-time messages via WebSocket
- Queue offline messages

**Key Methods:**
```python
class MessagingService(Protocol):
    async def send_message(
        self, sender_id: str, recipient_id: str, content: str
    ) -> Message:
        ...
    
    async def get_conversation(self, user_id: str, match_id: str) -> list[Message]:
        ...
    
    async def get_conversations(self, user_id: str) -> list[Conversation]:
        ...
    
    async def delete_conversation(self, user_id: str, match_id: str) -> None:
        ...
    
    async def mark_as_read(self, user_id: str, message_ids: list[str]) -> None:
        ...
```

### 7. Geolocation Service

**Responsibilities:**
- Store and update user locations
- Calculate distances using haversine formula
- Filter profiles by distance
- Support PostGIS spatial queries

**Key Methods:**
```python
@dataclass
class Coordinates:
    latitude: float
    longitude: float

class GeolocationService(Protocol):
    async def update_location(self, user_id: str, lat: float, lon: float) -> None:
        ...
    
    def calculate_distance(self, point1: Coordinates, point2: Coordinates) -> float:
        ...
    
    async def find_nearby(self, user_id: str, max_distance: float) -> list[Profile]:
        ...
    
    def validate_coordinates(self, lat: float, lon: float) -> bool:
        ...
```

### 8. Playground Service

**Responsibilities:**
- Manage favorite playgrounds
- Search playgrounds by location
- Share playground locations
- Store playground metadata

**Key Methods:**
```python
class PlaygroundService(Protocol):
    async def add_playground(self, user_id: str, data: PlaygroundInput) -> Playground:
        ...
    
    async def remove_playground(self, user_id: str, playground_id: str) -> None:
        ...
    
    async def get_favorite_playgrounds(self, user_id: str) -> list[Playground]:
        ...
    
    async def search_playgrounds(
        self, location: Coordinates, radius: float
    ) -> list[Playground]:
        ...
    
    async def search_by_name(self, query: str) -> list[Playground]:
        ...
```

### 9. Notification Service

**Responsibilities:**
- Send push notifications
- Queue notifications for offline users
- Manage notification preferences
- Track notification delivery

**Key Methods:**
```python
class NotificationService(Protocol):
    async def send_match_notification(self, user_id: str, match: Match) -> None:
        ...
    
    async def send_message_notification(self, user_id: str, message: Message) -> None:
        ...
    
    async def update_preferences(
        self, user_id: str, preferences: NotificationPreferences
    ) -> None:
        ...
    
    async def queue_notification(self, user_id: str, notification: Notification) -> None:
        ...
```

### 10. Recommendation Cache Service

**Responsibilities:**
- Pre-compute match recommendations
- Store recommendations in Redis
- Refresh recommendations periodically
- Handle cache invalidation

**Key Methods:**
```python
from typing import Protocol

class RecommendationCacheService(Protocol):
    async def get_cached_recommendations(self, user_id: str) -> list[str]:
        """Get cached profile IDs from Redis"""
        ...
    
    async def refresh_recommendations(self, user_id: str) -> None:
        """Recompute and cache recommendations for a user"""
        ...
    
    async def invalidate_cache(self, user_id: str) -> None:
        """Remove cached recommendations for a user"""
        ...
    
    async def batch_refresh_recommendations(self, user_ids: list[str]) -> None:
        """Background job to refresh multiple users' recommendations"""
        ...
```

### 11. Background Job Service (Celery Tasks)

**Responsibilities:**
- Schedule periodic recommendation refreshes
- Process offline notification delivery
- Clean up expired data
- Generate analytics

**Key Tasks:**
```python
from celery import Celery

celery_app = Celery('pupmatch', broker='redis://localhost:6379/0')

@celery_app.task
def refresh_recommendations_task():
    """Runs every 15 minutes to refresh recommendations"""
    ...

@celery_app.task
def cleanup_expired_data_task():
    """Runs daily to clean up old passes, expired tokens"""
    ...

@celery_app.task
def deliver_queued_notifications_task():
    """Runs every 5 minutes to deliver offline notifications"""
    ...
```

## Data Models

### User
```python
from datetime import datetime
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    id: str
    email: EmailStr
    password_hash: str
    created_at: datetime
    updated_at: datetime
```

### Profile
```python
from typing import Literal

class Profile(BaseModel):
    id: str
    user_id: str
    name: str
    age: int
    bio: str
    photos: list[Photo]
    prompts: list[Prompt]
    location: Coordinates
    preferences: UserPreferences
    created_at: datetime
    updated_at: datetime
```

### Photo
```python
class Photo(BaseModel):
    id: str
    profile_id: str
    url: str
    order: int
    created_at: datetime
```

### Prompt
```python
class Prompt(BaseModel):
    id: str
    profile_id: str
    question: str
    answer: str
    order: int
```

### UserPreferences
```python
ActivityLevel = Literal['low', 'medium', 'high']
DistanceUnit = Literal['miles', 'kilometers']

class UserPreferences(BaseModel):
    id: str
    profile_id: str
    min_age: int
    max_age: int
    max_distance: float
    activity_level: ActivityLevel
    distance_unit: DistanceUnit
```

### Like
```python
class Like(BaseModel):
    id: str
    user_id: str
    target_id: str
    created_at: datetime
```

### Pass
```python
class Pass(BaseModel):
    id: str
    user_id: str
    target_id: str
    created_at: datetime
```

### Match
```python
class Match(BaseModel):
    id: str
    user1_id: str
    user2_id: str
    created_at: datetime
```

### Message
```python
class Message(BaseModel):
    id: str
    conversation_id: str
    sender_id: str
    recipient_id: str
    content: str
    read: bool
    created_at: datetime
```

### Conversation
```python
from typing import Optional

class Conversation(BaseModel):
    id: str
    match_id: str
    user1_id: str
    user2_id: str
    last_message: Optional[Message] = None
    unread_count: int
    created_at: datetime
    updated_at: datetime
```

### Playground
```python
class Playground(BaseModel):
    id: str
    user_id: str
    name: str
    description: str
    location: Coordinates
    created_at: datetime
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Authentication Token Validity
*For any* valid authentication token, decoding and validating it should return the same user ID that was encoded in the token.
**Validates: Requirements 1.2, 1.5**

### Property 2: Password Hash Irreversibility
*For any* password, hashing it should produce a value that cannot be reversed to obtain the original password, and the same password should always produce a verifiable hash.
**Validates: Requirements 1.1**

### Property 3: Profile Photo Count Constraints
*For any* profile, the number of photos should always be between 2 and 6 (inclusive) after any photo operation completes.
**Validates: Requirements 2.4**

### Property 4: Photo Upload Validation
*For any* uploaded file, if it is not a valid image format (JPEG, PNG, WebP) or exceeds 10MB, the upload should be rejected.
**Validates: Requirements 3.2, 3.3**

### Property 5: Match Mutual Requirement
*For any* match record, both users must have liked each other (mutual likes must exist in the database).
**Validates: Requirements 5.3**

### Property 6: Match Uniqueness
*For any* two users, there should be at most one active match record between them at any time.
**Validates: Requirements 5.3**

### Property 7: Messaging Authorization
*For any* message sent between two users, a match must exist between those users.
**Validates: Requirements 7.2**

### Property 8: Distance Calculation Consistency
*For any* two geographic coordinates, calculating the distance from A to B should equal the distance from B to A.
**Validates: Requirements 8.2**

### Property 9: Distance Unit Conversion
*For any* distance in miles, converting to kilometers and back to miles should return the original value (within rounding tolerance).
**Validates: Requirements 8.3**

### Property 10: Coordinate Validation
*For any* coordinates, latitude must be between -90 and 90, and longitude must be between -180 and 180.
**Validates: Requirements 8.6**

### Property 11: Profile Discovery Exclusion
*For any* user requesting profile recommendations, the returned profiles should not include profiles they have already liked or passed.
**Validates: Requirements 4.2, 4.3**

### Property 12: Playground Location Validity
*For any* playground, the location coordinates must be valid (latitude between -90 and 90, longitude between -180 and 180).
**Validates: Requirements 9.1**

### Property 13: Rate Limiting Enforcement
*For any* user making API requests, if they exceed the rate limit threshold, subsequent requests should be rejected with a 429 status code.
**Validates: Requirements 12.4**

### Property 14: Token Expiration
*For any* expired authentication token, validation should fail and return an authentication error.
**Validates: Requirements 1.6**

### Property 15: Like/Pass Idempotency
*For any* user and target profile, performing the same like or pass action multiple times should have the same effect as performing it once.
**Validates: Requirements 5.5**

### Property 16: Unmatch Cascade
*For any* unmatch operation, the match record should be deleted and future messaging between those users should be prevented.
**Validates: Requirements 6.3, 7.2**

### Property 17: Photo Order Preservation
*For any* profile, after reordering photos, retrieving the profile should return photos in the new specified order.
**Validates: Requirements 3.5**

## Error Handling

### Error Categories

1. **Authentication Errors** (401)
   - Invalid credentials
   - Expired token
   - Missing token

2. **Authorization Errors** (403)
   - Insufficient permissions
   - Attempting to access another user's data

3. **Validation Errors** (400)
   - Invalid input data
   - Missing required fields
   - Data format errors

4. **Not Found Errors** (404)
   - Resource doesn't exist
   - User not found

5. **Conflict Errors** (409)
   - Duplicate email registration
   - Duplicate like/pass action

6. **Rate Limit Errors** (429)
   - Too many requests

7. **Server Errors** (500)
   - Database connection failures
   - External service failures

### Error Response Format

All errors will follow a consistent GraphQL error format:

```python
from typing import Any, Optional

class ErrorResponse(BaseModel):
    message: str
    code: str
    extensions: dict[str, Any]
    
class ErrorExtensions(BaseModel):
    status_code: int
    details: Optional[Any] = None
```

### Error Handling Strategy

- All service methods should throw typed errors
- GraphQL resolvers should catch and format errors
- Sensitive information should never be exposed in error messages
- All errors should be logged with context for debugging
- Client-facing errors should be user-friendly

## Testing Strategy

### Dual Testing Approach

The backend will use both unit tests and property-based tests to ensure correctness:

**Unit Tests:**
- Test specific examples and edge cases
- Test error conditions and validation
- Test integration between services
- Mock external dependencies (S3, Redis)

**Property-Based Tests:**
- Test universal properties across all inputs
- Use Hypothesis library for Python
- Run minimum 100 iterations per property test
- Each property test references its design document property

### Property Test Configuration

All property tests will:
- Run 100+ iterations with randomized inputs
- Be tagged with format: **Feature: backend-api, Property {number}: {property_text}**
- Reference the specific requirements they validate
- Use smart generators that constrain to valid input spaces

### Test Coverage Goals

- Minimum 80% code coverage
- 100% coverage of critical paths (authentication, matching, messaging)
- All correctness properties implemented as property tests
- Integration tests for GraphQL queries and mutations
- End-to-end tests for real-time messaging

### Testing Tools

- **pytest**: Test runner and assertion library
- **Hypothesis**: Property-based testing library for Python
- **httpx**: Async HTTP client for API testing
- **pytest-asyncio**: Async test support
- **Strawberry test client**: GraphQL testing utilities
- **WebSocket test client**: WebSocket testing

## Security Considerations

### Authentication & Authorization

- All passwords hashed with bcrypt (cost factor 12)
- JWT tokens with 24-hour expiration
- Refresh tokens stored in Redis with 30-day expiration
- All protected endpoints require valid JWT
- Role-based access control for admin operations

### Data Protection

- HTTPS/TLS for all communications
- Encrypted database connections
- S3 bucket encryption at rest
- Sensitive data (passwords, tokens) never logged
- Input sanitization to prevent injection attacks
- Pydantic validation for all inputs

### Rate Limiting

- Per-user rate limits: 100 requests per minute
- Per-IP rate limits: 1000 requests per minute
- Stricter limits on authentication endpoints
- Redis-based distributed rate limiting
- slowapi library for FastAPI rate limiting

### API Security

- CORS configuration for allowed origins
- GraphQL query depth limiting (max depth: 5)
- GraphQL query complexity analysis
- Request size limits (max 10MB)
- SQL injection prevention via SQLAlchemy ORM
- Parameterized queries only

## Performance Considerations

### Database Optimization

- Indexes on frequently queried fields (userId, email, location)
- PostGIS spatial indexes for geolocation queries
- Connection pooling (max 20 connections)
- Query optimization and explain analysis

### Caching Strategy

Multi-tier caching for optimal performance:

#### Tier 1: Local Memory Cache (L1)
- **Library**: cachetools (LRU cache)
- **Scope**: Per-process, in-memory
- **Use cases:**
  - Hot user profiles (1-minute TTL, max 1000 entries)
  - Active user sessions (5-minute TTL, max 5000 entries)
  - Frequently accessed playgrounds (2-minute TTL, max 500 entries)
- **Benefits:**
  - Microsecond latency (no network call)
  - Reduces Redis load
  - Automatic eviction (LRU policy)

#### Tier 2: Redis Cache (L2)
- **Scope**: Distributed, shared across all API instances
- **Use cases:**
  - User sessions (24-hour TTL)
  - Profile data (5-minute TTL)
  - **Match recommendations (pre-computed, 15-minute TTL)**
  - Playground search results (5-minute TTL)
  - Rate limiting counters
- **Benefits:**
  - Shared across multiple API servers
  - Persistent across restarts
  - Atomic operations

#### Cache Lookup Flow
```python
async def get_profile(user_id: str) -> Profile:
    # 1. Check L1 (local memory)
    if profile := l1_cache.get(f"profile:{user_id}"):
        return profile
    
    # 2. Check L2 (Redis)
    if profile_json := await redis.get(f"profile:{user_id}"):
        profile = Profile.parse_raw(profile_json)
        l1_cache.set(f"profile:{user_id}", profile, ttl=60)
        return profile
    
    # 3. Fetch from database
    profile = await db.query(Profile).filter_by(user_id=user_id).first()
    
    # 4. Populate both caches
    await redis.setex(f"profile:{user_id}", 300, profile.json())
    l1_cache.set(f"profile:{user_id}", profile, ttl=60)
    
    return profile
```

#### Cache Invalidation Strategy
- **Write-through**: Update database + invalidate both cache tiers
- **L1 invalidation**: Pub/Sub pattern via Redis
  - When API instance A updates data, it publishes invalidation message
  - All API instances (A, B, C) receive message and clear L1 cache
  - Ensures consistency across distributed instances

```python
# On data update
async def update_profile(user_id: str, data: ProfileUpdate):
    # 1. Update database
    await db.update(Profile).where(user_id=user_id).values(**data)
    
    # 2. Invalidate L2 (Redis)
    await redis.delete(f"profile:{user_id}")
    
    # 3. Broadcast L1 invalidation to all instances
    await redis.publish("cache:invalidate", f"profile:{user_id}")
    
    # 4. Clear local L1
    l1_cache.delete(f"profile:{user_id}")
```

#### Recommendation Caching Strategy

Match recommendations use both cache tiers for maximum performance:

1. **L1 Cache (Local Memory):**
   ```python
   # Key: "recs:{user_id}"
   # TTL: 5 minutes
   # Max entries: 1000 users
   ```

2. **L2 Cache (Redis):**
   ```python
   # Key: "recommendations:{user_id}"
   # Value: JSON list of profile IDs with scores
   # TTL: 15 minutes
   {
     "profiles": [
       {"id": "profile_123", "score": 0.95},
       {"id": "profile_456", "score": 0.87},
       ...
     ],
     "generated_at": "2024-01-15T10:30:00Z"
   }
   ```

3. **Background Refresh:**
   - Celery worker runs every 15 minutes
   - Recalculates recommendations for active users
   - Updates L2 (Redis) cache atomically
   - L1 caches populate on-demand from L2
   - Runs during low-traffic periods for inactive users

4. **Cache Miss Handling:**
   - Check L1 → Check L2 → Compute on-demand
   - Store result in L2 for future requests
   - L1 populates automatically on next request
   - Queue background refresh for next cycle

5. **Invalidation Triggers:**
   - User updates preferences → invalidate both tiers
   - User likes/passes → invalidate both tiers
   - New user joins → add to recommendation pools
   - Broadcast invalidation via Redis Pub/Sub

This two-tier approach ensures:
- **Ultra-fast reads** (L1: microseconds, L2: milliseconds)
- **Reduced Redis load** (L1 absorbs most traffic)
- **Consistency** (Pub/Sub invalidation across instances)
- **Scalability** (Each API instance has its own L1)
- **Fresh data** (15-minute background refresh)

### Scalability

- Stateless API servers (horizontal scaling)
- Redis for shared session state
- S3 for distributed file storage
- Database read replicas for scaling reads
- WebSocket server clustering with Redis adapter

### Monitoring

- Application performance monitoring (APM)
- Database query performance tracking
- Error rate monitoring and alerting
- Real-time messaging latency tracking
- API endpoint response time tracking
