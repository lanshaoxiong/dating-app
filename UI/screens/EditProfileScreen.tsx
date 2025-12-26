import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  Image,
  Alert,
} from 'react-native';
import { StackNavigationProp } from '@react-navigation/stack';
import { ProfileStackParamList, Prompt } from '../types/navigation';

type EditProfileScreenNavigationProp = StackNavigationProp<ProfileStackParamList, 'EditProfile'>;

interface Props {
  navigation: EditProfileScreenNavigationProp;
}

export default function EditProfileScreen({ navigation }: Props) {
  const [name, setName] = useState('Your Pup');
  const [age, setAge] = useState('2');
  const [bio, setBio] = useState("Friendly and playful pup looking for new friends! Love running, playing fetch, and making new buddies at the dog park.");
  const [prompts, setPrompts] = useState<Prompt[]>([
    {
      question: "My ideal playdate",
      answer: "Running around the park, playing with toys, and lots of treats!"
    },
    {
      question: "I'm looking for",
      answer: "A fun-loving pup who enjoys adventures and belly rubs"
    },
  ]);

  const handleSave = () => {
    // Validate
    if (!name.trim()) {
      Alert.alert('Error', 'Please enter your pup\'s name');
      return;
    }
    if (!age.trim() || isNaN(Number(age))) {
      Alert.alert('Error', 'Please enter a valid age');
      return;
    }

    // In a real app, save to backend/state management
    Alert.alert('Success', 'Profile updated!', [
      {
        text: 'OK',
        onPress: () => navigation.goBack(),
      },
    ]);
  };

  const handleCancel = () => {
    navigation.goBack();
  };

  const updatePromptAnswer = (index: number, answer: string) => {
    const newPrompts = [...prompts];
    newPrompts[index].answer = answer;
    setPrompts(newPrompts);
  };

  return (
    <View style={styles.container}>
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        <View style={styles.content}>
          {/* Photos Section */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Photos</Text>
            <Text style={styles.helperText}>Add at least 2 photos of your pup</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.photoScroll}>
              <TouchableOpacity style={styles.addPhotoButton}>
                <Text style={styles.addPhotoText}>+</Text>
                <Text style={styles.addPhotoLabel}>Add Photo</Text>
              </TouchableOpacity>
              <Image
                source={{ uri: `https://placedog.net/200/200?random=${Math.random()}` }}
                style={styles.photoThumb}
              />
              <Image
                source={{ uri: `https://placedog.net/200/200?random=${Math.random()}` }}
                style={styles.photoThumb}
              />
            </ScrollView>
          </View>

          {/* Basic Info */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Basic Info</Text>
            <View style={styles.inputGroup}>
              <Text style={styles.label}>Name</Text>
              <TextInput
                style={styles.input}
                value={name}
                onChangeText={setName}
                placeholder="Your pup's name"
                placeholderTextColor="#999"
              />
            </View>
            <View style={styles.inputGroup}>
              <Text style={styles.label}>Age</Text>
              <TextInput
                style={styles.input}
                value={age}
                onChangeText={setAge}
                placeholder="Age in years"
                placeholderTextColor="#999"
                keyboardType="numeric"
              />
            </View>
          </View>

          {/* Bio */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>About</Text>
            <TextInput
              style={[styles.input, styles.bioInput]}
              value={bio}
              onChangeText={setBio}
              placeholder="Tell other pups about yourself..."
              placeholderTextColor="#999"
              multiline
              maxLength={300}
            />
            <Text style={styles.charCount}>{bio.length}/300</Text>
          </View>

          {/* Prompts */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Prompts</Text>
            {prompts.map((prompt, index) => (
              <View key={index} style={styles.promptEdit}>
                <Text style={styles.promptQuestion}>{prompt.question}</Text>
                <TextInput
                  style={[styles.input, styles.promptInput]}
                  value={prompt.answer}
                  onChangeText={(text) => updatePromptAnswer(index, text)}
                  placeholder="Your answer..."
                  placeholderTextColor="#999"
                  multiline
                  maxLength={150}
                />
              </View>
            ))}
            <TouchableOpacity style={styles.addPromptButton}>
              <Text style={styles.addPromptText}>+ Add Another Prompt</Text>
            </TouchableOpacity>
          </View>
        </View>
      </ScrollView>

      {/* Action Buttons */}
      <View style={styles.actionButtons}>
        <TouchableOpacity style={styles.cancelButton} onPress={handleCancel}>
          <Text style={styles.cancelButtonText}>Cancel</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.saveButton} onPress={handleSave}>
          <Text style={styles.saveButtonText}>Save Changes</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  scrollView: {
    flex: 1,
  },
  content: {
    padding: 20,
    paddingBottom: 100,
  },
  section: {
    marginBottom: 30,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  helperText: {
    fontSize: 14,
    color: '#666',
    marginBottom: 15,
  },
  photoScroll: {
    flexDirection: 'row',
  },
  addPhotoButton: {
    width: 120,
    height: 120,
    backgroundColor: '#fff',
    borderRadius: 15,
    borderWidth: 2,
    borderColor: '#e9ecef',
    borderStyle: 'dashed',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 10,
  },
  addPhotoText: {
    fontSize: 40,
    color: '#e91e63',
  },
  addPhotoLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 5,
  },
  photoThumb: {
    width: 120,
    height: 120,
    borderRadius: 15,
    marginRight: 10,
    backgroundColor: '#e9ecef',
  },
  inputGroup: {
    marginBottom: 15,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 15,
    fontSize: 16,
    color: '#333',
    borderWidth: 1,
    borderColor: '#e9ecef',
  },
  bioInput: {
    minHeight: 100,
    textAlignVertical: 'top',
  },
  charCount: {
    fontSize: 12,
    color: '#999',
    textAlign: 'right',
    marginTop: 5,
  },
  promptEdit: {
    backgroundColor: '#fff',
    borderRadius: 15,
    padding: 15,
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
  promptInput: {
    minHeight: 60,
    textAlignVertical: 'top',
  },
  addPromptButton: {
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 15,
    borderWidth: 2,
    borderColor: '#e91e63',
    borderStyle: 'dashed',
    alignItems: 'center',
  },
  addPromptText: {
    fontSize: 16,
    color: '#e91e63',
    fontWeight: '600',
  },
  actionButtons: {
    flexDirection: 'row',
    padding: 20,
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: '#e9ecef',
    gap: 10,
  },
  cancelButton: {
    flex: 1,
    backgroundColor: '#f8f9fa',
    paddingVertical: 15,
    borderRadius: 10,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#e9ecef',
  },
  cancelButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#666',
  },
  saveButton: {
    flex: 1,
    backgroundColor: '#e91e63',
    paddingVertical: 15,
    borderRadius: 10,
    alignItems: 'center',
  },
  saveButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff',
  },
});
