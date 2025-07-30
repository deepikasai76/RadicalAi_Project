# 🤖 Radical AI - Document Q&A with Local AI

A simple web app that lets you upload PDF documents and ask questions about them using AI. Everything runs on your computer - no data sent to external servers.

## 🎯 What It Does

1. **Upload a PDF** - Any document you want to understand
2. **Ask Questions** - Get AI-powered answers about the content
3. **Generate Quizzes** - Test your knowledge with auto-generated questions
4. **Track Progress** - See your learning history and conversations

## 🚀 Quick Start

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install Ollama (Local AI)
```bash
# Windows
winget install Ollama.Ollama

# macOS
brew install ollama
```

### 3. Start Ollama & Download Model
```bash
# Start the AI server
ollama serve

# Download a model (in new terminal)
ollama pull mistral:7b
```

### 4. Run the App
```bash
streamlit run main_simplified.py
```

That's it! Open your browser and start uploading documents.

## 🔒 Privacy First

- **Everything runs locally** on your computer
- **No data sent to external servers**
- **No API keys needed** (unless you want to use OpenAI)
- **Completely free** after initial setup

## 📁 Project Structure

```
radical_ai/
├── main_simplified.py          # Main app (start here)
├── modules/
│   ├── ai_provider.py         # Handles AI (Ollama/OpenAI)
│   ├── document_processor.py  # Processes PDFs
│   ├── vector_store.py        # Stores document data
│   └── quiz_generator.py      # Creates quizzes
├── page_modules/
│   ├── upload_page.py         # Upload interface
│   ├── qa_page.py            # Q&A interface
│   ├── quiz_page.py          # Quiz interface
│   └── history_page.py       # History view
└── requirements.txt           # Python packages
```

## 🛠️ How It Works

1. **Document Processing**: PDF → Text → Chunks → Vector Database
2. **Question Answering**: Your question → Search relevant chunks → AI generates answer
3. **Quiz Generation**: Document content → AI creates questions → Interactive quiz
4. **History Tracking**: All conversations saved locally

## 🔧 Configuration

### Using Different AI Models
- **mistral:7b** (default) - Good balance of speed/quality
- **llama2:7b** - Fast and reliable
- **gemma3:latest** - High quality, slower

Switch models in the app's sidebar.

### Using OpenAI (Optional)
If you want cloud-based AI instead:
1. Get an OpenAI API key
2. Create `.env` file: `OPENAI_API_KEY=your_key_here`
3. Select OpenAI in the app sidebar

## 🆘 Common Issues

**"Ollama server not available"**
- Run `ollama serve` in terminal

**"Model not found"**
- Run `ollama pull model_name`

**"Import errors"**
- Run `pip install -r requirements.txt`

## 💡 Tips

- Start with shorter documents for faster processing
- Use specific questions for better answers
- Try different models to find what works best for you
- The app works offline once Ollama is running

---

**Built with**: Streamlit, Ollama, ChromaDB, Sentence Transformers
