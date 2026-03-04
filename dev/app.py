from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import json
import os

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, 
            template_folder=os.path.join(BASE_DIR, 'templates'))

# Ollama API endpoint
OLLAMA_API_URL = "http://localhost:11434/api/generate"

def fetch_website_content(url):
    """Fetch and extract text content from a website"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Limit text length to avoid overwhelming the model
        max_chars = 2000  # Reduced to prevent timeouts
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        
        return text
    except Exception as e:
        return None, str(e)

def summarize_with_ollama(content, model="llama2"):
    """Send content to Ollama for summarization"""
    try:
        prompt = f"""Summarize the following website content in 3-5 concise sentences. Focus only on the main points:

{content}

Summary:"""
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": True,  # Enable streaming for faster response
            "options": {
                "temperature": 0.5,
                "num_predict": 200  # Limit response length
            }
        }
        
        response = requests.post(OLLAMA_API_URL, json=payload, stream=True, timeout=180)
        response.raise_for_status()
        
        # Collect streamed response
        full_response = ""
        for line in response.iter_lines():
            if line:
                json_response = json.loads(line)
                if 'response' in json_response:
                    full_response += json_response['response']
                if json_response.get('done', False):
                    break
        
        return full_response if full_response else 'No summary generated'
    except requests.exceptions.Timeout:
        return None, "Request timed out. Try a shorter webpage or a faster model."
    except Exception as e:
        return None, str(e)

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    """Handle summarization requests"""
    data = request.get_json()
    url = data.get('url')
    model = data.get('model', 'llama2')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    # Fetch website content
    content = fetch_website_content(url)
    if isinstance(content, tuple):
        return jsonify({'error': f'Failed to fetch website: {content[1]}'}), 400
    
    # Summarize with Ollama
    summary = summarize_with_ollama(content, model)
    if isinstance(summary, tuple):
        return jsonify({'error': f'Ollama error: {summary[1]}'}), 500
    
    return jsonify({
        'url': url,
        'summary': summary,
        'model': model
    })

@app.route('/summarize-stream', methods=['POST'])
def summarize_stream():
    """Handle streaming summarization requests"""
    from flask import Response, stream_with_context
    
    data = request.get_json()
    url = data.get('url')
    model = data.get('model', 'llama2')
    
    def generate():
        # Fetch website content
        content = fetch_website_content(url)
        if isinstance(content, tuple):
            yield f"data: {json.dumps({'error': f'Failed to fetch website: {content[1]}'})}\n\n"
            return
        
        # Stream summary from Ollama
        try:
            prompt = f"""Summarize the following website content in 3-5 concise sentences. Focus only on the main points:

{content}

Summary:"""
            
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": 0.5,
                    "num_predict": 200
                }
            }
            
            response = requests.post(OLLAMA_API_URL, json=payload, stream=True, timeout=180)
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    json_response = json.loads(line)
                    if 'response' in json_response:
                        yield f"data: {json.dumps({'chunk': json_response['response']})}\n\n"
                    if json_response.get('done', False):
                        yield f"data: {json.dumps({'done': True})}\n\n"
                        break
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream')

@app.route('/models', methods=['GET'])
def get_models():
    """Get available Ollama models"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        response.raise_for_status()
        models = response.json()
        model_names = [model['name'] for model in models.get('models', [])]
        return jsonify({'models': model_names})
    except Exception as e:
        return jsonify({'models': ['llama2'], 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)