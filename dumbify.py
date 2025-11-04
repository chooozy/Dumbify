from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import anthropic
import traceback
import os
from werkzeug.utils import secure_filename
import PyPDF2
import io

app = Flask(__name__)
CORS(app)

API_KEY = ''  #ENTER API KEY HERE


# Configure upload settings
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'md', 'pdf'}
# Create uploads directory if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_file(file_stream, filename):
    """Extract text from uploaded file"""
    try:
        # Reset file stream position
        file_stream.seek(0)
        
        # Get file extension
        file_extension = filename.rsplit('.', 1)[1].lower()
        
        if file_extension == 'pdf':
            # Handle PDF files
            pdf_reader = PyPDF2.PdfReader(file_stream)
            text = ""
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
            
            return text.strip()
        else:
            # Handle text files (txt, md)
            text = file_stream.read().decode('utf-8')
            return text.strip()
            
    except Exception as e:
        return f"Error reading file: {str(e)}"

# Enhanced Professional HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dumbify - Personalized Learning Assistant</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary-color: #2563eb;
            --primary-dark: #1d4ed8;
            --secondary-color: #f1f5f9;
            --accent-color: #06b6d4;
            --success-color: #10b981;
            --warning-color: #f59e0b;
            --error-color: #ef4444;
            --text-primary: #1e293b;
            --text-secondary: #64748b;
            --border-color: #e2e8f0;
            --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
            --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
            --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
            --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
            --border-radius: 0.75rem;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            min-height: 100vh;
            color: var(--text-primary);
            line-height: 1.6;
        }

        .navbar {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid var(--border-color);
            padding: 1rem 0;
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .navbar-content {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .logo {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--primary-color);
        }

        .logo-icon {
            background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
            color: white;
            width: 2.5rem;
            height: 2.5rem;
            border-radius: 0.5rem;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .nav-links {
            display: flex;
            gap: 2rem;
            align-items: center;
        }

        .nav-link {
            color: var(--text-secondary);
            text-decoration: none;
            font-weight: 500;
            transition: color 0.2s ease;
        }

        .nav-link:hover {
            color: var(--primary-color);
        }

        .container {
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 2rem;
        }

        .hero-section {
            text-align: center;
            padding: 3rem 0 4rem;
        }

        .hero-title {
            font-size: 3.5rem;
            font-weight: 800;
            margin-bottom: 1rem;
            background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .hero-subtitle {
            font-size: 1.25rem;
            color: var(--text-secondary);
            margin-bottom: 2rem;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
        }

        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 3rem;
        }

        .feature-card {
            background: white;
            padding: 1.5rem;
            border-radius: var(--border-radius);
            box-shadow: var(--shadow-sm);
            border: 1px solid var(--border-color);
            text-align: center;
            transition: all 0.3s ease;
        }

        .feature-card:hover {
            box-shadow: var(--shadow-lg);
            transform: translateY(-2px);
        }

        .feature-icon {
            font-size: 2.5rem;
            margin-bottom: 1rem;
            color: var(--primary-color);
        }

        .feature-title {
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }

        .feature-description {
            color: var(--text-secondary);
            font-size: 0.9rem;
        }

        .main-content {
            background: white;
            border-radius: var(--border-radius);
            box-shadow: var(--shadow-xl);
            overflow: hidden;
            border: 1px solid var(--border-color);
        }

        .tabs {
            display: flex;
            background: var(--secondary-color);
            border-bottom: 1px solid var(--border-color);
        }

        .tab {
            flex: 1;
            padding: 1.5rem 2rem;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 600;
            color: var(--text-secondary);
            border-bottom: 3px solid transparent;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }

        .tab.active {
            color: var(--primary-color);
            border-bottom-color: var(--primary-color);
            background: white;
        }

        .tab:hover:not(.active) {
            background: rgba(37, 99, 235, 0.05);
            color: var(--primary-color);
        }

        .tab-content {
            display: none;
            padding: 2.5rem;
        }

        .tab-content.active {
            display: block;
        }

        .section-title {
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 2rem;
            color: var(--text-primary);
        }

        .examples-section {
            background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
            padding: 1.5rem;
            border-radius: var(--border-radius);
            margin-bottom: 2rem;
            border-left: 4px solid var(--accent-color);
        }

        .examples-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .example-item {
            margin: 0.75rem 0;
            color: var(--text-secondary);
            padding-left: 1rem;
            position: relative;
        }

        .example-item::before {
            content: "→";
            position: absolute;
            left: 0;
            color: var(--accent-color);
            font-weight: bold;
        }

        .form-group {
            margin-bottom: 2rem;
        }

        .form-label {
            display: block;
            margin-bottom: 0.75rem;
            font-weight: 600;
            color: var(--text-primary);
            font-size: 1rem;
        }

        .form-input, .form-select, .form-textarea {
            width: 100%;
            padding: 1rem;
            border: 2px solid var(--border-color);
            border-radius: var(--border-radius);
            font-size: 1rem;
            transition: all 0.3s ease;
            background: white;
            font-family: inherit;
        }

        .form-input:focus, .form-select:focus, .form-textarea:focus {
            outline: none;
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        }

        .form-textarea {
            resize: vertical;
            min-height: 120px;
        }

        .file-upload-area {
            border: 2px dashed var(--border-color);
            border-radius: var(--border-radius);
            padding: 3rem 2rem;
            text-align: center;
            background: var(--secondary-color);
            transition: all 0.3s ease;
            cursor: pointer;
            position: relative;
        }

        .file-upload-area:hover {
            border-color: var(--primary-color);
            background: rgba(37, 99, 235, 0.02);
        }

        .file-upload-area.drag-over {
            border-color: var(--accent-color);
            background: rgba(6, 182, 212, 0.05);
        }

        .file-upload-icon {
            font-size: 3rem;
            color: var(--text-secondary);
            margin-bottom: 1rem;
        }

        .file-upload-text {
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 0.5rem;
        }

        .file-upload-subtext {
            color: var(--text-secondary);
            font-size: 0.9rem;
        }

        .file-input {
            display: none;
        }

        .file-info {
            margin-top: 1rem;
            padding: 1rem;
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.2);
            border-radius: var(--border-radius);
            color: var(--success-color);
            display: none;
        }

        .primary-btn {
            background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
            color: white;
            padding: 1rem 2rem;
            border: none;
            border-radius: var(--border-radius);
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: var(--shadow-md);
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }

        .primary-btn:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
        }

        .primary-btn:active {
            transform: translateY(0);
        }

        .primary-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .result-container {
            margin-top: 2rem;
            padding: 2rem;
            background: var(--secondary-color);
            border-radius: var(--border-radius);
            border-left: 4px solid var(--success-color);
            display: none;
        }

        .result-container.show {
            display: block;
            animation: slideIn 0.5s ease;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .result-title {
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .result-content {
            line-height: 1.8;
            color: var(--text-primary);
            white-space: pre-wrap;
            background: white;
            padding: 1.5rem;
            border-radius: var(--border-radius);
            border: 1px solid var(--border-color);
        }

        .loading {
            display: none;
            text-align: center;
            padding: 3rem;
        }

        .loading.show {
            display: block;
        }

        .spinner {
            border: 4px solid var(--border-color);
            border-top: 4px solid var(--primary-color);
            border-radius: 50%;
            width: 3rem;
            height: 3rem;
            animation: spin 1s linear infinite;
            margin: 0 auto 1.5rem;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .loading-text {
            color: var(--text-secondary);
            font-size: 1.1rem;
        }

        .footer {
            text-align: center;
            padding: 3rem 0;
            margin-top: 4rem;
            color: var(--text-secondary);
            border-top: 1px solid var(--border-color);
        }

        @media (max-width: 768px) {
            .navbar-content {
                padding: 0 1rem;
            }
            
            .nav-links {
                display: none;
            }
            
            .container {
                padding: 0 1rem;
            }
            
            .hero-title {
                font-size: 2.5rem;
            }
            
            .tabs {
                flex-direction: column;
            }
            
            .tab-content {
                padding: 1.5rem;
            }
            
            .feature-grid {
                grid-template-columns: 1fr;
            }
        }

        .status-indicator {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            border-radius: 2rem;
            font-size: 0.875rem;
            font-weight: 500;
        }

        .status-success {
            background: rgba(16, 185, 129, 0.1);
            color: var(--success-color);
            border: 1px solid rgba(16, 185, 129, 0.2);
        }

        .pulse {
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="navbar-content">
            <div class="logo">
                <div class="logo-icon">
                    <i class="fas fa-graduation-cap"></i>
                </div>
                <span>Dumbify</span>
            </div>
        </div>
    </nav>

    <div class="container">
        <div class="hero-section">
            <h1 class="hero-title">Learn Anything, Your Way</h1>
            <p class="hero-subtitle">
                Transform complex topics into engaging lessons tailored to your interests and learning style. 
                Upload documents or explore new subjects with our AI-powered learning assistant.
            </p>
        </div>

        <div class="feature-grid">
            <div class="feature-card">
                <div class="feature-icon">
                    <i class="fas fa-brain"></i>
                </div>
                <div class="feature-title">Personalized Learning</div>
                <div class="feature-description">AI adapts explanations to your interests and preferred learning style</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">
                    <i class="fas fa-file-pdf"></i>
                </div>
                <div class="feature-title">Document Analysis</div>
                <div class="feature-description">Upload PDFs, text files, or paste content for instant explanation</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">
                    <i class="fas fa-lightbulb"></i>
                </div>
                <div class="feature-title">Smart Analogies</div>
                <div class="feature-description">Complex concepts explained through familiar topics you love</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">
                    <i class="fas fa-rocket"></i>
                </div>
                <div class="feature-title">Instant Results</div>
                <div class="feature-description">Get comprehensive explanations in seconds, not hours</div>
            </div>
        </div>

        <div class="main-content">
            <div class="tabs">
                <div class="tab active" onclick="switchTab('topic')">
                    <i class="fas fa-book"></i>
                    <span>Learn Topic</span>
                </div>
                <div class="tab" onclick="switchTab('document')">
                    <i class="fas fa-file-upload"></i>
                    <span>Explain Document</span>
                </div>
            </div>

            <!-- Topic Learning Tab -->
            <div class="tab-content active" id="topic-content">
                <h2 class="section-title">Explore Any Topic</h2>
                
                <div class="examples-section">
                    <h3 class="examples-title">
                        <i class="fas fa-magic"></i>
                        Example Combinations
                    </h3>
                    <div class="example-item"><strong>Machine Learning</strong> + <strong>Cooking</strong> = Learn algorithms through recipe analogies</div>
                    <div class="example-item"><strong>Physics</strong> + <strong>Basketball</strong> = Understand forces through sports mechanics</div>
                    <div class="example-item"><strong>History</strong> + <strong>Gaming</strong> = Explore empires like strategy games</div>
                    <div class="example-item"><strong>Chemistry</strong> + <strong>Art</strong> = Learn reactions through color mixing</div>
                </div>

                <form id="learningForm">
                    <div class="form-group">
                        <label for="topic" class="form-label">
                            <i class="fas fa-search"></i>
                            What topic would you like to learn?
                        </label>
                        <input type="text" id="topic" name="topic" class="form-input" 
                               placeholder="e.g., Machine Learning, Ancient Rome, Photosynthesis, Quantum Physics" required>
                    </div>

                    <div class="form-group">
                        <label for="interest" class="form-label">
                            <i class="fas fa-heart"></i>
                            What are you passionate about?
                        </label>
                        <input type="text" id="interest" name="interest" class="form-input" 
                               placeholder="e.g., Cooking, Gaming, Music, Sports, Art, Movies" required>
                    </div>

                    <div class="form-group">
                        <label for="learningStyle" class="form-label">
                            <i class="fas fa-cog"></i>
                            Preferred Learning Style
                        </label>
                        <select id="learningStyle" name="learningStyle" class="form-select">
                            <option value="beginner-friendly">🌱 Beginner-Friendly (Simple & Clear)</option>
                            <option value="technical">🔬 Technical & Detailed</option>
                            <option value="visual">🎨 Visual & Graphic</option>
                            <option value="practical">🛠️ Hands-On & Practical</option>
                        </select>
                    </div>

                    <button type="submit" class="primary-btn" id="learnBtn">
                        <i class="fas fa-magic"></i>
                        <span>Generate My Personalized Lesson</span>
                    </button>
                </form>
            </div>

            <!-- Document Learning Tab -->
            <div class="tab-content" id="document-content">
                <h2 class="section-title">Explain Any Document</h2>
                
                <div class="examples-section">
                    <h3 class="examples-title">
                        <i class="fas fa-info-circle"></i>
                        How It Works
                    </h3>
                    <div class="example-item">Upload research papers, articles, or textbooks for personalized explanations</div>
                    <div class="example-item">Supports PDF, TXT, and Markdown files up to 16MB</div>
                    <div class="example-item">Paste content directly for instant analysis</div>
                    <div class="example-item">Get explanations tailored to your interests and learning style</div>
                </div>

                <form id="documentForm">
                    <div class="form-group">
                        <label class="form-label">
                            <i class="fas fa-cloud-upload-alt"></i>
                            Upload Document or Paste Content
                        </label>
                        <div class="file-upload-area" id="fileUploadArea">
                            <div class="file-upload-icon">
                                <i class="fas fa-file-upload"></i>
                            </div>
                            <div class="file-upload-text">Click to upload or drag and drop</div>
                            <div class="file-upload-subtext">Supports PDF, TXT, MD files (max 16MB)</div>
                        </div>
                        <input type="file" id="documentFile" name="documentFile" accept=".pdf,.txt,.md" class="file-input">
                        <div class="file-info" id="fileInfo">
                            <i class="fas fa-check-circle"></i>
                            <strong>Selected:</strong> <span id="fileName"></span>
                        </div>
                    </div>

                    <div class="form-group">
                        <label for="directText" class="form-label">
                            <i class="fas fa-paste"></i>
                            Or paste your text here
                        </label>
                        <textarea id="directText" name="directText" class="form-textarea" 
                                  placeholder="Paste your document content, article text, or any material you'd like explained..."></textarea>
                    </div>

                    <div class="form-group">
                        <label for="documentInterest" class="form-label">
                            <i class="fas fa-heart"></i>
                            Connect it to your interests
                        </label>
                        <input type="text" id="documentInterest" name="documentInterest" class="form-input" 
                               placeholder="e.g., Cooking, Gaming, Music, Sports, Art, Movies" required>
                    </div>

                    <div class="form-group">
                        <label for="documentLearningStyle" class="form-label">
                            <i class="fas fa-cog"></i>
                            Preferred Learning Style
                        </label>
                        <select id="documentLearningStyle" name="documentLearningStyle" class="form-select">
                            <option value="beginner-friendly">🌱 Beginner-Friendly (Simple & Clear)</option>
                            <option value="technical">🔬 Technical & Detailed</option>
                            <option value="visual">🎨 Visual & Graphic</option>
                            <option value="practical">🛠️ Hands-On & Practical</option>
                        </select>
                    </div>

                    <button type="submit" class="primary-btn" id="documentLearnBtn">
                        <i class="fas fa-brain"></i>
                        <span>Explain My Document</span>
                    </button>
                </form>
            </div>

            <div class="loading" id="loading">
                <div class="spinner"></div>
                <div class="loading-text" id="loadingText">Creating your personalized explanation...</div>
            </div>

            <div class="result-container" id="resultContainer">
                <h3 class="result-title" id="resultTitle">
                    <i class="fas fa-lightbulb"></i>
                    <span>Your Personalized Learning Content</span>
                </h3>
                <div class="result-content" id="resultContent"></div>
            </div>
        </div>
    </div>

    <footer class="footer">
        <p>© 2024 Dumbify. Making learning personal and engaging for everyone.</p>
    </footer>

    <script>
        let selectedFile = null;

        function switchTab(tab) {
            // Remove active class from all tabs and content
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            // Add active class to selected tab and content
            event.target.closest('.tab').classList.add('active');
            document.getElementById(tab + '-content').classList.add('active');
            
            // Hide result container when switching tabs
            document.getElementById('resultContainer').classList.remove('show');
        }

        // File upload handling
        const fileUploadArea = document.getElementById('fileUploadArea');
        const fileInput = document.getElementById('documentFile');
        const fileInfo = document.getElementById('fileInfo');
        const fileName = document.getElementById('fileName');

        fileUploadArea.addEventListener('click', () => fileInput.click());

        fileUploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            fileUploadArea.classList.add('drag-over');
        });

        fileUploadArea.addEventListener('dragleave', () => {
            fileUploadArea.classList.remove('drag-over');
        });

        fileUploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            fileUploadArea.classList.remove('drag-over');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFileSelect(files[0]);
            }
        });

        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileSelect(e.target.files[0]);
            }
        });

        function handleFileSelect(file) {
            if (!file.name.match(/\.(txt|md|pdf)$/i)) {
                alert('Please select a .txt, .md, or .pdf file.');
                return;
            }
            
            selectedFile = file;
            fileName.textContent = file.name;
            fileInfo.style.display = 'block';
            
            // Update upload area to show success state
            const icon = fileUploadArea.querySelector('.file-upload-icon i');
            icon.className = 'fas fa-check-circle';
            icon.style.color = 'var(--success-color)';
        }

        // Topic learning form
        document.getElementById('learningForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const topic = document.getElementById('topic').value;
            const interest = document.getElementById('interest').value;
            const learningStyle = document.getElementById('learningStyle').value;
            
            await submitRequest('/learn', {
                topic: topic,
                interest: interest,
                learningStyle: learningStyle
            }, 'Analyzing topic and creating personalized content...', 'Your Personalized Learning Content');
        });

        // Document learning form
        document.getElementById('documentForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const directText = document.getElementById('directText').value.trim();
            
            if (!selectedFile && !directText) {
                alert('Please either upload a document file or paste content in the text area.');
                return;
            }
            
            const formData = new FormData();
            if (selectedFile) {
                formData.append('documentFile', selectedFile);
            }
            if (directText) {
                formData.append('directText', directText);
            }
            formData.append('interest', document.getElementById('documentInterest').value);
            formData.append('learningStyle', document.getElementById('documentLearningStyle').value);
            
            let loadingText = 'Reading and analyzing your document...';
            if (selectedFile && selectedFile.name.toLowerCase().endsWith('.pdf')) {
                loadingText = 'Extracting text from PDF and creating explanation...';
            }
            
            await submitFormData('/learn-document', formData, loadingText, 'Your Document Explained');
        });

        async function submitRequest(url, data, loadingText, resultTitle) {
            showLoading(loadingText);
            
            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                showResult(result, resultTitle);
                
            } catch (error) {
                console.error('Error:', error);
                hideLoading();
                showError('Something went wrong! Please try again.');
            }
        }

        async function submitFormData(url, formData, loadingText, resultTitle) {
            showLoading(loadingText);
            
            try {
                const response = await fetch(url, {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                showResult(result, resultTitle);
                
            } catch (error) {
                console.error('Error:', error);
                hideLoading();
                showError('Something went wrong! Please try again.');
            }
        }

        function showLoading(text) {
            document.getElementById('loadingText').textContent = text;
            document.getElementById('loading').classList.add('show');
            document.querySelectorAll('.primary-btn').forEach(btn => {
                btn.disabled = true;
                const spinner = btn.querySelector('.fa-magic, .fa-brain');
                if (spinner) {
                    spinner.className = 'fas fa-spinner fa-spin';
                }
            });
            document.getElementById('resultContainer').classList.remove('show');
        }

        function hideLoading() {
            document.getElementById('loading').classList.remove('show');
            document.querySelectorAll('.primary-btn').forEach(btn => {
                btn.disabled = false;
                const icons = btn.querySelectorAll('i');
                if (icons[0]) {
                    if (btn.id === 'learnBtn') {
                        icons[0].className = 'fas fa-magic';
                    } else if (btn.id === 'documentLearnBtn') {
                        icons[0].className = 'fas fa-brain';
                    }
                }
            });
        }

        function showResult(data, title) {
            hideLoading();
            
            const resultTitle = document.getElementById('resultTitle');
            const resultTitleSpan = resultTitle.querySelector('span');
            resultTitleSpan.textContent = title;
            
            if (data.error) {
                showError(data.error);
            } else {
                document.getElementById('resultContent').textContent = data.response;
                document.getElementById('resultContainer').classList.add('show');
                
                // Scroll to result
                document.getElementById('resultContainer').scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'start' 
                });
            }
        }

        function showError(message) {
            const resultContainer = document.getElementById('resultContainer');
            const resultContent = document.getElementById('resultContent');
            const resultTitle = document.getElementById('resultTitle');
            
            resultTitle.innerHTML = '<i class="fas fa-exclamation-triangle" style="color: var(--error-color);"></i><span>Error</span>';
            resultContent.innerHTML = `
                <div style="color: var(--error-color); padding: 1rem; background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: var(--border-radius);">
                    <i class="fas fa-exclamation-circle"></i> ${message}
                </div>
            `;
            resultContainer.classList.add('show');
        }

        // Add smooth scrolling for better UX
        document.addEventListener('DOMContentLoaded', function() {
            // Add loading animation to buttons
            const buttons = document.querySelectorAll('.primary-btn');
            buttons.forEach(btn => {
                btn.addEventListener('click', function() {
                    if (!this.disabled) {
                        this.style.transform = 'scale(0.98)';
                        setTimeout(() => {
                            this.style.transform = '';
                        }, 150);
                    }
                });
            });

            // Add typing effect to placeholders (optional enhancement)
            const inputs = document.querySelectorAll('.form-input');
            inputs.forEach(input => {
                input.addEventListener('focus', function() {
                    this.style.transform = 'translateY(-1px)';
                    this.style.boxShadow = '0 0 0 3px rgba(37, 99, 235, 0.1), 0 4px 6px -1px rgba(0, 0, 0, 0.1)';
                });
                
                input.addEventListener('blur', function() {
                    this.style.transform = '';
                    this.style.boxShadow = '';
                });
            });
        });

        // Add keyboard shortcuts for better accessibility
        document.addEventListener('keydown', function(e) {
            // Ctrl/Cmd + Enter to submit forms
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                const activeTab = document.querySelector('.tab-content.active');
                const form = activeTab.querySelector('form');
                if (form) {
                    form.dispatchEvent(new Event('submit'));
                }
            }
        });
    </script>
