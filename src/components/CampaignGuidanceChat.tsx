/**
 * FILENAME: CampaignGuidanceChat.tsx
 * DESCRIPTION/PURPOSE: Chat interface for refining campaign guidance with AI
 * Author: JP + 2025-06-16
 * 
 * This component provides a chat interface that allows users to interact with
 * the AI to refine and improve their campaign guidance through conversation.
 */

import React, { useState, useRef, useEffect } from 'react';
import { MessageCircle, Send, Bot, User, Lightbulb, Loader2 } from 'lucide-react';
import { toast } from 'sonner';

interface ChatMessage {
  role: 'user' | 'assistant';
  message: string;
  timestamp: string;
}

interface AIResponse {
  response: string;
  suggested_updates: Record<string, any>;
  explanation: string;
  next_questions: string[];
}

interface CampaignGuidanceChatProps {
  campaignId: string;
  onGuidanceUpdate: (updates: Record<string, any>) => void;
  isOpen: boolean;
  onClose: () => void;
}

export const CampaignGuidanceChat: React.FC<CampaignGuidanceChatProps> = ({
  campaignId,
  onGuidanceUpdate,
  isOpen,
  onClose
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [lastAIResponse, setLastAIResponse] = useState<AIResponse | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen && messages.length === 0) {
      // Add welcome message
      const welcomeMessage: ChatMessage = {
        role: 'assistant',
        message: "Hi! I'm here to help you refine your campaign guidance. You can ask me to adjust the visual style, clarify target audience, improve prompts, or explain campaign decisions. What would you like to improve?",
        timestamp: new Date().toISOString()
      };
      setMessages([welcomeMessage]);
    }
  }, [isOpen, messages.length]);

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      role: 'user',
      message: inputMessage,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch(`/api/v1/campaigns/${campaignId}/guidance-chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: inputMessage,
          conversation_history: messages
        })
      });

      if (!response.ok) throw new Error('Failed to get AI response');

      const data = await response.json();
      
      if (data.success) {
        const aiMessage: ChatMessage = {
          role: 'assistant',
          message: data.ai_response.response,
          timestamp: new Date().toISOString()
        };

        setMessages(prev => [...prev, aiMessage]);
        setLastAIResponse(data.ai_response);
        
        // Show suggested updates if any
        if (Object.keys(data.ai_response.suggested_updates).length > 0) {
          toast.success('AI has suggestions to improve your campaign guidance!');
        }
      } else {
        throw new Error('AI response was not successful');
      }

    } catch (error) {
      console.error('Chat error:', error);
      toast.error('Failed to get AI response. Please try again.');
      
      const errorMessage: ChatMessage = {
        role: 'assistant',
        message: "I'm sorry, I encountered an error. Please try your message again.",
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const applySuggestions = async () => {
    if (!lastAIResponse?.suggested_updates) return;

    try {
      const response = await fetch(`/api/v1/campaigns/${campaignId}/guidance`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(lastAIResponse.suggested_updates)
      });

      if (!response.ok) throw new Error('Failed to update guidance');

      const data = await response.json();
      
      if (data.success) {
        onGuidanceUpdate(data.updated_guidance);
        toast.success('Campaign guidance updated successfully!');
        setLastAIResponse(null);
      } else {
        throw new Error('Update was not successful');
      }

    } catch (error) {
      console.error('Update error:', error);
      toast.error('Failed to update campaign guidance. Please try again.');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-y-0 right-0 w-96 bg-gray-900 border-l border-gray-700 flex flex-col z-50">
      {/* Header */}
      <div className="p-4 border-b border-gray-700 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <MessageCircle className="text-purple-400" size={20} />
          <h3 className="font-semibold text-white">Campaign Guidance Chat</h3>
        </div>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-white transition-colors"
        >
          ✕
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {message.role === 'assistant' && (
              <div className="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center flex-shrink-0">
                <Bot size={16} className="text-white" />
              </div>
            )}
            
            <div
              className={`max-w-[280px] p-3 rounded-lg ${
                message.role === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-800 text-gray-100 border border-gray-700'
              }`}
            >
              <p className="text-sm whitespace-pre-wrap">{message.message}</p>
              <span className="text-xs opacity-70 mt-1 block">
                {new Date(message.timestamp).toLocaleTimeString()}
              </span>
            </div>

            {message.role === 'user' && (
              <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0">
                <User size={16} className="text-white" />
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="flex gap-3 justify-start">
            <div className="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center flex-shrink-0">
              <Bot size={16} className="text-white" />
            </div>
            <div className="bg-gray-800 text-gray-100 border border-gray-700 p-3 rounded-lg">
              <div className="flex items-center gap-2">
                <Loader2 size={16} className="animate-spin" />
                <span className="text-sm">AI is thinking...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggestions Panel */}
      {lastAIResponse?.suggested_updates && Object.keys(lastAIResponse.suggested_updates).length > 0 && (
        <div className="p-4 border-t border-gray-700 bg-purple-500/10">
          <div className="flex items-center gap-2 mb-2">
            <Lightbulb className="text-yellow-400" size={16} />
            <span className="text-sm font-medium text-yellow-400">AI Suggestions</span>
          </div>
          <p className="text-xs text-gray-300 mb-3">{lastAIResponse.explanation}</p>
          <button
            onClick={applySuggestions}
            className="w-full bg-purple-500 hover:bg-purple-600 text-white text-sm py-2 px-3 rounded-lg transition-colors"
          >
            Apply Suggestions
          </button>
        </div>
      )}

      {/* Input */}
      <div className="p-4 border-t border-gray-700">
        <div className="flex gap-2">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about your campaign guidance..."
            className="flex-1 bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-400 resize-none focus:outline-none focus:border-purple-400"
            rows={2}
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={!inputMessage.trim() || isLoading}
            className="bg-purple-500 hover:bg-purple-600 disabled:bg-gray-600 text-white p-2 rounded-lg transition-colors flex-shrink-0"
          >
            <Send size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}; 