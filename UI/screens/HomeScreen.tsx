import React, { useState, useRef } from 'react';
import { View, Text, Image, TouchableOpacity, StyleSheet, Dimensions, Animated, PanResponder } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { StackNavigationProp } from '@react-navigation/stack';
import { HomeStackParamList, Profile } from '../types/navigation';

const { width, height } = Dimensions.get('window');
const SWIPE_THRESHOLD = 120;

type HomeScreenNavigationProp = StackNavigationProp<HomeStackParamList, 'HomeScreen'>;

interface Props {
  navigation: HomeScreenNavigationProp;
}

const profiles: Profile[] = [
  {
    id: 1,
    name: 'Buddy',
    age: 2,
    photos: [
      `https://placedog.net/500/600?random=${Math.random()}`,
      `https://placedog.net/500/600?random=${Math.random()}`
    ],
    bio: "Energetic golden retriever who loves fetch and belly rubs! Always ready for an adventure at the dog park.",
    prompts: [
      {
        question: "My ideal playdate",
        answer: "Running at the beach, chasing tennis balls, and making new furry friends!"
      },
      {
        question: "I'm looking for",
        answer: "A playful pup who loves to run and doesn't mind getting a little muddy"
      }
    ],
    distance: 3
  },
  {
    id: 2,
    name: 'Luna',
    age: 1,
    photos: [
      `https://placedog.net/500/600?random=${Math.random()}`,
      `https://placedog.net/500/600?random=${Math.random()}`
    ],
    bio: "Sweet husky puppy who loves howling at sirens and stealing socks. Professional treat catcher!",
    prompts: [
      {
        question: "I'm looking for",
        answer: "A fun-loving pup who enjoys zoomies and long naps in the sun"
      },
      {
        question: "My simple pleasures",
        answer: "Morning walks, peanut butter treats, and cuddles on the couch"
      }
    ],
    distance: 5
  },
  {
    id: 3,
    name: 'Max',
    age: 3,
    photos: [
      `https://placedog.net/500/600?random=${Math.random()}`,
      `https://placedog.net/500/600?random=${Math.random()}`
    ],
    bio: "Gentle corgi with short legs and a big heart. Expert at herding and giving puppy eyes for snacks.",
    prompts: [
      {
        question: "My simple pleasures",
        answer: "Chasing squirrels, rolling in grass, and afternoon naps"
      },
      {
        question: "Best adventure story",
        answer: "Found a whole pizza box in the park and became a legend!"
      }
    ],
    distance: 2
  }
];

