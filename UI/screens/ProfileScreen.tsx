import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Image,
  TouchableOpacity,
  Dimensions,
} from 'react-native';
import { StackNavigationProp } from '@react-navigation/stack';
import { ProfileStackParamList, Profile } from '../types/navigation';

const { width } = Dimensions.get('window');

type ProfileScreenNavigationProp = StackNavigationProp<ProfileStackParamList, 'ProfileScreen'>;

interface Props {
  navigation: ProfileScreenNavigationProp;
}

// Mock user profile data
const myProfile: Profile = {
  id: 0,
  name: 'Your Pup',
  age: 2,
  photos: [
    `https://placedog.net/500/600?random=${Math.random()}`,
    `https://placedog.net/500/600?random=${Math.random()}`,
    `https://placedog.net/500/600?random=${Math.random()}`,
  ],
  bio: "Friendly and playful pup looking for new friends! Love running, playing fetch, and making new buddies at the dog park.",
  prompts: [
    {
      question: "My ideal playdate",
      answer: "Running around the park, playing with toys, and lots of treats!"
    },
    {
      question: "I'm looking for",
      answer: "A fun-loving pup who enjoys adventures and belly rubs"
    },
    {
      question: "My favorite things",
      answer: "Tennis balls, squeaky toys, and afternoon naps in the sun"
    }
  ],
};

export default function ProfileScreen({ navigation }: Props) {
  const handleEditProfile = () => {
    navigation.navigate('EditProfile');
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>🐶 My Pup</Text>
        <TouchableOpacity style={styles.editButton} onPress={handleEditProfile}>
          <Text style={styles.editButtonText}>Edit</Text>
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {/* Photo Gallery */}
        <ScrollView
          horizontal
          pagingEnabled
          showsHorizontalScrollIndicator={false}
          style={styles.photoGallery}
        >
          {myProfile.photos.map((photo, index) => (
            <Image
              key={index}
              source={{ uri: photo }}
              style={styles.photo}
              resizeMode="cover"
            />
          ))}
        </ScrollView>

        {/* Profile Info */}
        <View style={styles.infoContainer}>
          {/* Name and Age */}
          <View style={styles.nameSection}>
            <Text style={styles.name}>
              {myProfile.name}, {myProfile.age}
            </Text>
          </View>

          {/* Bio */}
          {myProfile.bio && (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>About</Text>
              <Text style={styles.bioText}>{myProfile.bio}</Text>
            </View>
          )}

          {/* Prompts */}
          {myProfile.prompts && myProfile.prompts.length > 0 && (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>My Answers</Text>
              {myProfile.prompts.map((prompt, index) => (
                <View key={index} style={styles.promptCard}>
                  <Text style={styles.promptQuestion}>{prompt.question}</Text>
                  <Text style={styles.promptAnswer}>{prompt.answer}</Text>
                </View>
              ))}
            </View>
          )}

          {/* Preview Note */}
          <View style={styles.previewNote}>
            <Text style={styles.previewText}>
              This is how other pups see your profile
            </Text>
          </View>
        </View>
      </ScrollView>
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
    paddingHorizontal: 20,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e9ecef',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#e91e63',
  },
  editButton: {
    backgroundColor: '#e91e63',
    paddingHorizontal: 20,
    paddingVertical: 8,
    borderRadius: 20,
  },
  editButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  scrollView: {
    flex: 1,
  },
  photoGallery: {
    height: 400,
  },
  photo: {
    width: width,
    height: 400,
    backgroundColor: '#e9ecef',
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
  },
  section: {
    marginBottom: 25,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  bioText: {
    fontSize: 16,
    color: '#555',
    lineHeight: 24,
  },
  promptCard: {
    backgroundColor: '#fff',
    borderRadius: 15,
    padding: 20,
    marginBottom: 15,
    borderWidth: 1,
    borderColor: '#e9ecef',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
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
  previewNote: {
    backgroundColor: '#fff3cd',
    padding: 15,
    borderRadius: 10,
    marginTop: 10,
    borderWidth: 1,
    borderColor: '#ffc107',
  },
  previewText: {
    fontSize: 14,
    color: '#856404',
    textAlign: 'center',
  },
});
