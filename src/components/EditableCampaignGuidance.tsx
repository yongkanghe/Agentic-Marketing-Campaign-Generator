/**
 * FILENAME: EditableCampaignGuidance.tsx
 * DESCRIPTION/PURPOSE: Editable campaign guidance component with form fields and chat integration
 * Author: JP + 2025-06-16
 */

import React, { useState } from 'react';
import { Edit3, MessageCircle, Palette, Save, X, Eye, EyeOff } from 'lucide-react';
import { CampaignGuidanceChat } from './CampaignGuidanceChat';
import { toast } from 'sonner';

interface CampaignGuidance {
  creative_direction?: string;
  target_context?: string;
  visual_style?: {
    photography_style?: string;
    color_palette?: string[];
    lighting?: string;
    composition?: string;
    mood?: string;
  };
  content_themes?: {
    primary_themes?: string[];
    visual_metaphors?: string[];
    emotional_triggers?: string[];
    call_to_action_style?: string;
  };
}

interface EditableCampaignGuidanceProps {
  campaignId: string;
  guidance: CampaignGuidance;
  onUpdate: (updatedGuidance: CampaignGuidance) => void;
}

export const EditableCampaignGuidance: React.FC<EditableCampaignGuidanceProps> = ({
  campaignId,
  guidance,
  onUpdate
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [isExpanded, setIsExpanded] = useState(true);
  const [editedGuidance, setEditedGuidance] = useState<CampaignGuidance>(guidance);

  const handleSave = async () => {
    try {
      const response = await fetch(`/api/v1/campaigns/${campaignId}/guidance`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editedGuidance)
      });

      if (!response.ok) throw new Error('Failed to update guidance');

      const data = await response.json();
      
      if (data.success) {
        onUpdate(editedGuidance);
        setIsEditing(false);
        toast.success('Campaign guidance updated successfully!');
      }
    } catch (error) {
      console.error('Update error:', error);
      toast.error('Failed to update campaign guidance.');
    }
  };

  const handleCancel = () => {
    setEditedGuidance(guidance);
    setIsEditing(false);
  };

  const updateField = (path: string, value: any) => {
    const keys = path.split('.');
    const updated = { ...editedGuidance };
    
    let current: any = updated;
    for (let i = 0; i < keys.length - 1; i++) {
      if (!current[keys[i]]) current[keys[i]] = {};
      current = current[keys[i]];
    }
    current[keys[keys.length - 1]] = value;
    
    setEditedGuidance(updated);
  };

  const getFieldValue = (path: string): any => {
    const keys = path.split('.');
    let current: any = editedGuidance;
    
    for (const key of keys) {
      if (!current || !current[key]) return '';
      current = current[key];
    }
    
    return current;
  };

  const renderEditableField = (label: string, path: string, type: 'text' | 'textarea' | 'array' = 'text') => {
    const value = getFieldValue(path);
    
    if (!isEditing) {
      if (type === 'array' && Array.isArray(value)) {
        return (
          <div className="mb-3">
            <span className="text-xs font-medium text-gray-400">{label}:</span>
            <div className="flex flex-wrap gap-1 mt-1">
              {value.map((item, index) => (
                <span key={index} className="text-xs bg-purple-500/20 text-purple-400 px-2 py-1 rounded-full">
                  {item}
                </span>
              ))}
            </div>
          </div>
        );
      }
      
      return (
        <div className="mb-3">
          <span className="text-xs font-medium text-gray-400">{label}:</span>
          <p className="text-sm text-gray-200 mt-1">{value || 'Not specified'}</p>
        </div>
      );
    }

    if (type === 'textarea') {
      return (
        <div className="mb-3">
          <label className="text-xs font-medium text-gray-400 block mb-1">{label}:</label>
          <textarea
            value={value || ''}
            onChange={(e) => updateField(path, e.target.value)}
            className="w-full bg-gray-800 border border-gray-600 rounded px-3 py-2 text-sm text-white resize-none focus:outline-none focus:border-purple-400"
            rows={3}
          />
        </div>
      );
    }

    if (type === 'array') {
      const arrayValue = Array.isArray(value) ? value.join(', ') : '';
      return (
        <div className="mb-3">
          <label className="text-xs font-medium text-gray-400 block mb-1">{label} (comma-separated):</label>
          <input
            type="text"
            value={arrayValue}
            onChange={(e) => updateField(path, e.target.value.split(',').map(s => s.trim()).filter(s => s))}
            className="w-full bg-gray-800 border border-gray-600 rounded px-3 py-2 text-sm text-white focus:outline-none focus:border-purple-400"
          />
        </div>
      );
    }

    return (
      <div className="mb-3">
        <label className="text-xs font-medium text-gray-400 block mb-1">{label}:</label>
        <input
          type="text"
          value={value || ''}
          onChange={(e) => updateField(path, e.target.value)}
          className="w-full bg-gray-800 border border-gray-600 rounded px-3 py-2 text-sm text-white focus:outline-none focus:border-purple-400"
        />
      </div>
    );
  };

  return (
    <>
      <div className="bg-gradient-to-br from-purple-500/10 to-blue-500/10 border border-purple-400/20 rounded-lg p-6 mb-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <Palette className="text-purple-400" size={20} />
            <h4 className="text-lg font-semibold text-white">Campaign Creative Guidance</h4>
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="text-gray-400 hover:text-white transition-colors"
            >
              {isExpanded ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
            
            <button
              onClick={() => setIsChatOpen(true)}
              className="flex items-center gap-2 bg-purple-500/20 text-purple-400 px-3 py-1 rounded-lg hover:bg-purple-500/30 transition-colors text-sm"
            >
              <MessageCircle size={16} />
              Chat to Refine
            </button>
            
            {!isEditing ? (
              <button
                onClick={() => setIsEditing(true)}
                className="flex items-center gap-2 bg-blue-500/20 text-blue-400 px-3 py-1 rounded-lg hover:bg-blue-500/30 transition-colors text-sm"
              >
                <Edit3 size={16} />
                Edit
              </button>
            ) : (
              <div className="flex gap-2">
                <button
                  onClick={handleSave}
                  className="flex items-center gap-2 bg-green-500/20 text-green-400 px-3 py-1 rounded-lg hover:bg-green-500/30 transition-colors text-sm"
                >
                  <Save size={16} />
                  Save
                </button>
                <button
                  onClick={handleCancel}
                  className="flex items-center gap-2 bg-red-500/20 text-red-400 px-3 py-1 rounded-lg hover:bg-red-500/30 transition-colors text-sm"
                >
                  <X size={16} />
                  Cancel
                </button>
              </div>
            )}
          </div>
        </div>

        {isExpanded && (
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h5 className="text-sm font-semibold text-white mb-3">Creative Direction</h5>
              {renderEditableField('Creative Vision', 'creative_direction', 'textarea')}
              {renderEditableField('Target Context', 'target_context', 'textarea')}
              
              <h5 className="text-sm font-semibold text-white mb-3 mt-4">Visual Style</h5>
              {renderEditableField('Photography Style', 'visual_style.photography_style')}
              {renderEditableField('Color Palette', 'visual_style.color_palette', 'array')}
              {renderEditableField('Lighting', 'visual_style.lighting')}
              {renderEditableField('Mood', 'visual_style.mood')}
            </div>
            
            <div>
              <h5 className="text-sm font-semibold text-white mb-3">Content Themes</h5>
              {renderEditableField('Primary Themes', 'content_themes.primary_themes', 'array')}
              {renderEditableField('Visual Metaphors', 'content_themes.visual_metaphors', 'array')}
              {renderEditableField('Emotional Triggers', 'content_themes.emotional_triggers', 'array')}
              {renderEditableField('CTA Style', 'content_themes.call_to_action_style')}
            </div>
          </div>
        )}
      </div>

      <CampaignGuidanceChat
        campaignId={campaignId}
        onGuidanceUpdate={onUpdate}
        isOpen={isChatOpen}
        onClose={() => setIsChatOpen(false)}
      />
    </>
  );
}; 