</body>
</html>
"""

class PersonalizedLearningBot:
    def __init__(self, api_key):
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def learn_topic(self, topic, interest, learning_style):
        prompt = f"""
        I want to learn about: {topic}
        Please explain this topic in a way that connects to my interest in: {interest}
        Learning preferences: {learning_style}
        
        Please:
        1. Start with a brief overview that connects the topic to my interest
        2. Break down the key concepts using analogies or examples from my area of interest
        3. Provide practical applications or real-world examples
        4. Suggest next steps for deeper learning
        5. Make it engaging and easy to understand
        
        Keep the explanation comprehensive but accessible, and really focus on making those connections to what I'm interested in.
        """
        
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            print(f"API Error: {str(e)}")
            return f"Error: {str(e)}"
    
    def explain_document(self, document_content, interest, learning_style):
        # Truncate content if it's too long to fit in the prompt
        max_content_length = 8000  # Leave room for the prompt and response
        if len(document_content) > max_content_length:
            document_content = document_content[:max_content_length] + "\n\n[Content truncated due to length...]"
        
        prompt = f"""
        I have a document with the following content:

        {document_content}

        Please explain this document's content in a way that connects to my interest in: {interest}
        Learning preferences: {learning_style}
        
        Please:
        1. Start with a brief summary of what the document is about
        2. Break down the main concepts using analogies or examples from my area of interest
        3. Explain the key points in an accessible way
        4. Connect the content to practical applications related to my interest
        5. Suggest how I might apply or further explore these concepts
        
        Make it engaging and easy to understand, focusing on connections to what I'm interested in.
        """
        
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=3000,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            print(f"API Error: {str(e)}")
            return f"Error: {str(e)}"

# Initialize the bot with your API key
bot = PersonalizedLearningBot(api_key=API_KEY)

@app.route('/')
def home():
    """Serve the main HTML page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/learn', methods=['POST'])
