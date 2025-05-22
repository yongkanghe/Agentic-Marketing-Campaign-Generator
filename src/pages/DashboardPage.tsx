
import React from 'react';
import { Link } from 'react-router-dom';
import { useMarketingContext } from '@/contexts/MarketingContext';
import { Plus, FileText, Calendar } from 'lucide-react';
import { MaterialCard } from '@/components/MaterialCard';
import { MaterialButton } from '@/components/MaterialButton';
import { MaterialAppBar } from '@/components/MaterialAppBar';

const DashboardPage: React.FC = () => {
  const { campaigns, loadCampaign } = useMarketingContext();

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <MaterialAppBar title="MarketVeo AI" />
      
      <div className="container py-8 flex-grow">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-medium">Your Marketing Campaigns</h1>
          <MaterialButton 
            variant="primary"
            className="flex items-center gap-2"
            asChild
          >
            <Link to="/new">
              <Plus size={18} />
              <span>New Campaign</span>
            </Link>
          </MaterialButton>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Link to="/new">
            <MaterialCard 
              className="h-64 flex flex-col justify-center items-center border-2 border-dashed border-border hover:border-primary/50 cursor-pointer"
              elevation={0}
              interactive
            >
              <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mb-4">
                <Plus size={32} className="text-muted-foreground" />
              </div>
              <h3 className="text-lg font-medium">Create New Campaign</h3>
              <p className="text-sm text-muted-foreground">Start creating a new marketing campaign</p>
            </MaterialCard>
          </Link>
          
          {campaigns.map((campaign) => (
            <Link
              key={campaign.id}
              to={`/ideation`}
              onClick={() => loadCampaign(campaign.id)}
            >
              <MaterialCard 
                className="h-64 flex flex-col overflow-hidden cursor-pointer" 
                elevation={1}
                interactive
              >
                <div className="h-32 bg-material-primary/10 p-4 flex items-center justify-center">
                  <FileText size={48} className="text-material-primary" />
                </div>
                <div className="p-4 flex-grow">
                  <h3 className="text-lg font-medium mb-1">{campaign.name}</h3>
                  <p className="text-sm text-muted-foreground line-clamp-2 mb-2">
                    {campaign.objective}
                  </p>
                  <div className="flex items-center text-xs text-muted-foreground">
                    <Calendar size={14} className="mr-1" />
                    {new Date(campaign.createdAt).toLocaleDateString()}
                  </div>
                </div>
              </MaterialCard>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
