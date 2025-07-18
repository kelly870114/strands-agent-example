# 👗 Outfit Assistant - Strands Agent Example

A demonstration of using Strands Agents to create an intelligent fashion consultant that provides personalized outfit recommendations based on weather, occasion, and user preferences.

## 🌟 Features

- **Intelligent Questioning**: AI proactively asks for missing information
- **Weather Integration**: Checks weather conditions for outfit planning  
- **Memory Learning**: Remembers user preferences and past conversations
- **Trend Research**: Searches web for current fashion trends
- **Personalized Advice**: Adapts recommendations to user's age, style, and occasion
- **Dual Interface**: Terminal and Streamlit web interface

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- UV package manager
- OpenWeatherMap API key (free): https://openweathermap.org/api

### Installation

1. **Install UV and Python 3.12**
```bash
cd ~
curl -LsSf https://astral.sh/uv/install.sh | sh
if [ "$SHELL" = "/bin/bash" ]; then
  echo 'eval "$(uv generate-shell-completion bash)"' >> ~/.bashrc
  echo 'eval "$(uvx --generate-shell-completion bash)"' >> ~/.bashrc
fi
source ~/.bashrc
uv self update
uv python install 3.12
```

2. **Setup Python Virtual Environment**
```bash
# Create requirements.txt
cat << EOF > requirements.txt
boto3
mcp[cli]
nova-act
opensearch-py
pandas
retrying
strands-agents 
strands-agents-tools[mem0_memory]
streamlit
tqdm
uv
EOF

# Install dependencies
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

## 🎯 Usage

### Terminal Version
```bash
uv run python3 ginny_weather_outift_assistant.py
```

**Interactive Commands:**
- `demo` - Start interactive demonstration (recommended)
- `chat` - General interaction mode
- `help` - View detailed instructions
- `exit` - End program

### Streamlit Web Interface
```bash
uv run streamlit run outfit_assistant_streamlit.py
```

Access the web interface at `http://localhost:8501`

## 💬 Example Conversations

**Basic Usage:**
- "I need outfit advice for tomorrow"
- "Help me dress for a date"
- "What should I wear to work?"

**Advanced Queries:**
- "I have an important meeting in Tokyo next week"
- "Suggest casual weekend outfits for cold weather"
- "I prefer minimalist style, what's good for summer?"

## 🔧 Core Components

### ginny_weather_outift_assistant.py
- Terminal-based interactive fashion consultant
- Real-time weather API integration
- Memory system for user preferences
- Professional styling advice with emoji-rich responses

### outfit_assistant_streamlit.py  
- Web-based interface with real-time monitoring
- Tool call visualization and debugging
- Interactive quick-start buttons
- Session state management

## 🛠️ Technical Details

### Tools Used
- **http_request**: Weather API calls and trend research
- **mem0_memory**: User preference storage and retrieval
- **OpenWeatherMap API**: Current weather and 5-day forecasts

### Key Features
- Intelligent conversation flow with follow-up questions
- Weather-aware clothing recommendations
- Style preference learning and memory
- Multi-language support (Chinese/English)
- Error handling and graceful degradation

## 🌤️ Weather Integration

The assistant uses OpenWeatherMap API to provide weather-appropriate recommendations:
- Current weather conditions
- 5-day forecasts (updated every 3 hours)
- Temperature, humidity, and precipitation data
- Location-based weather queries

## 🧠 Memory System

Powered by Mem0, the assistant remembers:
- User names and personal preferences
- Style choices and feedback
- Previous outfit recommendations
- Seasonal preferences and constraints

## 🎨 Styling Approach

The AI consultant provides:
- Specific clothing items (tops, bottoms, outerwear, shoes)
- Color coordination suggestions
- Material choices based on weather
- Accessory recommendations
- Practical styling tips

## 📝 Configuration

### Environment Variables
- `OPENWEATHER_API_KEY`: Your OpenWeatherMap API key
- `USER_ID`: Unique identifier for memory system
- `MEM0_API_KEY`: Configured in code (demo purposes)

### API Keys
- OpenWeatherMap: Free tier allows 1000 calls/day
- Mem0: Configured for demonstration

## 🚨 Troubleshooting

**Common Issues:**
- Missing API keys: Set environment variables or update code
- UV installation: Ensure shell completion is properly configured
- Memory issues: Check Mem0 API key configuration
- Weather data: Verify OpenWeatherMap API key validity

## 📄 License

This project is a demonstration of Strands Agents capabilities for educational purposes.

## 🤝 Contributing

This is an example project. For production use, consider:
- Securing API keys properly
- Adding user authentication
- Implementing rate limiting
- Adding comprehensive error handling