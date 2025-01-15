import { baseUrl } from "@/config/api";
import { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { Progress } from "@/components/ui/progress";

export default function PracticeSong() {
  const [skillLevel, setSkillLevel] = useState("beginner");
  const [instrument, setInstrument] = useState("Piano");
  const [style, setStyle] = useState("classical");
  const [practiceSongAudio, setPracticeSongAudio] = useState(null);
  const [practiceInstructions, setPracticeInstructions] = useState([]);
  const [additionalNotes, setAdditionalNotes] = useState("");
  const [sheetMusicPDF, setSheetMusicPDF] = useState(null);

  const handleGeneratePracticeSong = async () => {
    try {
      const response = await fetch(`${baseUrl}/api/generate-practice-song`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          skill_level: skillLevel.toLowerCase(),
          instrument,
          style,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          `HTTP error ${response.status}: ${
            errorData.message || "Failed to fetch practice song"
          }`
        );
      }

      const songData = await response.json();
      if (songData.sheet_music && songData.sheet_music.audio_data) {
        const audioBlob = new Blob(
          [
            Uint8Array.from(atob(songData.sheet_music.audio_data), (c) =>
              c.charCodeAt(0)
            ),
          ],
          { type: "audio/wav" }
        );
        const audioUrl = URL.createObjectURL(audioBlob);
        setPracticeSongAudio(audioUrl);
        setPracticeInstructions(songData.exercises || []);
        setAdditionalNotes(songData.notes || "");

        if (songData.sheet_music.sheet_music_data) {
          const pdfBlob = new Blob(
            [
              Uint8Array.from(
                atob(songData.sheet_music.sheet_music_data),
                (c) => c.charCodeAt(0)
              ),
            ],
            { type: "application/pdf" }
          );
          setSheetMusicPDF(URL.createObjectURL(pdfBlob));
        }
      } else {
        throw new Error(
          "Invalid song data received: Missing audio or sheet music."
        );
      }
    } catch (error) {
      console.error("Error generating practice song:", error);
      setPracticeSongAudio(null);
      setPracticeInstructions([]);
      setAdditionalNotes("");
      setSheetMusicPDF(null);
    }
  };

  useEffect(() => {
    return () => {
      if (practiceSongAudio) {
        URL.revokeObjectURL(practiceSongAudio);
      }
      if (sheetMusicPDF) {
        URL.revokeObjectURL(sheetMusicPDF);
      }
    };
  }, [practiceSongAudio, sheetMusicPDF]);

  return (
    <div className="p-4">
      <Card>
        <CardHeader>
          <CardTitle>Practice Songs</CardTitle>
          <CardDescription>
            Generate practice songs based on your preferences.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4">
            <Select onValueChange={setSkillLevel} value={skillLevel}>
              <SelectTrigger>
                <SelectValue placeholder="Skill Level" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="beginner">Beginner</SelectItem>
                <SelectItem value="intermediate">Intermediate</SelectItem>
                <SelectItem value="advanced">Advanced</SelectItem>
              </SelectContent>
            </Select>

            <Select onValueChange={setInstrument} value={instrument}>
              <SelectTrigger>
                <SelectValue placeholder="Instrument" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Piano">Piano</SelectItem>
                <SelectItem value="Guitar">Guitar</SelectItem>
                <SelectItem value="Violin">Violin</SelectItem>
              </SelectContent>
            </Select>

            <Select onValueChange={setStyle} value={style}>
              <SelectTrigger>
                <SelectValue placeholder="Style" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="classical">Classical</SelectItem>
                <SelectItem value="jazz">Jazz</SelectItem>
                <SelectItem value="pop">Pop</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Button className="mt-4" onClick={handleGeneratePracticeSong}>
            Generate Practice Song
          </Button>

          {practiceSongAudio && (
            <div className="mt-4">
              <audio controls src={practiceSongAudio}></audio>

              <div className="mt-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Practice Instructions</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul>
                      {practiceInstructions.map((instruction, index) => (
                        <li key={index}>{instruction}</li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>

                <Card className="mt-4">
                  <CardHeader>
                    <CardTitle>Additional Notes</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p>{additionalNotes}</p>
                  </CardContent>
                </Card>

                {sheetMusicPDF && (
                  <div className="mt-4">
                    <iframe
                      src={sheetMusicPDF}
                      title="Sheet Music"
                      width="100%"
                      height="500px"
                    />
                  </div>
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
