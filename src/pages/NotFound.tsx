/**
 * FILENAME: NotFound.tsx
 * DESCRIPTION/PURPOSE: 404 error page with VVL design system styling
 * Author: JP + 2025-06-15
 */

import { useLocation, Link } from 'react-router-dom';
import { useEffect } from 'react';
import { Home, ArrowLeft } from 'lucide-react';

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error(
      "404 Error: User attempted to access non-existent route:",
      location.pathname
    );
  }, [location.pathname]);

  return (
    <div className="min-h-screen vvl-gradient-bg flex items-center justify-center">
      <div className="text-center max-w-md mx-auto px-6">
        <div className="vvl-card p-8">
          <div className="w-24 h-24 mx-auto mb-6 rounded-full bg-gradient-to-r from-blue-500/20 to-purple-600/20 flex items-center justify-center">
            <span className="text-6xl font-bold vvl-text-accent">404</span>
          </div>
          
          <h1 className="text-3xl font-bold vvl-text-primary mb-4">Page Not Found</h1>
          <p className="text-lg vvl-text-secondary mb-8">
            Oops! The page you're looking for doesn't exist or has been moved.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/" className="vvl-button-primary inline-flex items-center gap-2">
              <Home size={18} />
              Return Home
            </Link>
            <button 
              onClick={() => window.history.back()} 
              className="vvl-button-secondary inline-flex items-center gap-2"
            >
              <ArrowLeft size={18} />
              Go Back
            </button>
          </div>
          
          <div className="mt-8 pt-6 border-t border-white/20">
            <p className="text-sm vvl-text-secondary">
              If you believe this is an error, please contact support.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NotFound;
