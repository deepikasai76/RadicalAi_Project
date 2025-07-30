# 🤖 Radical AI - Document Q&A & Quiz Generator

A powerful AI application that transforms your PDF documents into intelligent, interactive learning experiences. Built with modern AI technologies for seamless document analysis and interactive learning.

## ✨ **Key Features**

### 🎯 **Core Functionality**
- **📄 Smart Document Processing** - Upload PDFs and extract intelligent text chunks
- **❓ AI-Powered Q&A** - Ask questions about your documents with contextual answers
- **📝 Interactive Quiz Generation** - Create personalized quizzes from document content
- **💬 Conversation Memory** - AI remembers your previous questions and context
- **📊 Learning Analytics** - Track your learning progress and engagement

### 🤖 **AI Capabilities**
- **Multi-Provider AI Support** - Switch between Ollama (local) and OpenAI (cloud)
- **Intelligent Search** - Hybrid search combining keyword and semantic matching
- **Context-Aware Responses** - AI understands document context and conversation history
- **Adaptive Question Generation** - Creates questions based on document complexity
- **Real-time Processing** - Instant answers and quiz generation

### 🔒 **Security & Data Management**
- **Local Processing** - Efficient local document processing
- **Secure API Keys** - Protected OpenAI integration with secure key management
- **Data Control** - Complete control over your documents and data
- **Flexible Deployment** - Works both online and offline

### 🎨 **User Experience**
- **Intuitive Interface** - Clean, modern web interface
- **Drag & Drop Upload** - Easy PDF file upload
- **Real-time Feedback** - Instant processing status and results
- **Responsive Design** - Works on desktop, tablet, and mobile
- **Navigation Hub** - Seamless switching between features

## 🛠️ **Tech Stack**

### **Frontend & UI**
- **Streamlit** - Modern web application framework
- **Custom CSS** - Beautiful, responsive styling
- **Interactive Components** - Dynamic forms, buttons, and displays

### **AI & Machine Learning**
- **Ollama** - Local large language models (LLM)
- **OpenAI API** - Cloud-based AI (optional)
- **Sentence Transformers** - Text embeddings and similarity
- **ChromaDB** - Vector database for document storage and semantic search
- **Hybrid Search** - BM25 + semantic search combination

### **Document Processing**
- **PyPDF** - PDF text extraction and processing
- **Smart Chunking** - Intelligent document segmentation
- **Text Preprocessing** - Clean and optimize document content

### **Data Management**
- **ChromaDB Vector Database** - High-performance vector storage for document embeddings
- **Vector Storage** - Efficient document indexing and similarity search
- **Conversation Buffer** - Session and history management
- **Session State** - User session persistence

### **Development & Deployment**
- **Python 3.8+** - Modern Python with type hints
- **Modular Architecture** - Clean, maintainable code structure
- **Error Handling** - Robust error management and recovery
- **Performance Optimization** - Cached instances and efficient processing

## 🚀 **Quick Start**

### 1. **Install Python Dependencies**
```bash
pip install -r requirements.txt
```

### 2. **Install Ollama (Local AI)**
```bash
# Windows
winget install Ollama.Ollama

# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh
```

### 3. **Start Ollama & Download Model**
```bash
# Start the AI server
ollama serve

# Download a model (in new terminal)
ollama pull mistral:7b
```

### 4. **Run the Application**
```bash
streamlit run main_simplified.py
```

That's it! Open your browser and start uploading documents.

## 🎯 **How It Works**

### **Document Processing Pipeline**
```
📄 PDF Upload → 🔍 Text Extraction → 📝 Smart Chunking → 🗄️ ChromaDB Vector Storage → 🤖 AI Ready
```

### **Q&A Workflow**
```
❓ User Question → 🔍 Hybrid Search (BM25 + ChromaDB) → 📄 Context Retrieval → 🤖 AI Generation → 💬 Answer
```

### **Quiz Generation Process**
```
📚 Document Content → 🧠 AI Analysis → 📝 Question Creation → 🎯 Quiz Assembly → 📊 Interactive Quiz
```

### **ChromaDB Vector Database**
- **Document Embeddings** - Converts text chunks into high-dimensional vectors
- **Similarity Search** - Finds most relevant document sections using semantic similarity
- **Persistent Storage** - Stores embeddings locally for fast retrieval
- **Real-time Indexing** - Updates search index as new documents are added

## 🔧 **Configuration Options**

### **AI Provider Selection**
- **Ollama (Recommended)** - Local AI processing, free, works offline
- **OpenAI** - Cloud-based, requires API key, pay-per-use
- **Automatic Fallback** - Seamless switching between providers

### **Model Options**
- **mistral:7b** - Good balance of speed and quality
- **llama2:7b** - Fast and reliable
- **gemma3:latest** - High quality, slower processing
- **Custom Models** - Add your own Ollama models

### **Search Configuration**
- **ChromaDB Vector Search** - High-performance semantic similarity search
- **Hybrid Search** - Combines keyword (BM25) and semantic (ChromaDB) search
- **Keyword Search** - Exact term matching with BM25 algorithm
- **Semantic Search** - Meaning-based matching using ChromaDB embeddings
- **Customizable Weights** - Adjust search strategy between keyword and semantic

## 📁 **Project Structure**

