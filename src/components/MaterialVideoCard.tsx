
import React from 'react';
import { MaterialCard } from './MaterialCard';
import { MaterialButton } from './MaterialButton';
import { MaterialTag } from './MaterialTag';
import { Play, Twitter, Linkedin, Instagram, Check } from 'lucide-react';

type MaterialVideoCardProps = {
  idea: {
    id: string;
    title: string;
    description: string;
    videoUrl?: string;
    imageUrl?: string;
    platforms?: {
      linkedin?: string;
      twitter?: string;
      instagram?: string;
    };
    tags: string[];
    themes: string[];
    selected?: boolean;
  };
  onSelect?: (id: string) => void;
  showVideo?: boolean;
};

const MaterialVideoCard: React.FC<MaterialVideoCardProps> = ({
  idea,
  onSelect,
  showVideo = false
}) => {
  const handleShare = (platform: 'twitter' | 'linkedin' | 'instagram') => {
    // In a real implementation, this would open a share dialog for the specified platform
    alert(`Sharing to ${platform}...`);
  };

  return (
    <MaterialCard
      className={cn(
        'w-full overflow-hidden transition-all duration-300',
        idea.selected && 'ring-2 ring-material-primary'
      )}
      elevation={idea.selected ? 3 : 1}
      interactive
    >
      <div className="aspect-video bg-gray-100 relative">
        {showVideo && idea.videoUrl ? (
          <video 
            className="w-full h-full object-cover"
            src={idea.videoUrl}
            poster={idea.imageUrl}
            controls
          />
        ) : (
          <>
            <img 
              src={idea.imageUrl || "https://via.placeholder.com/400x225?text=AI+Generated+Video"} 
              alt={idea.title} 
              className="w-full h-full object-cover"
            />
            {idea.selected && (
              <div className="absolute top-2 right-2 bg-material-primary rounded-full w-6 h-6 flex items-center justify-center">
                <Check size={16} className="text-white" />
              </div>
            )}
          </>
        )}
        
        {!showVideo && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/20">
            <button 
              className="rounded-full bg-white/90 p-3 transform transition-transform duration-200 hover:scale-110"
              onClick={() => onSelect && onSelect(idea.id)}
            >
              {idea.selected ? (
                <Check size={24} className="text-material-primary" />
              ) : (
                <Play size={24} className="text-material-primary" />
              )}
            </button>
          </div>
        )}
      </div>
      
      <div className="p-4">
        <h3 className="text-lg font-medium mb-2">{idea.title}</h3>
        <p className="text-muted-foreground text-sm mb-4">{idea.description}</p>
        
        <div className="space-x-1 mb-4">
          {idea.tags.map(tag => (
            <MaterialTag key={tag} label={tag} />
          ))}
        </div>
        
        {showVideo && (
          <div className="flex flex-wrap gap-2 mt-4">
            <MaterialButton
              variant="outline"
              className="flex items-center gap-2"
              onClick={() => handleShare('twitter')}
            >
              <Twitter size={16} />
              <span>X</span>
            </MaterialButton>
            <MaterialButton
              variant="outline"
              className="flex items-center gap-2"
              onClick={() => handleShare('linkedin')}
            >
              <Linkedin size={16} />
              <span>LinkedIn</span>
            </MaterialButton>
            <MaterialButton
              variant="outline"
              className="flex items-center gap-2"
              onClick={() => handleShare('instagram')}
            >
              <Instagram size={16} />
              <span>Instagram</span>
            </MaterialButton>
          </div>
        )}
      </div>
    </MaterialCard>
  );
};

export { MaterialVideoCard };
