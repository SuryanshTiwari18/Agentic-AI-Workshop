"""
EduMind AI Learning Agent - WORKING VERSION
Model: gemini-2.5-flash
Run: python EDUMIND.py
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

try:
    from google import genai
    from google.genai import types
    GEMINI_OK = True
except ImportError:
    GEMINI_OK = False

sessions = {}

class Session:
    def __init__(self):
        self.history = []
        self.mode = 'tutor'
        self.subject = 'Mathematics'
        self.level = 'intermediate'
        
    def add(self, role, text):
        self.history.append({'role': role, 'content': text})
        if len(self.history) > 20:
            self.history = self.history[-20:]

PROMPTS = {
    'tutor': "You are a {level} level tutor for {subject}. Provide clear, step-by-step explanations.",
    'quiz': "You are a quiz master for {level} level {subject}. Create engaging test questions.",
    'explain': "You are a {level} level explainer for {subject}. Use simple analogies and examples.",
    'practice': "Generate {level} practice problems for {subject} with detailed solutions.",
    'debate': "Debate {subject} topics at {level} level with critical thinking."
}

HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>EduMind AI</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    padding: 20px;
}
.container { max-width: 1200px; margin: 0 auto; }
h1 { color: #fff; text-align: center; font-size: 2.5rem; margin-bottom: 10px; }
.subtitle { color: rgba(255,255,255,0.9); text-align: center; margin-bottom: 30px; }
.main { display: grid; grid-template-columns: 280px 1fr; gap: 20px; }
.sidebar {
    background: #fff;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}
.sidebar h3 { color: #667eea; margin-bottom: 15px; }
.mode-btn {
    width: 100%;
    padding: 12px;
    margin: 5px 0;
    border: 2px solid #e0e0e0;
    background: #fff;
    border-radius: 8px;
    cursor: pointer;
    text-align: left;
    font-size: 14px;
    transition: all 0.2s;
}
.mode-btn:hover { border-color: #667eea; background: #f8f9ff; }
.mode-btn.active { background: #667eea; color: #fff; border-color: #667eea; }
.input-group { margin-top: 15px; }
.input-group label {
    display: block;
    margin-bottom: 5px;
    font-weight: 600;
    font-size: 13px;
    color: #555;
}
.input-group input,
.input-group select {
    width: 100%;
    padding: 10px;
    border: 2px solid #e0e0e0;
    border-radius: 6px;
    font-size: 14px;
}
.chat-box {
    background: #fff;
    border-radius: 15px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    display: flex;
    flex-direction: column;
    height: 600px;
}
.messages {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
}
.message {
    margin: 12px 0;
    max-width: 80%;
    animation: slideIn 0.3s;
}
.message.user { margin-left: auto; text-align: right; }
.message-content {
    display: inline-block;
    padding: 12px 16px;
    border-radius: 12px;
    line-height: 1.5;
}
.message.user .message-content {
    background: #667eea;
    color: #fff;
}
.message.ai .message-content {
    background: #f0f0f0;
    color: #333;
    border-left: 3px solid #667eea;
}
.input-area {
    padding: 20px;
    border-top: 1px solid #e0e0e0;
    display: flex;
    gap: 10px;
}
#userInput {
    flex: 1;
    padding: 12px;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    font-size: 14px;
    resize: none;
    font-family: inherit;
}
#sendBtn {
    padding: 12px 30px;
    background: #667eea;
    color: #fff;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    font-size: 14px;
    transition: all 0.2s;
}
#sendBtn:hover { background: #5568d3; transform: translateY(-1px); }
#sendBtn:disabled { background: #ccc; cursor: not-allowed; }
.status {
    padding: 10px;
    margin: 10px 20px;
    border-radius: 8px;
    text-align: center;
    font-size: 13px;
    display: none;
}
.status.error { background: #fee; color: #c00; border: 1px solid #fcc; }
.status.success { background: #efe; color: #060; border: 1px solid #cfc; }
.status.info { background: #e3f2fd; color: #1976d2; border: 1px solid #90caf9; }
@keyframes slideIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
@media (max-width: 768px) {
    .main { grid-template-columns: 1fr; }
    h1 { font-size: 2rem; }
}
</style>
</head>
<body>
<div class="container">
    <h1>🎓 EduMind</h1>
    <p class="subtitle">AI Learning Companion • Gemini 2.5</p>
    
    <div class="main">
        <aside class="sidebar">
            <h3>Learning Modes</h3>
            <button class="mode-btn active" data-mode="tutor"> Tutor</button>
            <button class="mode-btn" data-mode="quiz">✏️ Quiz</button>
            <button class="mode-btn" data-mode="explain"> Explain</button>
            <button class="mode-btn" data-mode="practice"> Practice</button>
            <button class="mode-btn" data-mode="debate"> Debate</button>
            
            <div class="input-group">
                <label>Gemini API Key</label>
                <input type="password" id="apiKey" placeholder="Enter your API key">
            </div>
            <div class="input-group">
                <label>Subject</label>
                <input type="text" id="subject" value="Mathematics">
            </div>
            <div class="input-group">
                <label>Level</label>
                <select id="level">
                    <option value="beginner">Beginner</option>
                    <option value="intermediate" selected>Intermediate</option>
                    <option value="advanced">Advanced</option>
                    <option value="expert">Expert</option>
                </select>
            </div>
        </aside>
        
        <main class="chat-box">
            <div id="status" class="status"></div>
            <div class="messages" id="messages">
                <div class="message ai">
                    <div class="message-content">
                        <strong>Welcome to EduMind!</strong><br><br>
                        Enter your Gemini API key and start learning!
                    </div>
                </div>
            </div>
            <div class="input-area">
                <textarea id="userInput" rows="2" placeholder="Ask me anything..."></textarea>
                <button id="sendBtn">Send</button>
            </div>
        </main>
    </div>
</div>

<script>
let currentMode = 'tutor';
let sessionId = 'session_' + Date.now();

const savedKey = localStorage.getItem('gemini_api_key');
if (savedKey) document.getElementById('apiKey').value = savedKey;

document.getElementById('apiKey').addEventListener('change', function() {
    localStorage.setItem('gemini_api_key', this.value);
    showStatus('API key saved!', 'success');
});

document.querySelectorAll('.mode-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        currentMode = this.getAttribute('data-mode');
        document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        const msgs = {
            tutor: '📚 Tutor Mode - Step-by-step explanations',
            quiz: '✏️ Quiz Mode - Test your knowledge',
            explain: '💡 Explain Mode - Simplify complex topics',
            practice: '🎯 Practice Mode - Work on exercises',
            debate: '🗣️ Debate Mode - Critical discussion'
        };
        addMessage('ai', '<strong>' + msgs[currentMode] + '</strong>');
    });
});

document.getElementById('sendBtn').addEventListener('click', sendMessage);

document.getElementById('userInput').addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

function sendMessage() {
    const input = document.getElementById('userInput');
    const message = input.value.trim();
    
    if (!message) {
        showStatus('Please enter a message', 'error');
        return;
    }
    
    const apiKey = document.getElementById('apiKey').value.trim();
    if (!apiKey) {
        showStatus('Please enter your API key', 'error');
        return;
    }
    
    addMessage('user', message);
    input.value = '';
    
    const btn = document.getElementById('sendBtn');
    btn.disabled = true;
    btn.textContent = 'Thinking...';
    showStatus('Processing...', 'info');
    
    fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            sid: sessionId,
            msg: message,
            key: apiKey,
            mode: currentMode,
            subj: document.getElementById('subject').value,
            lvl: document.getElementById('level').value
        })
    })
    .then(r => r.ok ? r.json() : r.json().then(e => { throw new Error(e.error || 'Failed') }))
    .then(d => {
        addMessage('ai', d.response);
        showStatus(d.model ? 'Model: ' + d.model : '', 'success');
    })
    .catch(e => {
        showStatus('Error: ' + e.message, 'error');
        addMessage('ai', ' <strong>Error:</strong> ' + e.message);
    })
    .finally(() => {
        btn.disabled = false;
        btn.textContent = 'Send';
    });
}

function addMessage(type, text) {
    const div = document.getElementById('messages');
    const msg = document.createElement('div');
    msg.className = 'message ' + type;
    msg.innerHTML = '<div class="message-content">' + text + '</div>';
    div.appendChild(msg);
    div.scrollTop = div.scrollHeight;
}

function showStatus(msg, type) {
    const s = document.getElementById('status');
    if (!msg) { s.style.display = 'none'; return; }
    s.className = 'status ' + type;
    s.textContent = msg;
    s.style.display = 'block';
    if (type === 'success') setTimeout(() => s.style.display = 'none', 3000);
}
</script>
</body>
</html>"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/api/chat', methods=['POST'])
def chat():
    if not GEMINI_OK:
        return jsonify({'error':'Install new SDK: pip install google-genai'}), 500
    
    try:
        d = request.json
        sid = d.get('sid', 'default')
        msg = d.get('msg')
        key = d.get('key')
        
        if not key:
            return jsonify({'error':'API key required'}), 400
        
        if sid not in sessions:
            sessions[sid] = Session()
        
        s = sessions[sid]
        s.mode = d.get('mode', 'tutor')
        s.subject = d.get('subj', 'Mathematics')
        s.level = d.get('lvl', 'intermediate')
        
        # System instructions are now passed separately in the new SDK
        system_instructions = PROMPTS.get(s.mode, PROMPTS['tutor']).format(
            subject=s.subject,
            level=s.level
        )
        
        # Initialize Client with the provided key
        client = genai.Client(api_key=key)
        
        # New SDK Pattern: Generate Content
        response = client.models.generate_content(
            model='gemini-2.5-flash', # Updated to a stable release
            contents=msg,
            config=types.GenerateContentConfig(
                max_output_tokens=1024,
                system_instruction=system_instructions
            )
        )
        
        ai_response = response.text
        s.add('user', msg)
        s.add('ai', ai_response)
        
        return jsonify({'response': ai_response, 'model': 'gemini-2.0-flash'})
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__=='__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"\nEduMind AI - Running on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)