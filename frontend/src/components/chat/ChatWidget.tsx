import React, { useState, useEffect, useRef } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { MessageCircle, X, Send, Bot, User, Sparkles, BarChart3, HelpCircle, FileText, Calculator, Users, BookOpen } from 'lucide-react';
import { cn } from '@/lib/utils';
import { getApiUrl, API_ENDPOINTS, DEFAULT_FETCH_OPTIONS } from '@/config/api';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

// Type definitions
type Role = 'user' | 'bot';
type MessageType = 'general' | 'data-insight' | 'pdf-response';

interface PDFSource {
  name: string;
  file_id: string;
}

interface Message {
  id: string;
  role: Role;
  content: string;
  timestamp: Date;
  type?: MessageType;
  sources?: PDFSource[];
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
  sources?: PDFSource[];
}

/**
 * API response interface for multi-message chat responses
 */
interface ChatMultiMessageResponse {
  messages: string[];
  session_id: string;
  timestamp: string;
  sources?: PDFSource[];
}

/**
 * Union type for all possible chat API responses
 */
type ChatResponse = ChatApiResponse | ChatMultiMessageResponse;

/**
 * Type guard to check if response is multi-message
 */
function isMultiMessageResponse(response: ChatResponse): response is ChatMultiMessageResponse {
  return 'messages' in response && Array.isArray(response.messages);
}

/**
 * Suggested query configuration
 */
interface SuggestedQuery {
  label: string;
  query: string;
  icon: React.ReactNode;
}

const SUGGESTED_QUERIES: SuggestedQuery[] = [
  {
    label: 'Top 5 HCOs',
    query: 'Show top 5 HCOs with highest ghost patients',
    icon: <BarChart3 className="h-3 w-3" />,
  },
  {
    label: 'Patient Stats',
    query: 'Show patient statistics',
    icon: <Users className="h-3 w-3" />,
  },
  {
    label: 'Contract Templates',
    query: 'Show contract templates',
    icon: <FileText className="h-3 w-3" />,
  },
  {
    label: 'Help',
    query: 'What queries can I ask?',
    icon: <HelpCircle className="h-3 w-3" />,
  },
];

/**
 * Detect if message content is a data insight (contains markdown formatting)
 */
function isDataInsight(content: string): boolean {
  // Check for markdown table, bold text, or numbered lists
  return content.includes('|') || content.includes('**') || /^\d+\.\s/.test(content);
}

/**
 * Detect if message is a PDF-related query
 */
function isPDFQuery(message: string): boolean {
  const pdfKeywords = [
    'research', 'paper', 'document', 'guideline', 'policy',
    'study', 'literature', 'publication', 'according to'
  ];
  const messageLower = message.toLowerCase();
  return pdfKeywords.some(keyword => messageLower.includes(keyword));
}

/**
 * Pre-process markdown content to fix common formatting issues
 * specifically handles spaces in markdown links which breaks rendering
 */
function preprocessMessageContent(content: string): string {
  // Fix markdown links that have spaces in the URL part
  // Example: [Link](#target with space) -> [Link](#target%20with%20space)
  return content.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (match, text, url) => {
    if (url.includes(' ')) {
      return `[${text}](${url.replace(/ /g, '%20')})`;
    }
    return match;
  });
}

/**
 * ChatWidget Component
 * A floating chat widget with AI assistant functionality and data insights support
 */
