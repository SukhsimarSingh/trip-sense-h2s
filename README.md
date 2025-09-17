# 🧭 AI Trip Planner

An intelligent trip planning application powered by Google Gemini AI and Google Maps Platform APIs. Create personalized travel itineraries with real-time location data, weather forecasts, and smart recommendations.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.49+-red.svg)

## ✨ Features

### 🤖 AI-Powered Planning
- **Smart Itineraries**: Generate detailed day-by-day travel plans using Google Gemini AI
- **Conversational Interface**: Chat with the AI to refine and customize your trip
- **Contextual Recommendations**: Get suggestions based on your preferences, budget, and travel style

### 🗺️ Location Intelligence
- **Place Search**: Find destinations, landmarks, and points of interest
- **Nearby Attractions**: Discover tourist attractions, museums, parks, and cultural sites
- **Restaurant Finder**: Locate restaurants with dietary preference support
- **Hotel Search**: Find accommodations filtered by type and rating
- **Weather Integration**: Get weather forecasts for your travel dates

### 💾 Trip Management
- **Save Itineraries**: Store your favorite trip plans with custom names and descriptions
- **Trip Library**: Browse and manage all your saved trips
- **Detailed Views**: Access complete trip information including form data and AI responses

### 🎨 User Experience
- **Modern UI**: Clean, responsive Streamlit interface
- **Demo Mode**: Try the app without API keys using sample responses
- **Error Handling**: Graceful fallbacks when services are unavailable
- **Real-time Status**: Live API availability indicators

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Google Cloud Platform account (for API keys)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd tip-planner-fixed
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Create a `.env` file in the project root:
   ```env
   # Required for AI functionality
   GEMINI_API_KEY=your_gemini_api_key_here
   
   # Required for location services
   GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
   
   # Optional: Specify Gemini model (defaults to gemini-1.5-pro)
   GEMINI_MODEL=models/gemini-1.5-pro
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

6. **Open your browser**
   
   Navigate to `http://localhost:8501`

## 🔑 API Setup

### Google Gemini API
1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Create an API key
3. Add it to your `.env` file as `GEMINI_API_KEY`

### Google Maps Platform APIs
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the following APIs:
   - **Places API (New)** - For location search and nearby places
   - **Weather API** - For weather forecasts
4. Create credentials (API Key)
5. Add it to your `.env` file as `GOOGLE_MAPS_API_KEY`

### API Costs
- **Gemini API**: Generous free tier, pay-per-use pricing
- **Google Maps APIs**: Free tier available, usage-based pricing
- **Demo Mode**: Use the app without API keys for testing

## 📁 Project Structure

```
tip-planner-fixed/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── LICENSE                     # MIT license
├── .env                        # Environment variables (create this)
├── prompts/                    # AI prompt templates
│   ├── system.yaml            # System instructions for AI
│   └── user/
│       └── initial_prompt.txt # User prompt template
├── src/ai/                     # AI integration modules
│   ├── integration.py         # Main AI interface
│   ├── handlers.py            # Tool implementations
│   ├── tools.py               # Tool definitions for Gemini
│   ├── router.py              # Tool routing logic
│   ├── gemini_client.py       # Gemini API client
│   ├── prompt_loader.py       # Prompt loading utilities
│   └── trip_storage.py        # Trip persistence
└── saved_trips/               # Stored trip data (auto-created)
```

## 🛠️ Usage

### Planning a Trip

1. **Fill out the trip form**:
   - Destination (e.g., "Paris", "Tokyo", "New York")
   - Duration (1-30 days)
   - Travel type (Adventure, Cultural, Relaxation, Business, Family)
   - Budget level (Budget, Medium, Luxury)
   - Group size
   - Accommodation preference
   - Special requests

2. **Generate itinerary**: Click "Plan My Trip" to get AI-generated recommendations

3. **Chat with AI**: Ask follow-up questions to refine your trip:
   - "What are good vegetarian restaurants?"
   - "Add more outdoor activities"
   - "Find family-friendly attractions"

4. **Save your trip**: Use the "Save Itinerary" button to store your plan

### Managing Saved Trips

- **View all trips**: Navigate to "Saved Trips" in the sidebar
- **Trip details**: Click "View Details" to see complete information
- **Delete trips**: Remove trips you no longer need

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `GEMINI_API_KEY` | Yes* | Google Gemini API key | None |
| `GOOGLE_MAPS_API_KEY` | Yes* | Google Maps Platform API key | None |
| `GEMINI_MODEL` | No | Gemini model to use | `models/gemini-1.5-pro` |

*Required for full functionality. Demo mode available without keys.

### Customizing AI Behavior

Edit `prompts/system.yaml` to modify:
- AI personality and tone
- Response format preferences
- Tool usage policies
- Output guidelines

### Adding Custom Tools

1. Define tool function in `src/ai/handlers.py`
2. Add tool declaration dictionary
3. Register in `src/ai/router.py`
4. Add to tool list in `src/ai/tools.py`

## 🏗️ Architecture

### Core Components

- **Streamlit App** (`app.py`): User interface and main application logic
- **AI Integration** (`src/ai/integration.py`): Orchestrates AI interactions and tool usage
- **Tool System**: Modular functions for location search, weather, and trip management
- **Prompt System**: Template-based prompt generation for consistent AI behavior

### AI Workflow

1. **User Input**: Trip preferences collected via Streamlit form
2. **Prompt Generation**: User data rendered into structured prompts
3. **AI Processing**: Gemini AI generates response with potential tool calls
4. **Tool Execution**: Location searches, weather lookups performed as needed
5. **Response Synthesis**: AI creates final conversational response
6. **User Interaction**: Chat interface for follow-up questions

### Data Flow

```
User Input → Prompt Template → Gemini AI → Tool Calls → External APIs → AI Response → User Interface
```

## 🧪 Testing

### Demo Mode
Run without API keys to test the interface:
```bash
# Remove or comment out API keys in .env
streamlit run app.py
```

### Tool Testing
Test individual components:
```python
from src.ai.handlers import search_text
result = search_text({'query': 'Paris', 'max_results': 3})
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt

# Run with debug logging
export STREAMLIT_LOGGER_LEVEL=debug
streamlit run app.py
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini AI** for intelligent trip planning capabilities
- **Google Maps Platform** for location and weather data
- **Streamlit** for the beautiful web interface
- **Python Community** for excellent libraries and tools

## 📞 Support

- **Issues**: Report bugs and request features via GitHub Issues
- **Documentation**: Check this README and inline code comments
- **API Documentation**: 
  - [Google Gemini API](https://ai.google.dev/docs)
  - [Google Maps Platform](https://developers.google.com/maps/documentation)

## 🗺️ Roadmap

- [ ] Multi-language support
- [ ] Calendar integration
- [ ] Expense tracking
- [ ] Offline mode capabilities

---

**Built with ❤️ for travelers by travelers**
