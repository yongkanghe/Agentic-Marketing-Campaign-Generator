
import React from 'react';
import { cn } from '@/lib/utils';
import { Card } from '@/components/ui/card';

type MaterialCardProps = React.ComponentPropsWithoutRef<typeof Card> & {
  elevation?: 0 | 1 | 2 | 3 | 4;
  interactive?: boolean;
};

const MaterialCard = React.forwardRef<HTMLDivElement, MaterialCardProps>(
  ({ className, elevation = 1, interactive = false, children, ...props }, ref) => {
    const elevationClasses = [
      'shadow-none',
      'shadow-sm',
      'shadow',
      'shadow-md',
      'shadow-lg'
    ];

    return (
      <Card
        ref={ref}
        className={cn(
          'rounded-lg bg-card border-none overflow-hidden',
          elevationClasses[elevation],
          interactive && 'hover:shadow-lg transition-shadow duration-300',
          className
        )}
        {...props}
      >
        {children}
      </Card>
    );
  }
);

MaterialCard.displayName = 'MaterialCard';

export { MaterialCard };
