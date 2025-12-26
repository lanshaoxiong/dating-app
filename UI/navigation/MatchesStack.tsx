import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import { MatchesStackParamList } from '../types/navigation';
import MatchesScreen from '../screens/MatchesScreen';
import ChatScreen from '../screens/ChatScreen';

const Stack = createStackNavigator<MatchesStackParamList>();

export default function MatchesStack() {
  return (
    <Stack.Navigator>
      <Stack.Screen
        name="MatchesScreen"
        component={MatchesScreen}
        options={{ headerShown: false }}
      />
      <Stack.Screen
        name="Chat"
        component={ChatScreen}
        options={{
          headerShown: true,
          title: 'Chat',
        }}
      />
    </Stack.Navigator>
  );
}
