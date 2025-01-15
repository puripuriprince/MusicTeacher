import { useState, useCallback } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { SpiderChart } from "@/components/spider-chart";
import ReactPlayer from "react-player";
import { useDropzone } from "react-dropzone"; // For drag and drop

const MOCK_VIDEO_URL = "https://www.youtube.com/embed/tz56ac6BaJQ";

// Mock feedback data (for when "Mock Upload" is clicked)
const MOCK_FEEDBACK = {
  visual_feedback: {
    posture: {
      score: 8,
      feedback: ["Good posture overall"],
      style_rating: ["A", "#FFA500"],
    },
    finger_position: {
      score: 6,
      feedback: ["Finger positioning needs improvement"],
      style_rating: ["C", "#00FF00"],
    },
    confidence: {
      score: 9,
      feedback: ["Very confident performance!"],
      style_rating: ["S", "#FF0000"],
    },
  },
  audio_feedback: {
    tempo: {
      score: 7,
      feedback: ["Tempo was mostly consistent"],
      style_rating: ["B", "#FFD700"],
    },
    pitch: {
      score: 5,
      feedback: ["Pitch accuracy needs work"],
      style_rating: ["D", "#0000FF"],
    },
    rhythm: {
      score: 8.5,
      feedback: ["Rhythm was excellent"],
      style_rating: ["S", "#FF0000"],
    },
  },
  education_tips: {
    immediate_focus: ["Work on pitch accuracy"],
    technical_development: ["Practice finger exercises"],
    performance_growth: ["Try different musical styles"],
  },
  summary: {
    visual_grade: ["B", "#FFD700"],
    audio_grade: ["C", "#00FF00"],
    overall_grade: ["B", "#FFD700"],
    performance_summary:
      "A solid performance with areas for improvement in pitch and finger positioning.",
  },
};

// Utility function to get style rating based on score
function getStyleRating(score: number): [string, string] {
  if (score >= 9.5) return ["SSS", "#FF0000"];
  if (score >= 9.0) return ["SS", "#FF0000"];
  if (score >= 8.5) return ["S", "#FF0000"];
  if (score >= 8.0) return ["A", "#FFA500"];
  if (score >= 7.0) return ["B", "#FFD700"];
  if (score >= 6.0) return ["C", "#00FF00"];
  return ["D", "#0000FF"];
}

