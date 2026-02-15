# AI Fitness Trainer 🏋️‍♂️

An intelligent fitness training application that provides real-time form feedback and analysis for shoulder press exercises using computer visi
on and AI.

## 🌟 Features

- **Real-time Form Analysis**: Track your shoulder press form in real-time using your webcam
- **Smart Rep Counting**: Automatic rep counting with lenient thresholds for seamless workout tracking
- **Sweet Spot Detection**: Visual feedback for optimal depth (85-98° elbow angle)
- **Detailed Form Feedback**: Comprehensive analysis including:
  - Elbow extension and depth
  - Arm symmetry detection
  - Elbow flaring warnings
  - Rep-by-rep performance metrics
- **Video Analysis**: Upload recorded workout videos for post-session analysisU
- **AI-Powered Insights**: OpenAI integration for personalized training recommendations
- **Performance Reports**: Detailed statistics and progress tracking

## 🛠️ Tech Stack

### Frontend
- **React**: Modern, responsive user interface
- **React Webcam**: Real-time video capture
- **Axios**: HTTP client for API communication

### Backend
- **FastAPI**: High-performance Python web framework
- **Python 3.8+**: Core programming language
- **MediaPipe**: Google's ML solution for pose detection
- **OpenCV**: Computer vision and image processing
- **NumPy**: Numerical computing

### AI & ML
- **MediaPipe Pose**: Body landmark detection and tracking
- **OpenAI API**: Intelligent form feedback and recommendations

## 📋 Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- Webcam (for real-time tracking)
- OpenAI API key

## 🚀 Installation

### Backend Setup

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/ai-fitness-trainer.git
cd ai-fitness-trainer
```

2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

**requirements.txt:**
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
opencv-python==4.8.1.78
mediapipe==0.10.9
numpy==1.24.3
python-dotenv==1.0.0
openai==1.3.0
pydantic==2.5.0
```

4. **Download the MediaPipe Pose model:**
```bash
python download_model.py
```

**download_model.py:**
```python
import urllib.request
import os

model_url = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task"
model_path = "pose_landmarker_lite.task"

if not os.path.exists(model_path):
    print("Downloading pose landmarker model...")
    try:
        urllib.request.urlretrieve(model_url, model_path)
        print(f"✓ Model downloaded successfully to {model_path}")
    except Exception as e:
        print(f"Error downloading model: {e}")
        print("Please download manually from:")
        print(model_url)
else:
    print(f"✓ Model already exists at {model_path}")
```

5. **Create a `.env` file in the backend directory:**
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

6. **Start the FastAPI server:**
```bash
uvicorn main:app --reload
```

The backend will run on `http://localhost:8000`

### Frontend Setup

1. **Navigate to the frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Start the development server:**
```bash
npm start
```

The frontend will run on `http://localhost:3000`

## 📦 Project Structure
```
ai-fitness-trainer/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── PoseModule.py          # MediaPipe pose detection wrapper
│   ├── analyze_video.py       # Video analysis logic
│   ├── download_model.py      # Model download script
│   ├── pose_landmarker_lite.task  # MediaPipe model file
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── LiveTracker.jsx    # Real-time webcam tracking
│   │   │   ├── VideoUpload.jsx    # Video upload interface
│   │   │   └── ResultsDisplay.jsx # Analysis results
│   │   ├── App.js
│   │   └── index.js
│   ├── package.json
│   └── README.md
├── models/
│   └── pose_landmarker_lite.task
├── .gitignore
├── README.md
└── LICENSE
```

## 🎯 Usage

### Real-Time Tracking

1. Open the application in your browser
2. Allow camera permissions
3. Position yourself so your full upper body is visible
4. Start with arms extended overhead
5. Perform shoulder presses and receive instant feedback

**Controls:**
- `q` - Quit
- `r` - Reset counter
- `s` - Save current session report

### How to Run Live Demo Session

Use the command "python ShoulderPressCounter.py"

### Video Analysis

1. Navigate to the "Upload Video" tab
2. Select a video file of your workout
3. Click "Analyze"
4. Review detailed metrics and recommendations

## 📊 Understanding the Metrics

### Rep Counting Thresholds (Lenient)
- **Extension**: 150° - Arms must reach this angle to count as "extended"
- **Bent**: 120° - Arms must bend to this angle to count as "down"
- **Wrist Clearance**: 10px - Minimal overhead position requirement
- **Elbow Tolerance**: 170px - Generous tolerance for arm height

