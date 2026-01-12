import { useState, FormEvent, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { MessageCircle, X, Send, ChevronDown, ChevronUp, BookOpen, Info } from 'lucide-react';
import { PDFManager } from '@/components/chat/PDFManager';

interface ChatMessage {
  text: string;
  sender: 'user' | 'bot';
}

const MedAIAgent = () => {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [isDocLibraryOpen, setIsDocLibraryOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      text: '👋 Hello! I\'m your MedAI Assistant. I can help you with:\n\n• Healthcare organization information\n• Patient data insights\n• Contract details\n• HCO address lookups\n• Document search (research papers, policies, guidelines)\n\nTry asking: "What are the top 5 HCOs?" or "What does the research say about CAR-T therapy?"',
      sender: 'bot'
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleContactSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    alert('Thank you for your message! We will get back to you soon.');
    e.currentTarget.reset();
  };

  const handleChatSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    
    const message = inputMessage.trim();
    if (!message) return;

    // Add user message
    setMessages(prev => [...prev, { text: message, sender: 'user' }]);
    setInputMessage('');
    setIsTyping(true);

    try {
      const response = await fetch('http://localhost:8000/api/v1/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message })
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();
      setIsTyping(false);
      setMessages(prev => [...prev, { text: data.response, sender: 'bot' }]);
    } catch (error) {
      console.error('Chat error:', error);
      setIsTyping(false);
      setMessages(prev => [...prev, { 
        text: 'Sorry, I encountered an error. Please make sure the backend server is running.', 
        sender: 'bot' 
      }]);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-600 to-purple-800">
      {/* Header */}
      <header className="bg-white/95 backdrop-blur-sm shadow-lg sticky top-0 z-50">
        <nav className="container mx-auto px-6 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center">
              <svg className="h-12 w-auto" viewBox="0 0 300 80" xmlns="http://www.w3.org/2000/svg">
                <rect width="300" height="80" fill="#3d3d3d"/>
                <text x="25" y="35" fontFamily="Arial, sans-serif" fontSize="28" fontWeight="bold" fill="white">LEXINGTON</text>
                <rect x="65" y="18" width="15" height="3" fill="#e67e22"/>
                <rect x="65" y="27" width="15" height="3" fill="#e67e22"/>
                <rect x="65" y="36" width="15" height="3" fill="#e67e22"/>
                <text x="95" y="60" fontFamily="Arial, sans-serif" fontSize="20" fontWeight="normal" fill="white" letterSpacing="8">MEDICAL</text>
              </svg>
            </div>
            <ul className="hidden md:flex space-x-8">
              <li><a href="#home" className="text-gray-700 hover:text-purple-600 font-medium transition-colors">Home</a></li>
              <li><a href="#features" className="text-gray-700 hover:text-purple-600 font-medium transition-colors">Services</a></li>
              <li><a href="#about" className="text-gray-700 hover:text-purple-600 font-medium transition-colors">About</a></li>
              <li><a href="#contact" className="text-gray-700 hover:text-purple-600 font-medium transition-colors">Contact</a></li>
            </ul>
          </div>
        </nav>
      </header>

      {/* Hero Section */}
      <section id="home" className="text-center py-24 text-white">
        <div className="container mx-auto px-6">
          <h1 className="text-5xl md:text-6xl font-bold mb-4 drop-shadow-lg">Welcome to Lexington Medical</h1>
          <p className="text-xl md:text-2xl mb-8 opacity-95">Excellence in Healthcare Solutions with AI-Powered Assistance</p>
          <Button 
            onClick={() => setIsChatOpen(true)}
            size="lg"
            className="bg-white text-purple-600 hover:bg-gray-100 shadow-xl text-lg px-8 py-6 rounded-full"
          >
            Chat with MedAI Assistant
          </Button>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="bg-white py-20">
        <div className="container mx-auto px-6">
          <h2 className="text-4xl font-bold text-center mb-12 text-gray-900">Our Services</h2>
          
          {/* PDF RAG Info Banner */}
          <div className="max-w-4xl mx-auto mb-12">
            <Alert className="bg-gradient-to-r from-purple-50 to-indigo-50 border-purple-200">
              <BookOpen className="h-5 w-5 text-purple-600" />
              <AlertDescription className="text-gray-700">
                <strong className="text-purple-700">AI-Powered Document Search:</strong> Upload research papers, clinical guidelines, and policies to enable intelligent document search.
                Ask questions like "What does the research say about CAR-T therapy?" and get answers with source citations.
              </AlertDescription>
            </Alert>
          </div>

          {/* Document Library Section */}
          <div className="max-w-6xl mx-auto mb-12">
            <Collapsible open={isDocLibraryOpen} onOpenChange={setIsDocLibraryOpen}>
              <CollapsibleTrigger asChild>
                <Button
                  variant="outline"
                  className="w-full flex items-center justify-between p-6 h-auto hover:bg-purple-50 border-2 border-purple-200"
                >
                  <div className="flex items-center gap-3">
                    <BookOpen className="h-6 w-6 text-purple-600" />
                    <div className="text-left">
                      <h3 className="text-xl font-bold text-gray-900">Document Library</h3>
                      <p className="text-sm text-gray-600">Manage your research papers, policies, and clinical documents</p>
                    </div>
                  </div>
                  {isDocLibraryOpen ? (
                    <ChevronUp className="h-5 w-5 text-purple-600" />
                  ) : (
                    <ChevronDown className="h-5 w-5 text-purple-600" />
                  )}
                </Button>
              </CollapsibleTrigger>
              <CollapsibleContent className="mt-4">
                <PDFManager />
              </CollapsibleContent>
            </Collapsible>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <Card className="p-8 bg-gradient-to-br from-purple-600 to-purple-800 text-white hover:scale-105 transition-transform">
              <div className="text-5xl mb-4">🏥</div>
              <h3 className="text-2xl font-bold mb-4">Advanced Healthcare</h3>
              <p className="opacity-95">State-of-the-art medical facilities and cutting-edge technology to provide the best care for our patients.</p>
            </Card>
            <Card className="p-8 bg-gradient-to-br from-purple-600 to-purple-800 text-white hover:scale-105 transition-transform">
              <div className="text-5xl mb-4">🤖</div>
              <h3 className="text-2xl font-bold mb-4">AI-Powered Insights</h3>
              <p className="opacity-95">Our MedAI Assistant provides instant access to healthcare data, patient insights, organizational information, and document search.</p>
            </Card>
            <Card className="p-8 bg-gradient-to-br from-purple-600 to-purple-800 text-white hover:scale-105 transition-transform">
              <div className="text-5xl mb-4">💊</div>
              <h3 className="text-2xl font-bold mb-4">Comprehensive Care</h3>
              <p className="opacity-95">From preventive care to specialized treatments, we offer a full range of medical services.</p>
            </Card>
          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="bg-gray-50 py-20">
        <div className="container mx-auto px-6">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-4xl font-bold mb-6 text-gray-900">About Lexington Medical</h2>
              <p className="text-lg text-gray-700 mb-4">Lexington Medical is committed to providing exceptional healthcare services with a focus on patient-centered care and innovative medical solutions.</p>
              <p className="text-lg text-gray-700 mb-4">With years of experience in the healthcare industry, we have built a reputation for excellence, compassion, and cutting-edge medical technology.</p>
              <p className="text-lg text-gray-700">Our mission is to improve the health and well-being of our community through accessible, high-quality healthcare services powered by AI technology.</p>
            </div>
            <div className="bg-gradient-to-br from-purple-600 to-purple-800 h-96 rounded-2xl flex items-center justify-center text-white text-8xl">
              🏥
            </div>
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section id="contact" className="bg-white py-20">
        <div className="container mx-auto px-6">
          <h2 className="text-4xl font-bold text-center mb-12 text-gray-900">Contact Us</h2>
          <form onSubmit={handleContactSubmit} className="max-w-2xl mx-auto space-y-6">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">Name</label>
              <Input id="name" name="name" required className="w-full" />
            </div>
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">Email</label>
              <Input id="email" name="email" type="email" required className="w-full" />
            </div>
            <div>
              <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">Phone</label>
              <Input id="phone" name="phone" type="tel" className="w-full" />
            </div>
            <div>
              <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-2">Message</label>
              <Textarea id="message" name="message" required className="w-full min-h-[150px]" />
            </div>
            <Button type="submit" className="w-full bg-gradient-to-r from-purple-600 to-purple-800 hover:from-purple-700 hover:to-purple-900 text-white py-6 text-lg">
              Send Message
            </Button>
          </form>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-12">
        <div className="container mx-auto px-6">
          <div className="grid md:grid-cols-3 gap-8 mb-8">
            <div>
              <h3 className="text-xl font-bold mb-4 text-purple-400">Lexington Medical</h3>
              <p className="text-gray-300">Excellence in Healthcare Solutions</p>
              <p className="text-gray-300">Powered by MedAI Technology</p>
            </div>
            <div>
              <h3 className="text-xl font-bold mb-4 text-purple-400">Quick Links</h3>
              <div className="space-y-2">
                <a href="#home" className="block text-gray-300 hover:text-white transition-colors">Home</a>
                <a href="#features" className="block text-gray-300 hover:text-white transition-colors">Services</a>
                <a href="#about" className="block text-gray-300 hover:text-white transition-colors">About</a>
                <a href="#contact" className="block text-gray-300 hover:text-white transition-colors">Contact</a>
              </div>
            </div>
            <div>
              <h3 className="text-xl font-bold mb-4 text-purple-400">Contact Info</h3>
              <p className="text-gray-300">📍 123 Medical Center Drive</p>
              <p className="text-gray-300">📞 (555) 123-4567</p>
              <p className="text-gray-300">✉️ info@medaiagent.org</p>
            </div>
          </div>
          <div className="border-t border-gray-700 pt-8 text-center text-gray-400">
            <p>&copy; 2026 Lexington Medical | MedAIAgent.org. All rights reserved.</p>
          </div>
        </div>
      </footer>

      {/* Chat Widget */}
      <div className="fixed bottom-5 right-5 z-50">
        {!isChatOpen && (
          <Button
            onClick={() => setIsChatOpen(true)}
            size="lg"
            className="rounded-full w-16 h-16 bg-gradient-to-br from-purple-600 to-purple-800 hover:from-purple-700 hover:to-purple-900 shadow-2xl"
          >
            <MessageCircle className="w-8 h-8" />
          </Button>
        )}

        {isChatOpen && (
          <Card className="w-[400px] h-[600px] flex flex-col shadow-2xl">
            <div className="bg-gradient-to-r from-purple-600 to-purple-800 text-white p-4 rounded-t-lg flex justify-between items-center">
              <h3 className="text-lg font-bold">🤖 MedAI Assistant</h3>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsChatOpen(false)}
                className="text-white hover:bg-white/20"
              >
                <X className="w-5 h-5" />
              </Button>
            </div>

            <div className="flex-1 overflow-y-auto p-4 bg-gray-50 space-y-4">
              {messages.map((msg, idx) => (
                <div key={idx} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[70%] p-3 rounded-2xl whitespace-pre-line ${
                    msg.sender === 'user' 
                      ? 'bg-gradient-to-br from-purple-600 to-purple-800 text-white rounded-br-sm' 
                      : 'bg-white text-gray-900 rounded-bl-sm shadow'
                  }`}>
                    {msg.text}
                  </div>
                </div>
              ))}
              {isTyping && (
                <div className="flex justify-start">
                  <div className="bg-white p-3 rounded-2xl rounded-bl-sm shadow">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-purple-600 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                      <div className="w-2 h-2 bg-purple-600 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                      <div className="w-2 h-2 bg-purple-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            <form onSubmit={handleChatSubmit} className="p-4 bg-white border-t flex gap-2">
              <Input
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Type your message..."
                className="flex-1"
              />
              <Button type="submit" size="icon" className="bg-gradient-to-br from-purple-600 to-purple-800 hover:from-purple-700 hover:to-purple-900">
                <Send className="w-4 h-4" />
              </Button>
            </form>
          </Card>
        )}
      </div>
    </div>
  );
};

export default MedAIAgent;