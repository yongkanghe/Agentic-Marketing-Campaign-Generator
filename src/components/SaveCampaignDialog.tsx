/**
 * FILENAME: SaveCampaignDialog.tsx
 * DESCRIPTION/PURPOSE: Dialog component for saving campaign progress with a custom name
 * Author: JP + 2024-12-19
 */

import React, { useState } from 'react';
import { MaterialCard } from './MaterialCard';
import { MaterialButton } from './MaterialButton';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Save, Trash2, Calendar, FileText } from 'lucide-react';
import { useMarketingContext } from '../contexts/MarketingContext';
import { toast } from 'sonner';

interface SaveCampaignDialogProps {
  open: boolean;
  onClose: () => void;
}

const SaveCampaignDialog: React.FC<SaveCampaignDialogProps> = ({ open, onClose }) => {
  const { saveCampaign, loadCampaign, getSavedCampaigns, deleteSavedCampaign } = useMarketingContext();
  const [campaignName, setCampaignName] = useState('');
  const [saving, setSaving] = useState(false);
  const [savedCampaigns, setSavedCampaigns] = useState(getSavedCampaigns());

  const handleSave = async () => {
    if (!campaignName.trim()) {
      toast.error('Please enter a campaign name');
      return;
    }
    
    setSaving(true);
    try {
      await saveCampaign(campaignName.trim());
      setCampaignName('');
      setSavedCampaigns(getSavedCampaigns());
      toast.success('Campaign saved successfully!');
    } catch (error) {
      console.error('Error saving campaign:', error);
      toast.error('Failed to save campaign');
    } finally {
      setSaving(false);
    }
  };

  const handleLoad = async (campaignId: string) => {
    try {
      await loadCampaign(campaignId);
      toast.success('Campaign loaded successfully!');
      onClose();
    } catch (error) {
      console.error('Error loading campaign:', error);
      toast.error('Failed to load campaign');
    }
  };

  const handleDelete = (campaignId: string) => {
    deleteSavedCampaign(campaignId);
    setSavedCampaigns(getSavedCampaigns());
    toast.success('Campaign deleted');
  };

  const formatDate = (date: Date) => {
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <MaterialCard className="w-full max-w-2xl max-h-[80vh] overflow-y-auto m-4">
        <div className="p-6">
          <div className="flex items-center gap-2 mb-6">
            <Save className="text-blue-600" size={24} />
            <h2 className="text-xl font-semibold">Save & Load Campaigns</h2>
          </div>
          
          {/* Save Current Campaign */}
          <div className="mb-8">
            <h3 className="text-lg font-medium mb-4">Save Current Campaign</h3>
            <div className="flex gap-3">
              <div className="flex-1">
                <Label htmlFor="campaign-name">Campaign Name</Label>
                <Input
                  id="campaign-name"
                  value={campaignName}
                  onChange={(e) => setCampaignName(e.target.value)}
                  placeholder="Enter a name for your campaign..."
                  className="mt-1"
                />
              </div>
              <MaterialButton
                onClick={handleSave}
                disabled={!campaignName.trim() || saving}
                className="self-end flex items-center gap-2"
              >
                <Save size={16} />
                {saving ? 'Saving...' : 'Save'}
              </MaterialButton>
            </div>
          </div>

          {/* Saved Campaigns List */}
          {savedCampaigns.length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-medium mb-4">
                Saved Campaigns ({savedCampaigns.length})
              </h3>
              <div className="space-y-3">
                {savedCampaigns.map((campaign) => (
                  <MaterialCard
                    key={campaign.id}
                    className="p-4 hover:bg-gray-50 cursor-pointer transition-colors"
                    onClick={() => handleLoad(campaign.id)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <h4 className="font-medium text-lg">{campaign.name}</h4>
                          <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                            {campaign.campaignData.campaignType}
                          </span>
                        </div>
                        <div className="text-sm text-gray-600 space-y-1">
                          <div className="flex items-center gap-1">
                            <Calendar size={14} />
                            Created: {formatDate(campaign.createdAt)}
                          </div>
                          <div className="flex items-center gap-1">
                            <Calendar size={14} />
                            Modified: {formatDate(campaign.lastModified)}
                          </div>
                          {campaign.campaignData.businessDescription && (
                            <div className="flex items-start gap-1">
                              <FileText size={14} className="mt-0.5" />
                              <span className="line-clamp-2">
                                {campaign.campaignData.businessDescription.substring(0, 150)}...
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                      <MaterialButton
                        variant="outline"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete(campaign.id);
                        }}
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                      >
                        <Trash2 size={16} />
                      </MaterialButton>
                    </div>
                  </MaterialCard>
                ))}
              </div>
            </div>
          )}

          {savedCampaigns.length === 0 && (
            <div className="text-center py-8">
              <FileText size={48} className="mx-auto text-gray-400 mb-4" />
              <p className="text-gray-600">
                No saved campaigns yet. Save your current progress to continue later!
              </p>
            </div>
          )}

          {/* Actions */}
          <div className="flex justify-end pt-4 border-t">
            <MaterialButton variant="outline" onClick={onClose}>
              Close
            </MaterialButton>
          </div>
        </div>
      </MaterialCard>
    </div>
  );
};

export default SaveCampaignDialog; 