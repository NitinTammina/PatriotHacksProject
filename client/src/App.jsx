import { useState } from 'react'
import './App.css'

function App() {
  const [videoFile, setVideoFile] = useState(null);
  const [feedback, setFeedback] = useState("Waiting for analysis...");
  const [isLoading, setIsLoading] = useState(false);

  const handleVideoUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    console.log("File selected:", file.name, file.size, "bytes");

    // show video locally
    const url = URL.createObjectURL(file);
    setVideoFile(url);

    // send to backend - USE CODESPACES URL
    const formData = new FormData();
    formData.append("file", file);

    setFeedback("Analyzing form...");
    setIsLoading(true);

    try {
      // Use Codespaces forwarded URL - CORS is already configured
      const backendUrl = "https://friendly-orbit-jjrq75v6446r2q6jp-8000.app.github.dev/analyze";
      
      console.log("Uploading to:", backendUrl);
      
      const res = await fetch(backendUrl, {
        method: "POST",
        body: formData,
      });

      console.log("Response status:", res.status);

      if (!res.ok) {
        const errorText = await res.text();
        console.error("Error response:", errorText);
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      
      const data = await res.json();
      console.log("Success! Data:", data);

      if (data.error) {
        setFeedback(`Error: ${data.error}`);
        return;
      }

      setFeedback(data.ai_summary || "Analysis complete!");

    } catch (err) {
      console.error("Upload error:", err);
      setFeedback(`Connection failed: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <header className="header">
        Fit Trainer 🏋️‍♂️
      </header>
    
      <main className="main-container">
        <div className="motto">
          AI powered application to improve your fitness
        </div>

        <div className="content-row">
          <div className="video-section">
            <video className="video-feed"
              src={videoFile || null}
              controls
              autoPlay
              playsInline
            />
            <label 
              className="button"
              htmlFor="video-upload"
              style={{
                display: "inline-block",
                marginTop: "15px",
                padding: "10px 20px",
                backgroundColor: isLoading ? "#999" : "#6c2929",
                color: "rgb(249, 247, 243)",
                borderRadius: "8px",
                cursor: isLoading ? "not-allowed" : "pointer",
                fontWeight: "bold",
                fontSize: "23px",
                textAlign: "center",
                writingMode: "vertical-rl",   
                transform: "rotate(180deg)",
                opacity: isLoading ? 0.6 : 1
              }}
            >
              {isLoading ? "ANALYZING..." : "UPLOAD VIDEO"}
            </label>
            <input 
              type="file" 
              id="video-upload" 
              accept="video/*" 
              onChange={handleVideoUpload}
              disabled={isLoading}
              style={{ display: "none" }} 
            />
          </div>

          <div className="ai-section">
            <h2>AI Form Feedback</h2>
            <div className="ai-box">
              {feedback}
            </div>
          </div>
        </div>
      </main>
    </>
  );
}

export default App