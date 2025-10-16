import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Send, Loader2 } from "lucide-react";
import { toast } from "sonner";
import API_ENDPOINTS from "@/lib/config";

export function AIAssistant() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([
    { role: "assistant", text: "Upload a sketch to start designing with AI" },
  ]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    // Add user's message
    const userMsg = { role: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);
    const currentInput = input;
    setInput("");
    setIsLoading(true);

    try {
      // Call the backend assistant endpoint
      const response = await fetch(API_ENDPOINTS.AI_ASSISTANT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: currentInput,
          context: "You are an AI assistant helping with UI/UX design. Provide helpful suggestions for improving designs, creating better user experiences, and implementing modern design patterns."
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.status === 'ok' && result.data && result.data.response) {
        const aiReply = {
          role: "assistant",
          text: result.data.response,
        };
        setMessages((prev) => [...prev, aiReply]);
        
        // Save to history
        const historyItem = {
          id: `chat_${Date.now()}`,
          type: "chat" as const,
          timestamp: new Date().toISOString(),
          title: "AI Assistant Chat",
          message: `${currentInput} → ${result.data.response}`,
        };
        
        const existingHistory = JSON.parse(localStorage.getItem("app_history") || "[]");
        const updatedHistory = [historyItem, ...existingHistory];
        localStorage.setItem("app_history", JSON.stringify(updatedHistory));
      } else {
        throw new Error(result.message || 'Failed to get AI response');
      }
    } catch (error) {
      console.error('Error getting AI response:', error);
      let errorMessage = "Sorry, I'm having trouble connecting to the AI service. Please try again later.";
      
      if (error instanceof Error) {
        if (error.message.includes('500')) {
          errorMessage = "The AI service is currently unavailable. Please check if the Gemini API key is configured correctly.";
        } else if (error.message.includes('401') || error.message.includes('403')) {
          errorMessage = "Authentication failed. Please check the Gemini API key configuration.";
        } else if (error.message.includes('429')) {
          errorMessage = "Rate limit exceeded. Please wait a moment and try again.";
        }
      }
      
      const errorReply = {
        role: "assistant",
        text: errorMessage,
      };
      setMessages((prev) => [...prev, errorReply]);
      toast.error("Failed to get AI response");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="p-6 glassmorphism border-border/50 flex flex-col">
      <h3 className="text-lg font-semibold mb-3">AI Assistant</h3>

      {/* Chat area */}
      <div className="flex-1 space-y-3 mb-4 min-h-[150px] max-h-[250px] overflow-y-auto pr-2">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${
              msg.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`px-3 py-2 rounded-lg text-sm max-w-[80%] ${
                msg.role === "user"
                  ? "bg-primary text-primary-foreground rounded-br-none"
                  : "bg-muted/30 text-muted-foreground rounded-bl-none"
              }`}
            >
              {msg.text}
            </div>
          </div>
        ))}
      </div>

      {/* Input + Send button */}
      <div className="flex items-center gap-2">
        <input
          type="text"
          placeholder="Refine this design, change button style..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          className="w-full px-4 py-2 bg-input border border-border/50 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
        />
        <Button
          size="icon"
          onClick={handleSend}
          disabled={isLoading}
          className="bg-gradient-primary hover:opacity-90"
        >
          {isLoading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Send className="w-4 h-4" />
          )}
        </Button>
      </div>
    </Card>
  );
}
