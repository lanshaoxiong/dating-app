export interface Profile {
  id: number;
  name: string;
  age: number;
  photos: string[];
  bio?: string;
  prompts: Prompt[];
  distance?: number;
}

export interface Prompt {
  question: string;
  answer: string;
}

export interface Match {
  id: number;
  name: string;
  age: number;
  photo: string;
}

export interface Conversation {
  id: number;
  matchId: number;
  matchProfile: {
    id: number;
    name: string;
    photo: string;
  };
  lastMessage: string;
  timestamp: Date;
  unread: boolean;
}

export type RootStackParamList = {
  Main: undefined;
  MatchCelebration: {
    currentUser: {
      id: string;
      name: string;
      photos: string[];
    };
    matchedUser: Profile;
  };
};

export type TabParamList = {
  Home: undefined;
  Matches: undefined;
  Messages: undefined;
  Profile: undefined;
};

export type HomeStackParamList = {
  HomeScreen: undefined;
  ProfileDetail: {
    profile: Profile;
  };
};

export type MatchesStackParamList = {
  MatchesScreen: undefined;
  Chat: {
    matchId: number;
    matchProfile: Match | { id: number; name: string; photo: string };
  };
};

export type MessagesStackParamList = {
  MessagesScreen: undefined;
  Chat: {
    matchId: number;
    matchProfile: Match | { id: number; name: string; photo: string };
  };
};

export type ProfileStackParamList = {
  ProfileScreen: undefined;
  EditProfile: undefined;
};
