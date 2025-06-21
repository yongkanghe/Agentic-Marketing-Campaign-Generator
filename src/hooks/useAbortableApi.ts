/**
 * FILENAME: useAbortableApi.ts
 * DESCRIPTION/PURPOSE: Custom hook for abortable API calls with proper cleanup and error handling
 * Author: JP + 2025-06-20
 */

import { useRef, useCallback, useEffect } from 'react';

interface AbortableApiOptions {
  onSuccess?: (data: any) => void;
  onError?: (error: Error) => void;
  onAbort?: () => void;
}

export const useAbortableApi = () => {
  const abortControllerRef = useRef<AbortController | null>(null);
  const isActiveRef = useRef(true);

  // Cleanup function to abort ongoing requests
  const cleanup = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
  }, []);

  // Create a new AbortController for a request
  const createAbortController = useCallback(() => {
    // Abort any existing request
    cleanup();
    
    // Create new controller
    abortControllerRef.current = new AbortController();
    return abortControllerRef.current;
  }, [cleanup]);

  // Execute an abortable API call
  const executeAbortableCall = useCallback(async <T>(
    apiCall: (signal: AbortSignal) => Promise<T>,
    options: AbortableApiOptions = {}
  ): Promise<T | null> => {
    const controller = createAbortController();
    
    try {
      const result = await apiCall(controller.signal);
      
      // Check if component is still mounted and request wasn't aborted
      if (isActiveRef.current && !controller.signal.aborted) {
        options.onSuccess?.(result);
        return result;
      }
      
      return null;
    } catch (error) {
      // Check if error is due to abort
      if (error instanceof Error && error.name === 'AbortError') {
        console.log('🚫 API request aborted');
        options.onAbort?.();
        return null;
      }
      
      // Handle other errors
      if (isActiveRef.current) {
        console.error('❌ API request failed:', error);
        options.onError?.(error instanceof Error ? error : new Error('Unknown error'));
      }
      
      throw error;
    }
  }, [createAbortController]);

  // Check if there's an active request
  const hasActiveRequest = useCallback(() => {
    return abortControllerRef.current !== null;
  }, []);

  // Manually abort current request
  const abortCurrentRequest = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      console.log('🚫 Manually aborted current API request');
    }
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      isActiveRef.current = false;
      cleanup();
    };
  }, [cleanup]);

  return {
    executeAbortableCall,
    hasActiveRequest,
    abortCurrentRequest,
    cleanup
  };
};

export default useAbortableApi; 