export const ChatWidget: React.FC<ChatWidgetProps> = ({
  title = 'AI Assistant',
  description = 'Ask me anything about the dashboard',
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isPDFSearching, setIsPDFSearching] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Initialize with welcome message
  useEffect(() => {
    const welcomeMessage: Message = {
      id: '1',
      role: 'bot',
      content: `Hello! I'm your ${title}. ${description}\n\nTry asking me about HCOs, patients, contracts, or outcomes. Click one of the suggested queries below!`,
      timestamp: new Date(),
      type: 'general',
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

  const handleSendMessage = async (messageText?: string) => {
    const textToSend = messageText || inputValue.trim();
    if (!textToSend || isLoading) return;

    // Clear any previous errors
    setError(null);

    // Check if this is a PDF query
    const isPDF = isPDFQuery(textToSend);
    if (isPDF) {
      setIsPDFSearching(true);
    }

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: textToSend,
      timestamp: new Date(),
      type: 'general',
    };

    setMessages((prev) => [...prev, userMessage]);
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
            message: textToSend,
            session_id: sessionId,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }

      const data: ChatResponse = await response.json();

      // Store session_id for conversation continuity
      if (data.session_id && !sessionId) {
        setSessionId(data.session_id);
      }

      // Check if response contains multiple messages
      if (isMultiMessageResponse(data)) {
        // Handle multiple messages - add them sequentially
        const botMessages: Message[] = data.messages.map((content, index) => {
          // Check if content contains markdown links (buttons)
          const hasMarkdownLink = content.includes('[') && content.includes('](#');
          const hasSources = data.sources && data.sources.length > 0;
          const messageType = hasSources ? 'pdf-response' : (isDataInsight(content) || hasMarkdownLink) ? 'data-insight' : 'general';
          console.log(`Multi-message ${index + 1}:`, {
            content: content.substring(0, 100),
            hasMarkdownLink,
            messageType,
            role: 'bot'
          });
          return {
            id: (Date.now() + index + 1).toString(),
            role: 'bot',
            content: content,
            timestamp: new Date(data.timestamp),
            type: messageType,
            sources: data.sources,
          };
        });

        console.log('Adding bot messages:', botMessages.length);
        setMessages((prev) => [...prev, ...botMessages]);
      } else {
        // Handle single message response
        const hasSources = data.sources && data.sources.length > 0;
        const messageType = hasSources ? 'pdf-response' : isDataInsight(data.response) ? 'data-insight' : 'general';

        // Add bot response
        const botResponse: Message = {
          id: (Date.now() + 1).toString(),
          role: 'bot',
          content: data.response,
          timestamp: new Date(data.timestamp),
          type: messageType,
          sources: data.sources,
        };

        setMessages((prev) => [...prev, botResponse]);
      }
    } catch (err) {
      console.error('Error sending message:', err);
      setError('Failed to send message. Please try again.');
      
      // Add error message to chat
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'bot',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
        type: 'general',
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setIsPDFSearching(false);
    }
  };

  const handleSuggestedQuery = (query: string) => {
    handleSendMessage(query);
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const showSuggestedQueries = messages.length <= 1 && !isLoading;

  return (
    <>
      {/* Floating Button - Speech Bubble Shape */}
      <div
        className={cn(
          'fixed bottom-6 right-6 z-50 transition-all duration-300',
          isOpen ? 'scale-0 opacity-0' : 'scale-100 opacity-100'
        )}
      >
        <div className="relative">
          {/* Speech Bubble Tail for Button */}
          <div className="absolute -bottom-2 right-6 w-0 h-0 border-l-[12px] border-l-transparent border-r-[12px] border-r-transparent border-t-[12px] border-t-purple-600"></div>
          
          <Button
            onClick={handleToggle}
            className="h-[70px] w-[100px] rounded-2xl shadow-lg bg-gradient-to-br from-purple-600 to-indigo-700 hover:from-purple-700 hover:to-indigo-800 border-0"
            aria-label="Chat with MedAI"
            aria-expanded={isOpen}
          >
            <div className="flex flex-col items-center justify-center">
              <div className="text-sm font-bold text-white leading-none">
                MED<span className="text-orange-400">AI</span>
              </div>
              <div className="text-[8px] tracking-wider text-gray-200 font-light mt-0.5">AGENT</div>
            </div>
          </Button>
        </div>
      </div>

      {/* Chat Window with Speech Bubble Tail */}
      <div
        className={cn(
          'fixed bottom-6 right-6 z-50 transition-all duration-300',
          'w-[400px] max-w-[calc(100vw-48px)] sm:w-[400px]',
          isOpen ? 'scale-100 opacity-100' : 'scale-0 opacity-0'
        )}
      >
        <div className="relative">
          {/* Speech Bubble Tail */}
          <div className="absolute -bottom-4 right-8 w-0 h-0 border-l-[20px] border-l-transparent border-r-[20px] border-r-transparent border-t-[20px] border-t-white z-10"></div>
          
          <Card className="flex flex-col h-[600px] max-h-[calc(100vh-48px)] shadow-xl rounded-lg overflow-hidden">
          {/* Header - MedAI Branded */}
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4 border-b bg-gradient-to-r from-purple-600 to-indigo-700">
            <div className="flex-1">
              <CardTitle className="text-lg flex items-center gap-2 text-white">
                <div className="w-6 h-6 bg-orange-500 rounded flex items-center justify-center flex-shrink-0">
                  <svg viewBox="0 0 24 24" fill="none" className="w-4 h-4" stroke="white" strokeWidth="2">
                    <circle cx="12" cy="12" r="3" />
                    <path d="M12 2v4m0 12v4M2 12h4m12 0h4m-3.5-7.5l-2.8 2.8m-7.4 7.4l-2.8 2.8m14.2 0l-2.8-2.8m-7.4-7.4l-2.8-2.8" />
                  </svg>
                </div>
                <span className="font-bold">MED<span className="text-orange-400">AI</span> Agent</span>
              </CardTitle>
              <p className="text-sm text-purple-100 mt-1">Your healthcare sales & compliance assistant</p>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={handleToggle}
              className="h-8 w-8 text-white hover:bg-white/20"
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
                      <Avatar className="h-8 w-8 flex-shrink-0">
                        <AvatarFallback className="bg-gradient-to-br from-purple-600 to-indigo-700 text-white">
                          <div className="flex flex-col items-center justify-center scale-75">
                            <div className="text-[8px] font-bold leading-none">
                              MED<span className="text-orange-400">AI</span>
                            </div>
                          </div>
                        </AvatarFallback>
                      </Avatar>
                    )}
                    <div
                      className={cn(
                        'rounded-lg px-4 py-3 max-w-[85%]',
                        message.role === 'user'
                          ? 'bg-primary text-primary-foreground'
                          : message.type === 'pdf-response'
                          ? 'bg-purple-50 dark:bg-purple-950 border border-purple-200 dark:border-purple-800'
                          : message.type === 'data-insight'
                          ? 'bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800'
                          : 'bg-muted'
                      )}
                    >
                      {message.type === 'pdf-response' && message.role === 'bot' && (
                        <div className="flex items-center gap-2 mb-2 pb-2 border-b border-purple-200 dark:border-purple-800">
                          <BookOpen className="h-4 w-4 text-purple-600 dark:text-purple-400" />
                          <Badge variant="secondary" className="text-xs bg-purple-100 dark:bg-purple-900">
                            Document Search
                          </Badge>
                        </div>
                      )}
                      {message.type === 'data-insight' && message.role === 'bot' && (
                        <div className="flex items-center gap-2 mb-2 pb-2 border-b border-blue-200 dark:border-blue-800">
                          <BarChart3 className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                          <Badge variant="secondary" className="text-xs">
                            Data Insight
                          </Badge>
                        </div>
                      )}
                      {message.role === 'bot' ? (
                        (() => {
                          console.log('Rendering bot message:', message.content.substring(0, 200));
                          console.log('Message type:', message.type);
                          console.log('Is bot?:', message.role === 'bot');
                          return (
                            <div className="text-sm">
                              <Markdown
                                remarkPlugins={[remarkGfm]}
                            components={{
                              // Intercept special action links
                              a: ({ node, href, children, ...props }) => {
                                console.log('Link component called:', { href, children });
                                
                                // Check if this is an HCO address lookup link
                                if (href && href.startsWith('#lookup-address:')) {
                                  const hcoName = decodeURIComponent(href.replace('#lookup-address:', ''));
                                  console.log('Rendering HCO lookup link:', hcoName);
                                  
                                  return (
                                    <a
                                      href="#"
                                      onClick={(e) => {
                                        e.preventDefault();
                                        console.log('HCO link clicked:', hcoName);
                                        handleSendMessage(`What is the address of ${hcoName}?`);
                                      }}
                                      className="text-primary hover:underline cursor-pointer font-medium !text-blue-600 dark:!text-blue-400"
                                      style={{ color: 'var(--primary)', textDecoration: 'underline' }}
                                      {...props}
                                    >
                                      {children}
                                    </a>
                                  );
                                }
                                
                                // Check if this is a fetch external data link
                                if (href && href.startsWith('#fetch-external:')) {
                                  const authorName = decodeURIComponent(href.replace('#fetch-external:', ''));
                                  console.log('Rendering fetch external link:', authorName);
                                  
                                  return (
                                    <button
                                      type="button"
                                      onClick={(e) => {
                                        e.preventDefault();
                                        e.stopPropagation();
                                        console.log('Fetch external clicked:', authorName);
                                        handleSendMessage(`Fetch external data for ${authorName}`);
                                      }}
                                      className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 rounded-md shadow-sm transition-all cursor-pointer no-underline mt-2 border-0"
                                    >
                                      {children}
                                    </button>
                                  );
                                }
                                
                                // Regular links - render normally
                                return (
                                  <a
                                    href={href}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-primary hover:underline !text-blue-600 dark:!text-blue-400"
                                    style={{ color: 'var(--primary)', textDecoration: 'underline' }}
                                    {...props}
                                  >
                                    {children}
                                  </a>
                                );
                              },
                              // Style tables
                              table: ({ node, ...props }) => (
                                <div className="overflow-x-auto my-2">
                                  <table className="min-w-full text-sm border-collapse" {...props} />
                                </div>
                              ),
                              th: ({ node, ...props }) => (
                                <th className="border border-border px-2 py-1 bg-muted font-semibold text-left" {...props} />
                              ),
                              td: ({ node, ...props }) => (
                                <td className="border border-border px-2 py-1" {...props} />
                              ),
                              // Style lists
                              ul: ({ node, ...props }) => (
                                <ul className="list-disc list-inside space-y-1 my-2" {...props} />
                              ),
                              ol: ({ node, ...props }) => (
                                <ol className="list-decimal list-inside space-y-1 my-2" {...props} />
                              ),
                              // Style paragraphs
                              p: ({ node, ...props }) => (
                                <p className="my-1" {...props} />
                              ),
                              // Style strong/bold
                              strong: ({ node, ...props }) => (
                                <strong className="font-bold text-foreground" {...props} />
                              ),
                            }}
                          >
                            {preprocessMessageContent(message.content)}
                              </Markdown>
                            </div>
                          );
                        })()
                      ) : (
                        <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                      )}
                      
                      {/* Display PDF sources if available */}
                      {message.sources && message.sources.length > 0 && (
                        <div className="mt-3 pt-3 border-t border-purple-200 dark:border-purple-800">
                          <p className="text-xs font-semibold text-purple-700 dark:text-purple-300 mb-2">
                            📚 Sources:
                          </p>
                          <div className="flex flex-wrap gap-1.5">
                            {message.sources.map((source, idx) => (
                              <Badge
                                key={idx}
                                variant="outline"
                                className="text-xs bg-purple-100 dark:bg-purple-900 border-purple-300 dark:border-purple-700"
                              >
                                <FileText className="h-3 w-3 mr-1" />
                                {source.name}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                    {message.role === 'user' && (
                      <Avatar className="h-8 w-8 flex-shrink-0">
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
                      <AvatarFallback className="bg-gradient-to-br from-purple-600 to-indigo-700 text-white">
                        <div className="flex flex-col items-center justify-center scale-75">
                          <div className="text-[8px] font-bold leading-none">
                            MED<span className="text-orange-400">AI</span>
                          </div>
                        </div>
                      </AvatarFallback>
                    </Avatar>
                    <div className="rounded-lg px-4 py-3 bg-muted">
                      {isPDFSearching ? (
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <BookOpen className="h-4 w-4 animate-pulse" />
                          <span>Searching documents...</span>
                        </div>
                      ) : (
                        <div className="flex gap-1">
                          <span className="w-2 h-2 bg-foreground/40 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                          <span className="w-2 h-2 bg-foreground/40 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                          <span className="w-2 h-2 bg-foreground/40 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Suggested Queries */}
                {showSuggestedQueries && (
                  <div className="space-y-2 pt-2">
                    <p className="text-xs text-muted-foreground px-1">Suggested queries:</p>
                    <div className="flex flex-wrap gap-2">
                      {SUGGESTED_QUERIES.map((query, index) => (
                        <Button
                          key={index}
                          variant="outline"
                          size="sm"
                          onClick={() => handleSuggestedQuery(query.query)}
                          className="text-xs h-8 gap-1.5"
                        >
                          {query.icon}
                          {query.label}
                        </Button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </ScrollArea>

            {/* Error Message */}
            {error && (
              <div className="px-4 py-2 bg-destructive/10 text-destructive text-sm border-t border-destructive/20">
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
                  placeholder="Ask about data insights..."
                  disabled={isLoading}
                  aria-label="Type your message"
                  className="flex-1"
                />
                <Button
                  onClick={() => handleSendMessage()}
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
      </div>
    </>
  );
};