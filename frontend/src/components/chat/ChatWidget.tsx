import React, { useState, useEffect, useRef } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { MessageCircle, X, Send, Bot, User } from 'lucide-react';
import { cn } from '@/lib/utils';
import { getApiUrl, API_ENDPOINTS, DEFAULT_FETCH_OPTIONS } from '@/config/api';

// Type definitions
type Role = 'user' | 'bot';

interface Message {
  id: string;
  role: Role;
  content: string;
  timestamp: Date;
}

export interface ChatWidgetProps {
  title?: string;
  description?: string;
}

/**
 * API response interface for chat messages
 */
interface ChatApiResponse {
  response: string;
  session_id: string;
  timestamp: string;
}

/**
 * ChatWidget Component
 * A floating chat widget with AI assistant functionality
 */
export const ChatWidget: React.FC<ChatWidgetProps> = ({
  title = 'AI Assistant',
  description = 'Ask me anything about the dashboard',
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Initialize with welcome message
  useEffect(() => {
    const welcomeMessage: Message = {
      id: '1',
      role: 'bot',
      content: `Hello! I'm your ${title}. ${description} How can I help you today?`,
      timestamp: new Date(),
    };
    setMessages([welcomeMessage]);
  }, [title, description]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollContainer = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight;
      }
    }
  }, [messages]);

  // Focus input when chat opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const handleToggle = () => {
    setIsOpen(!isOpen);
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    // Clear any previous errors
    setError(null);

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const messageContent = inputValue.trim();
    setInputValue('');
    setIsLoading(true);

    try {
      // Call backend API
      const response = await fetch(
        getApiUrl(API_ENDPOINTS.chat.message),
        {
          ...DEFAULT_FETCH_OPTIONS,
          method: 'POST',
          body: JSON.stringify({
            message: messageContent,
            session_id: sessionId,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }

      const data: ChatApiResponse = await response.json();

      // Store session_id for conversation continuity
      if (data.session_id && !sessionId) {
        setSessionId(data.session_id);
      }

      // Add bot response
      const botResponse: Message = {
        id: (Date.now() + 1).toString(),
        role: 'bot',
        content: data.response,
        timestamp: new Date(data.timestamp),
      };

      setMessages((prev) => [...prev, botResponse]);
    } catch (err) {
      console.error('Error sending message:', err);
      setError('Failed to send message. Please try again.');
      
      // Add error message to chat
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'bot',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <>
      {/* Floating Button */}
      <Button
        onClick={handleToggle}
        className={cn(
          'fixed bottom-6 right-6 h-[60px] w-[60px] rounded-full shadow-lg transition-all duration-300 z-50',
          isOpen ? 'scale-0 opacity-0' : 'scale-100 opacity-100'
        )}
        size="icon"
        aria-label="Chat with AI"
        aria-expanded={isOpen}
      >
        <MessageCircle className="h-6 w-6" />
      </Button>

      {/* Chat Window */}
      <div
        className={cn(
          'fixed bottom-6 right-6 z-50 transition-all duration-300',
          'w-[350px] max-w-[calc(100vw-48px)] sm:w-[350px]',
          isOpen ? 'scale-100 opacity-100' : 'scale-0 opacity-0'
        )}
      >
        <Card className="flex flex-col h-[500px] max-h-[calc(100vh-48px)] shadow-xl">
          {/* Header */}
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
            <div className="flex-1">
              <CardTitle className="text-lg">{title}</CardTitle>
              <p className="text-sm text-muted-foreground mt-1">{description}</p>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={handleToggle}
              className="h-8 w-8"
              aria-label="Close chat"
            >
              <X className="h-4 w-4" />
            </Button>
          </CardHeader>

          {/* Messages Area */}
          <CardContent className="flex-1 flex flex-col p-0 overflow-hidden">
            <ScrollArea ref={scrollAreaRef} className="flex-1 px-4">
              <div className="space-y-4 py-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={cn(
                      'flex gap-3',
                      message.role === 'user' ? 'justify-end' : 'justify-start'
                    )}
                  >
                    {message.role === 'bot' && (
                      <Avatar className="h-8 w-8">
                        <AvatarFallback className="bg-primary text-primary-foreground">
                          <Bot className="h-4 w-4" />
                        </AvatarFallback>
                      </Avatar>
                    )}
                    <div
                      className={cn(
                        'rounded-lg px-4 py-2 max-w-[80%]',
                        message.role === 'user'
                          ? 'bg-primary text-primary-foreground'
                          : 'bg-muted'
                      )}
                    >
                      <p className="text-sm">{message.content}</p>
                    </div>
                    {message.role === 'user' && (
                      <Avatar className="h-8 w-8">
                        <AvatarFallback className="bg-secondary text-secondary-foreground">
                          <User className="h-4 w-4" />
                        </AvatarFallback>
                      </Avatar>
                    )}
                  </div>
                ))}
                {/* Loading indicator */}
                {isLoading && (
                  <div className="flex gap-3 justify-start">
                    <Avatar className="h-8 w-8">
                      <AvatarFallback className="bg-primary text-primary-foreground">
                        <Bot className="h-4 w-4" />
                      </AvatarFallback>
                    </Avatar>
                    <div className="rounded-lg px-4 py-2 bg-muted">
                      <div className="flex gap-1">
                        <span className="w-2 h-2 bg-foreground/40 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                        <span className="w-2 h-2 bg-foreground/40 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                        <span className="w-2 h-2 bg-foreground/40 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </ScrollArea>

            {/* Error Message */}
            {error && (
              <div className="px-4 py-2 bg-destructive/10 text-destructive text-sm">
                {error}
              </div>
            )}

            {/* Input Area */}
            <div className="border-t p-4">
              <div className="flex gap-2">
                <Input
                  ref={inputRef}
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your message..."
                  disabled={isLoading}
                  aria-label="Type your message"
                  className="flex-1"
                />
                <Button
                  onClick={handleSendMessage}
                  disabled={!inputValue.trim() || isLoading}
                  size="icon"
                  aria-label="Send message"
                >
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </>
  );
};