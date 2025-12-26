# Design Document - Navigation and Core Screens

## Overview

This design implements a tab-based navigation structure with four main screens: Home (card stack), Matches, Messages, and Profile. It includes profile detail views, match celebration screens, and profile creation/editing flows.

## Architecture

### Navigation Structure

We'll use React Navigation v6 with a bottom tab navigator as the root navigator. Each tab will contain its own stack navigator for nested navigation.

**Design Rationale:** The tab-based structure provides familiar mobile navigation patterns. Stack navigators within each tab allow for deep navigation while maintaining tab context. The modal stack for match celebrations creates an exciting, interruptive experience that feels special.

```
TabNavigator
├── HomeStack
│   ├── HomeScreen (card swiping)
│   └── ProfileDetailScreen
├── MatchesStack
│   ├── MatchesScreen
│   └── ChatScreen
├── MessagesStack
│   ├── MessagesScreen
│   └── ChatScreen
└── ProfileStack
    ├── ProfileScreen
    └── EditProfileScreen

ModalStack (overlays)
└── MatchCelebrationScreen
```

**Note:** ChatScreen is accessible from both MatchesStack and MessagesStack, allowing users to reach conversations from either entry point (Requirements 4.3, 5.3).

### State Management

For Phase 2, we'll use React Context API for:
- User profile data
- Matches list
- Messages/conversations
- Current user authentication state

**Design Rationale:** React Context provides sufficient state management for this phase without adding external dependencies. It allows sharing state across the navigation tree while keeping the implementation simple. For future phases with more complex state requirements, we can migrate to Redux or Zustand if needed.

## Components and Interfaces

### 1. Tab Navigator Component

**Purpose:** Root navigation component with bottom tabs

**Props:**
```typescript
interface TabNavigatorProps {
  initialRoute?: 'Home' | 'Matches' | 'Messages' | 'Profile';
}
```

**Tabs:**
- Home: Card stack icon
- Matches: Heart icon with badge for new matches
- Messages: Chat bubble icon with badge for unread messages
- Profile: User icon

### 2. Profile Detail Screen

**Purpose:** Full-screen view of a profile with all details

**Props:**
```typescript
interface ProfileDetailScreenProps {
  profile: Profile;
  onLike: () => void;
  onPass: () => void;
  onClose: () => void;
}
```

**Features:**
- Scrollable photo gallery with page indicators
- Name, age, and distance
- Bio section
- Prompt Q&A cards
- Floating action buttons (like/pass)
- Swipe down to dismiss gesture

**Design Rationale:** The swipe-down gesture provides an intuitive way to dismiss the detail view, mimicking common mobile patterns. Floating action buttons remain accessible while scrolling through content. The full-screen view allows users to focus on one profile at a time without distractions (Requirement 2.6).

### 3. Match Celebration Screen

**Purpose:** Modal screen shown when a match occurs

**Props:**
```typescript
interface MatchCelebrationProps {
  currentUser: Profile;
  matchedUser: Profile;
  onSendMessage: () => void;
  onKeepSwiping: () => void;
}
```

**Design:**
- Animated entrance (scale + fade)
- Both profile photos in a heart shape or side-by-side
- "It's a Match!" text with celebration animation
- Two action buttons: "Send Message" and "Keep Swiping"

**Design Rationale:** The modal presentation creates an exciting, interruptive moment that celebrates the connection. The animation adds delight and makes matches feel special. Providing both "Send Message" and "Keep Swiping" options respects different user preferences - some want to message immediately, others prefer to continue browsing (Requirements 3.1, 3.4, 3.5).

### 4. Matches Screen

**Purpose:** Grid view of all matches

**State:**
```typescript
interface MatchesScreenState {
  matches: Profile[];
  loading: boolean;
}
```

**Layout:**
- 2-column grid of match cards
- Each card shows photo, name, age
- Tap to open chat
- Empty state with encouraging message

**Design Rationale:** The grid layout maximizes screen space and allows users to see more matches at once. The empty state provides encouragement rather than making users feel unsuccessful, maintaining positive engagement (Requirement 4.5).

