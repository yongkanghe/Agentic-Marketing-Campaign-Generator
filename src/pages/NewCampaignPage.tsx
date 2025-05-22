
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMarketingContext } from '@/contexts/MarketingContext';
import { MaterialCard } from '@/components/MaterialCard';
import { MaterialButton } from '@/components/MaterialButton';
import { MaterialAppBar } from '@/components/MaterialAppBar';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { ArrowLeft } from 'lucide-react';
import { toast } from 'sonner';

const NewCampaignPage: React.FC = () => {
  const navigate = useNavigate();
  const { createNewCampaign } = useMarketingContext();
  
  const [name, setName] = useState('');
  const [businessDescription, setBusinessDescription] = useState('');
  const [objective, setObjective] = useState('');
  const [exampleContent, setExampleContent] = useState('');
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!name || !businessDescription || !objective) {
      toast.error('Please fill in all required fields');
      return;
    }
    
    createNewCampaign({
      name,
      businessDescription,
      objective,
      exampleContent
    });
    
    toast.success('Campaign created! Now let\'s generate some ideas.');
    navigate('/ideation');
  };
  
  return (
    <div className="min-h-screen bg-background flex flex-col">
      <MaterialAppBar title="New Campaign">
        <MaterialButton 
          variant="text" 
          className="mr-2 flex items-center gap-1"
          onClick={() => navigate('/')}
        >
          <ArrowLeft size={16} />
          <span>Back</span>
        </MaterialButton>
      </MaterialAppBar>
      
      <div className="container py-8">
        <MaterialCard className="max-w-2xl mx-auto">
          <form onSubmit={handleSubmit} className="p-6">
            <h1 className="text-2xl font-medium mb-6">Create New Marketing Campaign</h1>
            
            <div className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="name">Campaign Name *</Label>
                <Input
                  id="name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="E.g., Summer Product Launch"
                  required
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="objective">Campaign Objective *</Label>
                <Input
                  id="objective"
                  value={objective}
                  onChange={(e) => setObjective(e.target.value)}
                  placeholder="E.g., Increase brand awareness, Drive sales, etc."
                  required
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="description">Business Description *</Label>
                <Textarea
                  id="description"
                  value={businessDescription}
                  onChange={(e) => setBusinessDescription(e.target.value)}
                  placeholder="Describe your business, products, services, and target audience..."
                  className="min-h-[120px]"
                  required
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="example">Example Content (Optional)</Label>
                <Textarea
                  id="example"
                  value={exampleContent}
                  onChange={(e) => setExampleContent(e.target.value)}
                  placeholder="Add any example content you'd like the AI to reference..."
                  className="min-h-[80px]"
                />
              </div>
            </div>
            
            <div className="mt-8 flex justify-end">
              <MaterialButton
                type="button"
                variant="outline" 
                className="mr-4"
                onClick={() => navigate('/')}
              >
                Cancel
              </MaterialButton>
              <MaterialButton type="submit">
                Next
              </MaterialButton>
            </div>
          </form>
        </MaterialCard>
      </div>
    </div>
  );
};

export default NewCampaignPage;
