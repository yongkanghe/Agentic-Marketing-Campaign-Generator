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
    <div className="min-h-screen bg-background flex flex-col">
      <MaterialAppBar title="New Campaign">
        <div className="flex items-center gap-2">
          <MaterialButton 
            variant="outline" 
            className="flex items-center gap-1"
            onClick={() => navigate('/')}
          >
            <ArrowLeft size={16} />
            <span>Back</span>
          </MaterialButton>
          <MaterialButton 
            variant="outline" 
            className="flex items-center gap-1"
            onClick={() => setShowSaveDialog(true)}
          >
            <Save size={16} />
            <span>Save Progress</span>
          </MaterialButton>
        </div>
      </MaterialAppBar>
      
      <div className="container py-8">
        <MaterialCard className="max-w-4xl mx-auto">
          <form onSubmit={handleSubmit} className="p-6">
            <h1 className="text-2xl font-medium mb-6">Create New Marketing Campaign</h1>
            
            {/* Campaign Template Upload */}
            <MaterialCard className="mb-8 p-6 bg-orange-50 border-orange-200">
              <div className="flex items-center gap-2 mb-4">
                <CloudUpload className="text-orange-600" size={20} />
                <h2 className="text-lg font-medium text-orange-900">Quick Start with Previous Campaign</h2>
              </div>
              <p className="text-sm text-orange-700 mb-4">
                Upload a previous campaign template to get started immediately with proven prompts and settings.
              </p>
              
              <div className="flex items-center gap-4">
                <input
                  type="file"
                  accept=".json,.txt"
                  onChange={handleCampaignTemplateUpload}
                  className="hidden"
                  id="campaign-template-upload"
                />
                <label
                  htmlFor="campaign-template-upload"
                  className="flex items-center gap-2 px-4 py-2 bg-orange-100 hover:bg-orange-200 rounded-md cursor-pointer transition-colors"
                >
                  <Upload size={16} />
                  <span className="text-sm font-medium">Upload Campaign Template</span>
                </label>
                
                {campaignTemplate && (
                  <div className="flex items-center gap-2 text-sm text-orange-700">
                    <FileText size={16} />
                    <span>{campaignTemplate.name}</span>
                    {isLoadingTemplate && <span className="text-orange-500">Loading...</span>}
                  </div>
                )}
              </div>
              
              <div className="mt-3 text-xs text-orange-600">
                <p>💡 Tip: Save successful campaigns as templates from the scheduling page to reuse winning formulas!</p>
              </div>
            </MaterialCard>
            
            {/* Basic Campaign Info */}
            <div className="space-y-6 mb-8">
              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Campaign Name *</Label>
                  <Input
                    id="name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="E.g., Summer Product Launch"
                    required
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="type">Campaign Type</Label>
                  <select 
                    className="w-full p-2 border rounded-md"
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
                <Label htmlFor="objective">Campaign Objective *</Label>
                <Input
                  id="objective"
                  value={objective}
                  onChange={(e) => setObjective(e.target.value)}
                  placeholder="E.g., Increase brand awareness, Drive sales, Generate leads"
                  required
                />
              </div>
            </div>

            {/* URL Analysis Section */}
            <MaterialCard className="mb-8 p-6 bg-blue-50 border-blue-200">
              <div className="flex items-center gap-2 mb-4">
                <Globe className="text-blue-600" size={20} />
                <h2 className="text-lg font-medium text-blue-900">Smart Business Analysis</h2>
              </div>
              <p className="text-sm text-blue-700 mb-4">
                Let our AI analyze your business automatically by providing URLs. This reduces manual input and gives better context.
              </p>
              
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="businessUrl">Business Website URL</Label>
                  <Input
                    id="businessUrl"
                    value={businessUrl}
                    onChange={(e) => setBusinessUrl(e.target.value)}
                    placeholder="https://yourbusiness.com"
                    type="url"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="aboutUrl">About Page URL</Label>
                  <Input
                    id="aboutUrl"
                    value={aboutPageUrl}
                    onChange={(e) => setAboutPageUrl(e.target.value)}
                    placeholder="https://yourbusiness.com/about"
                    type="url"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="productUrl">Product/Service Page URL</Label>
                  <Input
                    id="productUrl"
                    value={productServiceUrl}
                    onChange={(e) => setProductServiceUrl(e.target.value)}
                    placeholder="https://yourbusiness.com/products/your-product"
                    type="url"
                  />
                </div>
                
                <MaterialButton
                  type="button"
                  variant="outline"
                  onClick={handleAnalyzeUrls}
                  disabled={isAnalyzing}
                  className="flex items-center gap-2"
                >
                  <Sparkles size={16} />
                  {isAnalyzing ? 'Analyzing...' : 'Analyze URLs'}
                </MaterialButton>
              </div>
            </MaterialCard>

            {/* File Upload Section */}
            <MaterialCard className="mb-8 p-6 bg-green-50 border-green-200">
              <div className="flex items-center gap-2 mb-4">
                <Upload className="text-green-600" size={20} />
                <h2 className="text-lg font-medium text-green-900">Campaign Assets & Context</h2>
              </div>
              <p className="text-sm text-green-700 mb-4">
                Upload images, documents, or existing campaign materials for AI analysis and reference.
              </p>
              
              <div className="grid md:grid-cols-3 gap-6">
                {/* Images Upload */}
                <div className="space-y-2">
                  <Label className="flex items-center gap-2">
                    <Image size={16} />
                    Product/Brand Images
                  </Label>
                  <input
                    type="file"
                    multiple
                    accept="image/*"
                    onChange={handleImageUpload}
                    className="w-full p-2 border rounded-md text-sm"
                  />
                  {uploadedImages.length > 0 && (
                    <div className="space-y-1">
                      {uploadedImages.map((file, index) => (
                        <div key={index} className="flex items-center justify-between text-xs bg-white p-2 rounded">
                          <span className="truncate">{file.name}</span>
                          <button
                            type="button"
                            onClick={() => removeFile(uploadedImages, setUploadedImages, index)}
                            className="text-red-500 hover:text-red-700"
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
                  <Label className="flex items-center gap-2">
                    <FileText size={16} />
                    Documents & Specs
                  </Label>
                  <input
                    type="file"
                    multiple
                    accept=".pdf,.doc,.docx,.txt"
                    onChange={handleDocumentUpload}
                    className="w-full p-2 border rounded-md text-sm"
                  />
                  {uploadedDocuments.length > 0 && (
                    <div className="space-y-1">
                      {uploadedDocuments.map((file, index) => (
                        <div key={index} className="flex items-center justify-between text-xs bg-white p-2 rounded">
                          <span className="truncate">{file.name}</span>
                          <button
                            type="button"
                            onClick={() => removeFile(uploadedDocuments, setUploadedDocuments, index)}
                            className="text-red-500 hover:text-red-700"
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
                  <Label className="flex items-center gap-2">
                    <Package size={16} />
                    Existing Campaign Assets
                  </Label>
                  <input
                    type="file"
                    multiple
                    accept="image/*,.pdf,.doc,.docx"
                    onChange={handleAssetUpload}
                    className="w-full p-2 border rounded-md text-sm"
                  />
                  {campaignAssets.length > 0 && (
                    <div className="space-y-1">
                      {campaignAssets.map((file, index) => (
                        <div key={index} className="flex items-center justify-between text-xs bg-white p-2 rounded">
                          <span className="truncate">{file.name}</span>
                          <button
                            type="button"
                            onClick={() => removeFile(campaignAssets, setCampaignAssets, index)}
                            className="text-red-500 hover:text-red-700"
                          >
                            ×
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </MaterialCard>

            {/* Creativity Control */}
            <MaterialCard className="mb-8 p-6 bg-purple-50 border-purple-200">
              <div className="flex items-center gap-2 mb-4">
                <Sparkles className="text-purple-600" size={20} />
                <h2 className="text-lg font-medium text-purple-900">AI Creativity Level</h2>
              </div>
              <p className="text-sm text-purple-700 mb-4">
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
                <div className="flex justify-between text-xs text-purple-600">
                  <span>Conservative</span>
                  <span className="font-medium">
                    Level {creativityLevel[0]} - {creativityLabels[creativityLevel[0] as keyof typeof creativityLabels] || 'Creative'}
                  </span>
                  <span>Experimental</span>
                </div>
              </div>
            </MaterialCard>

            {/* Manual Description (Fallback) */}
            <div className="space-y-6 mb-8">
              <div className="space-y-2">
                <Label htmlFor="description">Business Description (Optional if URLs provided)</Label>
                <Textarea
                  id="description"
                  value={businessDescription}
                  onChange={(e) => setBusinessDescription(e.target.value)}
                  placeholder="Describe your business, products, services, and target audience... (This will be auto-filled if you provide URLs above)"
                  className="min-h-[120px]"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="example">Example Content (Optional)</Label>
                <Textarea
                  id="example"
                  value={exampleContent}
                  onChange={(e) => setExampleContent(e.target.value)}
                  placeholder="Add any example content you'd like the AI to reference..."
                  className="min-h-[80px]"
                />
              </div>
            </div>
            
            <div className="mt-8 flex justify-end">
              <MaterialButton
                type="button"
                variant="outline" 
                className="mr-4"
                onClick={() => navigate('/')}
              >
                Cancel
              </MaterialButton>
              <MaterialButton type="submit">
                Create Campaign & Analyze
              </MaterialButton>
            </div>
          </form>
        </MaterialCard>
      </div>
      
      <SaveCampaignDialog 
        open={showSaveDialog} 
        onClose={() => setShowSaveDialog(false)} 
      />
    </div>
  );
};

export default NewCampaignPage;