export default function HomeScreen({ navigation }: Props) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [photoIndex, setPhotoIndex] = useState(0);
  
  const position = useRef(new Animated.ValueXY()).current;
  const rotate = position.x.interpolate({
    inputRange: [-width / 2, 0, width / 2],
    outputRange: ['-10deg', '0deg', '10deg'],
    extrapolate: 'clamp',
  });

  const likeOpacity = position.x.interpolate({
    inputRange: [0, width / 4],
    outputRange: [0, 1],
    extrapolate: 'clamp',
  });

  const nopeOpacity = position.x.interpolate({
    inputRange: [-width / 4, 0],
    outputRange: [1, 0],
    extrapolate: 'clamp',
  });

  const currentProfile = profiles[currentIndex];

  const nextProfile = () => {
    setCurrentIndex((prev) => (prev + 1) % profiles.length);
    setPhotoIndex(0);
    position.setValue({ x: 0, y: 0 });
  };

  const handleSwipeComplete = (direction: 'left' | 'right') => {
    const x = direction === 'right' ? width + 100 : -width - 100;
    Animated.timing(position, {
      toValue: { x, y: 0 },
      duration: 250,
      useNativeDriver: false,
    }).start(() => {
      if (direction === 'right') {
        console.log(`Liked ${currentProfile.name}`);
      } else {
        console.log(`Passed ${currentProfile.name}`);
      }
      nextProfile();
    });
  };

  const panResponder = useRef(
    PanResponder.create({
      onStartShouldSetPanResponder: () => true,
      onPanResponderMove: (_, gesture) => {
        position.setValue({ x: gesture.dx, y: gesture.dy });
      },
      onPanResponderRelease: (_, gesture) => {
        if (gesture.dx > SWIPE_THRESHOLD) {
          handleSwipeComplete('right');
        } else if (gesture.dx < -SWIPE_THRESHOLD) {
          handleSwipeComplete('left');
        } else {
          Animated.spring(position, {
            toValue: { x: 0, y: 0 },
            useNativeDriver: false,
          }).start();
        }
      },
    })
  ).current;

  const nextPhoto = () => {
    setPhotoIndex((prev) => (prev + 1) % currentProfile.photos.length);
  };

  const likeProfile = () => {
    // Simulate a match (50% chance)
    const isMatch = Math.random() > 0.5;
    
    if (isMatch) {
      // Show match celebration
      (navigation as any).navigate('MatchCelebration', {
        currentUser: {
          id: 'current-user',
          name: 'Your Pup',
          photos: [`https://placedog.net/500/600?random=${Math.random()}`],
        },
        matchedUser: currentProfile,
      });
    } else {
      handleSwipeComplete('right');
    }
  };

  const passProfile = () => {
    handleSwipeComplete('left');
  };

  const openProfileDetail = () => {
    navigation.navigate('ProfileDetail', { profile: currentProfile });
  };

  const cardStyle = {
    transform: [
      { translateX: position.x },
      { translateY: position.y },
      { rotate },
    ],
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>🐾 PupMatch</Text>
      </View>

      <View style={styles.cardContainer}>
        <Animated.View 
          style={[styles.card, cardStyle]} 
          {...panResponder.panHandlers}
        >
          <Animated.View style={[styles.likeLabel, { opacity: likeOpacity }]}>
            <Text style={styles.labelText}>LIKE</Text>
          </Animated.View>
          
          <Animated.View style={[styles.nopeLabel, { opacity: nopeOpacity }]}>
            <Text style={styles.labelText}>NOPE</Text>
          </Animated.View>

          <TouchableOpacity onPress={nextPhoto} style={styles.photoContainer}>
            <Image 
              source={{ uri: currentProfile.photos[photoIndex] }} 
              style={styles.photo}
            />
            <LinearGradient
              colors={['transparent', 'rgba(0,0,0,0.7)']}
              style={styles.gradient}
            />
            
            <View style={styles.photoDots}>
              {currentProfile.photos.map((_, index) => (
                <View 
                  key={index}
                  style={[styles.dot, index === photoIndex && styles.activeDot]}
                />
              ))}
            </View>
          </TouchableOpacity>

          <TouchableOpacity onPress={openProfileDetail} style={styles.infoSection}>
            <Text style={styles.name}>{currentProfile.name}, {currentProfile.age}</Text>
            
            <View style={styles.promptSection}>
              <Text style={styles.promptQuestion}>{currentProfile.prompts[0].question}</Text>
              <Text style={styles.promptAnswer}>{currentProfile.prompts[0].answer}</Text>
            </View>
          </TouchableOpacity>

          <View style={styles.actionButtons}>
            <TouchableOpacity style={styles.passButton} onPress={passProfile}>
              <Text style={styles.buttonText}>✕</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.likeButton} onPress={likeProfile}>
              <Text style={styles.buttonText}>♥</Text>
            </TouchableOpacity>
          </View>
        </Animated.View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  header: {
    paddingTop: 50,
    paddingBottom: 20,
    alignItems: 'center',
    backgroundColor: '#fff',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#e91e63',
  },
  cardContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  card: {
    width: width - 40,
    height: height * 0.7,
    backgroundColor: '#fff',
    borderRadius: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  photoContainer: {
    flex: 1,
    position: 'relative',
  },
  photo: {
    width: '100%',
    height: '70%',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
  },
  gradient: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    height: '30%',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
  },
  photoDots: {
    position: 'absolute',
    top: 20,
    left: 0,
    right: 0,
    flexDirection: 'row',
    justifyContent: 'center',
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: 'rgba(255,255,255,0.5)',
    marginHorizontal: 4,
  },
  activeDot: {
    backgroundColor: '#fff',
  },
  infoSection: {
    padding: 20,
    flex: 1,
  },
  name: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  promptSection: {
    marginTop: 10,
  },
  promptQuestion: {
    fontSize: 16,
    fontWeight: '600',
    color: '#666',
    marginBottom: 8,
  },
  promptAnswer: {
    fontSize: 16,
    color: '#333',
    lineHeight: 22,
  },
  actionButtons: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingBottom: 30,
  },
  passButton: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#ff6b6b',
    justifyContent: 'center',
    alignItems: 'center',
  },
  likeButton: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#4ecdc4',
    justifyContent: 'center',
    alignItems: 'center',
  },
  buttonText: {
    fontSize: 24,
    color: '#fff',
    fontWeight: 'bold',
  },
  likeLabel: {
    position: 'absolute',
    top: 50,
    right: 40,
    zIndex: 1000,
    borderWidth: 4,
    borderColor: '#4ecdc4',
    borderRadius: 10,
    padding: 10,
    transform: [{ rotate: '30deg' }],
  },
  nopeLabel: {
    position: 'absolute',
    top: 50,
    left: 40,
    zIndex: 1000,
    borderWidth: 4,
    borderColor: '#ff6b6b',
    borderRadius: 10,
    padding: 10,
    transform: [{ rotate: '-30deg' }],
  },
  labelText: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#fff',
    letterSpacing: 2,
  },
});
