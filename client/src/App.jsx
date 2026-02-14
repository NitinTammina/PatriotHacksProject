import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

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
            <video className="video-feed" autoPlay playsInline />
          </div>
        

       <div className="ai-section">
        <h2>AI Form Feedback</h2>
          <div className="ai-box">
            Waiting for analysis...
          </div>
        </div>
       </div>

      </main>
    </>
        
  )
}

export default App
