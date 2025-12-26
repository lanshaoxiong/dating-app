# Dating App

A React Native dating app similar to Hinge, built with Expo for easy Android/iOS deployment.

## Features

- Swipeable profile cards
- Multiple photos per profile
- Prompt-based conversations
- Like/Pass functionality
- Native mobile experience

## Setup

1. Install Node.js and npm
2. Install Expo CLI: `npm install -g @expo/cli`
3. Install dependencies: `npm install`
4. Start the app: `npm start`

## Build for Android

1. Install Android Studio and set up Android SDK
2. Run: `expo build:android`
3. Or use EAS Build: `eas build --platform android`

## Build for iOS

1. Have a Mac with Xcode installed
2. Run: `expo build:ios`
3. Or use EAS Build: `eas build --platform ios`

## Development

- `npm start` - Start the Expo development server
- `npm run android` - Run on Android emulator/device
- `npm run ios` - Run on iOS simulator/device
- `npm run web` - Run in web browser

## Customization

- Edit `App.js` to modify the main app logic
- Update `profiles` array with your own data
- Customize styles in the StyleSheet
- Add more features like messaging, matching, etc.

## Next Steps

- Add user authentication
- Implement backend API
- Add messaging functionality
- Include location-based matching
- Add profile creation/editing
