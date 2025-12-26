import React, { useEffect, useRef } from 'react';
import {
  View,
  Text,
  Image,
  TouchableOpacity,
  StyleSheet,
  Dimensions,
  Animated,
} from 'react-native';

const { width, height } = Dimensions.get('window');

export default function MatchCelebrationScreen({ route, navigation }) {
  const { currentUser, matchedUser } = route.params || {};
  
  const scaleAnim = useRef(new Animated.Value(0)).current;
  const fadeAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    // Entrance animation
    Animated.parallel([
      Animated.spring(scaleAnim, {
        toValue: 1,
        tension: 50,
        friction: 7,
        useNativeDriver: true,
      }),
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 300,
        useNativeDriver: true,
      }),
    ]).start();
  }, []);

  const handleSendMessage = () => {
    navigation.navigate('Messages', {
      screen: 'Chat',
      params: { matchId: matchedUser?.id, matchProfile: matchedUser },
    });
  };

  const handleKeepSwiping = () => {
    navigation.goBack();
  };

  if (!currentUser || !matchedUser) {
    return null;
  }

  return (
    <View style={styles.container}>
      <Animated.View
        style={[
          styles.content,
          {
            opacity: fadeAnim,
            transform: [{ scale: scaleAnim }],
          },
        ]}
      >
        {/* Celebration Text */}
        <Text style={styles.celebrationText}>It's a Match! 🐶💕</Text>
        <Text style={styles.subtitle}>
          Your pup and {matchedUser.name} want to be friends!
        </Text>

        {/* Profile Photos */}
        <View style={styles.photosContainer}>
          <View style={styles.photoWrapper}>
            <Image
              source={{ uri: currentUser.photos[0] }}
              style={styles.photo}
            />
          </View>
          <View style={styles.heartContainer}>
            <Text style={styles.heartIcon}>💕</Text>
          </View>
          <View style={styles.photoWrapper}>
            <Image
              source={{ uri: matchedUser.photos[0] }}
              style={styles.photo}
            />
          </View>
        </View>

        {/* Action Buttons */}
        <View style={styles.buttonsContainer}>
          <TouchableOpacity
            style={styles.sendMessageButton}
            onPress={handleSendMessage}
          >
            <Text style={styles.sendMessageText}>Arrange Playdate</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.keepSwipingButton}
            onPress={handleKeepSwiping}
          >
            <Text style={styles.keepSwipingText}>Keep Sniffing</Text>
          </TouchableOpacity>
        </View>
      </Animated.View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.85)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  content: {
    width: width * 0.9,
    backgroundColor: '#fff',
    borderRadius: 20,
    padding: 30,
    alignItems: 'center',
  },
  celebrationText: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#e91e63',
    marginBottom: 10,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginBottom: 30,
    textAlign: 'center',
  },
  photosContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 40,
  },
  photoWrapper: {
    width: 120,
    height: 120,
    borderRadius: 60,
    overflow: 'hidden',
    borderWidth: 4,
    borderColor: '#e91e63',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  photo: {
    width: '100%',
    height: '100%',
  },
  heartContainer: {
    marginHorizontal: 20,
  },
  heartIcon: {
    fontSize: 40,
  },
  buttonsContainer: {
    width: '100%',
  },
  sendMessageButton: {
    backgroundColor: '#e91e63',
    paddingVertical: 16,
    borderRadius: 30,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  sendMessageText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  keepSwipingButton: {
    backgroundColor: '#f8f9fa',
    paddingVertical: 16,
    borderRadius: 30,
    borderWidth: 2,
    borderColor: '#e9ecef',
  },
  keepSwipingText: {
    color: '#666',
    fontSize: 18,
    fontWeight: '600',
    textAlign: 'center',
  },
});
