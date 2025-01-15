"use client";
import { useState, useEffect } from "react";
import { ThemeProvider, useTheme } from "@/components/theme-provider";
import { cn } from "@/lib/utils";
import { Sun, Moon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import AnalyzeVideo from "./pages/analyze-video";
import PracticeSong from "./pages/practice-song";
import ProgressDashboard from "./pages/progress-dashboard";

const ModeToggle = () => {
  const { setTheme, theme } = useTheme();

  return (
    <Button
      variant="outline"
      size="icon"
      onClick={() => setTheme(theme === "light" ? "dark" : "light")}
    >
      <Sun
        className={cn(
          "h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all",
          {
            hidden: theme !== "light",
          }
        )}
      />
      <Moon
        className={cn(
          "absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all",
          {
            hidden: theme !== "dark",
          }
        )}
      />
      <span className="sr-only">Toggle theme</span>
    </Button>
  );
};

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  // Handle login state change and localStorage
  const handleLoginToggle = () => {
    const newLoginStatus = !isLoggedIn;
    setIsLoggedIn(newLoginStatus);
    localStorage.setItem("isLoggedIn", newLoginStatus.toString());
  };

  useEffect(() => {
    // Check localStorage for login status on mount
    const storedLoginStatus = localStorage.getItem("isLoggedIn");
    if (storedLoginStatus === "true") {
      setIsLoggedIn(true);
    }
  }, []);

  return (
    <ThemeProvider defaultTheme="system" storageKey="vite-ui-theme">
      <div
        className={cn(
          "relative flex min-h-screen flex-col",
          "bg-background font-sans"
        )}
      >
        <header className="sticky top-0 z-40 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
          <div className="container flex h-14 max-w-screen-2xl items-center">
            <div className="mr-4 hidden md:flex">
              <a href="#" className="mr-6 flex items-center space-x-2">
                <span className="hidden font-bold sm:inline-block">
                  Music Teacher AI
                </span>
              </a>
            </div>
            <div className="flex flex-1 items-center justify-between space-x-2 md:justify-end">
              <div className="w-full flex-1 md:w-auto md:flex-none">
                <Tabs
                  defaultValue="analyze"
                  className="md:mx-auto lg:max-w-5xl"
                >
                  <TabsList className="grid w-full grid-cols-3">
                    <TabsTrigger value="analyze">Upload & Analyze</TabsTrigger>
                    <TabsTrigger value="practice">Practice Songs</TabsTrigger>
                    <TabsTrigger value="progress">Progress Tracker</TabsTrigger>
                  </TabsList>
                </Tabs>
              </div>
              <div className="flex items-center space-x-2">
                <ModeToggle />
                <Button variant="outline" onClick={handleLoginToggle}>
                  {isLoggedIn ? "Logout" : "Login"}
                </Button>
              </div>
            </div>
          </div>
        </header>
        <main className="flex-1 container pt-6">
          <Tabs defaultValue="analyze" className="space-y-4">
            <TabsContent value="analyze">
              <AnalyzeVideo />
            </TabsContent>
            <TabsContent value="practice">
              <PracticeSong />
            </TabsContent>
            <TabsContent value="progress">
              <ProgressDashboard
                isLoggedIn={isLoggedIn}
                handleLoginToggle={handleLoginToggle}
              />
            </TabsContent>
          </Tabs>
        </main>
      </div>
    </ThemeProvider>
  );
}

export default App;
