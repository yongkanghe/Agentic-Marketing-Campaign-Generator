
import React from 'react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';

type MaterialButtonProps = React.ComponentPropsWithoutRef<typeof Button> & {
  variant?: 'primary' | 'secondary' | 'outline' | 'text';
  elevation?: number;
};

const MaterialButton = React.forwardRef<HTMLButtonElement, MaterialButtonProps>(
  ({ className, variant = 'primary', elevation = 2, children, ...props }, ref) => {
    const elevationClasses = [
      'shadow-none',
      'shadow-sm',
      'shadow-md',
      'shadow-lg',
      'shadow-xl'
    ];

    const getVariantClasses = () => {
      switch(variant) {
        case 'primary':
          return 'bg-material-primary hover:bg-material-primary-dark text-white';
        case 'secondary':
          return 'bg-material-secondary hover:bg-material-secondary-dark text-white';
        case 'outline':
          return 'bg-transparent border border-material-primary text-material-primary hover:bg-material-primary/10';
        case 'text':
          return 'bg-transparent text-material-primary hover:bg-material-primary/10 shadow-none';
        default:
          return 'bg-material-primary hover:bg-material-primary-dark text-white';
      }
    };

    return (
      <Button
        ref={ref}
        className={cn(
          'rounded-md font-medium transition-all duration-200',
          getVariantClasses(),
          variant !== 'text' && elevation >= 0 && elevation < elevationClasses.length && elevationClasses[elevation],
          className
        )}
        {...props}
      >
        {children}
      </Button>
    );
  }
);

MaterialButton.displayName = 'MaterialButton';

export { MaterialButton };
