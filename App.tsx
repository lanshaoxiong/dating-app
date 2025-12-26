import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import TabNavigator from './UI/navigation/TabNavigator';
import MatchCelebrationScreen from './UI/screens/MatchCelebrationScreen';

const RootStack = createStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <RootStack.Navigator screenOptions={{ headerShown: false }}>
        <RootStack.Screen name="Main" component={TabNavigator} />
        <RootStack.Screen
          name="MatchCelebration"
          component={MatchCelebrationScreen}
          options={{
            presentation: 'transparentModal',
            cardStyle: { backgroundColor: 'transparent' },
          }}
        />
      </RootStack.Navigator>
    </NavigationContainer>
  );
}
