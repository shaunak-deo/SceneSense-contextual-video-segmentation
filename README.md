# SceneSense: AI-Powered Video Segmentation & Ad Suggestion

SceneSense is an intelligent web application that automatically segments videos, analyzes their content using AI, and suggests relevant advertisements based on the context of each segment. Perfect for content creators, marketers, and video producers looking to understand and monetize their content better.

## 🌟 Features

- **Smart Video Segmentation**: Automatically detects scene changes and segments your video
- **AI-Powered Scene Analysis**: Uses advanced AI to generate descriptive labels for each segment
- **Intelligent Ad Matching**: Suggests relevant advertisements based on scene content
- **Visual Preview**: Shows key frames from each segment for quick reference
- **Modern UI/UX**: Clean, responsive interface with smooth interactions
- **Real-time Processing**: Live progress tracking and instant results

## 🚀 Quick Start

### Using Docker (Recommended)

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/SceneSense-contextual-video-segmentation.git
   cd SceneSense-contextual-video-segmentation
   ```

2. **Configure Environment Variables**

   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Build and Run with Docker Compose**

   ```bash
   docker-compose up --build
   ```

4. Open your browser and visit `http://localhost:5001`

### Manual Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/SceneSense-contextual-video-segmentation.git
   cd SceneSense-contextual-video-segmentation
   ```

2. **Set Up Virtual Environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   Create a `.env` file in the root directory:

   ```env
   OPENAI_API_KEY=your_openai_api_key
   GOOGLE_API_KEY=your_google_api_key
   GOOGLE_CSE_ID=your_google_cse_id
   ```

5. **Run the Application**

   ```bash
   python run.py
   ```

6. Open your browser and visit `http://localhost:5001`

## 🛠️ Technical Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **AI/ML**: OpenAI GPT-4 Vision API
- **Video Processing**: FFmpeg, scene-detect
- **Ad Integration**: Google Custom Search API
- **Containerization**: Docker

## 📁 Project Structure

```
SceneSense/
├── app/
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   ├── templates/
│   ├── __init__.py
│   ├── ad_search.py
│   ├── frame_extractor.py
│   ├── openai_labeler.py
│   ├── segmenter.py
│   ├── utils.py
│   └── web_app.py
├── uploads/
├── .env
├── .env.example
├── .gitignore
├── .dockerignore
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── run.py
```

## 🔧 Configuration

### Required API Keys

1. **OpenAI API Key**: For scene analysis and labeling

   - Sign up at [OpenAI](https://openai.com)
   - Create an API key
   - Add to `.env` file

2. **Google API Keys**: For ad suggestions
   - Create a project in [Google Cloud Console](https://console.cloud.google.com)
   - Enable Custom Search API
   - Create API credentials
   - Set up a Custom Search Engine
   - Add both keys to `.env` file

## 🎯 Usage

1. Upload a video file (supported formats: MP4, MOV, AVI, MKV)
2. Wait for processing (progress bar indicates status)
3. View segmented results with:
   - Preview frames for each segment
   - AI-generated labels
   - Relevant ad suggestions
4. Click on ads to view more details

## 🐳 Docker Commands

### Build and Start

```bash
# Build and start containers
docker-compose up --build

# Run in detached mode
docker-compose up -d
```

### Management

```bash
# Stop containers
docker-compose down

# View logs
docker-compose logs -f

# Restart containers
docker-compose restart
```

### Cleanup

```bash
# Remove containers and networks
docker-compose down

# Remove containers, networks, and volumes
docker-compose down -v

# Remove all unused containers, networks, and images
docker system prune
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for their powerful Vision API
- Google for Custom Search API
- FFmpeg for video processing
- PySceneDetect for scene detection
