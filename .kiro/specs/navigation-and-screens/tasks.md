# Implementation Plan: Navigation and Core Screens

## Overview

This implementation plan builds a complete navigation structure with tab-based navigation and all core screens for the dating app. We'll use React Navigation v6 with bottom tabs, implement profile details, match celebrations, matches list, messages, chat, and profile management screens.

## Tasks

- [x] 1. Set up React Navigation and tab structure
  - Install React Navigation dependencies (@react-navigation/native, @react-navigation/bottom-tabs, @react-navigation/stack)
  - Install required peer dependencies (react-native-screens, react-native-safe-area-context)
  - Create TabNavigator component with four tabs (Home, Matches, Messages, Profile)
  - Configure tab icons and labels for each tab
  - Set up stack navigators for each tab
  - _Requirements: 1.1, 1.3_

- [ ]* 1.1 Write property test for tab navigation
  - **Property 1: Tab Navigation Consistency**
  - **Validates: Requirements 1.2, 1.4**

- [ ]* 1.2 Write property test for tab navigator visibility
  - **Property 2: Tab Navigator Visibility**
  - **Validates: Requirements 1.5**

- [x] 2. Implement Profile Detail Screen
  - [x] 2.1 Create ProfileDetailScreen component with scrollable layout
    - Build photo gallery with horizontal scroll and page indicators
    - Display profile name, age, and distance
    - Render bio section
    - Display all prompt Q&A cards
    - Add floating like and pass action buttons
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

  - [x] 2.2 Add swipe-down gesture to dismiss
    - Implement PanResponder for swipe-down gesture
    - Add back button handler
    - Navigate back to previous screen on dismiss
    - _Requirements: 2.6_

  - [ ]* 2.3 Write property tests for profile detail view
    - **Property 3: Profile Detail Completeness**
    - **Property 4: Profile Detail Interaction**
    - **Property 5: Profile Detail Dismissal**
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.6**

- [x] 3. Checkpoint - Ensure profile detail navigation works
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Implement Match Celebration Screen
  - [x] 4.1 Create MatchCelebrationScreen modal component
    - Design modal layout with both profile photos
    - Add "It's a Match!" congratulatory message
    - Implement entrance animation (scale + fade)
    - Add "Send Message" and "Keep Swiping" buttons
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

  - [x] 4.2 Wire match celebration navigation
    - Configure modal presentation in navigation stack
    - Implement "Send Message" navigation to chat
    - Implement "Keep Swiping" dismissal to home
    - _Requirements: 3.4, 3.5_

  - [ ]* 4.3 Write property tests for match celebration
    - **Property 6: Match Mutual Requirement**
    - **Property 7: Match Screen Completeness**
    - **Property 8: Match Screen Dismissal**
    - **Validates: Requirements 3.1, 3.2, 3.5**

- [x] 5. Implement Matches Screen
  - [x] 5.1 Create MatchesScreen with grid layout
    - Build 2-column grid of match cards
    - Display match photo, name, and age on each card
    - Implement tap handler to navigate to chat
    - _Requirements: 4.1, 4.2, 4.4_

  - [x] 5.2 Add empty state for no matches
    - Create encouraging empty state message component
    - Show empty state when matches array is empty
    - _Requirements: 4.5_

  - [ ]* 5.3 Write property tests for matches screen
    - **Property 9: Matches List Completeness**
    - **Property 10: Match Navigation**
    - **Property 13: Empty State Display (Matches)**
    - **Validates: Requirements 4.2, 4.3, 4.4, 4.5**

- [x] 6. Implement Messages Screen
  - [x] 6.1 Create MessagesScreen with conversation list
    - Build list of conversation rows
    - Display profile photo, name, last message preview, and timestamp
    - Add unread indicator badge
    - Implement tap handler to navigate to chat
    - _Requirements: 5.1, 5.2, 5.4_

  - [x] 6.2 Add swipe actions and empty state
    - Implement swipe actions (delete, unmatch)
    - Create empty state with conversation tips
    - Show empty state when conversations array is empty
    - _Requirements: 5.5_

  - [ ]* 6.3 Write property tests for messages screen
    - **Property 11: Messages List Completeness**
    - **Property 12: Conversation Navigation**
    - **Property 13: Empty State Display (Messages)**
    - **Validates: Requirements 5.2, 5.3, 5.4, 5.5**

- [x] 7. Checkpoint - Ensure matches and messages screens work
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Implement Chat Screen
  - [x] 8.1 Create ChatScreen component
    - Build message list with sent/received bubble styling
    - Add match profile header with photo and name
    - Implement timestamp grouping for messages
    - Create message input field with send button
    - Wire up to both MatchesStack and MessagesStack
    - _Requirements: 4.3, 5.3_

  - [ ]* 8.2 Write unit tests for chat screen
    - Test message bubble rendering
    - Test input field and send button
    - Test timestamp grouping logic

- [x] 9. Implement Profile Screen
  - [x] 9.1 Create ProfileScreen with view mode
    - Display user's own photos in gallery
    - Show bio and prompts
    - Add edit button to switch to edit mode
    - Add preview button to see profile as others see it
    - _Requirements: 6.1, 6.2, 6.3_

  - [x] 9.2 Create EditProfileScreen component
    - Build photo management UI (add/remove/reorder)
    - Create bio text editor
    - Build prompt selector and answer editor
    - Add save and cancel buttons
    - _Requirements: 6.4, 6.5_

  - [x] 9.3 Implement profile edit persistence
    - Save profile changes to state/storage
    - Update profile view after save
    - Navigate back to view mode after save
    - _Requirements: 6.6_

  - [ ]* 9.4 Write property tests for profile screen
    - **Property 14: Profile Display Completeness**
    - **Property 15: Profile Edit Persistence**
    - **Validates: Requirements 6.2, 6.4, 6.5, 6.6**

- [ ] 10. Implement Profile Creation Flow
  - [ ] 10.1 Create profile creation screens
    - Build welcome screen
    - Create photo upload screen with minimum 2 photos validation
    - Build basic info screen (name, age)
    - Create bio input screen (optional)
    - Build prompt selection and answer screen with minimum 1 required
    - Create review screen
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

  - [ ] 10.2 Wire profile creation navigation
    - Set up linear flow with progress indicator
    - Implement validation at each step
    - Navigate to home screen on completion
    - _Requirements: 7.6_

  - [ ]* 10.3 Write property tests for profile creation
    - **Property 16: Profile Creation Validation**
    - **Property 17: Profile Creation Completion**
    - **Validates: Requirements 7.2, 7.5, 7.6**

- [ ] 11. Set up state management with React Context
  - Create UserContext for user profile data
  - Create MatchesContext for matches list
  - Create MessagesContext for conversations
  - Create AuthContext for authentication state
  - Wire contexts to all screens

- [x] 12. Final checkpoint - Integration testing
  - Test complete user flow: profile creation → swiping → matching → messaging
  - Verify tab switching preserves state
  - Test all navigation paths
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- React Navigation v6 is the standard for React Native navigation
- Context API provides sufficient state management for this phase
