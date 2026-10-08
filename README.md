# MotionLift

A computer vision application that provides real-time form feedback and analysis for the shoulder press. It uses MediaPipe pose detection to track body landmarks from a webcam or uploaded video, counts repetitions, grades form, and generates training recommendations through the OpenAI API.

## Features

- **Real-time form analysis** from a webcam feed
- **Automatic rep counting** with lenient thresholds so reps are not missed
- **Depth detection** against an optimal elbow angle range (85-98 degrees)
- **Form feedback** covering elbow extension, depth, arm symmetry, and elbow flaring
- **Video analysis** for recorded workouts, with rep-by-rep metrics
- **AI-generated recommendations** via the OpenAI API
- **Session reports** with summary statistics

## Tech Stack

| Layer | Technologies |
| --- | --- |
| Frontend | React, React Webcam, Axios |
| Backend | Python 3.8+, FastAPI, Uvicorn |
| Computer vision | MediaPipe Pose, OpenCV, NumPy |
| AI | OpenAI API |

## Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- A webcam (for real-time tracking)
- An OpenAI API key

## Installation

### Backend

1. Clone the repository and enter the project directory:

   ```bash
   git clone https://github.com/yourusername/ai-fitness-trainer.git
   cd ai-fitness-trainer/backend
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Download the MediaPipe pose model:

   ```bash
   python download_model.py
   ```

   If the download fails, fetch the file manually and place it in the `backend` directory:

   ```bash
   curl -O https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task
   ```

5. Create a `.env` file in the `backend` directory:

   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

6. Start the server:

   ```bash
   uvicorn main:app --reload
   ```

   The API runs at `http://localhost:8000`.

### Frontend

```bash
cd frontend
npm install
npm start
```

The app runs at `http://localhost:3000`.

## Project Structure

```
ai-fitness-trainer/
├── backend/
│   ├── main.py                    # FastAPI application
│   ├── PoseModule.py              # MediaPipe pose detection wrapper
│   ├── analyze_video.py           # Video analysis logic
│   ├── download_model.py          # Model download script
│   ├── pose_landmarker_lite.task  # MediaPipe model file
│   └── requirements.txt           # Python dependencies
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── LiveTracker.jsx    # Real-time webcam tracking
│   │   │   ├── VideoUpload.jsx    # Video upload interface
│   │   │   └── ResultsDisplay.jsx # Analysis results
│   │   ├── App.js
│   │   └── index.js
│   └── package.json
├── models/
│   └── pose_landmarker_lite.task
├── .gitignore
├── LICENSE
└── README.md
```

## Usage

### Real-Time Tracking

1. Open the application in your browser and allow camera access.
2. Position yourself so your full upper body is visible.
3. Start with your arms extended overhead.
4. Perform shoulder presses and review the live feedback.

### Standalone Live Demo

Run the demo script directly from the backend directory:

```bash
python ShoulderPressCounter.py
```

Keyboard controls:

| Key | Action |
| --- | --- |
| `q` | Quit |
| `r` | Reset rep counter |
| `s` | Save the current session report |

### Video Analysis

1. Open the **Upload Video** tab.
2. Select a recorded workout video.
3. Click **Analyze**.
4. Review the metrics and recommendations.

## Metrics and Thresholds

### Rep Counting (lenient)

| Parameter | Value | Description |
| --- | --- | --- |
| Extension | 150° | Elbow angle that counts as extended |
| Bent | 120° | Elbow angle that counts as the bottom of the rep |
| Wrist clearance | 10 px | Minimum overhead wrist position |
| Elbow tolerance | 170 px | Allowed variation in arm height |

### Depth (optimal range)

| Elbow angle | Result |
| --- | --- |
| Above 98° | Not deep enough |
| 85°-98° | Optimal depth |
| Below 85° | Too deep (shifts emphasis toward the upper chest) |

### Form Grading (strict)

| Parameter | Threshold | Description |
| --- | --- | --- |
| Max elbow angle | 155° | Arms must extend fully at the top |
| Arm difference | 20° | Maximum allowed left/right difference |
| Shoulder angle | 75° | Maximum elbow flare from the body |

### Feedback Categories

- **Perfect form:** all metrics are within range.
- **Not deep enough:** the sweet-spot depth was not reached.
- **Too deep:** the press went below the optimal range.
- **Incomplete extension:** the arms did not fully extend at the top.
- **Arms uneven:** left and right arms differ beyond the allowed threshold.
- **Elbows flaring:** the elbows drift too far from the body.

### Elbow Flaring

Elbow flaring occurs when the elbows move out to the sides, perpendicular to the torso, during the press. Elbows held slightly forward of the body (roughly 30-45° from the torso) are safer and stronger. Flaring increases the risk of shoulder impingement and rotator cuff strain, reduces pressing power, and places excess stress on the shoulder joint.

## Configuration

Thresholds are defined in `analyze_video.py` and the main tracking script:

```python
# Rep counting (lenient)
EXTENSION_THRESHOLD = 150
BENT_THRESHOLD = 120
WRIST_CLEARANCE = 10
ELBOW_TOLERANCE = 170

# Optimal depth
SWEET_SPOT_MIN = 85
SWEET_SPOT_MAX = 98

# Form grading (strict)
FEEDBACK_MAX_ELBOW = 155
FEEDBACK_DIFF = 20
FEEDBACK_SHOULDER = 75
```

## Troubleshooting

**Camera not working**
- Confirm the browser has camera permission.
- Close any other application using the camera.
- Try Chrome.

**Pose not detected**
- Use bright, even lighting.
- Stand 3-6 feet from the camera.
- Keep your shoulders through hips in frame.
- Wear clothing that contrasts with the background and keep the background uncluttered.

**Reps not counting**
- Start with arms fully extended (elbow angle of 150° or more).
- Lower to at least 120°.
- Keep elbows at shoulder height throughout the movement.
- Return to full extension to complete each rep.
- Check the on-screen position indicators (for example, "Wrists: OK" and "Elbows: OK").

**High CPU usage**
- Close other applications that use the camera.
- Reduce the video resolution.
- Use video upload instead of live tracking.

**API connection issues**
- Verify the backend is running on `http://localhost:8000`.
- Confirm `.env` contains a valid OpenAI API key.
- Check that no firewall is blocking local connections.
- Review the browser console for error details.

## Privacy and Security

- The OpenAI API key is used server-side only and is never exposed to the client.
- Video recordings are not stored. Only pose landmarks and derived metrics are used.
- Collected data is limited to rep counts, form metrics, session timestamps, and device type.
- No location data or personal information is collected.
- No third-party analytics or tracking cookies are used.

## Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Describe your change"`
4. Push the branch: `git push origin feature/your-feature`
5. Open a pull request.

Guidelines:
- Follow PEP 8 for Python and ESLint rules for JavaScript/React.
- Write descriptive commit messages.
- Add tests for new features.
- Update documentation as needed.

## References

- [MediaPipe documentation](https://google.github.io/mediapipe/)
- [FastAPI documentation](https://fastapi.tiangolo.com/)
- [React documentation](https://react.dev/)
- [Proper shoulder press form](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6279907/)
- [Biomechanics of the overhead press](https://journals.lww.com/nsca-scj/fulltext/2016/04000/the_overhead_press.7.aspx)

## License

Released under the MIT License. See [LICENSE](LICENSE) for details.

## Authors

Abas Yakoobi, Nitin Tammina, Abel Tolla

## Acknowledgments

Google's MediaPipe team, the FastAPI community, OpenAI, the React team, and the OpenCV contributors.
