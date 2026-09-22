import { useSyncExternalStore } from "react";
import type { SearchDocument, SearchRequest } from "@/types/search";

export type ChatMessageStatus = "pending" | "done" | "error";

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  status: ChatMessageStatus;
  sources?: SearchDocument[];
  responseTimeMs?: number | null;
  error?: string;
}

export interface ChatSession {
  messages: ChatMessage[];
  input: string;
  settings: SearchRequest;
}

const DEFAULT_SETTINGS: SearchRequest = {
  query: "",
  retrieve_limit: 30,
  merge_limit: 10,
  top_k: 5,
  temperature: 0.3,
  max_tokens: 1024,
  only_context: false,
};

const EMPTY_SESSION: ChatSession = {
  messages: [],
  input: "",
  settings: DEFAULT_SETTINGS,
};

const sessions = new Map<string, ChatSession>();
const listeners = new Set<() => void>();

const emitChange = () => {
  listeners.forEach((listener) => listener());
};

const getSession = (collectionId: string): ChatSession => {
  return sessions.get(collectionId) ?? EMPTY_SESSION;
};

const updateSession = (collectionId: string, updater: (prev: ChatSession) => ChatSession) => {
  const next = updater(getSession(collectionId));
  sessions.set(collectionId, next);
  emitChange();
};

export const chatStore = {
  setInput(collectionId: string, input: string) {
    updateSession(collectionId, (prev) => ({ ...prev, input }));
  },

  setSettings(collectionId: string, settings: SearchRequest) {
    updateSession(collectionId, (prev) => ({ ...prev, settings }));
  },

  appendMessage(collectionId: string, message: ChatMessage) {
    updateSession(collectionId, (prev) => ({
      ...prev,
      messages: [...prev.messages, message],
    }));
  },

  updateMessage(collectionId: string, messageId: string, patch: Partial<ChatMessage>) {
    updateSession(collectionId, (prev) => ({
      ...prev,
      messages: prev.messages.map((message) =>
        message.id === messageId ? { ...message, ...patch } : message
      ),
    }));
  },

  removeMessage(collectionId: string, messageId: string) {
    updateSession(collectionId, (prev) => ({
      ...prev,
      messages: prev.messages.filter((message) => message.id !== messageId),
    }));
  },

  clearMessages(collectionId: string) {
    updateSession(collectionId, (prev) => ({ ...prev, messages: [] }));
  },

  reset(collectionId: string) {
    sessions.delete(collectionId);
    emitChange();
  },
};

const subscribe = (listener: () => void) => {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
};

/** Состояние чата конкретной коллекции — живёт между страницами (модульный store). */
export const useChatSession = (collectionId: string | undefined) => {
  const session = useSyncExternalStore(
    subscribe,
    () => (collectionId ? getSession(collectionId) : EMPTY_SESSION),
    () => EMPTY_SESSION
  );

  return session;
};

export const createMessageId = () =>
  `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
