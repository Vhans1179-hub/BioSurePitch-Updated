import { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { MessageSquare, Building2, TrendingUp, Shield, Bot } from 'lucide-react';
import { ChatWidget } from '@/components/chat/ChatWidget';
import { cn } from '@/lib/utils';

const LexingtonLanding = () => {
  const [activeTab, setActiveTab] = useState('about');

  return (
    <div className="min-h-screen bg-white">
      {/* Black Navigation Bar */}
      <nav className="bg-gray-900 text-white">
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            {/* Lexington Medical Logo - Left */}
            <div className="flex items-center gap-2">
              <div className="leading-none">
                <div className="flex items-center gap-0">
                  <span className="text-lg font-bold text-white">L</span>
                  <div className="flex flex-col gap-[1.5px] mx-[1.5px]">
                    <div className="w-[11px] h-[2.5px] bg-orange-500 rounded-sm"></div>
                    <div className="w-[11px] h-[2.5px] bg-orange-500 rounded-sm"></div>
                    <div className="w-[11px] h-[2.5px] bg-orange-500 rounded-sm"></div>
                  </div>
                  <span className="text-lg font-bold text-white">XINGTON</span>
                </div>
                <div className="text-[9px] tracking-[0.2em] text-gray-300 font-light text-right">MEDICAL</div>
              </div>
            </div>
            
            {/* Navigation Tabs - Center */}
            <div className="flex items-center gap-8">
              <button
                onClick={() => setActiveTab('about')}
                className={cn(
                  "text-sm font-medium transition-colors hover:text-teal-400",
                  activeTab === 'about' ? 'text-teal-400' : 'text-white'
                )}
              >
                About
              </button>
              <button
                onClick={() => setActiveTab('sales')}
                className={cn(
                  "text-sm font-medium transition-colors hover:text-teal-400",
                  activeTab === 'sales' ? 'text-teal-400' : 'text-white'
                )}
              >
                Sales
              </button>
              <button
                onClick={() => setActiveTab('compliance')}
                className={cn(
                  "text-sm font-medium transition-colors hover:text-teal-400",
                  activeTab === 'compliance' ? 'text-teal-400' : 'text-white'
                )}
              >
                Compliance
              </button>
            </div>

            {/* MedAI Logo - Right */}
            <div className="flex items-center gap-1.5">
              <div className="w-7 h-7 bg-teal-500 rounded flex items-center justify-center flex-shrink-0">
                <svg viewBox="0 0 24 24" fill="none" className="w-4 h-4" stroke="white" strokeWidth="2">
                  <circle cx="12" cy="12" r="3" />
                  <path d="M12 2v4m0 12v4M2 12h4m12 0h4m-3.5-7.5l-2.8 2.8m-7.4 7.4l-2.8 2.8m14.2 0l-2.8-2.8m-7.4-7.4l-2.8-2.8" />
                </svg>
              </div>
              <div className="leading-none">
                <div className="text-sm font-bold text-white">
                  MED<span className="text-teal-500">AI</span>
                </div>
                <div className="text-[8px] tracking-[0.15em] text-gray-300 font-light">AGENT</div>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Purple Hero Banner - Compact */}
      <section className="bg-gradient-to-br from-slate-600 via-slate-700 to-slate-800 py-8 text-center text-white">
        <div className="container mx-auto px-4">
          <h1 className="text-3xl md:text-4xl font-bold mb-2 drop-shadow-lg">
            MedAI Agent: Intelligent Execution for Lexington Medical
          </h1>
          <p className="text-base md:text-lg opacity-95 max-w-3xl mx-auto">
            Mobilize your Sales Team with autonomous, real-time HCP profiling and automated regulatory clearance to accelerate sales cycles.
          </p>
        </div>
      </section>

      {/* Main Content - Tabs */}
      <section className="py-16 bg-gradient-to-br from-slate-600 via-slate-700 to-slate-800">
        <div className="container mx-auto px-4">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">

            {/* About Tab */}
            <TabsContent value="about" className="space-y-6">
              <Card className="bg-white/95 backdrop-blur-sm shadow-xl">
                <CardHeader>
                  <CardTitle className="text-3xl text-slate-700">About MedAI Agent</CardTitle>
                  <CardDescription className="text-lg">
                    Your intelligent healthcare sales and compliance assistant
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="text-gray-700 text-lg leading-relaxed">
                    MedAI Agent is an AI-powered platform designed specifically for Lexington Medical's sales and
                    compliance teams. We combine cutting-edge artificial intelligence with deep healthcare industry
                    knowledge to streamline your workflows, seamlessly integrated into your current technology stack.
                  </p>
                  <p className="text-gray-700 text-lg leading-relaxed">
                    Our intelligent assistant provides instant access to healthcare organization data,
                    contract information, and regulatory compliance guidance - all through a simple conversational interface.
                  </p>
                  <p className="text-gray-700 text-lg leading-relaxed">
                    Whether you're looking up HCO addresses, MedAI Agent is your trusted partner in Sales Enablement and Regulatory Compliance.
                  </p>
                </CardContent>
              </Card>

              <div className="grid md:grid-cols-3 gap-6">
                <Card className="bg-gradient-to-br from-teal-600 to-teal-700 text-white shadow-xl">
                  <CardHeader>
                    <div className="text-4xl mb-2">💬</div>
                    <CardTitle>Conversational AI</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="opacity-95">
                      Ask questions in natural language and get instant, accurate answers from our AI assistant.
                    </p>
                  </CardContent>
                </Card>

                <Card className="bg-gradient-to-br from-teal-600 to-teal-700 text-white shadow-xl">
                  <CardHeader>
                    <div className="text-4xl mb-2">📊</div>
                    <CardTitle>Real-Time Data</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="opacity-95">
                      HCP and affiliated HCO information and Research Publications
                    </p>
                  </CardContent>
                </Card>

                <Card className="bg-gradient-to-br from-teal-600 to-teal-700 text-white shadow-xl">
                  <CardHeader>
                    <div className="text-4xl mb-2">🛡️</div>
                    <CardTitle>Compliance Built-In</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="opacity-95">
                      HIPAA-compliant platform with built-in regulatory guidance and security features.
                    </p>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* Sales Tab */}
            <TabsContent value="sales" className="space-y-6">
              <Card className="bg-white/95 backdrop-blur-sm shadow-xl">
                <CardHeader>
                  <CardTitle className="text-3xl text-slate-700">Sales Solutions</CardTitle>
                  <CardDescription className="text-lg">
                    Empowering your sales team with data-driven insights
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="text-gray-700 text-lg leading-relaxed">
                    Our AI-powered sales platform helps healthcare organizations identify opportunities, 
                    track performance, and optimize their sales strategies.
                  </p>
                </CardContent>
              </Card>

              <div className="grid md:grid-cols-2 gap-6">
                <Card className="bg-white/95 backdrop-blur-sm shadow-xl">
                  <CardHeader>
                    <CardTitle className="text-slate-700">📊 Market Intelligence</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2 text-gray-700">
                      <li>• Real-time HCO performance tracking</li>
                      <li>• Competitive landscape insights</li>
                      <li>• Territory optimization</li>
                    </ul>
                  </CardContent>
                </Card>

                <Card className="bg-white/95 backdrop-blur-sm shadow-xl">
                  <CardHeader>
                    <CardTitle className="text-slate-700">🎯 Lead Generation</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2 text-gray-700">
                      <li>• Identify high-value prospects</li>
                      <li>• Contract renewal predictions</li>
                      <li>• Automated outreach recommendations</li>
                    </ul>
                  </CardContent>
                </Card>

                <Card className="bg-white/95 backdrop-blur-sm shadow-xl">
                  <CardHeader>
                    <CardTitle className="text-slate-700">💼 Sales Enablement</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2 text-gray-700">
                      <li>• AI-powered chat assistant</li>
                      <li>• Instant HCO address lookup</li>
                      <li>• Contract details on demand</li>
                      <li>• Performance dashboards</li>
                    </ul>
                  </CardContent>
                </Card>

                <Card className="bg-white/95 backdrop-blur-sm shadow-xl">
                  <CardHeader>
                    <CardTitle className="text-slate-700">📈 Analytics & Reporting</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2 text-gray-700">
                      <li>• Custom sales reports</li>
                      <li>• Pipeline visualization</li>
                      <li>• ROI tracking</li>
                      <li>• Forecasting models</li>
                    </ul>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* Compliance Tab */}
            <TabsContent value="compliance" className="space-y-6">
              <Card className="bg-white/95 backdrop-blur-sm shadow-xl">
                <CardHeader>
                  <CardTitle className="text-3xl text-slate-700">Compliance & Security</CardTitle>
                  <CardDescription className="text-lg">
                    Ensuring the highest standards of data protection and regulatory compliance
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="text-gray-700 text-lg leading-relaxed">
                    At Lexington Medical, we prioritize the security and privacy of healthcare data. 
                    Our platform is built with compliance at its core.
                  </p>
                </CardContent>
              </Card>

              <div className="grid md:grid-cols-2 gap-6">
                <Card className="bg-white/95 backdrop-blur-sm shadow-xl">
                  <CardHeader>
                    <CardTitle className="text-slate-700">🔒 HIPAA Compliance</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2 text-gray-700">
                      <li>• End-to-end encryption</li>
                      <li>• Secure data transmission</li>
                      <li>• Access control and audit logs</li>
                      <li>• Regular security assessments</li>
                      <li>• Business Associate Agreements (BAA)</li>
                    </ul>
                  </CardContent>
                </Card>

                <Card className="bg-white/95 backdrop-blur-sm shadow-xl">
                  <CardHeader>
                    <CardTitle className="text-slate-700">📋 Regulatory Standards</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2 text-gray-700">
                      <li>• FDA compliance for medical devices</li>
                      <li>• CMS data usage guidelines</li>
                      <li>• State healthcare regulations</li>
                      <li>• GDPR for international data</li>
                      <li>• SOC 2 Type II certified</li>
                    </ul>
                  </CardContent>
                </Card>

                <Card className="bg-white/95 backdrop-blur-sm shadow-xl">
                  <CardHeader>
                    <CardTitle className="text-slate-700">🛡️ Data Protection</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2 text-gray-700">
                      <li>• Multi-factor authentication</li>
                      <li>• Role-based access control</li>
                      <li>• Data anonymization</li>
                      <li>• Secure backup and recovery</li>
                      <li>• Incident response procedures</li>
                    </ul>
                  </CardContent>
                </Card>

                <Card className="bg-white/95 backdrop-blur-sm shadow-xl">
                  <CardHeader>
                    <CardTitle className="text-slate-700">✅ Certifications</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2 text-gray-700">
                      <li>• HITRUST CSF Certified</li>
                      <li>• ISO 27001 compliant</li>
                      <li>• PCI DSS for payment data</li>
                      <li>• Annual third-party audits</li>
                      <li>• Continuous monitoring</li>
                    </ul>
                  </CardContent>
                </Card>
              </div>

              <Card className="bg-gradient-to-br from-teal-600 to-teal-700 text-white shadow-xl">
                <CardHeader>
                  <CardTitle className="text-2xl">Our Commitment to Compliance</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-lg opacity-95 leading-relaxed">
                    We understand that healthcare data is sensitive and requires the highest level of protection. 
                    Our team continuously monitors regulatory changes and updates our systems to ensure ongoing 
                    compliance. We work closely with healthcare organizations to meet their specific compliance 
                    requirements and provide comprehensive documentation and support.
                  </p>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12 mt-20">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-3 gap-8">
            <div>
              <h3 className="text-xl font-bold mb-4 text-teal-400">Lexington Medical</h3>
              <p className="text-gray-400">Excellence in Healthcare Solutions</p>
              <p className="text-gray-400">Powered by MedAI Technology</p>
            </div>
            <div>
              <h3 className="text-xl font-bold mb-4 text-teal-400">Quick Links</h3>
              <ul className="space-y-2">
                <li><a href="#about" className="text-gray-400 hover:text-white transition">About</a></li>
                <li><a href="#sales" className="text-gray-400 hover:text-white transition">Sales</a></li>
                <li><a href="#compliance" className="text-gray-400 hover:text-white transition">Compliance</a></li>
              </ul>
            </div>
            <div>
              <h3 className="text-xl font-bold mb-4 text-teal-400">Contact Info</h3>
              <p className="text-gray-400">📍 123 Medical Center Drive</p>
              <p className="text-gray-400">📞 (555) 123-4567</p>
              <p className="text-gray-400">✉️ info@medaiagent.org</p>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2026 Lexington Medical | MedAIAgent.org. All rights reserved.</p>
          </div>
        </div>
      </footer>

      {/* Chat Widget */}
      <ChatWidget />
    </div>
  );
};

export default LexingtonLanding;