```
radical_ai/
├── main_simplified.py          # Main application entry point
├── app_config.py              #  Configuration and initialization
├── ui_components.py           #  UI components and sidebar
├── page_modules/              #  User interface pages
│   ├── upload_page.py         #  Document upload interface
│   ├── qa_page.py            #  Q&A interface
│   ├── quiz_page.py          #  Quiz generation interface
│   └── history_page.py       #  Conversation history
├── modules/                   # Core AI and processing logic
│   ├── ai_provider.py        #  AI provider management
│   ├── document_processor.py #  PDF processing
│   ├── vector_store.py       #  ChromaDB document storage
│   ├── hybrid_search.py      #  Intelligent search (BM25 + ChromaDB)
│   ├── quiz_generator.py     #  Quiz generation
│   └── conversation_buffer.py # Conversation memory
├── static/                   #  Styling and assets
│   └── style.css            #  Custom CSS styling
├── requirements.txt          # Python dependencies
├── .env                     #  Environment variables (not in Git)
└── .gitignore              #  Security protection
```

## 🎓 **Use Cases**

### **📚 Education & Learning**
- **Study Aid** - Ask questions about textbooks and research papers
- **Quiz Creation** - Generate practice tests from course materials
- **Research Assistant** - Analyze academic papers and documents
- **Language Learning** - Practice with foreign language documents

### **💼 Business & Professional**
- **Document Analysis** - Extract insights from reports and manuals
- **Training Materials** - Create quizzes from company documentation
- **Research Tool** - Analyze market reports and industry papers
- **Knowledge Base** - Build interactive company knowledge systems

### **🔬 Research & Development**
- **Literature Review** - Analyze research papers and publications
- **Data Analysis** - Extract information from technical documents
- **Collaboration** - Share insights from research materials
- **Documentation** - Create interactive technical documentation

### **📖 Personal Use**
- **Book Analysis** - Deep dive into books and articles
- **Learning Enhancement** - Interactive learning from any document
- **Knowledge Management** - Organize and understand personal documents
- **Study Planning** - Create study guides from educational materials

## 🔒 **Security & Data Management**

### **Data Protection**
- **Local Processing** - Efficient local document processing
- **Secure Storage** - Protected local database storage
- **Session Management** - Conversation history stored locally
- **Data Control** - Complete control over your documents

### **AI Processing**
- **Local AI Models** - Ollama runs locally for fast processing
- **Cloud AI Integration** - OpenAI for advanced capabilities
- **Secure API Keys** - Environment variable protection
- **Flexible Processing** - Choose local or cloud AI as needed

### **User Control**
- **Data Ownership** - Complete control over your data
- **Deletion Control** - Remove documents and conversations anytime
- **Export Capability** - Download your data in standard formats
- **Session Management** - Manage conversation history

## 🆘 **Troubleshooting**

### **Common Issues**

**"Ollama server not available"**
- Run `ollama serve` in terminal

**"Model not found"**
- Run `ollama pull model_name`

**"Import errors"**
- Run `pip install -r requirements.txt`

**"Document processing failed"**
- Check if PDF is corrupted or password-protected

### **Performance Tips**

**For Faster Processing:**
- Use smaller PDF files
- Choose faster AI models (llama2:7b)
- Close other applications to free up RAM
- Use SSD storage for better performance

**For Better Results:**
- Use high-quality PDFs with clear text
- Ask specific questions for better answers
- Use hybrid search for comprehensive results
- Let the AI model warm up before heavy use

## 🚀 **Advanced Features**

### **Custom AI Models**
```bash
# Add custom Ollama models
ollama pull your-custom-model
# Select in the app sidebar
```

### **API Integration**
```python
# Use OpenAI as fallback
OPENAI_API_KEY=your_key_here
# Automatically switches when Ollama unavailable
```

### **Document Management**
- **Multiple Documents** - Upload and manage multiple PDFs
- **Document Switching** - Easy switching between documents
- **Document Deletion** - Safe removal with confirmation
- **Document Analytics** - Track usage and performance

### **Conversation Features**
- **Context Memory** - AI remembers previous conversations
- **Session Management** - Multiple conversation sessions
- **Export Conversations** - Download chat history
- **Search Conversations** - Find specific interactions

## 💡 **Tips for Best Results**

### **Document Preparation**
- **High-Quality PDFs** - Use clear, text-based PDFs
- **Structured Content** - Well-organized documents work better
- **Reasonable Size** - Large documents may take longer to process
- **Text-Rich Content** - Avoid image-heavy documents

### **Question Asking**
- **Be Specific** - Specific questions get better answers
- **Use Context** - Reference previous questions for follow-ups
- **Try Different Phrasings** - Rephrase if you don't get the answer you want
- **Use Hybrid Search** - Combines keyword and semantic search

### **Quiz Generation**
- **Choose Appropriate Difficulty** - Match quiz level to document complexity
- **Vary Question Types** - Mix multiple choice, true/false, and short answer
- **Review Generated Questions** - Check accuracy before using
- **Use for Learning** - Quizzes help reinforce understanding

## 🤝 **Contributing**

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Test thoroughly**
5. **Submit a pull request**

### **Development Setup**
```bash
# Clone the repository
git clone https://github.com/yourusername/radical-ai.git
cd radical-ai

# Install dependencies
pip install -r requirements.txt

# Run in development mode
streamlit run main_simplified.py
```

## 📝 **License**

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## 🙏 **Acknowledgments**

- **Ollama** - For providing local AI capabilities
- **Streamlit** - For the excellent web framework
- **ChromaDB** - For high-performance vector database and semantic search
- **Sentence Transformers** - For text embeddings and similarity
- **OpenAI** - For cloud AI integration

---

**💡 Pro Tip**: Start with Ollama for local processing and cost-effectiveness, then add OpenAI if you need cloud-based features!

**🚀 Ready to transform your documents into intelligent learning experiences?**

