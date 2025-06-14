/**
 * FILENAME: LandingPage.tsx
 * DESCRIPTION/PURPOSE: Professional SaaS landing page for Video Venture Launch - Agentic AI Marketing Campaign Manager
 * Author: JP + 2024-12-19
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { MaterialCard } from '@/components/MaterialCard';
import { MaterialButton } from '@/components/MaterialButton';
import { 
  Sparkles, 
  Zap, 
  Target, 
  Clock, 
  TrendingUp, 
  Users, 
  BarChart3, 
  Rocket,
  CheckCircle,
  ArrowRight,
  Play,
  Globe,
  MessageSquare,
  Video,
  Image as ImageIcon,
  Calendar,
  Bot
} from 'lucide-react';
import Footer from '@/components/Footer';

const LandingPage: React.FC = () => {
  const navigate = useNavigate();

  const features = [
    {
      icon: <Bot className="w-8 h-8" />,
      title: "AI-Powered Campaign Creation",
      description: "Advanced AI agents analyze your business context and generate targeted marketing campaigns in minutes, not hours."
    },
    {
      icon: <Globe className="w-8 h-8" />,
      title: "Multi-Platform Content Generation",
      description: "Create optimized content for LinkedIn, Twitter, Instagram, Facebook, and TikTok with platform-specific adaptations."
    },
    {
      icon: <Video className="w-8 h-8" />,
      title: "AI Video & Image Creation",
      description: "Generate professional videos with Google's Veo API and stunning images tailored to your brand and message."
    },
    {
      icon: <Calendar className="w-8 h-8" />,
      title: "Automated Scheduling",
      description: "Smart scheduling optimization ensures your content reaches audiences at peak engagement times across all platforms."
    },
    {
      icon: <BarChart3 className="w-8 h-8" />,
      title: "Performance Analytics",
      description: "Real-time monitoring and analytics help you track campaign performance and optimize for better results."
    },
    {
      icon: <Zap className="w-8 h-8" />,
      title: "Lightning Fast Deployment",
      description: "From business analysis to published content in under 10 minutes. Scale your marketing efforts instantly."
    }
  ];

  const benefits = [
    {
      icon: <Clock className="w-6 h-6 text-blue-500" />,
      title: "90% Time Savings",
      description: "Reduce campaign creation time from days to minutes"
    },
    {
      icon: <TrendingUp className="w-6 h-6 text-green-500" />,
      title: "3x Better Engagement",
      description: "AI-optimized content performs significantly better"
    },
    {
      icon: <Users className="w-6 h-6 text-purple-500" />,
      title: "Multi-Platform Reach",
      description: "Expand your audience across 5+ social platforms"
    },
    {
      icon: <Target className="w-6 h-6 text-orange-500" />,
      title: "Precision Targeting",
      description: "AI analyzes your audience for maximum impact"
    }
  ];

  const useCases = [
    {
      title: "Product Launches",
      description: "Generate buzz and drive sales with AI-crafted launch campaigns",
      icon: <Rocket className="w-12 h-12 text-blue-500" />
    },
    {
      title: "Brand Awareness",
      description: "Build consistent brand presence across all social platforms",
      icon: <Sparkles className="w-12 h-12 text-purple-500" />
    },
    {
      title: "Service Promotion",
      description: "Showcase your services with compelling, conversion-focused content",
      icon: <MessageSquare className="w-12 h-12 text-green-500" />
    },
    {
      title: "Event Marketing",
      description: "Drive attendance and engagement for your events and webinars",
      icon: <Calendar className="w-12 h-12 text-orange-500" />
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="relative z-10">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">Video Venture Launch</h1>
                <p className="text-xs text-gray-400">Agentic AI Marketing</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <button 
                className="vvl-button-secondary"
                onClick={() => navigate('/about')}
              >
                About
              </button>
              <button 
                className="vvl-button-secondary"
                onClick={() => navigate('/campaigns')}
              >
                View Campaigns
              </button>
              <button 
                className="vvl-button-primary"
                onClick={() => navigate('/new-campaign')}
              >
                Create Your Campaign
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative py-20 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-purple-600/10"></div>
        <div className="container mx-auto px-4 relative z-10">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 bg-blue-500/20 text-blue-300 px-4 py-2 rounded-full text-sm mb-8">
              <Sparkles className="w-4 h-4" />
              Powered by Google's ADK & Gemini AI
            </div>
            
            <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
              The Modern
              <span className="bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent"> AI Marketing </span>
              Platform
            </h1>
            
            <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto leading-relaxed">
              Transform your marketing workflow with AI agents that create, optimize, and publish 
              campaigns across all social platforms. Get your "Aha!" moment in under 60 seconds.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
              <button 
                className="vvl-button-primary text-lg px-8 py-4 flex items-center gap-2"
                onClick={() => navigate('/new-campaign')}
              >
                <Rocket className="w-5 h-5" />
                Create Your Campaign
              </button>
              
              <button 
                className="vvl-button-secondary text-lg px-8 py-4 flex items-center gap-2"
                onClick={() => navigate('/campaigns')}
              >
                <Play className="w-5 h-5" />
                View Demo
              </button>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-2xl mx-auto">
              {benefits.map((benefit, index) => (
                <div key={index} className="text-center">
                  <div className="flex justify-center mb-2">
                    {benefit.icon}
                  </div>
                  <div className="text-lg font-semibold text-white">{benefit.title}</div>
                  <div className="text-sm text-gray-400">{benefit.description}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-slate-800/50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">
              AI-Powered Marketing That Just Works
            </h2>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">
              Our agentic AI system handles every aspect of your marketing campaign, 
              from business analysis to content creation and automated publishing.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <MaterialCard key={index} className="p-6 bg-slate-700/50 border-slate-600 hover:bg-slate-700/70 transition-all duration-300">
                <div className="text-blue-400 mb-4">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold text-white mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-300 leading-relaxed">
                  {feature.description}
                </p>
              </MaterialCard>
            ))}
          </div>
        </div>
      </section>

      {/* Use Cases Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">
              Perfect for Every Marketing Need
            </h2>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">
              Whether you're launching a product, building brand awareness, or promoting services, 
              our AI adapts to your specific goals and industry.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {useCases.map((useCase, index) => (
              <MaterialCard key={index} className="p-6 bg-gradient-to-br from-slate-800 to-slate-700 border-slate-600 text-center hover:scale-105 transition-transform duration-300">
                <div className="flex justify-center mb-4">
                  {useCase.icon}
                </div>
                <h3 className="text-lg font-semibold text-white mb-3">
                  {useCase.title}
                </h3>
                <p className="text-gray-300 text-sm leading-relaxed">
                  {useCase.description}
                </p>
              </MaterialCard>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 bg-slate-800/50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">
              From Idea to Published in Minutes
            </h2>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">
              Our streamlined workflow gets you from concept to live campaigns faster than ever before.
            </p>
          </div>

          <div className="max-w-4xl mx-auto">
            <div className="grid md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl font-bold text-white">1</span>
                </div>
                <h3 className="text-xl font-semibold text-white mb-3">Analyze Your Business</h3>
                <p className="text-gray-300">
                  Upload your website, documents, or describe your business. Our AI extracts key insights and context.
                </p>
              </div>

              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-600 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl font-bold text-white">2</span>
                </div>
                <h3 className="text-xl font-semibold text-white mb-3">Generate Content</h3>
                <p className="text-gray-300">
                  AI creates optimized text, images, and videos for each platform, tailored to your brand and audience.
                </p>
              </div>

              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-r from-pink-500 to-orange-600 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl font-bold text-white">3</span>
                </div>
                <h3 className="text-xl font-semibold text-white mb-3">Schedule & Publish</h3>
                <p className="text-gray-300">
                  Automated scheduling ensures optimal posting times while you monitor performance in real-time.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-purple-700">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold text-white mb-4">
            Ready to Transform Your Marketing?
          </h2>
          <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
            Join the future of marketing with AI that understands your business and creates campaigns that convert.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <MaterialButton 
              size="lg"
              className="bg-white text-blue-600 hover:bg-gray-100 text-lg px-8 py-4 font-semibold"
              onClick={() => navigate('/new-campaign')}
            >
              <Rocket className="w-5 h-5 mr-2" />
              Create Your First Campaign
            </MaterialButton>
            
            <MaterialButton 
              variant="outline" 
              size="lg"
              className="text-white border-white/30 hover:border-white hover:bg-white/10 text-lg px-8 py-4"
              onClick={() => navigate('/campaigns')}
            >
              Explore Features
              <ArrowRight className="w-5 h-5 ml-2" />
            </MaterialButton>
          </div>

          <div className="mt-8 text-blue-100 text-sm">
            <div className="flex items-center justify-center gap-4">
              <div className="flex items-center gap-1">
                <CheckCircle className="w-4 h-4" />
                <span>No credit card required</span>
              </div>
              <div className="flex items-center gap-1">
                <CheckCircle className="w-4 h-4" />
                <span>MVP-grade functionality</span>
              </div>
              <div className="flex items-center gap-1">
                <CheckCircle className="w-4 h-4" />
                <span>Powered by Google AI</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default LandingPage; 