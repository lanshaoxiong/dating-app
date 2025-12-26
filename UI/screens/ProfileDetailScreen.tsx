import React, { useState, useRef } from 'react';
import {
  View,
  Text,
  Image,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Dimensions,
  Animated,
  PanResponder,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

const { width, height } = Dimensions.get('window');

export default function ProfileDetailScreen({ route, navigation }) {
  const { profile } = route.params || {};
  const [photoIndex, setPhotoIndex] = useState(0);
  const scrollY = useRef(new Animated.Value(0)).current;

  // Pan responder for swipe down to dismiss
  const panResponder = useRef(
    PanResponder.create({
      onStartShouldSetPanResponder: (evt, gestureState) => {
        // Only respond if scrolled to top and swiping down
        return gestureState.dy > 0;
      },
      onMoveShouldSetPanResponder: (evt, gestureState) => {
        return gestureState.dy > 10;
      },
      onPanResponderRelease: (evt, gestureState) => {
        if (gestureState.dy > 100) {
          navigation.goBack();
        }
      },
    })
  ).current;

  const nextPhoto = () => {
    if (profile?.photos) {
      setPhotoIndex((prev) => (prev + 1) % profile.photos.length);
    }
  };

  const previousPhoto = () => {
    if (profile?.photos) {
      setPhotoIndex((prev) => (prev - 1 + profile.photos.length) % profile.photos.length);
    }
  };

  const handleLike = () => {
    console.log(`Liked ${profile?.name}`);
    navigation.goBack();
  };

  const handlePass = () => {
    console.log(`Passed ${profile?.name}`);
    navigation.goBack();
  };

  if (!profile) {
    return (
      <View style={styles.container}>
        <Text>No profile data</Text>
      </View>
    );
  }

  return (
    <View style={styles.container} {...panResponder.panHandlers}>
      <ScrollView
        style={styles.scrollView}
        showsVerticalScrollIndicator={false}
        onScroll={Animated.event(
          [{ nativeEvent: { contentOffset: { y: scrollY } } }],
          { useNativeDriver: false }
        )}
        scrollEventThrottle={16}
      >
        {/* Photo Gallery */}
        <View style={styles.photoGallery}>
          <TouchableOpacity
            style={styles.photoTouchLeft}
            onPress={previousPhoto}
            activeOpacity={1}
          />
          <TouchableOpacity
            style={styles.photoTouchRight}
            onPress={nextPhoto}
            activeOpacity={1}
          />
          
          <Image
            source={{ uri: profile.photos[photoIndex] }}
            style={styles.photo}
            resizeMode="cover"
          />
          
          <LinearGradient
            colors={['transparent', 'rgba(0,0,0,0.3)']}
            style={styles.photoGradient}
          />

          {/* Photo indicators */}
          <View style={styles.photoIndicators}>
            {profile.photos.map((_, index) => (
              <View
                key={index}
                style={[
                  styles.indicator,
                  index === photoIndex && styles.activeIndicator,
                ]}
              />
            ))}
          </View>

          {/* Close button */}
          <TouchableOpacity
            style={styles.closeButton}
            onPress={() => navigation.goBack()}
          >
            <Text style={styles.closeButtonText}>✕</Text>
          </TouchableOpacity>
        </View>

        {/* Profile Info */}
        <View style={styles.infoContainer}>
          {/* Name and Age */}
          <View style={styles.nameSection}>
            <Text style={styles.name}>
              {profile.name}, {profile.age}
            </Text>
            {profile.distance && (
              <Text style={styles.distance}>{profile.distance} miles away</Text>
            )}
          </View>

          {/* Bio */}
          {profile.bio && (
            <View style={styles.bioSection}>
              <Text style={styles.sectionTitle}>About</Text>
              <Text style={styles.bioText}>{profile.bio}</Text>
            </View>
          )}

          {/* Prompts */}
          {profile.prompts && profile.prompts.length > 0 && (
            <View style={styles.promptsSection}>
              {profile.prompts.map((prompt, index) => (
                <View key={index} style={styles.promptCard}>
                  <Text style={styles.promptQuestion}>{prompt.question}</Text>
                  <Text style={styles.promptAnswer}>{prompt.answer}</Text>
                </View>
              ))}
            </View>
          )}

          {/* Spacer for floating buttons */}
          <View style={{ height: 100 }} />
        </View>
      </ScrollView>

      {/* Floating Action Buttons */}
      <View style={styles.floatingButtons}>
        <TouchableOpacity style={styles.passButton} onPress={handlePass}>
          <Text style={[styles.buttonIcon, { color: '#ff6b6b' }]}>✕</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.likeButton} onPress={handleLike}>
          <Text style={[styles.buttonIcon, { color: '#fff' }]}>♥</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  scrollView: {
    flex: 1,
  },
  photoGallery: {
    width: width,
    height: height * 0.6,
    position: 'relative',
  },
  photo: {
    width: '100%',
    height: '100%',
  },
  photoGradient: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    height: 100,
  },
  photoTouchLeft: {
    position: 'absolute',
    left: 0,
    top: 0,
    bottom: 0,
    width: '50%',
    zIndex: 10,
  },
  photoTouchRight: {
    position: 'absolute',
    right: 0,
    top: 0,
    bottom: 0,
    width: '50%',
    zIndex: 10,
  },
  photoIndicators: {
    position: 'absolute',
    top: 60,
    left: 0,
    right: 0,
    flexDirection: 'row',
    justifyContent: 'center',
    paddingHorizontal: 20,
  },
  indicator: {
    flex: 1,
    height: 3,
    backgroundColor: 'rgba(255,255,255,0.5)',
    marginHorizontal: 2,
    borderRadius: 2,
  },
  activeIndicator: {
    backgroundColor: '#fff',
  },
  closeButton: {
    position: 'absolute',
    top: 50,
    right: 20,
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 20,
  },
  closeButtonText: {
    color: '#fff',
    fontSize: 24,
    fontWeight: 'bold',
  },
  infoContainer: {
    padding: 20,
  },
  nameSection: {
    marginBottom: 20,
  },
  name: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  distance: {
    fontSize: 16,
    color: '#666',
  },
  bioSection: {
    marginBottom: 25,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 10,
  },
  bioText: {
    fontSize: 16,
    color: '#555',
    lineHeight: 24,
  },
  promptsSection: {
    marginBottom: 20,
  },
  promptCard: {
    backgroundColor: '#f8f9fa',
    borderRadius: 15,
    padding: 20,
    marginBottom: 15,
    borderWidth: 1,
    borderColor: '#e9ecef',
  },
  promptQuestion: {
    fontSize: 16,
    fontWeight: '600',
    color: '#666',
    marginBottom: 10,
  },
  promptAnswer: {
    fontSize: 16,
    color: '#333',
    lineHeight: 24,
  },
  floatingButtons: {
    position: 'absolute',
    bottom: 30,
    left: 0,
    right: 0,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 30,
  },
  passButton: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#fff',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
    borderWidth: 2,
    borderColor: '#ff6b6b',
  },
  likeButton: {
    width: 70,
    height: 70,
    borderRadius: 35,
    backgroundColor: '#e91e63',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  buttonIcon: {
    fontSize: 28,
    fontWeight: 'bold',
  },
});
