# Implementation Plan: Backend API

## Overview

This implementation plan builds a complete Python backend API for PupMatch using FastAPI, GraphQL, PostgreSQL, and Redis. We'll implement authentication, profile management, matching algorithms, real-time messaging, geolocation services, playground mapping, and a two-tier caching system with background job processing.

## Tasks

- [x] 1. Set up project structure and dependencies
  - Initialize Python project with Poetry or pip
  - Install FastAPI, Strawberry GraphQL, SQLAlchemy, Pydantic
  - Install PostgreSQL driver (asyncpg), Redis client (redis-py)
  - Install Celery for background jobs
  - Install boto3 for S3, python-jose for JWT
  - Install pytest, Hypothesis for testing
  - Create project structure (app/, services/, models/, schemas/)
  - Set up environment configuration (.env file)
  - _Requirements: 12.1, 12.2_

- [ ]* 1.1 Write unit tests for project setup
  - Test environment variable loading
  - Test database connection
  - Test Redis connection

- [x] 2. Set up database and migrations
  - [x] 2.1 Configure PostgreSQL with PostGIS extension
    - Create database schema
    - Enable PostGIS extension for geospatial queries
    - Set up connection pooling
    - _Requirements: 8.1, 8.2_

  - [x] 2.2 Define SQLAlchemy models
    - Create User, Profile, Photo, Prompt models
    - Create Like, Pass, Match models
    - Create Message, Conversation models
    - Create Playground model
    - Add indexes on frequently queried fields
    - Add PostGIS geometry columns for locations
    - _Requirements: 2.1, 5.1, 7.3, 9.1_

  - [x] 2.3 Set up Alembic migrations
    - Initialize Alembic
    - Create initial migration
    - Test migration up/down
    - _Requirements: 2.1_

  - [ ]* 2.4 Write property tests for database models
    - **Property 3: Profile Photo Count Constraints**
    - **Property 10: Coordinate Validation**
    - **Validates: Requirements 2.4, 8.6**

- [ ] 3. Checkpoint - Ensure database setup works
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 4. Implement authentication service
  - [ ] 4.1 Create authentication service
    - Implement user registration with password hashing (bcrypt)
    - Implement login with JWT token generation
    - Implement token validation middleware
    - Implement password reset flow
    - _Requirements: 1.1, 1.2, 1.4, 1.5_

  - [ ] 4.2 Create Pydantic schemas for auth
    - RegisterRequest, LoginRequest schemas
    - AuthToken response schema
    - User response schema
    - _Requirements: 1.1, 1.2_

  - [ ]* 4.3 Write property tests for authentication
    - **Property 1: Authentication Token Validity**
    - **Property 2: Password Hash Irreversibility**
    - **Property 14: Token Expiration**
    - **Validates: Requirements 1.1, 1.2, 1.5, 1.6**

- [ ] 5. Implement profile management service
  - [ ] 5.1 Create profile service
    - Implement create profile with validation
    - Implement update profile
    - Implement get profile
    - Implement delete profile (cascade deletion)
    - Implement prompt management
    - _Requirements: 2.1, 2.2, 2.5, 2.6, 2.7_

  - [ ] 5.2 Create Pydantic schemas for profiles
    - ProfileInput, ProfileUpdate schemas
    - Profile response schema with nested photos and prompts
    - PromptInput schema
    - _Requirements: 2.1, 2.5_

  - [ ]* 5.3 Write property tests for profile service
    - **Property 3: Profile Photo Count Constraints**
    - **Property 17: Photo Order Preservation**
    - **Validates: Requirements 2.4, 3.5**

- [ ] 6. Implement photo storage service
  - [ ] 6.1 Create S3 photo storage service
    - Implement photo upload to S3
    - Implement photo deletion from S3
    - Implement signed URL generation
    - Implement file validation (type, size)
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

  - [ ] 6.2 Integrate photo service with profile service
    - Add photo upload endpoint
    - Add photo delete endpoint
    - Add photo reorder endpoint
    - _Requirements: 3.1, 3.4, 3.5_

  - [ ]* 6.3 Write property tests for photo storage
    - **Property 4: Photo Upload Validation**
    - **Validates: Requirements 3.2, 3.3**

- [ ] 7. Checkpoint - Ensure auth and profile management works
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Implement geolocation service
  - [ ] 8.1 Create geolocation service
    - Implement location update with PostGIS
    - Implement haversine distance calculation
    - Implement coordinate validation
    - Implement distance unit conversion (miles/km)
    - Implement nearby profile search
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.6_

  - [ ]* 8.2 Write property tests for geolocation
    - **Property 8: Distance Calculation Consistency**
    - **Property 9: Distance Unit Conversion**
    - **Property 10: Coordinate Validation**
    - **Validates: Requirements 8.2, 8.3, 8.6**

- [ ] 9. Implement matching service
  - [ ] 9.1 Create matching algorithm
    - Implement compatibility score calculation
    - Implement preference filtering (age, distance, activity)
    - Implement exclusion logic (already liked/passed)
    - Implement profile ordering by compatibility
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

  - [ ] 9.2 Create recommendation cache service
    - Implement L1 cache (cachetools LRU)
    - Implement L2 cache (Redis)
    - Implement cache lookup flow (L1 → L2 → DB)
    - Implement cache invalidation with Pub/Sub
    - _Requirements: 4.1_

  - [ ]* 9.3 Write property tests for matching
    - **Property 11: Profile Discovery Exclusion**
    - **Validates: Requirements 4.2, 4.3**

