/**
 * FILENAME: safeStorage.ts
 * DESCRIPTION/PURPOSE: Safe localStorage utility with error handling, size limits, and data validation
 * Author: JP + 2025-06-20
 */

interface StorageResult<T> {
  success: boolean;
  data?: T;
  error?: string;
}

export const safeStorage = {
  /**
   * Safely get data from localStorage with fallback
   */
  get<T>(key: string, fallback: T): T {
    try {
      const raw = localStorage.getItem(key);
      if (!raw) return fallback;
      
      const parsed = JSON.parse(raw) as T;
      return parsed;
    } catch (error) {
      console.warn(`🗑️ Corrupt localStorage key "${key}" - falling back to default:`, error);
      localStorage.removeItem(key);
      return fallback;
    }
  },

  /**
   * Safely set data to localStorage with size checking
   */
  set(key: string, value: unknown): boolean {
    try {
      const serialized = JSON.stringify(value);
      
      // Check size limit (localStorage typically has 5MB limit, use 4MB safety margin)
      if (serialized.length > 4 * 1024 * 1024) {
        console.error(`💾 localStorage quota would be exceeded for key "${key}" (${(serialized.length / 1024 / 1024).toFixed(2)}MB)`);
        return false;
      }
      
      localStorage.setItem(key, serialized);
      return true;
    } catch (error) {
      console.error(`💾 localStorage set failed for key "${key}":`, error);
      return false;
    }
  },

  /**
   * Safely remove data from localStorage
   */
  remove(key: string): boolean {
    try {
      localStorage.removeItem(key);
      return true;
    } catch (error) {
      console.error(`🗑️ localStorage remove failed for key "${key}":`, error);
      return false;
    }
  },

  /**
   * Get data with detailed result information
   */
  getWithResult<T>(key: string, fallback: T): StorageResult<T> {
    try {
      const raw = localStorage.getItem(key);
      if (!raw) {
        return { success: true, data: fallback };
      }
      
      const parsed = JSON.parse(raw) as T;
      return { success: true, data: parsed };
    } catch (error) {
      console.warn(`🗑️ Corrupt localStorage key "${key}" - falling back:`, error);
      localStorage.removeItem(key);
      return { 
        success: false, 
        data: fallback, 
        error: error instanceof Error ? error.message : 'Parse error' 
      };
    }
  },

  /**
   * Check if localStorage is available
   */
  isAvailable(): boolean {
    try {
      const testKey = '__localStorage_test__';
      localStorage.setItem(testKey, 'test');
      localStorage.removeItem(testKey);
      return true;
    } catch {
      return false;
    }
  },

  /**
   * Get localStorage usage information
   */
  getUsageInfo(): { used: number; total: number; available: number } {
    if (!this.isAvailable()) {
      return { used: 0, total: 0, available: 0 };
    }

    let used = 0;
    for (let key in localStorage) {
      if (localStorage.hasOwnProperty(key)) {
        used += localStorage[key].length + key.length;
      }
    }

    const total = 5 * 1024 * 1024; // 5MB typical limit
    return {
      used,
      total,
      available: total - used
    };
  },

  /**
   * Clear all localStorage data with confirmation
   */
  clearAll(): boolean {
    try {
      localStorage.clear();
      console.log('🗑️ All localStorage data cleared');
      return true;
    } catch (error) {
      console.error('🗑️ Failed to clear localStorage:', error);
      return false;
    }
  }
};

export default safeStorage; 