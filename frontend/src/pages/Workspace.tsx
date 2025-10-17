import { useState } from "react";
import Navbar from "@/components/Navbar";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Upload, Wand2, Download, Share2, Loader2 } from "lucide-react";
import { toast } from "sonner";
// import { Send } from "lucide-react";
import { AIAssistant } from "@/components/AIAssistant";
import API_ENDPOINTS from "@/lib/config";
import { API_ENDPOINTS as ENDPOINTS, API_BASE_URL } from "@/lib/config";

export default function Workspace() {
  const [mode, setMode] = useState<"ui" | "3d">("ui");
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [description, setDescription] = useState<string>("");
  const [generatedImage, setGeneratedImage] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState<boolean>(false);

  const handleDownload = async () => {
    if (!generatedImage) return;
    try {
      const link = document.createElement('a');
      link.href = generatedImage;
      link.download = `ai_design_${Date.now()}.png`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success("Image downloaded");
    } catch (e) {
      toast.error("Failed to download image");
    }
  };

  const handleShare = async () => {
    if (!generatedImage) return;
    try {
      if (navigator.share && navigator.canShare) {
        const res = await fetch(generatedImage);
        const blob = await res.blob();
        const file = new File([blob], `ai_design_${Date.now()}.png`, { type: 'image/png' });
        if (navigator.canShare({ files: [file] } as any)) {
          await navigator.share({
            title: 'AI Generated Design',
            text: 'Check out this design!',
            files: [file] as any,
          } as any);
          return;
        }
      }
      if (navigator.share) {
        await navigator.share({
          title: 'AI Generated Design',
          text: 'Check out this design!',
          url: generatedImage,
        } as any);
      } else {
        // Fallback: copy URL
        await navigator.clipboard.writeText(generatedImage);
        toast.success("Image URL copied to clipboard");
      }
    } catch (e) {
      // Fallback to mailto or WhatsApp
      const mailto = `mailto:?subject=${encodeURIComponent('AI Generated Design')}&body=${encodeURIComponent('Check out this design! ' + generatedImage)}`;
      window.location.href = mailto;
    }
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setUploadedImage(e.target?.result as string);
        toast.success("Sketch uploaded successfully!");
      };
      reader.readAsDataURL(file);
    }
  };

  const handleGenerate = async () => {
    if (!uploadedImage || !description.trim()) {
      toast.error("Please upload an image and provide a description");
      return;
    }

    setIsGenerating(true);
    toast.success("AI is generating your design...");

    try {
      // Convert base64 image to blob
      const response = await fetch(uploadedImage);
      const blob = await response.blob();
      
      // Create form data
      const formData = new FormData();
      formData.append('sketch', blob, 'sketch.png');
      formData.append('prompt', description);
      formData.append('guidance', '7.5');
      formData.append('steps', '30');

      // Call backend endpoint
      const apiResponse = await fetch(API_ENDPOINTS.GENERATE, {
        method: 'POST',
        body: formData,
      });

      if (!apiResponse.ok) {
        throw new Error(`HTTP error! status: ${apiResponse.status}`);
      }

      const result = await apiResponse.json();
      
      if (result.status === 'ok' && result.data) {
        if (result.data.image_base64) {
          setGeneratedImage(`data:image/png;base64,${result.data.image_base64}`);
        } else if (result.data.latest_path || result.data.image_path) {
          // Normalize path from backend (handles windows backslashes and leading ./)
          const normalizedPath = String(result.data.latest_path || result.data.image_path)
            .replace(/\\/g, "/")
            .replace(/^\.\//, "");
          const apiBase = ENDPOINTS.HEALTH.replace(/\/health$/, "");
          const isAbsolute = normalizedPath.startsWith("http://") || normalizedPath.startsWith("https://") || normalizedPath.startsWith("/");
          const base = apiBase || API_BASE_URL;
          let imageUrl = isAbsolute
            ? (normalizedPath.startsWith("/") ? `${base}${normalizedPath}` : normalizedPath)
            : `${base}/${normalizedPath}`;
          // Cache-bust to ensure latest.png refreshes
          const bust = `t=${Date.now()}`;
          imageUrl += (imageUrl.includes("?") ? "&" : "?") + bust;
          setGeneratedImage(imageUrl);
        } else {
          throw new Error('Backend response missing image data');
        }
        toast.success("Design generated successfully!");
        
        // Save to history
        const historyItem = {
          id: `gen_${Date.now()}`,
          type: "generation" as const,
          timestamp: new Date().toISOString(),
          title: `Generated ${mode === "ui" ? "UI" : "3D"} Design`,
          description: description,
          imageUrl: result.data.image_base64 ? `data:image/png;base64,${result.data.image_base64}` : 
                    (result.data.latest_path ? `${ENDPOINTS.HEALTH.replace(/\/health$/, "")}/${result.data.latest_path.replace(/\\/g, "/").replace(/^\.\//, "")}` : 
                    (result.data.image_path ? `${ENDPOINTS.HEALTH.replace(/\/health$/, "")}/${result.data.image_path.replace(/\\/g, "/").replace(/^\.\//, "")}` : undefined))
        };
        
        const existingHistory = JSON.parse(localStorage.getItem("app_history") || "[]");
        const updatedHistory = [historyItem, ...existingHistory];
        localStorage.setItem("app_history", JSON.stringify(updatedHistory));
      } else {
        throw new Error(result.message || 'Failed to generate image');
      }
    } catch (error) {
      console.error('Error generating image:', error);
      let errorMessage = 'Unknown error';
      
      if (error instanceof Error) {
        if (error.message.includes('500')) {
          errorMessage = 'Server error. Please check if the AI model is loaded correctly.';
        } else if (error.message.includes('413')) {
          errorMessage = 'Image file is too large. Please try with a smaller image.';
        } else if (error.message.includes('400')) {
          errorMessage = 'Invalid request. Please check your image and description.';
        } else {
          errorMessage = error.message;
        }
      }
      
      toast.error(`Failed to generate image: ${errorMessage}`);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <main className="container mx-auto px-6 pt-24 pb-12">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2 glow-text-purple">AI Workspace</h1>
        </div>

        {/* Mode Toggle */}
        <Tabs defaultValue="ui" className="mb-6" onValueChange={(v) => setMode(v as "ui" | "3d")}>
          <TabsList className="glassmorphism">
            <TabsTrigger value="ui" className="data-[state=active]:bg-primary/20 data-[state=active]:text-primary">
              Sketch → UI
            </TabsTrigger>
            <TabsTrigger value="3d" className="data-[state=active]:bg-accent/20 data-[state=active]:text-accent">
              Sketch → 3D Product
            </TabsTrigger>
          </TabsList>
        </Tabs>

        <div className="grid lg:grid-cols-2 gap-6">
          {/* Upload Area */}
          <Card className="p-8 glassmorphism border-border/50">
            <h2 className="text-xl font-semibold mb-4">Upload Sketch</h2>
            
            <div className="relative">
              <input
                type="file"
                accept="image/*"
                onChange={handleImageUpload}
                className="hidden"
                id="sketch-upload"
              />
              <label
                htmlFor="sketch-upload"
                className="flex flex-col items-center justify-center min-h-[300px] border-2 border-dashed border-border/50 rounded-lg cursor-pointer hover:border-primary/50 transition-all group"
              >
                {uploadedImage ? (
                  <img
                    src={uploadedImage}
                    alt="Uploaded sketch"
                    className="max-h-[300px] object-contain rounded-lg"
                  />
                ) : (
                  <>
                    <Upload className="w-12 h-12 text-muted-foreground group-hover:text-primary transition-colors mb-4" />
                    <p className="text-muted-foreground">Drag and drop or click to upload</p>
                    <p className="text-sm text-muted-foreground/60 mt-2">PNG, JPG up to 2MB</p>
                  </>
                )}
              </label>
            </div>

            {uploadedImage && (
              <div className="mt-6">
                <label className="block text-sm font-medium mb-2">
                  Describe your design
                </label>
                <textarea
                  placeholder="Describe how your UI or 3D product should look... (e.g., 'Modern e-commerce homepage with blue theme' or '3D product with metallic finish')"
                  className="w-full px-4 py-3 bg-input border border-border/50 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 min-h-[100px] resize-none"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                />
              </div>
            )}

            <Button
              onClick={handleGenerate}
              disabled={!uploadedImage || !description.trim() || isGenerating}
              className="w-full mt-6 bg-gradient-primary hover:opacity-90 transition-opacity"
            >
              {isGenerating ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Wand2 className="w-4 h-4 mr-2" />
              )}
              {isGenerating ? "Generating..." : `Generate ${mode === "ui" ? "UI" : "3D Model"}`}
            </Button>
          </Card>

          {/* Preview & AI Chat Area */}
          <div className="space-y-6">
            {/* Preview Panel */}
            <Card className="p-8 glassmorphism border-border/50">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold">Preview</h2>
                <div className="flex gap-2">
                  <Button variant="ghost" size="icon" onClick={handleDownload} disabled={!generatedImage}>
                    <Download className="w-4 h-4" />
                  </Button>
                  <Button variant="ghost" size="icon" onClick={handleShare} disabled={!generatedImage}>
                    <Share2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
              
              <div className="flex items-center justify-center min-h-[300px] border border-border/50 rounded-lg bg-muted/20">
                {isGenerating ? (
                  <div className="flex flex-col items-center justify-center space-y-4">
                    <Loader2 className="w-8 h-8 animate-spin text-primary" />
                    <p className="text-muted-foreground">Generating your design...</p>
                    <p className="text-sm text-muted-foreground/60">This may take a few moments</p>
                  </div>
                ) : generatedImage ? (
                  <img
                    src={generatedImage}
                    alt="Generated design"
                    className="max-h-[300px] object-contain rounded-lg"
                  />
                ) : (
                  <div className="text-center">
                    <p className="text-muted-foreground mb-2">Your generated design will appear here</p>
                    <p className="text-sm text-muted-foreground/60">Upload a sketch and add a description to get started</p>
                  </div>
                )}
              </div>
            </Card>

            {/* AI Assistant */}
            
            {/* <Card className="p-6 glassmorphism border-border/50">
              <h3 className="text-lg font-semibold mb-3">AI Assistant</h3>
              <div className="space-y-3 mb-4 min-h-[120px]">
                <div className="bg-muted/30 rounded-lg p-3 text-sm">
                  <p className="text-muted-foreground">Upload a sketch to start designing with AI</p>
                </div>
              </div>
              <input
                type="text"
                placeholder="Refine this design, change button style..."
                className="w-full px-4 py-2 bg-input border border-border/50 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
              />
              <Button size="icon" className="bg-gradient-primary hover:opacity-90">
                  <Send className="w-4 h-4" />
                </Button>
            </Card> */}
            
            <AIAssistant 
              uploadedImage={uploadedImage}
              onPromptGenerated={(prompt) => setDescription(prompt)}
            />

          </div>
        </div>
      </main>
    </div>
  );
}
