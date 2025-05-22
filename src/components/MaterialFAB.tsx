
import React from 'react';
import { cn } from '@/lib/utils';
import { Plus } from 'lucide-react';

type MaterialFABProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  icon?: React.ReactNode;
  color?: 'primary' | 'secondary';
  size?: 'normal' | 'small';
};

const MaterialFAB = React.forwardRef<HTMLButtonElement, MaterialFABProps>(
  ({ className, icon, color = 'primary', size = 'normal', ...props }, ref) => {
    const sizeClasses = {
      normal: 'h-14 w-14',
      small: 'h-10 w-10',
    };

    const colorClasses = {
      primary: 'bg-material-primary hover:bg-material-primary-dark',
      secondary: 'bg-material-secondary hover:bg-material-secondary-dark',
    };

    return (
      <button
        ref={ref}
        className={cn(
          'rounded-full flex items-center justify-center shadow-lg hover:shadow-xl transition-shadow duration-200 text-white',
          colorClasses[color],
          sizeClasses[size],
          className
        )}
        {...props}
      >
        {icon || <Plus size={size === 'normal' ? 24 : 18} />}
      </button>
    );
  }
);

MaterialFAB.displayName = 'MaterialFAB';

export { MaterialFAB };
