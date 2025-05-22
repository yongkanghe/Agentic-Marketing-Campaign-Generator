
import React from 'react';
import { cn } from '@/lib/utils';
import { X } from 'lucide-react';

type MaterialTagProps = React.HTMLAttributes<HTMLDivElement> & {
  label: string;
  selected?: boolean;
  onDelete?: () => void;
  onClick?: () => void;
};

const MaterialTag = ({
  className,
  label,
  selected = false,
  onDelete,
  onClick,
  ...props
}: MaterialTagProps) => {
  return (
    <div
      className={cn(
        'inline-flex items-center px-3 py-1 rounded-full text-sm font-medium transition-colors cursor-pointer',
        selected
          ? 'bg-material-primary text-white'
          : 'bg-muted text-muted-foreground hover:bg-muted/80',
        onClick && 'cursor-pointer',
        className
      )}
      onClick={onClick}
      {...props}
    >
      <span>{label}</span>
      {onDelete && (
        <button
          type="button"
          className="ml-1 rounded-full p-0.5 hover:bg-white/20"
          onClick={(e) => {
            e.stopPropagation();
            onDelete();
          }}
        >
          <X size={14} />
        </button>
      )}
    </div>
  );
};

export { MaterialTag };
