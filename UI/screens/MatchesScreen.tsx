import React from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, Image, Dimensions } from 'react-native';

const { width } = Dimensions.get('window');
const CARD_WIDTH = (width - 60) / 2; // 2 columns with padding

// Mock matches data
const mockMatches = [
  {
    id: 1,
    name: 'Buddy',
    age: 2,
    photo: `https://placedog.net/400/400?random=${Math.random()}`,
  },
  {
    id: 2,
    name: 'Luna',
    age: 1,
    photo: `https://placedog.net/400/400?random=${Math.random()}`,
  },
  {
    id: 3,
    name: 'Max',
    age: 3,
    photo: `https://placedog.net/400/400?random=${Math.random()}`,
  },
  {
    id: 4,
    name: 'Bella',
    age: 2,
    photo: `https://placedog.net/400/400?random=${Math.random()}`,
  },
  {
    id: 5,
    name: 'Charlie',
    age: 4,
    photo: `https://placedog.net/400/400?random=${Math.random()}`,
  },
  {
    id: 6,
    name: 'Daisy',
    age: 1,
    photo: `https://placedog.net/400/400?random=${Math.random()}`,
  },
];

export default function MatchesScreen({ navigation }) {
  const handleMatchPress = (match) => {
    navigation.navigate('Chat', {
      matchId: match.id,
      matchProfile: match,
    });
  };

  const renderMatchCard = ({ item }) => (
    <TouchableOpacity
      style={styles.matchCard}
      onPress={() => handleMatchPress(item)}
      activeOpacity={0.8}
    >
      <Image source={{ uri: item.photo }} style={styles.matchPhoto} />
      <View style={styles.matchInfo}>
        <Text style={styles.matchName}>{item.name}, {item.age}</Text>
      </View>
    </TouchableOpacity>
  );

  const renderEmptyState = () => (
    <View style={styles.emptyState}>
      <Text style={styles.emptyIcon}>🐾</Text>
      <Text style={styles.emptyTitle}>No matches yet!</Text>
      <Text style={styles.emptyText}>
        Keep swiping to find the perfect playmate for your pup
      </Text>
    </View>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>🐾 Matches</Text>
      </View>
      
      {mockMatches.length > 0 ? (
        <FlatList
          data={mockMatches}
          renderItem={renderMatchCard}
          keyExtractor={(item) => item.id.toString()}
          numColumns={2}
          contentContainerStyle={styles.gridContainer}
          columnWrapperStyle={styles.row}
          showsVerticalScrollIndicator={false}
        />
      ) : (
        renderEmptyState()
      )}
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
    borderBottomWidth: 1,
    borderBottomColor: '#e9ecef',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#e91e63',
  },
  gridContainer: {
    padding: 20,
  },
  row: {
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  matchCard: {
    width: CARD_WIDTH,
    backgroundColor: '#fff',
    borderRadius: 15,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  matchPhoto: {
    width: '100%',
    height: CARD_WIDTH * 1.2,
    backgroundColor: '#e9ecef',
  },
  matchInfo: {
    padding: 12,
  },
  matchName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  emptyIcon: {
    fontSize: 80,
    marginBottom: 20,
  },
  emptyTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  emptyText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    lineHeight: 24,
  },
});
