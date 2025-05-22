
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { MarketingProvider } from "@/contexts/MarketingContext";

// Pages
import DashboardPage from "./pages/DashboardPage";
import NewCampaignPage from "./pages/NewCampaignPage";
import IdeationPage from "./pages/IdeationPage";
import ProposalsPage from "./pages/ProposalsPage";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <MarketingProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/new" element={<NewCampaignPage />} />
            <Route path="/ideation" element={<IdeationPage />} />
            <Route path="/proposals" element={<ProposalsPage />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </MarketingProvider>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
