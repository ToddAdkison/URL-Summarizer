# Website Summarizer with Ollama

A Flask web application that uses a local Ollama instance to summarize website content.

## Prerequisites

1. **Python 3.8+** installed on your system
2. **Ollama** installed and running locally
   - Download from: https://ollama.ai
   - Install at least one model (e.g., `ollama pull llama2`)

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt --break-system-packages
```

## Running the Application

1. Make sure Ollama is running:
```bash
ollama serve
```

2. In a separate terminal, navigate to the project directory and start the Flask application:

**Option A - Using the run script (recommended):**
```bash
./run.sh
```

**Option B - Running directly:**
```bash
cd /path/to/project/directory
python app.py
```

**Important:** Make sure you're in the same directory as app.py when you run it!

3. Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

1. Enter a website URL in the input field (e.g., `https://example.com`)
2. Select your preferred Ollama model from the dropdown
3. Click "Summarize Website"
4. Wait for the application to fetch and summarize the content
5. The summary will appear below the form

## Features

- **Website Content Extraction**: Fetches and cleans HTML content from any URL
- **Ollama Integration**: Uses your local Ollama instance for AI-powered summarization
- **Model Selection**: Automatically detects available Ollama models
- **Clean UI**: Modern, responsive interface
- **Error Handling**: Graceful error messages for failed requests

## How It Works

1. **Content Fetching**: The app uses `requests` and `BeautifulSoup` to fetch and extract text from the website
2. **Text Cleaning**: Removes scripts, styles, and excess whitespace
3. **Summarization**: Sends the cleaned text to your local Ollama instance
4. **Display**: Returns the AI-generated summary to the webpage

## Configuration

- **Ollama API URL**: Default is `http://localhost:11434` (modify in `app.py` if needed)
- **Max Content Length**: Limited to 2000 characters (configurable in `app.py`)
- **Timeout**: 180 seconds (configurable in `app.py`)
- **Default Model**: llama2 (can be changed via the UI)
- **Streaming**: Enabled by default for real-time summary generation

## Troubleshooting

**Error: "Request timed out"**
- The website content might be too large
- Try using a faster model (e.g., `mistral` or `llama3.2`)
- Large models like `llama2:70b` will be slower
- The app now limits content to 2000 characters to prevent timeouts
- Consider using streaming mode (automatically enabled)

**Error: "Failed to fetch website"**
- Check if the URL is accessible
- Some websites may block automated requests

**Error: "Ollama error"**
- Ensure Ollama is running (`ollama serve`)
- Check if the selected model is installed (`ollama list`)
- Try pulling the model: `ollama pull llama2`

**No models appear in dropdown**
- Run `ollama list` to see installed models
- Install a model: `ollama pull llama2` or `ollama pull mistral`

**Recommended models for speed:**
- `llama3.2` - Fast and accurate (recommended)
- `mistral` - Very fast
- `phi3` - Lightweight and quick
- `llama2` - Good balance (default)

## Supported Ollama Models

Any model installed in your Ollama instance will work. Popular choices:
- llama2
- mistral
- codellama
- llama3
- gemma

To install a new model:
```bash
ollama pull <model-name>
```

## Notes

- Processing time depends on the website size and Ollama model used
- Larger models provide better summaries but take longer
- The app limits content to 4000 characters to avoid overwhelming the model