import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TextInput,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  Image,
} from 'react-native';
import { RouteProp } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import { MatchesStackParamList, MessagesStackParamList } from '../types/navigation';

type ChatScreenRouteProp = RouteProp<MatchesStackParamList | MessagesStackParamList, 'Chat'>;
type ChatScreenNavigationProp = StackNavigationProp<MatchesStackParamList | MessagesStackParamList, 'Chat'>;

interface Props {
  route: ChatScreenRouteProp;
  navigation: ChatScreenNavigationProp;
}

interface ChatMessage {
  id: string;
  senderId: string;
  text: string;
  timestamp: Date;
}

export default function ChatScreen({ route, navigation }: Props) {
  const { matchProfile } = route.params;
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      senderId: 'other',
      text: `Hi! I'm ${matchProfile.name}! 🐶`,
      timestamp: new Date(Date.now() - 1000 * 60 * 30),
    },
    {
      id: '2',
      senderId: 'me',
      text: 'Hey! Nice to meet you! Want to arrange a playdate?',
      timestamp: new Date(Date.now() - 1000 * 60 * 25),
    },
    {
      id: '3',
      senderId: 'other',
      text: "Yes! I'd love that! My human is free this weekend 🎾",
      timestamp: new Date(Date.now() - 1000 * 60 * 20),
    },
  ]);
  const [inputText, setInputText] = useState('');
  const flatListRef = useRef<FlatList>(null);

  useEffect(() => {
    // Set header title to match name
    navigation.setOptions({
      title: matchProfile.name,
    });
  }, [matchProfile.name, navigation]);

  const handleSend = () => {
    if (inputText.trim().length === 0) return;

    const newMessage: ChatMessage = {
      id: Date.now().toString(),
      senderId: 'me',
      text: inputText.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, newMessage]);
    setInputText('');

    // Scroll to bottom
    setTimeout(() => {
      flatListRef.current?.scrollToEnd({ animated: true });
    }, 100);
  };

  const formatTime = (date: Date): string => {
    const hours = date.getHours();
    const minutes = date.getMinutes();
    const ampm = hours >= 12 ? 'PM' : 'AM';
    const formattedHours = hours % 12 || 12;
    const formattedMinutes = minutes < 10 ? `0${minutes}` : minutes;
    return `${formattedHours}:${formattedMinutes} ${ampm}`;
  };

  const renderMessage = ({ item, index }: { item: ChatMessage; index: number }) => {
    const isMe = item.senderId === 'me';
    const showTimestamp = index === 0 || 
      (messages[index - 1] && 
       item.timestamp.getTime() - messages[index - 1].timestamp.getTime() > 1000 * 60 * 5);

    return (
      <View>
        {showTimestamp && (
          <Text style={styles.timestamp}>{formatTime(item.timestamp)}</Text>
        )}
        <View style={[styles.messageContainer, isMe ? styles.myMessage : styles.theirMessage]}>
          {!isMe && (
            <Image
              source={{ uri: matchProfile.photo }}
              style={styles.avatar}
            />
          )}
          <View style={[styles.messageBubble, isMe ? styles.myBubble : styles.theirBubble]}>
            <Text style={[styles.messageText, isMe ? styles.myText : styles.theirText]}>
              {item.text}
            </Text>
          </View>
        </View>
      </View>
    );
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
    >
      <FlatList
        ref={flatListRef}
        data={messages}
        renderItem={renderMessage}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.messagesList}
        onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
      />

      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          value={inputText}
          onChangeText={setInputText}
          placeholder="Type a message..."
          placeholderTextColor="#999"
          multiline
          maxLength={500}
        />
        <TouchableOpacity
          style={[styles.sendButton, inputText.trim().length === 0 && styles.sendButtonDisabled]}
          onPress={handleSend}
          disabled={inputText.trim().length === 0}
        >
          <Text style={styles.sendButtonText}>Send</Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  messagesList: {
    padding: 15,
    paddingBottom: 20,
  },
  timestamp: {
    textAlign: 'center',
    color: '#999',
    fontSize: 12,
    marginVertical: 10,
  },
  messageContainer: {
    flexDirection: 'row',
    marginVertical: 5,
    alignItems: 'flex-end',
  },
  myMessage: {
    justifyContent: 'flex-end',
  },
  theirMessage: {
    justifyContent: 'flex-start',
  },
  avatar: {
    width: 32,
    height: 32,
    borderRadius: 16,
    marginRight: 8,
    backgroundColor: '#e9ecef',
  },
  messageBubble: {
    maxWidth: '75%',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 20,
  },
  myBubble: {
    backgroundColor: '#e91e63',
    borderBottomRightRadius: 4,
  },
  theirBubble: {
    backgroundColor: '#fff',
    borderBottomLeftRadius: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  messageText: {
    fontSize: 16,
    lineHeight: 22,
  },
  myText: {
    color: '#fff',
  },
  theirText: {
    color: '#333',
  },
  inputContainer: {
    flexDirection: 'row',
    padding: 10,
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: '#e9ecef',
    alignItems: 'flex-end',
  },
  input: {
    flex: 1,
    backgroundColor: '#f8f9fa',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 10,
    marginRight: 10,
    fontSize: 16,
    maxHeight: 100,
    color: '#333',
  },
  sendButton: {
    backgroundColor: '#e91e63',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  sendButtonDisabled: {
    backgroundColor: '#ccc',
  },
  sendButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});
