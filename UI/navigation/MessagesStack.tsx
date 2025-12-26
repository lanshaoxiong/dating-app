import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import { MessagesStackParamList } from '../types/navigation';
import MessagesScreen from '../screens/MessagesScreen';
import ChatScreen from '../screens/ChatScreen';

const Stack = createStackNavigator<MessagesStackParamList>();

export default function MessagesStack() {
  return (
    <Stack.Navigator>
      <Stack.Screen
        name="MessagesScreen"
        component={MessagesScreen}
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
