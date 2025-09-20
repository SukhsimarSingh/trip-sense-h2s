# AI Trip Planner

An intelligent travel planning application powered by Google's Gemini AI that creates personalized itineraries using real-time data from Google Maps, Places, and Weather APIs. Built with Streamlit for a modern, interactive web interface.

## Features

### AI-Powered Planning
- Smart Itinerary Generation: Creates detailed day-by-day travel plans
- Real-time Data Integration: Uses Google Places, Maps, and Weather APIs
- Personalized Recommendations: Tailored to your travel style and preferences
- Interactive Chat Interface: Refine and customize your itinerary through conversation

### Travel Personalization
- Travel Styles: Adventure, Culture, Relaxation, Food, Nightlife, Family, Photography, Shopping, Nature, Mixed
- Budget Levels: Low, Medium, High with appropriate recommendations
- Special Requests: Vegetarian options, accessibility features, specific attractions
- Group Planning: Solo, couple, family, or group travel optimization

### Smart Features
- Function Calling: Automatic integration with Google APIs for real-time data
- Trip Storage: Save and manage multiple trip plans
- PDF Export: Export trips to PDF format
- Session Management: Efficient state handling and caching
- Error Handling: Robust error recovery and user feedback

## Quick Start

### Prerequisites
- Python 3.8+
- Google Cloud Platform account
- API keys for Google Maps Platform and Gemini AI

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-trip-planner-h2s
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
   GEMINI_MODEL=gemini-2.0-flash
   ```

5. **Enable Google APIs**
   In your Google Cloud Console, enable:
   - Places API (New)
   - Weather API
   - Maps JavaScript API

6. **Run the application**
   ```bash
   streamlit run streamlit_app.py
   ```

## Architecture

### Project Structure
```
ai-trip-planner-h2s/
├── streamlit_app.py      # Main application entry point
├── pages/                # Streamlit pages
│   ├── landing.py        # Landing page
│   ├── form.py          # Trip planning form
│   ├── chatbot.py       # AI chat interface
│   └── trips.py         # Saved trips management
├── services/            # Core business logic
│   ├── gemini.py        # AI integration
│   ├── tools.py         # Google API functions
│   ├── trip_storage.py  # Trip persistence
│   ├── export.py        # Trip export functionality
│   ├── logging.py       # Logging and metrics
│   └── prompt_loader.py # Template management
├── prompts/             # AI prompts and templates
│   ├── system.yaml      # System instructions
│   └── user/
│       └── initial_prompt.jinja
├── styles/              # UI styling
│   └── styles.py
├── saved_trips/         # Trip storage (JSON files)
├── requirements.txt     # Python dependencies
└── trip_planner.log     # Application logs
```

### Key Components

#### AI Engine (services/gemini.py)
- TripSenseAI Class: Main AI orchestration
- Function Calling: Automatic tool execution
- Response Processing: Handles multi-part responses
- Context Management: Optimized conversation handling
- Caching: Efficient client initialization

#### Tool Integration (services/tools.py)
- search_text: Location resolution and coordinates
- get_nearby_attractions: Tourist attractions and sights
- get_nearby_restaurants: Dining recommendations
- get_hotels: Accommodation options
- get_weather: Weather forecasts
- save_trip: Trip persistence

#### Data Management (services/trip_storage.py)
- Trip Persistence: JSON-based storage
- CRUD Operations: Create, read, update, delete trips
- Data Validation: Ensures data integrity
- File Management: Organized trip storage

## Technology Stack

### Core Technologies
- **Python 3.8+**: Main programming language
- **Streamlit 1.49+**: Web application framework
- **Google Gemini AI**: Advanced language model with function calling
- **Google Maps Platform**: Location services and weather data
- **Jinja2**: Template engine for dynamic prompts
- **PyYAML**: Configuration file management

### Key Dependencies
- google-genai: Google Gemini AI integration
- streamlit: Web app framework
- python-dotenv: Environment variable management
- jinja2: Template rendering
- pyyaml: YAML configuration parsing
- reportlab: PDF generation for exports
- requests: HTTP client for API calls

## Configuration

### Environment Variables
| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini AI API key | Yes |
| `GOOGLE_MAPS_API_KEY` | Google Maps Platform API key | Yes |
| `GEMINI_MODEL` | Gemini model to use (default: gemini-2.0-flash) | No |

### Model Configuration
The application is configured to use:
- **Model**: gemini-2.0-flash (configurable via environment variable)
- **Temperature**: 0.7 for balanced creativity and accuracy
- **Max Output Tokens**: 2048 for comprehensive responses
- **Safety Settings**: Configured to block harmful content
- **Function Calling**: Enabled for real-time data integration

## Application Workflow

### User Journey
1. **Landing Page**: Welcome screen with feature overview
2. **Trip Planning Form**: Input destination, dates, preferences, and budget
3. **AI Processing**: Gemini AI generates personalized itinerary using real-time data
4. **Interactive Chat**: Refine and customize the itinerary through conversation
5. **Trip Management**: Save, view, export, and manage multiple trips

### Data Flow
1. **User Input**: Form data collected and validated
2. **Prompt Generation**: Dynamic prompts created using Jinja2 templates
3. **AI Processing**: Gemini AI processes request with function calling
4. **API Integration**: Real-time data fetched from Google APIs
5. **Response Rendering**: Markdown-formatted itinerary displayed
6. **Storage**: Trip data saved locally in JSON format

## Features Deep Dive

### AI Function Calling
The application uses Google's Gemini AI with function calling to automatically:
1. Resolve locations to coordinates
2. Fetch weather data for travel dates
3. Find attractions based on travel preferences
4. Recommend restaurants with dietary considerations
5. Suggest accommodations within budget
6. Save trips when requested

### Smart Context Management
- Limited History: Uses only last 3 messages for efficiency
- Token Optimization: Excludes system prompts from token counting
- Session Persistence: Maintains trip data across page navigation
- Itinerary Tracking: Separates main itinerary from chat responses

### Performance Optimization
- Client Caching: Gemini client cached using Streamlit's cache_resource
- Session Management: Efficient state handling across page navigation
- Token Management: Optimized context window usage
- Lazy Loading: Resources loaded only when needed
- Response Streaming: Real-time response display for better UX

## Troubleshooting

### Common Issues

#### API Key Issues
```bash
Error: GOOGLE_MAPS_API_KEY not set
```
**Solution**: Ensure `.env` file contains valid API keys

#### Places API Disabled
```bash
Google Places API is not enabled
```
**Solution**: Enable Places API (New) in Google Cloud Console

#### Weather API Errors
```bash
Weather API error: 404 Not Found
```
**Solution**: Ensure Weather API is enabled and API key has proper permissions

### Debug Mode
Enable debug logging by setting log level in `services/logging.py`:
```python
logger.setLevel(logging.DEBUG)
```

## Security Considerations

### API Key Security
- Environment Variables: Never commit API keys to version control
- Key Restrictions: Restrict API keys to specific APIs and domains
- Regular Rotation: Rotate API keys periodically

### Data Privacy
- Local Storage: Trip data stored locally in JSON files
- No External Transmission: User data not sent to third parties
- Session Management: Secure session state handling

## Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Code Style
- Python: Follow PEP 8 guidelines
- Documentation: Comprehensive docstrings
- Type Hints: Use type annotations
- Error Handling: Explicit exception handling

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- **Issues**: Create an issue on GitHub for bugs or feature requests
- **Documentation**: Check this README and inline code comments
- **Logs**: Check `trip_planner.log` for detailed error information

---

**Built with Google Gemini AI and Streamlit**

*Last updated: September 2025*