import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import LineChart from "@/components/line-chart";

interface ProgressDashboardProps {
  isLoggedIn: boolean;
  handleLoginToggle: () => void;
}

export default function ProgressDashboard({
  isLoggedIn,
  handleLoginToggle,
}: ProgressDashboardProps) {
  const [isLoading, setIsLoading] = useState(true);
  const [fakeData, setFakeData] = useState<{ x: Date; y: number }[]>([]);

  useEffect(() => {
    setIsLoading(false); // Data loading is simulated
  }, []);

  useEffect(() => {
    if (isLoggedIn) {
      generateFakeData();
    }
  }, [isLoggedIn]);

  const generateFakeData = () => {
    const data: { x: Date; y: number }[] = [];
    const today = new Date();
    for (let i = 0; i < 30; i++) {
      const date = new Date(today);
      date.setDate(today.getDate() - i);
      data.push({
        x: date,
        y: Math.random() * 10, // Random score between 0 and 10
      });
    }
    setFakeData(data);
  };

  if (isLoading) {
    return <div className="p-4">Loading...</div>;
  }

  return (
    <div className="p-4">
      {isLoggedIn ? (
        <>
          <Card>
            <CardHeader>
              <CardTitle>Progress Dashboard</CardTitle>
            </CardHeader>
            <CardContent>
              <LineChart data={fakeData} />
            </CardContent>
          </Card>
          <Button onClick={handleLoginToggle} className="mt-4">
            Logout
          </Button>
        </>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle>Login</CardTitle>
          </CardHeader>
          <CardContent>
            {/* Fake login form */}
            <div className="space-y-4">
              <Input placeholder="Username (not validated)" type="text" />
              <Input placeholder="Password (not validated)" type="password" />
              <Button onClick={handleLoginToggle} className="w-full">
                Login
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
