import React from 'react';
import { render, screen, act, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { MarketingProvider } from '@/contexts/MarketingContext';
import ProposalsPage from '@/pages/ProposalsPage';
import { vi } from 'vitest';

// Create a mock context with the required data
const mockContextValue = {
  currentCampaign: {
    id: '1',
    name: 'Test Campaign',
    objective: 'Test objective',
    businessDescription: 'Test business',
    createdAt: new Date().toISOString(),
  },
  generatedIdeas: [
    {
      id: '1',
      title: 'Marketing Idea 1',
      description: 'Test idea description',
      tags: ['Business'],
      themes: ['Professional'],
      selected: false,
    }
  ],
  toggleIdeaSelection: vi.fn(),
  generateVideos: vi.fn(),
  exportToText: vi.fn(),
};

// Mock the context
vi.mock('@/contexts/MarketingContext', () => ({
  useMarketingContext: () => mockContextValue,
  MarketingProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

describe('Happy path UX flow', () => {
  test('proposals page renders correctly', async () => {
    render(
      <BrowserRouter>
        <MarketingProvider>
          <ProposalsPage />
        </MarketingProvider>
      </BrowserRouter>
    );

    // Check if the proposals page renders
    await act(async () => {
      expect(screen.getByText(/Marketing Proposals/i)).toBeInTheDocument();
    });

    // Check for generated ideas
    await act(async () => {
      expect(screen.getByText(/Marketing Idea 1/i)).toBeInTheDocument();
    });
  });
});