### 5. Messages Screen

**Purpose:** List of conversations

**State:**
```typescript
interface Message {
  id: string;
  matchId: string;
  matchProfile: Profile;
  lastMessage: string;
  timestamp: Date;
  unread: boolean;
}

interface MessagesScreenState {
  conversations: Message[];
  loading: boolean;
}
```

**Layout:**
- List of conversation rows
- Each row: profile photo, name, last message preview, timestamp
- Unread indicator badge
- Swipe actions (delete, unmatch)
- Empty state with tips

**Design Rationale:** The list format is familiar from messaging apps and allows for quick scanning. The last message preview and timestamp help users prioritize which conversations to engage with. Swipe actions provide quick access to management functions without cluttering the UI. The empty state provides helpful tips to encourage users to start conversations (Requirement 5.5).

### 6. Chat Screen

**Purpose:** One-on-one messaging interface

**Props:**
```typescript
interface ChatScreenProps {
  matchId: string;
  matchProfile: Profile;
}

interface ChatMessage {
  id: string;
  senderId: string;
  text: string;
  timestamp: Date;
}
```

**Features:**
- Message bubbles (different colors for sent/received)
- Input field with send button
- Timestamp grouping
- Match profile header with photo and name

### 7. Profile Screen

**Purpose:** Display and edit user's own profile

**Modes:**
- View mode: Shows profile as others see it
- Edit mode: Allows modifications

**Features:**
- Photo management (add/remove/reorder)
- Bio text editor
- Prompt selector and answer editor
- Settings button
- Preview button to see profile as others see it

**Design Rationale:** Separating view and edit modes prevents accidental changes while allowing easy access to editing. The preview feature helps users understand how they're presenting themselves to potential matches. Photo reordering allows users to control which photo appears first, which is critical for first impressions (Requirements 6.3, 6.4, 6.5, 6.6).

### 8. Profile Creation Flow

**Purpose:** Onboarding for new users

**Steps:**
1. Welcome screen
2. Photo upload (minimum 2 required - Requirement 7.2)
3. Basic info (name, age - Requirement 7.3)
4. Bio (optional - Requirement 7.4)
5. Prompts (select and answer minimum 1 required - Requirement 7.5)
6. Review and complete

**Navigation:** Linear flow with progress indicator

**Validation:**
- Cannot proceed from photo step without at least 2 photos
- Cannot complete flow without at least 1 prompt answer
- Name and age are required fields

**Design Rationale:** The linear flow with progress indicator provides clear guidance for new users. Minimum requirements (2 photos, 1 prompt) ensure profiles have enough content to be engaging while not being overly burdensome. The review step allows users to see their profile before going live.

## Data Models

### Profile Model
```typescript
interface Profile {
  id: string;
  name: string;
  age: number;
  photos: string[]; // URLs
  bio?: string;
  prompts: Prompt[];
  distance?: number; // miles away
  lastActive?: Date;
}

interface Prompt {
  question: string;
  answer: string;
}
```

### Match Model
```typescript
interface Match {
  id: string;
  userId: string;
  matchedUserId: string;
  matchedAt: Date;
  conversationId: string;
}
```

