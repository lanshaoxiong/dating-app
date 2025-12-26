import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Image,
} from 'react-native';
import { StackNavigationProp } from '@react-navigation/stack';
import { MessagesStackParamList, Conversation } from '../types/navigation';

type MessagesScreenNavigationProp = StackNavigationProp<MessagesStackParamList, 'MessagesScreen'>;

interface Props {
  navigation: MessagesScreenNavigationProp;
}

// Mock conversations data
const mockConversations: Conversation[] = [
  {
    id: 1,
    matchId: 1,
    matchProfile: {
      id: 1,
      name: 'Buddy',
      photo: `https://placedog.net/400/400?random=${Math.random()}`,
    },
    lastMessage: "Let's meet at the dog park tomorrow! 🐕",
    timestamp: new Date(Date.now() - 1000 * 60 * 30), // 30 minutes ago
    unread: true,
  },
  {
    id: 2,
    matchId: 2,
    matchProfile: {
      id: 2,
      name: 'Luna',
      photo: `https://placedog.net/400/400?random=${Math.random()}`,
    },
    lastMessage: 'My human says I can come play on Saturday!',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2), // 2 hours ago
    unread: false,
  },
  {
    id: 3,
    matchId: 3,
    matchProfile: {
      id: 3,
      name: 'Max',
      photo: `https://placedog.net/400/400?random=${Math.random()}`,
    },
    lastMessage: 'Woof woof! 🎾',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24), // 1 day ago
    unread: false,
  },
];

export default function MessagesScreen({ navigation }: Props) {
  const formatTimestamp = (date: Date): string => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 1000 / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (minutes < 60) {
      return `${minutes}m ago`;
    } else if (hours < 24) {
      return `${hours}h ago`;
    } else if (days === 1) {
      return 'Yesterday';
    } else {
      return `${days}d ago`;
    }
  };

  const handleConversationPress = (conversation: Conversation) => {
    navigation.navigate('Chat', {
      matchId: conversation.matchId,
      matchProfile: conversation.matchProfile,
    });
  };

  const renderConversation = ({ item }: { item: Conversation }) => (
    <TouchableOpacity
      style={styles.conversationRow}
      onPress={() => handleConversationPress(item)}
      activeOpacity={0.7}
    >
      <Image
        source={{ uri: item.matchProfile.photo }}
        style={styles.profilePhoto}
      />
      <View style={styles.conversationContent}>
        <View style={styles.conversationHeader}>
          <Text style={styles.matchName}>{item.matchProfile.name}</Text>
          <Text style={styles.timestamp}>{formatTimestamp(item.timestamp)}</Text>
        </View>
        <View style={styles.messagePreviewContainer}>
          <Text
            style={[
              styles.messagePreview,
              item.unread && styles.unreadMessage,
            ]}
            numberOfLines={1}
          >
            {item.lastMessage}
          </Text>
          {item.unread && <View style={styles.unreadBadge} />}
        </View>
      </View>
    </TouchableOpacity>
  );

  const renderEmptyState = () => (
    <View style={styles.emptyState}>
      <Text style={styles.emptyIcon}>💬</Text>
      <Text style={styles.emptyTitle}>No playdates yet!</Text>
      <Text style={styles.emptyText}>
        When you match with a pup, you can arrange playdates here
      </Text>
    </View>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>💬 Playdates</Text>
      </View>

      {mockConversations.length > 0 ? (
        <FlatList
          data={mockConversations}
          renderItem={renderConversation}
          keyExtractor={(item) => item.id.toString()}
          contentContainerStyle={styles.listContainer}
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
  listContainer: {
    paddingVertical: 10,
  },
  conversationRow: {
    flexDirection: 'row',
    padding: 15,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  profilePhoto: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#e9ecef',
    marginRight: 15,
  },
  conversationContent: {
    flex: 1,
    justifyContent: 'center',
  },
  conversationHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 5,
  },
  matchName: {
    fontSize: 17,
    fontWeight: '600',
    color: '#333',
  },
  timestamp: {
    fontSize: 13,
    color: '#999',
  },
  messagePreviewContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  messagePreview: {
    flex: 1,
    fontSize: 15,
    color: '#666',
  },
  unreadMessage: {
    fontWeight: '600',
    color: '#333',
  },
  unreadBadge: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: '#e91e63',
    marginLeft: 8,
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