def learn():
    """Handle topic learning requests"""
    try:
        print("Received topic learning request:", request.json)
        data = request.json
        response = bot.learn_topic(
            data['topic'], 
            data['interest'], 
            data['learningStyle']
        )
        print("Sending response:", response[:100] + "...")
        return jsonify({'response': response})
    except Exception as e:
        print("Error in /learn:", str(e))
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/learn-document', methods=['POST'])
def learn_document():
    """Handle document learning requests (PDF, TXT, MD)"""
    try:
        print("Received document learning request")
        
        document_content = ""
        
        # Check for uploaded file
        if 'documentFile' in request.files:
            file = request.files['documentFile']
            if file.filename != '' and allowed_file(file.filename):
                document_content = extract_text_from_file(file.stream, file.filename)
                if document_content.startswith('Error'):
                    return jsonify({'error': document_content}), 400
        
        # Check for direct text input
        direct_text = request.form.get('directText', '').strip()
        if direct_text:
            document_content = direct_text
        
        if not document_content:
            return jsonify({'error': 'No document content provided'}), 400
        
        if len(document_content.strip()) == 0:
            return jsonify({'error': 'Document content is empty'}), 400
        
        # Get form data
        interest = request.form.get('interest', '')
        learning_style = request.form.get('learningStyle', 'beginner-friendly')
        
        print(f"Document content length: {len(document_content)} characters")
        print(f"Interest: {interest}, Learning style: {learning_style}")
        
        # Generate explanation
        response = bot.explain_document(document_content, interest, learning_style)
        
        print("Sending document response:", response[:100] + "...")
        return jsonify({'response': response})
        
    except Exception as e:
        print("Error in /learn-document:", str(e))
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# Keep the old endpoint for backwards compatibility
@app.route('/learn-text', methods=['POST'])
def learn_text():
    """Handle text learning requests - redirects to learn-document"""
    return learn_document()

if __name__ == '__main__':
    print("🎓 Starting Dumbify Professional Learning Assistant...")
    print("🌐 Open your browser and go to: http://127.0.0.1:5001")
    app.run(debug=True, host='0.0.0.0', port=5001)