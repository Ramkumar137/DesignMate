import Navbar from "@/components/Navbar";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Sparkles, Layers, Box } from "lucide-react";
import { Link } from "react-router-dom";

export default function Index() {
  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      {/* Animated background effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/10 rounded-full blur-3xl animate-glow-pulse" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-accent/10 rounded-full blur-3xl animate-glow-pulse" style={{ animationDelay: '1s' }} />
      </div>

      <Navbar />

      {/* Hero Section */}
      <section className="relative container mx-auto px-6 pt-32 pb-20 text-center">
        <div className="max-w-4xl mx-auto animate-fade-in">
          <div className="inline-flex items-center gap-2 px-4 py-2 mb-6 rounded-full border border-primary/30 bg-primary/5 backdrop-blur-sm">
            <Sparkles className="w-4 h-4 text-primary" />
            <span className="text-sm text-primary font-medium">AI-Powered Design Platform</span>
          </div>

          <h1 className="text-6xl md:text-7xl font-bold mb-6 leading-tight">
            Welcome to{" "}
            <span className="bg-gradient-primary bg-clip-text text-transparent glow-text-purple">
              DesignMate
            </span>{" "}
            — transform sketches into UI or 3D prototypes
          </h1>

          <p className="text-xl text-muted-foreground mb-10 max-w-2xl mx-auto">
            Upload your hand-drawn sketches and watch AI transform them into production-ready UI screens or stunning 3D product concepts. The future of design is here.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link to="/workspace">
              <Button variant="hero" size="xl" className="group">
                <Layers className="w-5 h-5 group-hover:rotate-12 transition-transform" />
                Try Sketch to UI
              </Button>
            </Link>
            <Link to="/workspace">
              <Button variant="outline-glow" size="xl" className="group">
                <Box className="w-5 h-5 group-hover:rotate-12 transition-transform" />
                Try Sketch to 3D
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
