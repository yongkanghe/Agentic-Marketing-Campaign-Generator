import { render } from '@testing-library/react';
import { act } from 'react-dom/test-utils';
import React from 'react';
import { MarketingProvider, useMarketingContext } from '../MarketingContext';

describe('MarketingContext', () => {
  test('toggleIdeaSelection toggles selected flag', async () => {
    let ctx: any;
    const Capture = () => {
      ctx = useMarketingContext();
      return null;
    };

    render(
      <MarketingProvider>
        <Capture />
      </MarketingProvider>
    );

    await act(async () => {
      ctx.createNewCampaign({
        name: 'test',
        businessDescription: 'desc',
        objective: 'obj',
      });
    });

    await act(async () => {
      await ctx.generateIdeas();
    });

    const id = ctx.generatedIdeas[0].id;
    expect(ctx.generatedIdeas[0].selected).toBe(false);

    act(() => {
      ctx.toggleIdeaSelection(id);
    });
    expect(ctx.generatedIdeas.find((i: any) => i.id === id)?.selected).toBe(true);

    act(() => {
      ctx.toggleIdeaSelection(id);
    });
    expect(ctx.generatedIdeas.find((i: any) => i.id === id)?.selected).toBe(false);
  });
});
