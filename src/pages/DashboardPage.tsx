/**
 * FILENAME: DashboardPage.tsx
 * DESCRIPTION/PURPOSE: Dashboard page for viewing and managing marketing campaigns with VVL design system
 * Author: JP + 2025-06-15
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { useMarketingContext } from '@/contexts/MarketingContext';
import { Plus, FileText, Calendar, ArrowRight } from 'lucide-react';
import Footer from '@/components/Footer';

const DashboardPage: React.FC = () => {
  const { campaigns, loadCampaign } = useMarketingContext();

  return (
    <div className="min-h-screen vvl-gradient-bg flex flex-col">
      {/* Header */}
      <header className="vvl-header-blur">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">VVL</span>
              </div>
              <h1 className="text-xl font-bold vvl-text-primary">Video Venture Launch</h1>
            </div>
            <nav className="flex items-center space-x-4">
              <Link to="/about" className="vvl-button-secondary text-sm">
                About
              </Link>
              <Link to="/new-campaign" className="vvl-button-primary text-sm flex items-center gap-2">
                <Plus size={16} />
                New Campaign
              </Link>
            </nav>
          </div>
        </div>
      </header>
      
      <div className="container mx-auto px-6 py-12 flex-grow">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold vvl-text-primary mb-4">Your Marketing Campaigns</h2>
            <p className="text-lg vvl-text-secondary">Manage and track your AI-powered marketing campaigns</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Create New Campaign Card */}
            <Link to="/new-campaign" className="group">
              <div className="vvl-card vvl-card-hover h-64 flex flex-col justify-center items-center border-2 border-dashed border-white/30 hover:border-blue-400/50 cursor-pointer p-6">
                <div className="w-16 h-16 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-200">
                  <Plus size={32} className="text-white" />
                </div>
                <h3 className="text-lg font-semibold vvl-text-primary mb-2">Create New Campaign</h3>
                <p className="text-sm vvl-text-secondary text-center">Start creating a new AI-powered marketing campaign</p>
                <div className="mt-4 flex items-center vvl-text-accent text-sm font-medium">
                  Get Started <ArrowRight size={16} className="ml-1 group-hover:translate-x-1 transition-transform duration-200" />
                </div>
              </div>
            </Link>
            
            {/* Existing Campaigns */}
            {campaigns.map((campaign) => (
              <Link
                key={campaign.id}
                to={`/ideation`}
                onClick={() => loadCampaign(campaign.id)}
                className="group"
              >
                <div className="vvl-card vvl-card-hover h-64 flex flex-col overflow-hidden cursor-pointer">
                  <div className="h-32 bg-gradient-to-br from-blue-500/20 to-purple-600/20 p-6 flex items-center justify-center">
                    <FileText size={48} className="text-blue-400 group-hover:scale-110 transition-transform duration-200" />
                  </div>
                  <div className="p-6 flex-grow">
                    <h3 className="text-lg font-semibold vvl-text-primary mb-2 line-clamp-1">{campaign.name}</h3>
                    <p className="text-sm vvl-text-secondary line-clamp-2 mb-4">
                      {campaign.objective}
                    </p>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center text-xs vvl-text-secondary">
                        <Calendar size={14} className="mr-1" />
                        {new Date(campaign.createdAt).toLocaleDateString()}
                      </div>
                      <div className="flex items-center vvl-text-accent text-sm font-medium">
                        Open <ArrowRight size={14} className="ml-1 group-hover:translate-x-1 transition-transform duration-200" />
                      </div>
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>

          {campaigns.length === 0 && (
            <div className="text-center py-16">
              <div className="w-24 h-24 mx-auto mb-6 rounded-full bg-gradient-to-r from-blue-500/20 to-purple-600/20 flex items-center justify-center">
                <FileText size={48} className="text-blue-400" />
              </div>
              <h3 className="text-xl font-semibold vvl-text-primary mb-2">No campaigns yet</h3>
              <p className="vvl-text-secondary mb-6">Create your first AI-powered marketing campaign to get started</p>
              <Link to="/new-campaign" className="vvl-button-primary inline-flex items-center gap-2">
                <Plus size={18} />
                Create Your First Campaign
              </Link>
            </div>
          )}
        </div>
      </div>
      
      <Footer />
    </div>
  );
};

export default DashboardPage;