### Conversation Model
```typescript
interface Conversation {
  id: string;
  matchId: string;
  participants: string[]; // user IDs
  messages: ChatMessage[];
  lastMessageAt: Date;
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Tab Navigation Consistency
*For any* tab selection, the active tab indicator should match the currently displayed screen and the screen content should correspond to the selected tab
**Validates: Requirements 1.2, 1.4**

### Property 2: Tab Navigator Visibility
*For any* navigation to a main screen (Home, Matches, Messages, Profile), the tab navigator should remain visible
**Validates: Requirements 1.5**

### Property 3: Profile Detail Completeness
*For any* profile displayed in detail view, all profile fields (photos, name, age, bio, prompts) should be rendered in the view
**Validates: Requirements 2.2, 2.3, 2.4**

### Property 4: Profile Detail Interaction
*For any* profile card tap, the app should display the Profile_Detail_View with like and pass buttons
**Validates: Requirements 2.1**

### Property 5: Profile Detail Dismissal
*For any* swipe down or back button tap on Profile_Detail_View, the view should close and return to the previous screen
**Validates: Requirements 2.6**

### Property 6: Match Mutual Requirement
*For any* match celebration shown, both users must have mutually liked each other
**Validates: Requirements 3.1**

### Property 7: Match Screen Completeness
*For any* match celebration displayed, both users' profile photos should be shown along with action buttons (send message, keep swiping)
**Validates: Requirements 3.2**

### Property 8: Match Screen Dismissal
*For any* match screen dismissal, the app should navigate back to the home screen
**Validates: Requirements 3.5**

### Property 9: Matches List Completeness
*For any* set of matches, all matches should be displayed in the grid/list with their photo and name
**Validates: Requirements 4.2, 4.4**

### Property 10: Match Navigation
*For any* match tapped in the matches list, the app should navigate to the conversation with that specific user
**Validates: Requirements 4.3**

### Property 11: Messages List Completeness
*For any* set of conversations, all conversations should be displayed in the list with the match's photo, name, and last message preview
**Validates: Requirements 5.2, 5.4**

### Property 12: Conversation Navigation
*For any* conversation tapped in the messages list, the app should open the chat interface for that specific conversation
**Validates: Requirements 5.3**

### Property 13: Empty State Display
*For any* list screen (matches, messages) with zero items, an empty state message should be displayed
**Validates: Requirements 4.5, 5.5**

### Property 14: Profile Display Completeness
*For any* user viewing their own profile, all profile fields (photos, bio, prompts) should be displayed
**Validates: Requirements 6.2**

### Property 15: Profile Edit Persistence
*For any* profile edit (photos, bio, prompts) that is saved, the changes should be reflected in the profile view and the app should return to view mode
**Validates: Requirements 6.4, 6.5, 6.6**

### Property 16: Profile Creation Validation
*For any* profile creation attempt, the app should require minimum 2 photos and 1 prompt answer before allowing completion
**Validates: Requirements 7.2, 7.5**

### Property 17: Profile Creation Completion
*For any* completed profile creation flow, the app should navigate to the home screen
**Validates: Requirements 7.6**

## Error Handling

### Navigation Errors
- Handle missing profile data gracefully
- Show error screen if navigation fails
- Provide retry mechanism

### Data Loading Errors
- Show loading states during data fetch
- Display error messages for failed requests
- Implement pull-to-refresh

### Profile Creation Errors
- Validate photo uploads
- Check required fields before allowing progression
- Show inline validation errors

## Testing Strategy

### Unit Tests
- Test navigation state transitions for all tabs
- Validate profile data rendering with specific examples
- Test empty state conditions for matches and messages
- Verify form validation logic for profile creation
- Test gesture handlers (swipe down, tap back)
- Verify button interactions (like, pass, send message)

### Property-Based Tests
- Generate random profiles and verify all fields render correctly (Property 3, 14)
- Test navigation sequences with random tab selections (Property 1, 2)
- Verify match conditions with random like/pass combinations (Property 6)
- Test profile edit operations with random valid inputs (Property 15)
- Generate random match and conversation lists to verify completeness (Property 9, 11)
- Test profile creation validation with random photo counts and prompt answers (Property 16)
- Verify navigation actions return to correct screens (Property 5, 8, 10, 12, 17)

### Integration Tests
- Test complete user flows (profile creation → swiping → matching → messaging)
- Verify tab switching preserves state within each stack
- Test deep linking to specific screens
- Verify match celebration triggers correctly on mutual likes
- Test profile edit persistence across navigation

### Configuration
- Minimum 100 iterations per property test
- Each test tagged with feature name and property number
- Example tag: **Feature: navigation-and-screens, Property 1: Tab Navigation Consistency**

**Testing Rationale:** The combination of unit tests for specific scenarios and property-based tests for universal behaviors provides comprehensive coverage. Property-based tests are particularly valuable for navigation flows and data rendering, where many different inputs should produce consistent behavior.
