# Google Calendar Integration

This project provides tools to analyze your Google Calendar events and generate insights about your time management. It includes two versions:

1. **Local Analysis**: Analyzes your calendar data locally without requiring external API calls
2. **Claude-powered Analysis**: Uses Anthropic's Claude AI to provide more sophisticated analysis (requires an API key)

## Setup

### Prerequisites

- Python 3.8 or higher
- Google Calendar API credentials
- Anthropic API key (for Claude-powered analysis only)

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/GoogleCalendarIntegration.git
   cd GoogleCalendarIntegration
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up Google Calendar API:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable the Google Calendar API
   - Create OAuth 2.0 credentials
   - Download the credentials as `credentials.json` and place it in the project directory

4. Set up environment variables:
   - Copy `.env.template` to `.env`
   - For Claude-powered analysis, add your Anthropic API key to the `.env` file

## Usage

### Local Calendar Analysis

This version works without requiring an Anthropic API key:

```
python calendar_analysis_local.py [--days DAYS]
```

Options:
- `--days`: Number of days to analyze (default: 7)

### Claude-powered Calendar Analysis

This version provides more sophisticated analysis using Anthropic's Claude AI:

```
python calendar_analysis.py [--days DAYS] [--api-key API_KEY]
```

Options:
- `--days`: Number of days to analyze (default: 7)
- `--api-key`: Anthropic API key (if not provided, will use the key from `.env`)

### Testing Anthropic API Connection

To test your connection to the Anthropic API:

```
python test_anthropic_dotenv.py
```

## Troubleshooting

### Anthropic API Issues

If you encounter authentication errors with the Anthropic API:

1. Verify your API key in the `.env` file
2. Ensure your API key is valid and active
3. API keys should start with `sk-ant-`
4. Get a new API key from [Anthropic Console](https://console.anthropic.com/) if needed

### Google Calendar API Issues

If you encounter issues with the Google Calendar API:

1. Ensure `credentials.json` is in the project directory
2. Check that the Google Calendar API is enabled in your Google Cloud project
3. Verify that your OAuth consent screen is configured correctly

## License

This project is licensed under the MIT License - see the LICENSE file for details. 