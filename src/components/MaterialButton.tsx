
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
          return 'bg-primary hover:bg-primary/90 text-primary-foreground';
        case 'secondary':
          return 'bg-secondary hover:bg-secondary/80 text-secondary-foreground';
        case 'outline':
          return 'border border-input bg-background hover:bg-accent hover:text-accent-foreground';
        case 'text':
          return 'bg-transparent hover:bg-accent hover:text-accent-foreground shadow-none';
        default:
          return 'bg-primary hover:bg-primary/90 text-primary-foreground';
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
