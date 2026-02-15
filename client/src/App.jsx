import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

  function App() {
  const [videoFile, setVideoFile] = useState(null);
  const [feedback, setFeedback] = useState("Waiting for analysis...");

  const handleVideoUpload = async (event) => {
  const file = event.target.files[0];
  if (!file) return;

  // show video locally
  const url = URL.createObjectURL(file);
  setVideoFile(url);

  // send to backend
  const formData = new FormData();
  formData.append("file", file); // MUST be "file" (matches FastAPI)

  setFeedback("Analyzing form...");

  try {
    const res = await fetch("http://localhost:8000/analyze", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    console.log(data);

    if (data.error) {
      setFeedback(data.error);
      return;
    }

    setFeedback(
      `Frames analyzed: ${data.framesProcessed}
       Frames with body detected: ${data.framesWithPose}`
    );
  } catch (err) {
    console.error(err);
    setFeedback("Server error. Is backend running?");
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
              src={videoFile || ""}
              controls
              autoPlay
              playsInline
            />
            <label 
              className= "button"
              htmlFor="video-upload"
              style={{
                display: "inline-block",
                marginTop: "15px",
                padding: "10px 20px",
                backgroundColor: "#6c2929",
                color: "rgb(249, 247, 243)",
                borderRadius: "8px",
                cursor: "pointer",
                fontWeight: "bold",
                fontSize: "23px",
                textAlign: "center",
                writingMode: "vertical-rl",   
                transform: "rotate(180deg)"
                
              }}
            >UPLOAD VIDEO</label>
            <input type="file" id="video-upload" accept="video/*" onChange={handleVideoUpload}
             style={{ display: "none" }} />
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