### Sweet Spot (Optimal Depth)
- **Perfect Range**: 85-98° elbow angle
- **Above 98°**: Not deep enough - go lower
- **85-98°**: Perfect depth! - optimal shoulder activation
- **Below 85°**: Too deep - targets upper chest more

### Form Grading Thresholds (Strict)
- **Max Elbow**: 155° - Must extend well at the top
- **Arm Difference**: 20° - Arms should be relatively even
- **Shoulder Angle**: 75° - Elbows shouldn't flare too much

### Feedback Categories
- ✅ **Perfect Form**: All metrics within optimal ranges
- ⚠️ **Not Deep Enough**: Didn't reach sweet spot depth
- ⚠️ **Too Deep**: Went below optimal range (upper chest focus)
- ⚠️ **Incomplete Extension**: Didn't fully extend at top
- ⚠️ **Arms Uneven**: Significant difference between left and right
- ⚠️ **Elbows Flaring**: Elbows too far from body

### What is Elbow Flaring?
**Elbow flaring** occurs when your elbows stick out too far to the sides (perpendicular to your body) during the shoulder press.

**Good Form (elbows slightly forward):**
```
        Head
         O
    Elbow/  \Elbow
        |    |
      Body  Body
      
Elbows at ~30-45° angle from body
```

**Bad Form (elbows flaring):**
```
        Head
         O
  Elbow _____ Elbow
        |    |
      Body  Body
      
Elbows at 90° (perpendicular to body)
```

**Why it matters:**
- ❌ Increases risk of shoulder impingement and rotator cuff injury
- ❌ Reduces power and mechanical advantage
- ❌ Places excessive stress on shoulder joint
- ✅ Proper form: Elbows slightly forward creates safer, stronger pressing angle

## 🔧 Configuration

### Adjusting Thresholds

Edit the threshold values in `analyze_video.py` or the main tracking script:
```python
# ========================================
# THRESHOLDS CONFIGURATION
# ========================================

# Rep Counting (Lenient - easy to count reps)
EXTENSION_THRESHOLD = 150      # Arms extended
BENT_THRESHOLD = 120           # Arms bent down
WRIST_CLEARANCE = 10           # Minimal overhead clearance
ELBOW_TOLERANCE = 170          # Generous arm height tolerance

# Sweet Spot (Optimal shoulder activation)
SWEET_SPOT_MIN = 85            # Lower bound for optimal depth
SWEET_SPOT_MAX = 98            # Upper bound for optimal depth

# Form Grading (Strict - proper form required)
FEEDBACK_MAX_ELBOW = 155       # Must extend well
FEEDBACK_DIFF = 20             # Arms should be even
FEEDBACK_SHOULDER = 75         # Elbows must stay in (prevent flaring)
```

## 🐛 Troubleshooting

### Camera Not Working
- Ensure browser has camera permissions
- Check if another application is using the camera
- Try a different browser (Chrome recommended)
- Check that your webcam is properly connected

### Pose Not Detected
- **Ensure adequate lighting** - Bright, even lighting works best
- **Stand 3-6 feet from the camera** - Too close or too far reduces accuracy
- **Make sure your full upper body is visible** - Include shoulders to hips
- **Wear contrasting clothing** - Avoid clothing that blends with background
- **Clear background** - Minimize clutter behind you

### Rep Not Counting
- **Ensure arms start fully extended overhead** - Begin at 150°+ elbow angle
- **Check that you're reaching the minimum depth** - Go down to at least 120°
- **Verify elbows stay at shoulder height throughout** - Don't drop arms to sides
- **Arms must return to full extension to count** - Complete the full range of motion
- **Check position indicators** - Watch for "Wrists: OK" and "Elbows: OK" on screen

### Model Download Issues
If the automatic download fails, manually download:
```bash
# Manual download
wget https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task

# Or using curl
curl -O https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task
```

### High CPU Usage
- Close other applications using the camera
- Reduce video resolution if possible
- Ensure you're using hardware acceleration in your browser
- Consider using the video upload feature instead of real-time tracking

### API Connection Issues
- Verify FastAPI backend is running on `http://localhost:8000`
- Check `.env` file contains valid OpenAI API key
- Ensure no firewall is blocking connections
- Check browser console for detailed error messages

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use ESLint for JavaScript/React code
- Write descriptive commit messages
- Add tests for new features
- Update documentation as needed

## 🔐 Privacy & Security

We take your privacy seriously:

