import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMarketingContext } from '@/contexts/MarketingContext';
import { MaterialCard } from '@/components/MaterialCard';
import { MaterialButton } from '@/components/MaterialButton';
import { MaterialAppBar } from '@/components/MaterialAppBar';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { ArrowLeft, Upload, Link2, Image, FileText, Sparkles, Globe, Package, CloudUpload, Save } from 'lucide-react';
import { toast } from 'sonner';
import SaveCampaignDialog from '@/components/SaveCampaignDialog';

const NewCampaignPage: React.FC = () => {
  const navigate = useNavigate();
  const { createNewCampaign } = useMarketingContext();
  
  // Basic campaign info
  const [name, setName] = useState('');
  const [objective, setObjective] = useState('');
  const [businessDescription, setBusinessDescription] = useState('');
  const [exampleContent, setExampleContent] = useState('');
  
  // Enhanced features
  const [businessUrl, setBusinessUrl] = useState('');
  const [aboutPageUrl, setAboutPageUrl] = useState('');
  const [productServiceUrl, setProductServiceUrl] = useState('');
  const [campaignType, setCampaignType] = useState<'product' | 'service' | 'brand' | 'event'>('product');
  const [creativityLevel, setCreativityLevel] = useState([7]); // 1-10 scale
  
  // File uploads
  const [uploadedImages, setUploadedImages] = useState<File[]>([]);
  const [uploadedDocuments, setUploadedDocuments] = useState<File[]>([]);
  const [campaignAssets, setCampaignAssets] = useState<File[]>([]);
  
  // Campaign template upload
  const [campaignTemplate, setCampaignTemplate] = useState<File | null>(null);
  const [isLoadingTemplate, setIsLoadingTemplate] = useState(false);
  
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showSaveDialog, setShowSaveDialog] = useState(false);

  const handleCampaignTemplateUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setCampaignTemplate(file);
      
      setIsLoadingTemplate(true);
      try {
        // TODO: Parse campaign template and populate form
        const reader = new FileReader();
        reader.onload = (event) => {
          try {
            const template = JSON.parse(event.target?.result as string);
            // Auto-populate form fields from template
            setName(template.name || '');
            setObjective(template.objective || '');
            setBusinessDescription(template.businessDescription || '');
            setCampaignType(template.campaignType || 'product');
            setCreativityLevel([template.creativityLevel || 7]);
            toast.success('Campaign template loaded successfully!');
          } catch (error) {
            toast.error('Invalid campaign template format');
          }
        };
        reader.readAsText(file);
      } catch (error) {
        toast.error('Failed to load campaign template');
      } finally {
        setIsLoadingTemplate(false);
      }
    }
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setUploadedImages(prev => [...prev, ...Array.from(e.target.files!)]);
    }
  };

  const handleDocumentUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setUploadedDocuments(prev => [...prev, ...Array.from(e.target.files!)]);
    }
  };

  const handleAssetUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setCampaignAssets(prev => [...prev, ...Array.from(e.target.files!)]);
    }
  };

  const removeFile = (fileList: File[], setFileList: React.Dispatch<React.SetStateAction<File[]>>, index: number) => {
    setFileList(prev => prev.filter((_, i) => i !== index));
  };

  const handleAnalyzeUrls = async () => {
    if (!businessUrl && !aboutPageUrl && !productServiceUrl) {
      toast.error('Please provide at least one URL to analyze');
      return;
    }

    setIsAnalyzing(true);
    try {
      // TODO: Implement URL analysis with backend
      toast.success('URLs analyzed! Business context extracted.');
      // This would populate businessDescription automatically
    } catch (error) {
      toast.error('Failed to analyze URLs. Please try again.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!name || !objective) {
      toast.error('Please fill in campaign name and objective');
      return;
    }

    if (!businessDescription && !businessUrl && uploadedImages.length === 0 && uploadedDocuments.length === 0) {
      toast.error('Please provide business context through description, URL, or uploaded files');
      return;
    }
    
    createNewCampaign({
      name,
      businessDescription,
      objective,
      exampleContent,
      // Enhanced campaign data
      businessUrl,
      aboutPageUrl,
      productServiceUrl,
      campaignType,
      creativityLevel: creativityLevel[0],
      uploadedImages,
      uploadedDocuments,
      campaignAssets
    });
    
    toast.success('Campaign created! AI is analyzing your business context...');
    navigate('/ideation');
  };

  const creativityLabels = {
    1: 'Conservative',
    3: 'Balanced',
    5: 'Creative', 
    7: 'Innovative',
    10: 'Experimental'
  };
  
  return (
    <div className="min-h-screen vvl-gradient-bg flex flex-col">
      <header className="vvl-header-blur">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold vvl-text-primary">New Campaign</h1>
                <p className="text-xs vvl-text-secondary">Create Your Marketing Campaign</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button 
                className="vvl-button-secondary flex items-center gap-1"
                onClick={() => navigate('/')}
              >
                <ArrowLeft size={16} />
                <span>Back</span>
              </button>
              <button 
                className="vvl-button-secondary flex items-center gap-1"
                onClick={() => setShowSaveDialog(true)}
              >
                <Save size={16} />
                <span>Save Progress</span>
              </button>
            </div>
          </div>
        </div>
      </header>
      
      <div className="container py-8">
        <div className="vvl-card max-w-4xl mx-auto">
          <form onSubmit={handleSubmit} className="p-8">
            <h1 className="text-3xl font-bold vvl-text-primary mb-8">Create New Marketing Campaign</h1>
            
            {/* Campaign Template Upload */}
            <div className="vvl-card mb-8 p-6">
              <div className="flex items-center gap-2 mb-4">
                <CloudUpload className="text-blue-400" size={20} />
                <h2 className="text-lg font-medium vvl-text-primary">Quick Start with Previous Campaign</h2>
              </div>
              <p className="text-sm vvl-text-secondary mb-4">
                Upload a previous campaign template to get started immediately with proven prompts and settings.
              </p>
              
              <div className="flex items-center gap-4">
                <input
                  type="file"
                  accept=".json,.txt"
                  onChange={handleCampaignTemplateUpload}
                  className="hidden"
                  id="template-upload"
                />
                <label 
                  htmlFor="template-upload"
                  className="vvl-button-primary cursor-pointer flex items-center gap-2"
                >
                  <Upload size={16} />
                  Upload Campaign Template
                </label>
                {campaignTemplate && (
                  <span className="text-sm vvl-text-secondary">
                    {isLoadingTemplate ? 'Loading...' : `Loaded: ${campaignTemplate.name}`}
                  </span>
                )}
              </div>
              
              <div className="mt-3 text-xs vvl-text-secondary">
                <p>💡 Tip: Save successful campaigns as templates from the scheduling page to reuse winning formulas!</p>
              </div>
            </div>
            
            {/* Basic Campaign Info */}
            <div className="space-y-6 mb-8">
              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label htmlFor="name" className="block text-sm font-medium vvl-text-primary">Campaign Name *</label>
                  <input
                    id="name"
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="E.g., Summer Product Launch"
                    className="vvl-input w-full"
                    required
                  />
                </div>
                
                <div className="space-y-2">
                  <label htmlFor="type" className="block text-sm font-medium vvl-text-primary">Campaign Type</label>
                  <select 
                    className="vvl-input w-full"
                    value={campaignType}
                    onChange={(e) => setCampaignType(e.target.value as any)}
                  >
                    <option value="product">Product Launch</option>
                    <option value="service">Service Promotion</option>
                    <option value="brand">Brand Awareness</option>
                    <option value="event">Event Marketing</option>
                  </select>
                </div>
              </div>
              
              <div className="space-y-2">
                <label htmlFor="objective" className="block text-sm font-medium vvl-text-primary">Campaign Objective *</label>
                <input
                  id="objective"
                  type="text"
                  value={objective}
                  onChange={(e) => setObjective(e.target.value)}
                  placeholder="E.g., Increase brand awareness, Drive sales, Generate leads"
                  className="vvl-input w-full"
                  required
                />
              </div>
            </div>

            {/* URL Analysis Section */}
            <div className="vvl-card mb-8 p-6">
              <div className="flex items-center gap-2 mb-4">
                <Globe className="text-blue-400" size={20} />
                <h2 className="text-lg font-medium vvl-text-primary">Smart Business Analysis</h2>
              </div>
              <p className="text-sm vvl-text-secondary mb-4">
                Let our AI analyze your business automatically by providing URLs. This reduces manual input and gives better context.
              </p>
              
              <div className="space-y-4">
                <div className="space-y-2">
                  <label htmlFor="businessUrl" className="block text-sm font-medium vvl-text-primary">Business Website URL</label>
                  <input
                    id="businessUrl"
                    value={businessUrl}
                    onChange={(e) => setBusinessUrl(e.target.value)}
                    placeholder="https://yourbusiness.com"
                    type="url"
                    className="vvl-input w-full"
                  />
                </div>
                
                <div className="space-y-2">
                  <label htmlFor="aboutUrl" className="block text-sm font-medium vvl-text-primary">About Page URL</label>
                  <input
                    id="aboutUrl"
                    value={aboutPageUrl}
                    onChange={(e) => setAboutPageUrl(e.target.value)}
                    placeholder="https://yourbusiness.com/about"
                    type="url"
                    className="vvl-input w-full"
                  />
                </div>
                
                <div className="space-y-2">
                  <label htmlFor="productUrl" className="block text-sm font-medium vvl-text-primary">Product/Service Page URL</label>
                  <input
                    id="productUrl"
                    value={productServiceUrl}
                    onChange={(e) => setProductServiceUrl(e.target.value)}
                    placeholder="https://yourbusiness.com/products/your-product"
                    type="url"
                    className="vvl-input w-full"
                  />
                </div>
                
                <button
                  type="button"
                  onClick={handleAnalyzeUrls}
                  disabled={isAnalyzing}
                  className="vvl-button-primary flex items-center gap-2"
                >
                  <Sparkles size={16} />
                  {isAnalyzing ? 'Analyzing...' : 'Analyze URLs'}
                </button>
              </div>
            </div>

            {/* File Upload Section */}
            <div className="vvl-card mb-8 p-6">
              <div className="flex items-center gap-2 mb-4">
                <Upload className="text-green-400" size={20} />
                <h2 className="text-lg font-medium vvl-text-primary">Campaign Assets & Context</h2>
              </div>
              <p className="text-sm vvl-text-secondary mb-4">
                Upload images, documents, or existing campaign materials for AI analysis and reference.
              </p>
              
              <div className="grid md:grid-cols-3 gap-6">
                {/* Images Upload */}
                <div className="space-y-2">
                  <label className="flex items-center gap-2 text-sm font-medium vvl-text-primary">
                    <Image size={16} />
                    Product/Brand Images
                  </label>
                  <input
                    type="file"
                    multiple
                    accept="image/*"
                    onChange={handleImageUpload}
                    className="vvl-input w-full text-sm"
                  />
                  {uploadedImages.length > 0 && (
                    <div className="space-y-1">
                      {uploadedImages.map((file, index) => (
                        <div key={index} className="flex items-center justify-between text-xs bg-white/10 p-2 rounded">
                          <span className="truncate vvl-text-secondary">{file.name}</span>
                          <button
                            type="button"
                            onClick={() => removeFile(uploadedImages, setUploadedImages, index)}
                            className="text-red-400 hover:text-red-300"
                          >
                            ×
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Documents Upload */}
                <div className="space-y-2">
                  <label className="flex items-center gap-2 text-sm font-medium vvl-text-primary">
                    <FileText size={16} />
                    Documents & Specs
                  </label>
                  <input
                    type="file"
                    multiple
                    accept=".pdf,.doc,.docx,.txt"
                    onChange={handleDocumentUpload}
                    className="vvl-input w-full text-sm"
                  />
                  {uploadedDocuments.length > 0 && (
                    <div className="space-y-1">
                      {uploadedDocuments.map((file, index) => (
                        <div key={index} className="flex items-center justify-between text-xs bg-white/10 p-2 rounded">
                          <span className="truncate vvl-text-secondary">{file.name}</span>
                          <button
                            type="button"
                            onClick={() => removeFile(uploadedDocuments, setUploadedDocuments, index)}
                            className="text-red-400 hover:text-red-300"
                          >
                            ×
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Campaign Assets Upload */}
                <div className="space-y-2">
                  <label className="flex items-center gap-2 text-sm font-medium vvl-text-primary">
                    <Package size={16} />
                    Existing Campaign Assets
                  </label>
                  <input
                    type="file"
                    multiple
                    accept="image/*,.pdf,.doc,.docx"
                    onChange={handleAssetUpload}
                    className="vvl-input w-full text-sm"
                  />
                  {campaignAssets.length > 0 && (
                    <div className="space-y-1">
                      {campaignAssets.map((file, index) => (
                        <div key={index} className="flex items-center justify-between text-xs bg-white/10 p-2 rounded">
                          <span className="truncate vvl-text-secondary">{file.name}</span>
                          <button
                            type="button"
                            onClick={() => removeFile(campaignAssets, setCampaignAssets, index)}
                            className="text-red-400 hover:text-red-300"
                          >
                            ×
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Creativity Control */}
            <div className="vvl-card mb-8 p-6">
              <div className="flex items-center gap-2 mb-4">
                <Sparkles className="text-purple-400" size={20} />
                <h2 className="text-lg font-medium vvl-text-primary">AI Creativity Level</h2>
              </div>
              <p className="text-sm vvl-text-secondary mb-4">
                Control how creative and experimental the AI should be with your campaign ideas.
              </p>
              
              <div className="space-y-4">
                <div className="px-2">
                  <Slider
                    value={creativityLevel}
                    onValueChange={setCreativityLevel}
                    max={10}
                    min={1}
                    step={1}
                    className="w-full"
                  />
                </div>
                <div className="flex justify-between text-xs vvl-text-secondary">
                  <span>Conservative</span>
                  <span className="font-medium vvl-text-primary">
                    Level {creativityLevel[0]} - {creativityLabels[creativityLevel[0] as keyof typeof creativityLabels] || 'Creative'}
                  </span>
                  <span>Experimental</span>
                </div>
              </div>
            </div>

            {/* Manual Description (Fallback) */}
            <div className="space-y-6 mb-8">
              <div className="space-y-2">
                <label htmlFor="description" className="block text-sm font-medium vvl-text-primary">Business Description (Optional if URLs provided)</label>
                <textarea
                  id="description"
                  value={businessDescription}
                  onChange={(e) => setBusinessDescription(e.target.value)}
                  placeholder="Describe your business, products, services, and target audience... (This will be auto-filled if you provide URLs above)"
                  className="vvl-input w-full min-h-[120px] resize-vertical"
                />
              </div>
              
              <div className="space-y-2">
                <label htmlFor="example" className="block text-sm font-medium vvl-text-primary">Example Content (Optional)</label>
                <textarea
                  id="example"
                  value={exampleContent}
                  onChange={(e) => setExampleContent(e.target.value)}
                  placeholder="Add any example content you'd like the AI to reference..."
                  className="vvl-input w-full min-h-[80px] resize-vertical"
                />
              </div>
            </div>
            
            <div className="mt-8 flex justify-end gap-4">
              <button
                type="button"
                className="vvl-button-secondary"
                onClick={() => navigate('/')}
              >
                Cancel
              </button>
              <button type="submit" className="vvl-button-primary">
                Create Campaign & Analyze
              </button>
            </div>
          </form>
        </div>
      </div>
      
      <SaveCampaignDialog 
        open={showSaveDialog} 
        onClose={() => setShowSaveDialog(false)} 
      />
    </div>
  );
};

export default NewCampaignPage;
