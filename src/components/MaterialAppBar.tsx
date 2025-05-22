
import React from 'react';
import { cn } from '@/lib/utils';
import { Link } from 'react-router-dom';
import { Menu } from 'lucide-react';

type MaterialAppBarProps = React.HTMLAttributes<HTMLDivElement> & {
  title: string;
  onMenuClick?: () => void;
};

const MaterialAppBar = React.forwardRef<HTMLDivElement, MaterialAppBarProps>(
  ({ className, title, onMenuClick, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          'h-16 bg-material-primary text-white flex items-center px-4 shadow-md',
          className
        )}
        {...props}
      >
        {onMenuClick && (
          <button onClick={onMenuClick} className="mr-4 p-2 rounded-full hover:bg-white/10">
            <Menu size={24} />
          </button>
        )}
        <Link to="/" className="text-xl font-medium">
          {title}
        </Link>
        <div className="flex-grow" />
        {children}
      </div>
    );
  }
);

MaterialAppBar.displayName = 'MaterialAppBar';

export { MaterialAppBar };
