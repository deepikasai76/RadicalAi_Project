# 🤖 Radical AI - Privacy-Focused Document Q&A & Quiz Generator

A powerful, privacy-focused AI application for document analysis, Q&A, and quiz generation using local AI models.

## ✨ Features

- **📄 Document Processing**: Upload and analyze PDF documents
- **❓ Smart Q&A**: Ask questions about your documents with AI-powered answers
- **📝 Quiz Generation**: Create interactive quizzes from document content
- **💬 Conversation History**: Track and review your learning journey
- **📊 Export Functionality**: Download conversation history as JSON
- **Learning Analytics**: Track your engagement and progress

### 🤖 **Multi-Provider AI Support**
- **Ollama (Local)**: Privacy-focused, free local AI
- **OpenAI API**: Cloud-based AI with latest models
- **Automatic Fallback**: Seamless switching between providers
- **Provider Testing**: Built-in connection testing

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- AI Provider (choose one):
  - **Ollama (Local)** - Privacy-focused, free (recommended)
  - **OpenAI API** - Cloud-based, requires API key

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/radical-ai.git
   cd radical-ai
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up AI Provider**
   
   **Option A: Ollama (Local) - Recommended**
   ```bash
   # Install Ollama
   winget install Ollama.Ollama  # Windows
   brew install ollama           # macOS
   
   # Start Ollama server
   ollama serve
   
   # Download a model
   ollama pull llama2:7b
   ```
   
   **Option B: OpenAI API**
   ```bash
   # Copy the example environment file
   cp env.example .env
   
   # Edit .env and add your OpenAI API key
   OPENAI_API_KEY=your_actual_api_key_here
   ```

4. **Run the application**
   ```bash
   streamlit run main_simplified.py
   ```

## 🔐 Security & API Keys

### **Important Security Notes:**

1. **Never commit API keys to Git**
   - The `.env` file is already in `.gitignore`
   - Only `env.example` is tracked (contains no real keys)

2. **Setting up API keys safely:**
   ```bash
   # Copy the example file
   cp env.example .env
   
   # Edit .env with your real API key
   # DO NOT commit .env to Git!
   ```

3. **Environment Variables:**
   - `OPENAI_API_KEY`: Your OpenAI API key (only if using OpenAI)
   - `OLLAMA_BASE_URL`: Ollama server URL (default: http://localhost:11434)
   - `OLLAMA_DEFAULT_MODEL`: Default model name (default: mistral:7b)

4. **Privacy Protection:**
   - Ollama runs completely locally - no data leaves your machine
   - OpenAI API sends data to external servers
   - Choose based on your privacy requirements

## 🎯 Usage

### Basic Workflow

1. **Upload Document**: Upload a PDF file through the web interface
2. **Process**: The system extracts and indexes the content
3. **Ask Questions**: Use the Q&A interface to ask questions about the document
4. **Generate Quizzes**: Create interactive quizzes to test understanding
5. **Review History**: Track your learning progress and conversations

### AI Provider Selection

- **Ollama (Recommended)**: Privacy-focused, free, works offline
- **OpenAI**: Cloud-based, requires API key, pay-per-use
- **Automatic Fallback**: System switches providers if one fails

## 🔧 Configuration

### AI Provider Setup
- **Ollama (Local)**: Privacy-focused, free, runs locally
- **OpenAI API**: Cloud-based, requires API key, pay-per-use

### Environment Variables (Optional)
- `OPENAI_API_KEY`: Your OpenAI API key (only needed for OpenAI provider)

### Customization
- Modify `static/style.css` for custom styling
- Adjust AI provider settings in `modules/ai_provider.py`
- Configure document processing in `modules/document_processor.py`

## 🏗️ Project Structure

```
radical_ai/
├── main_simplified.py       # Main application (simplified)
├── main.py                  # Original main application
├── app_config.py           # Application configuration
├── ui_components.py        # UI components and sidebar
├── page_modules/
│   ├── upload_page.py      # Document upload interface
│   ├── qa_page.py         # Q&A interface
│   ├── quiz_page.py       # Quiz generation
│   └── history_page.py    # History and analytics
├── modules/
│   ├── document_processor.py # PDF processing
│   ├── vector_store.py      # ChromaDB operations
│   ├── hybrid_search.py     # Search functionality
│   ├── quiz_generator.py    # Quiz generation
│   ├── conversation_buffer.py # Conversation management
│   └── ai_provider.py       # AI provider management
├── static/
│   └── style.css           # Custom styling
├── uploads/                # Uploaded documents
├── chroma_db/             # Vector database
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in Git)
├── env.example           # Example environment file
└── .gitignore           # Git ignore rules
```

## 🚀 Development

### Local Development
```bash
streamlit run main_simplified.py
```

### Adding New Features
- AI Providers: Extend `modules/ai_provider.py`
- UI Components: Modify `ui_components.py`
- Page Modules: Add to `page_modules/`
- Document Processing: Enhance `modules/document_processor.py`

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 🆘 Troubleshooting

### Common Issues

1. **Ollama Timeout**: Check if Ollama server is running with `ollama serve`
2. **Model Not Found**: Run `ollama pull model_name`
3. **API Key Issues**: Check `.env` file configuration
4. **Import Errors**: Install missing dependencies with `pip install -r requirements.txt`

### Getting Help

- Check the troubleshooting guides
- Review the documentation
- Open an issue on GitHub

---

**💡 Tip**: Start with Ollama for privacy and cost-effectiveness, then add OpenAI if you need cloud-based features!