- ✅ **All video processing happens locally** - Video is processed on your device
- ✅ **No video data stored on servers** - Only metrics are transmitted
- ✅ **Anonymized metrics only** - No personally identifiable information
- ✅ **Secure API communication** - All API calls use HTTPS
- ✅ **OpenAI API calls server-side** - Your API key is never exposed to the client
- ✅ **No third-party tracking** - We don't use analytics or tracking cookies

### Data We Collect
- Rep counts and form metrics (anonymized)
- Timestamp of workout sessions
- Device type (for compatibility improvements)

### Data We DON'T Collect
- Video recordings
- Personal information
- Location data
- Biometric data beyond pose landmarks

## 📄 License

This project is licensed under the MIT License:
```
MIT License

Copyright (c) 2024 AI Fitness Trainer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 👥 Authors

- **Your Name** - *Initial work* - [YourGitHub](https://github.com/yourusername)

## 🙏 Acknowledgments

- **MediaPipe team at Google** - For the excellent pose detection model
- **FastAPI community** - For the high-performance web framework
- **OpenAI** - For the GPT API enabling intelligent feedback
- **React team** - For the amazing frontend library
- **OpenCV contributors** - For computer vision capabilities
- **All contributors and testers** - Your feedback makes this better!

## 📧 Contact & Support

### Get Help
- 📖 **Documentation**: [Read the docs](https://github.com/yourusername/ai-fitness-trainer/wiki)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/yourusername/ai-fitness-trainer/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/ai-fitness-trainer/discussions)
- 💬 **Discord**: [Join our community](https://discord.gg/yourserver)

### Contact Information
- **Email**: your.email@example.com
- **Twitter**: [@yourhandle](https://twitter.com/yourhandle)
- **Website**: [yourwebsite.com](https://yourwebsite.com)

### Reporting Security Issues
If you discover a security vulnerability, please email security@yourproject.com instead of using the issue tracker.

## ⭐ Star Us!

If you find this project helpful, please consider giving it a star on GitHub! It helps others discover the project and motivates us to keep imp
roving it.

[![GitHub stars](https://img.shields.io/github/stars/yourusername/ai-fitness-trainer.svg?style=social&label=Star)](https://github.com/yourusern
ame/ai-fitness-trainer)

## 📈 Project Stats

![GitHub issues](https://img.shields.io/github/issues/yourusername/ai-fitness-trainer)
![GitHub pull requests](https://img.shields.io/github/issues-pr/yourusername/ai-fitness-trainer)
![GitHub](https://img.shields.io/github/license/yourusername/ai-fitness-trainer)
![GitHub last commit](https://img.shields.io/github/last-commit/yourusername/ai-fitness-trainer)

---

## 📚 Additional Resources

### Tutorials
- [Getting Started Guide](docs/getting-started.md)
- [API Documentation](docs/api-reference.md)
- [Customizing Thresholds](docs/customization.md)
- [Video Recording Tips](docs/video-tips.md)

### Related Projects
- [MediaPipe Documentation](https://google.github.io/mediapipe/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)

### Scientific References
- [Proper Shoulder Press Form](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6279907/)
- [Biomechanics of Overhead Press](https://journals.lww.com/nsca-scj/fulltext/2016/04000/the_overhead_press.7.aspx)

---

## .gitignore

Create a `.gitignore` file in your project root:
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
venv/
env/
ENV/
env.bak/
venv.bak/

# MediaPipe model
*.task
!pose_landmarker_lite.task

# Environment variables
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*.swn
.DS_Store

# Jupyter Notebook
.ipynb_checkpoints

# Python testing
.pytest_cache/
.coverage
htmlcov/
.tox/
.nox/

# Frontend
node_modules/
build/
dist/
.cache/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnp
.pnp.js

# Testing
coverage/

# Production
/build

# Misc
.DS_Store
.env.local
.env.development.local
.env.test.local
.env.production.local
Thumbs.db

# Logs
*.log
logs/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Temporary files
*.tmp
*.temp
.temp/
tmp/

# Video files (optional - add if you don't want to commit test videos)
*.mp4
*.avi
*.mov
*.mkv

# Model weights (if you have custom trained models)
models/*.h5
models/*.pb
models/*.onnx
```

---

Made with ❤️ by fitness enthusiasts, for fitness enthusiasts

<<<<<<< HEAD
**Train smarter, not harder! 💪🤖**
=======
**Train smarter, not harder! 💪🤖**