export default function AnalyzeVideo() {
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [feedback, setFeedback] = useState<typeof MOCK_FEEDBACK | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showMockVideo, setShowMockVideo] = useState(false);
  const [testScores, setTestScores] = useState({
    posture: 0,
    finger_position: 0,
    confidence: 0,
    tempo: 0,
    pitch: 0,
    rhythm: 0,
  });

  // Handle drag and drop
  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file.type.startsWith("video/")) {
      setVideoFile(file);
      setShowMockVideo(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "video/*": [".mp4", ".mov"],
    },
  });

  const handleAnalyzePerformance = async () => {
    setIsLoading(true);
    const formData = new FormData();
    if (videoFile) {
      formData.append("video", videoFile);
    }

    try {
      const response = await fetch("/api/analyze-performance", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setFeedback(data);
      } else {
        console.error("Analysis failed:", response.status);
        setFeedback(null);
      }
    } catch (error) {
      console.error("An error occurred:", error);
      setFeedback(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleMockUpload = () => {
    setShowMockVideo(true);
    setFeedback(MOCK_FEEDBACK);
  };

  // Function to generate feedback based on test scores
  const handleTestScoring = () => {
    const fakeFeedback = {
      visual_feedback: {
        posture: {
          score: testScores.posture,
          feedback: [],
          style_rating: getStyleRating(testScores.posture),
        },
        finger_position: {
          score: testScores.finger_position,
          feedback: [],
          style_rating: getStyleRating(testScores.finger_position),
        },
        confidence: {
          score: testScores.confidence,
          feedback: [],
          style_rating: getStyleRating(testScores.confidence),
        },
      },
      audio_feedback: {
        tempo: {
          score: testScores.tempo,
          feedback: [],
          style_rating: getStyleRating(testScores.tempo),
        },
        pitch: {
          score: testScores.pitch,
          feedback: [],
          style_rating: getStyleRating(testScores.pitch),
        },
        rhythm: {
          score: testScores.rhythm,
          feedback: [],
          style_rating: getStyleRating(testScores.rhythm),
        },
      },
      education_tips: {
        immediate_focus: ["Adjusted based on test scores"],
        technical_development: ["Techniques adjusted based on test scores"],
        performance_growth: ["Suggestions adjusted based on test scores"],
      },
      summary: {
        visual_grade: getStyleRating(
          (testScores.posture +
            testScores.finger_position +
            testScores.confidence) /
            3
        ),
        audio_grade: getStyleRating(
          (testScores.tempo + testScores.pitch + testScores.rhythm) / 3
        ),
        overall_grade: getStyleRating(
          (testScores.posture +
            testScores.finger_position +
            testScores.confidence +
            testScores.tempo +
            testScores.pitch +
            testScores.rhythm) /
            6
        ),
        performance_summary: "Summary based on adjusted test scores",
      },
    };
    setFeedback(fakeFeedback);
  };

  return (
    <div className="p-4">
      <Card>
        <CardHeader>
          <CardTitle>Analyze Your Performance</CardTitle>
          <CardDescription>
            Upload a video (drag and drop or click) or try a mock analysis.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* Drag and Drop Area */}
          <div
            {...getRootProps()}
            className={`p-6 border-2 border-dashed rounded-md cursor-pointer text-center ${
              isDragActive ? "bg-gray-100" : ""
            }`}
          >
            <input {...getInputProps()} />
            {isDragActive ? (
              <p>Drop the video file here...</p>
            ) : (
              <p>Drag and drop a video file here, or click to select a file</p>
            )}
          </div>

          {/* Mock Upload Button */}
          <Button onClick={handleMockUpload} className="mt-4">
            Mock Upload
          </Button>

          {/* Analyze Performance Button (only show if a real video is uploaded) */}
          {videoFile && (
            <Button
              onClick={handleAnalyzePerformance}
              className="mt-4"
              disabled={isLoading}
            >
              {isLoading ? "Analyzing..." : "Analyze Performance"}
            </Button>
          )}

          {/* Video Player (for mock upload) */}
          {showMockVideo && (
            <div className="mt-4">
              <ReactPlayer url={MOCK_VIDEO_URL} controls width="100%" />
            </div>
          )}

          {/* Instrument Picker */}
          <div className="mt-4">
            <Select>
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Select Instrument" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ukulele">Ukulele</SelectItem>
                <SelectItem disabled value={""}>More instruments coming soon!</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Scoring Test Area */}
          <Card className="mt-4">
            <CardHeader>
              <CardTitle>Scoring Test</CardTitle>
              <CardDescription>
                Manually adjust scores to see how they affect the feedback.
              </CardDescription>
            </CardHeader>
            <CardContent>
              {/* Input fields for test scores (same as before) */}
              <div className="grid grid-cols-3 gap-4">
                {/* Visual Feedback Test Scores */}
                <div>
                  <label
                    htmlFor="posture"
                    className="block text-sm font-medium text-gray-700"
                  >
                    Posture (0-10)
                  </label>
                  <input
                    type="range"
                    id="posture"
                    min="0"
                    max="10"
                    value={testScores.posture}
                    onChange={(e) =>
                      setTestScores({
                        ...testScores,
                        posture: parseInt(e.target.value, 10),
                      })
                    }
                    className="mt-1 w-full"
                  />
                </div>
                <div>
                  <label
                    htmlFor="finger_position"
                    className="block text-sm font-medium text-gray-700"
                  >
                    Finger Position (0-10)
                  </label>
                  <input
                    type="range"
                    id="finger_position"
                    min="0"
                    max="10"
                    value={testScores.finger_position}
                    onChange={(e) =>
                      setTestScores({
                        ...testScores,
                        finger_position: parseInt(e.target.value, 10),
                      })
                    }
                    className="mt-1 w-full"
                  />
                </div>
                <div>
                  <label
                    htmlFor="confidence"
                    className="block text-sm font-medium text-gray-700"
                  >
                    Confidence (0-10)
                  </label>
                  <input
                    type="range"
                    id="confidence"
                    min="0"
                    max="10"
                    value={testScores.confidence}
                    onChange={(e) =>
                      setTestScores({
                        ...testScores,
                        confidence: parseInt(e.target.value, 10),
                      })
                    }
                    className="mt-1 w-full"
                  />
                </div>

                {/* Audio Feedback Test Scores */}
                <div>
                  <label
                    htmlFor="tempo"
                    className="block text-sm font-medium text-gray-700"
                  >
                    Tempo (0-10)
                  </label>
                  <input
                    type="range"
                    id="tempo"
                    min="0"
                    max="10"
                    value={testScores.tempo}
                    onChange={(e) =>
                      setTestScores({
                        ...testScores,
                        tempo: parseInt(e.target.value, 10),
                      })
                    }
                    className="mt-1 w-full"
                  />
                </div>
                <div>
                  <label
                    htmlFor="pitch"
                    className="block text-sm font-medium text-gray-700"
                  >
                    Pitch (0-10)
                  </label>
                  <input
                    type="range"
                    id="pitch"
                    min="0"
                    max="10"
                    value={testScores.pitch}
                    onChange={(e) =>
                      setTestScores({
                        ...testScores,
                        pitch: parseInt(e.target.value, 10),
                      })
                    }
                    className="mt-1 w-full"
                  />
                </div>
                <div>
                  <label
                    htmlFor="rhythm"
                    className="block text-sm font-medium text-gray-700"
                  >
                    Rhythm (0-10)
                  </label>
                  <input
                    type="range"
                    id="rhythm"
                    min="0"
                    max="10"
                    value={testScores.rhythm}
                    onChange={(e) =>
                      setTestScores({
                        ...testScores,
                        rhythm: parseInt(e.target.value, 10),
                      })
                    }
                    className="mt-1 w-full"
                  />
                </div>
              </div>
              <Button onClick={handleTestScoring} className="mt-4">
                Test Scoring
              </Button>
            </CardContent>
          </Card>

          {/* Feedback and Spider Chart Display */}
          {feedback && (
            <div className="mt-8">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Summary Grades */}
                <Card>
                  <CardHeader>
                    <CardTitle>Summary</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-3 gap-4">
                      <div>
                        <div
                          className="text-lg font-bold"
                          style={{ color: feedback.summary.visual_grade[1] }}
                        >
                          Visual: {feedback.summary.visual_grade[0]}
                        </div>
                      </div>
                      <div>
                        <div
                          className="text-lg font-bold"
                          style={{ color: feedback.summary.audio_grade[1] }}
                        >
                          Audio: {feedback.summary.audio_grade[0]}
                        </div>
                      </div>
                      <div>
                        <div
                          className="text-lg font-bold"
                          style={{ color: feedback.summary.overall_grade[1] }}
                        >
                          Overall: {feedback.summary.overall_grade[0]}
                        </div>
                      </div>
                    </div>
                    <p className="mt-4">
                      {feedback.summary.performance_summary}
                    </p>
                  </CardContent>
                </Card>

                {/* Spider Charts */}
                <Card>
                  <CardHeader>
                    <CardTitle>Performance Analysis</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex justify-center">
                      <SpiderChart
                        data={{
                          labels: [
                            "Posture",
                            "Finger Position",
                            "Confidence",
                            "Tempo",
                            "Pitch",
                            "Rhythm",
                          ],
                          datasets: [
                            {
                              label: "Visual",
                              data: [
                                feedback.visual_feedback.posture.score,
                                feedback.visual_feedback.finger_position.score,
                                feedback.visual_feedback.confidence.score,
                              ],
                              backgroundColor: "rgba(76, 201, 240, 0.3)",
                              borderColor: "#4CC9F0",
                              borderWidth: 1,
                            },
                            {
                              label: "Audio",
                              data: [
                                feedback.audio_feedback.tempo.score,
                                feedback.audio_feedback.pitch.score,
                                feedback.audio_feedback.rhythm.score,
                              ],
                              backgroundColor: "rgba(255, 165, 0, 0.3)",
                              borderColor: "#FFA500",
                              borderWidth: 1,
                            },
                          ],
                        }}
                        options={{
                          scales: {
                            r: {
                              min: 0,
                              max: 10,
                              ticks: {
                                stepSize: 1,
                                color: "white",
                              },
                              pointLabels: {
                                color: "white",
                              },
                              grid: {
                                color: "rgba(255, 255, 255, 0.2)",
                              },
                              angleLines: {
                                color: "white",
                              },
                            },
                          },
                        }}
                      />
                    </div>
                  </CardContent>
                </Card>

                {/* Detailed Feedback */}
                <Card>
                  <CardHeader>
                    <CardTitle>Visual Feedback</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {Object.entries(feedback.visual_feedback).map(
                      ([key, value]: [string, any]) => (
                        <div key={key}>
                          <span style={{ color: value.style_rating[1] }}>
                            {key.replace("_", " ").toUpperCase()}:{" "}
                            {value.style_rating[0]}
                          </span>
                          {value.feedback &&
                            value.feedback.map(
                              (item: string, index: number) => (
                                <p key={index}>{item}</p>
                              )
                            )}
                        </div>
                      )
                    )}
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Audio Feedback</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {Object.entries(feedback.audio_feedback).map(
                      ([key, value]: [string, any]) => (
                        <div key={key}>
                          <span style={{ color: value.style_rating[1] }}>
                            {key.replace("_", " ").toUpperCase()}:{" "}
                            {value.style_rating[0]}
                          </span>
                          {value.feedback &&
                            value.feedback.map(
                              (item: string, index: number) => (
                                <p key={index}>{item}</p>
                              )
                            )}
                        </div>
                      )
                    )}
                  </CardContent>
                </Card>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
