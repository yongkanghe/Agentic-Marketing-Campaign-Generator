/**
 * FILENAME: logger.ts
 * DESCRIPTION/PURPOSE: Frontend logging utility for AI Marketing Campaign Post Generator
 * Author: JP + 2025-06-18
 * 
 * This module provides comprehensive frontend logging with:
 * - Debug level logging to console
 * - Structured log formatting
 * - Environment-based log levels
 * - Request/Response logging
 * - Error tracking with stack traces
 */

type LogLevel = 'DEBUG' | 'INFO' | 'WARN' | 'ERROR';

interface LogEntry {
  timestamp: string;
  level: LogLevel;
  message: string;
  data?: any;
  component?: string;
  stack?: string;
}

class FrontendLogger {
  private logLevel: LogLevel;
  private isDevelopment: boolean;
  private logs: LogEntry[] = [];
  private maxLogs = 1000; // Keep last 1000 logs in memory

  constructor() {
    this.isDevelopment = import.meta.env.DEV;
    this.logLevel = this.getLogLevel();
    
    if (this.isDevelopment) {
      console.log('🎨 Frontend Logger Initialized');
      console.log(`📊 Log Level: ${this.logLevel}`);
      console.log(`🔧 Development Mode: ${this.isDevelopment}`);
    }
  }

  private getLogLevel(): LogLevel {
    const envLogLevel = import.meta.env.VITE_LOG_LEVEL as LogLevel;
    return envLogLevel || (this.isDevelopment ? 'DEBUG' : 'INFO');
  }

  private shouldLog(level: LogLevel): boolean {
    const levels: Record<LogLevel, number> = {
      DEBUG: 0,
      INFO: 1,
      WARN: 2,
      ERROR: 3
    };
    return levels[level] >= levels[this.logLevel];
  }

  private formatTimestamp(): string {
    return new Date().toISOString();
  }

  private createLogEntry(level: LogLevel, message: string, data?: any, component?: string): LogEntry {
    const entry: LogEntry = {
      timestamp: this.formatTimestamp(),
      level,
      message,
      component
    };

    if (data !== undefined) {
      entry.data = data;
    }

    if (level === 'ERROR' && data instanceof Error) {
      entry.stack = data.stack;
    }

    // Keep logs in memory for debugging
    this.logs.push(entry);
    if (this.logs.length > this.maxLogs) {
      this.logs.shift();
    }

    return entry;
  }

  private logToConsole(entry: LogEntry): void {
    const prefix = `[${entry.timestamp}] ${entry.level}`;
    const componentPrefix = entry.component ? ` [${entry.component}]` : '';
    const fullMessage = `${prefix}${componentPrefix}: ${entry.message}`;

    switch (entry.level) {
      case 'DEBUG':
        if (this.isDevelopment) {
          console.debug(fullMessage, entry.data || '');
        }
        break;
      case 'INFO':
        console.info(fullMessage, entry.data || '');
        break;
      case 'WARN':
        console.warn(fullMessage, entry.data || '');
        break;
      case 'ERROR':
        console.error(fullMessage, entry.data || '');
        if (entry.stack) {
          console.error('Stack trace:', entry.stack);
        }
        break;
    }
  }

  debug(message: string, data?: any, component?: string): void {
    if (!this.shouldLog('DEBUG')) return;
    
    const entry = this.createLogEntry('DEBUG', message, data, component);
    this.logToConsole(entry);
  }

  info(message: string, data?: any, component?: string): void {
    if (!this.shouldLog('INFO')) return;
    
    const entry = this.createLogEntry('INFO', message, data, component);
    this.logToConsole(entry);
  }

  warn(message: string, data?: any, component?: string): void {
    if (!this.shouldLog('WARN')) return;
    
    const entry = this.createLogEntry('WARN', message, data, component);
    this.logToConsole(entry);
  }

  error(message: string, error?: any, component?: string): void {
    if (!this.shouldLog('ERROR')) return;
    
    const entry = this.createLogEntry('ERROR', message, error, component);
    this.logToConsole(entry);
  }

  // API request/response logging
  logApiRequest(method: string, url: string, data?: any): void {
    this.debug(`🔌 API Request: ${method} ${url}`, data, 'API');
  }

  logApiResponse(method: string, url: string, status: number, data?: any, duration?: number): void {
    const durationText = duration ? ` (${duration}ms)` : '';
    if (status >= 200 && status < 300) {
      this.debug(`✅ API Response: ${method} ${url} - ${status}${durationText}`, data, 'API');
    } else if (status >= 400) {
      this.warn(`❌ API Error: ${method} ${url} - ${status}${durationText}`, data, 'API');
    } else {
      this.info(`🔌 API Response: ${method} ${url} - ${status}${durationText}`, data, 'API');
    }
  }

  logApiError(method: string, url: string, error: any): void {
    this.error(`💥 API Request Failed: ${method} ${url}`, error, 'API');
  }

  // Component lifecycle logging
  logComponentMount(componentName: string): void {
    this.debug(`🎨 Component mounted: ${componentName}`, undefined, componentName);
  }

  logComponentUnmount(componentName: string): void {
    this.debug(`🗑️ Component unmounted: ${componentName}`, undefined, componentName);
  }

  logComponentUpdate(componentName: string, props?: any): void {
    this.debug(`🔄 Component updated: ${componentName}`, props, componentName);
  }

  // User interaction logging
  logUserAction(action: string, data?: any, component?: string): void {
    this.info(`👤 User Action: ${action}`, data, component);
  }

  // Get logs for debugging
  getLogs(): LogEntry[] {
    return [...this.logs];
  }

  getRecentLogs(count: number = 50): LogEntry[] {
    return this.logs.slice(-count);
  }

  clearLogs(): void {
    this.logs = [];
    this.info('🧹 Logs cleared');
  }

  // Export logs for debugging
  exportLogs(): string {
    return JSON.stringify(this.logs, null, 2);
  }
}

// Global logger instance
const logger = new FrontendLogger();

// Export logger and convenience functions
export { logger };

export const debug = (message: string, data?: any, component?: string) => 
  logger.debug(message, data, component);

export const info = (message: string, data?: any, component?: string) => 
  logger.info(message, data, component);

export const warn = (message: string, data?: any, component?: string) => 
  logger.warn(message, data, component);

export const error = (message: string, error?: any, component?: string) => 
  logger.error(message, error, component);

export const logApiRequest = (method: string, url: string, data?: any) => 
  logger.logApiRequest(method, url, data);

export const logApiResponse = (method: string, url: string, status: number, data?: any, duration?: number) => 
  logger.logApiResponse(method, url, status, data, duration);

export const logApiError = (method: string, url: string, error: any) => 
  logger.logApiError(method, url, error);

export const logComponentMount = (componentName: string) => 
  logger.logComponentMount(componentName);

export const logComponentUnmount = (componentName: string) => 
  logger.logComponentUnmount(componentName);

export const logUserAction = (action: string, data?: any, component?: string) => 
  logger.logUserAction(action, data, component);

export default logger; 