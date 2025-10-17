import { Link, useLocation, useNavigate } from "react-router-dom";
import { Sparkles, User, LogOut } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import { AuthModal } from "@/components/AuthModal";

interface UserData {
  id: number;
  username: string;
  email: string;
}

const Navbar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [user, setUser] = useState<UserData | null>(null);
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  
  const isActive = (path: string) => location.pathname === path;
  
  // Check for existing auth
  useEffect(() => {
    const token = localStorage.getItem("auth_token");
    const userId = localStorage.getItem("user_id");
    const username = localStorage.getItem("username");
    
    if (token && userId && username) {
      setUser({ 
        id: parseInt(userId), 
        username,
        email: "user@example.com" // You can fetch this from /auth/me if needed
      });
    }
  }, []);


  const handleAuthSuccess = (token: string, userData: { id: number; username: string }) => {
    setUser({ 
      id: userData.id, 
      username: userData.username,
      email: "user@example.com"
    });
    setIsAuthOpen(false);
  };

  const handleLogout = () => {
    localStorage.removeItem("auth_token");
    localStorage.removeItem("user_id");
    localStorage.removeItem("username");
    setUser(null);
    toast.success("Logged out successfully");
    navigate("/");
  };


  const userInitial = user ? user.username.charAt(0).toUpperCase() : "U";

  return (
    <>
      <nav className="fixed top-0 left-0 right-0 z-50 border-b border-border/40 bg-background/80 backdrop-blur-xl">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <Link to="/" className="flex items-center gap-2 group">
              <div className="p-2 rounded-lg bg-gradient-primary">
                <Sparkles className="w-5 h-5 text-primary-foreground" />
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
                DesignMate
              </span>
            </Link>

            {/* Navigation Links removed per requirement */}

            {/* Right Side - User Menu or Sign In */}
            <div className="flex items-center gap-4">
              {user ? (
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="rounded-full w-10 h-10 bg-gradient-primary text-primary-foreground hover:opacity-90"
                    >
                      {userInitial}
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="w-56 bg-card/95 backdrop-blur-xl border-border/40">
                    <DropdownMenuLabel>
                      <div className="flex flex-col gap-1">
                        <p className="text-sm font-medium">My Account</p>
                        <p className="text-xs text-muted-foreground">{user.email}</p>
                      </div>
                    </DropdownMenuLabel>
                    <DropdownMenuSeparator className="bg-border/60" />
                    <DropdownMenuItem className="cursor-pointer text-destructive focus:text-destructive" onClick={handleLogout}>
                      <LogOut className="w-4 h-4 mr-2" />
                      Logout
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              ) : (
                <Button onClick={() => setIsAuthOpen(true)} variant="outline" size="sm">
                  <User className="w-4 h-4 mr-2" />
                  Sign In
                </Button>
              )}
            </div>
          </div>
        </div>
      </nav>
      
      <AuthModal 
        isOpen={isAuthOpen} 
        onClose={() => setIsAuthOpen(false)} 
        onSuccess={handleAuthSuccess}
      />
    </>
  );
};

export default Navbar;