- [ ] 10. Implement like/pass service
  - [ ] 10.1 Create like/pass service
    - Implement like action with timestamp
    - Implement pass action with timestamp
    - Implement mutual match detection
    - Implement unlike with cascade deletion
    - Implement match retrieval
    - Implement unmatch operation
    - _Requirements: 5.1, 5.2, 5.3, 5.5, 5.6, 6.1, 6.3_

  - [ ]* 10.2 Write property tests for like/pass
    - **Property 5: Match Mutual Requirement**
    - **Property 6: Match Uniqueness**
    - **Property 15: Like/Pass Idempotency**
    - **Property 16: Unmatch Cascade**
    - **Validates: Requirements 5.3, 5.5, 6.3**

- [ ] 11. Checkpoint - Ensure matching and like/pass works
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 12. Implement messaging service
  - [ ] 12.1 Create messaging service
    - Implement send message with authorization check
    - Implement conversation retrieval
    - Implement conversation list
    - Implement mark as read
    - Implement conversation deletion (soft delete)
    - _Requirements: 7.2, 7.3, 7.4, 7.7_

  - [ ] 12.2 Implement WebSocket real-time messaging
    - Create WebSocket endpoint for chat
    - Implement connection management
    - Implement message broadcasting
    - Implement offline message queuing
    - _Requirements: 7.1, 7.5, 7.6_

  - [ ]* 12.3 Write property tests for messaging
    - **Property 7: Messaging Authorization**
    - **Validates: Requirements 7.2**

- [ ] 13. Implement playground service
  - [ ] 13.1 Create playground service
    - Implement add playground with location
    - Implement remove playground
    - Implement get favorite playgrounds
    - Implement radius search with PostGIS
    - Implement name search
    - _Requirements: 9.1, 9.2, 9.3, 9.5, 9.6_

  - [ ]* 13.2 Write property tests for playground
    - **Property 12: Playground Location Validity**
    - **Validates: Requirements 9.1**

- [ ] 14. Implement GraphQL API layer
  - [ ] 14.1 Create Strawberry GraphQL schema
    - Define GraphQL types for all models
    - Create queries (getProfile, getMatches, getRecommendations, etc.)
    - Create mutations (updateProfile, likeProfile, sendMessage, etc.)
    - Add authentication middleware
    - _Requirements: 1.5, 2.6, 4.1, 5.1, 6.1, 7.4, 9.2_

  - [ ] 14.2 Integrate GraphQL with FastAPI
    - Mount Strawberry GraphQL on FastAPI
    - Configure GraphQL Playground
    - Add query depth limiting
    - Add query complexity analysis
    - _Requirements: 12.3_

  - [ ]* 14.3 Write integration tests for GraphQL API
    - Test authentication flow
    - Test profile CRUD operations
    - Test matching flow
    - Test messaging flow

- [ ] 15. Checkpoint - Ensure GraphQL API works
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 16. Implement rate limiting and security
  - [ ] 16.1 Add rate limiting middleware
    - Implement per-user rate limiting (100 req/min)
    - Implement per-IP rate limiting (1000 req/min)
    - Use Redis for distributed rate limiting
    - Return 429 status on limit exceeded
    - _Requirements: 12.3, 12.4_

  - [ ] 16.2 Add security middleware
    - Configure CORS for allowed origins
    - Add request size limits (10MB max)
    - Add input sanitization
    - Add SQL injection prevention checks
    - _Requirements: 12.2, 12.5_

  - [ ]* 16.3 Write property tests for rate limiting
    - **Property 13: Rate Limiting Enforcement**
    - **Validates: Requirements 12.4**

- [ ] 17. Implement background jobs with Celery
  - [ ] 17.1 Set up Celery worker
    - Configure Celery with Redis broker
    - Create task for recommendation refresh (every 15 min)
    - Create task for expired data cleanup (daily)
    - Create task for offline notification delivery (every 5 min)
    - _Requirements: 4.1_

  - [ ] 17.2 Implement recommendation refresh task
    - Batch process active users
    - Recalculate compatibility scores
    - Update L2 cache (Redis) atomically
    - Broadcast L1 cache invalidation
    - _Requirements: 4.1_

  - [ ]* 17.3 Write unit tests for background jobs
    - Test recommendation refresh logic
    - Test cache invalidation
    - Test task scheduling

- [ ] 18. Implement notification service
  - [ ] 18.1 Create notification service
    - Implement push notification sending (Firebase/APNs)
    - Implement notification queuing for offline users
    - Implement notification preferences management
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

  - [ ]* 18.2 Write unit tests for notifications
    - Test notification queuing
    - Test preference handling

- [ ] 19. Add monitoring and logging
  - Set up structured logging (loguru)
  - Add request/response logging
  - Add error tracking (Sentry)
  - Add performance monitoring (APM)
  - Add health check endpoint
  - _Requirements: 12.6_

- [ ] 20. Final checkpoint - Integration testing
  - Test complete user flow: register → create profile → get recommendations → like → match → message
  - Test caching behavior (L1 and L2)
  - Test background job execution
  - Test rate limiting
  - Test WebSocket messaging
  - Load test with multiple concurrent users
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties using Hypothesis
- Unit tests validate specific examples and edge cases
- FastAPI provides excellent async performance for I/O-bound operations
- Two-tier caching (L1: local memory, L2: Redis) ensures optimal performance
- Celery handles background job processing for recommendation refresh
- GraphQL provides flexible data querying for mobile clients
- WebSocket enables real-time messaging
- PostGIS enables efficient geospatial queries for location-based features
