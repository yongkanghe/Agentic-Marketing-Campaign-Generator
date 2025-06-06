import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from '@/App';

describe('Happy path UX flow', () => {
  test('user can create a campaign and generate videos', async () => {
    window.history.pushState({}, '', '/');
    render(<App />);

    // Dashboard page
    const newCampaignLink = screen.getAllByRole('link', { name: /new campaign/i })[0];
    await userEvent.click(newCampaignLink);

    // New Campaign page
    await userEvent.type(screen.getByLabelText(/campaign name/i), 'Test Campaign');
    await userEvent.type(screen.getByLabelText(/campaign objective/i), 'Increase brand awareness');
    await userEvent.type(screen.getByLabelText(/business description/i), 'We sell test products');
    await userEvent.click(screen.getByRole('button', { name: /next/i }));

    // Ideation page - select first theme and tag
    const theme = await screen.findByText('Professional');
    await userEvent.click(theme);
    const tag = await screen.findByText('Business');
    await userEvent.click(tag);
    await userEvent.click(screen.getByRole('button', { name: /generate ideas/i }));

    // Proposals page - ideas rendered
    await screen.findByText(/marketing idea 1/i);
    await userEvent.click(screen.getByRole('button', { name: /generate videos/i }));

    // After videos generated
    await screen.findByText(/generated videos/i);
  });
});
