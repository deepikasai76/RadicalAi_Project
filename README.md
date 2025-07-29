# 🚀 Radical AI - Advanced Document Intelligence Platform

Transform your documents into intelligent knowledge bases with AI-powered Q&A, quiz generation, and conversation memory.

## ✨ Features

### 📄 **Document Processing**
- **PDF Upload & Processing**: Upload PDF documents and extract text content
- **Intelligent Chunking**: Smart text segmentation for optimal AI understanding
- **Vector Embeddings**: Convert document content into searchable vectors

### ❓ **AI-Powered Q&A**
- **Context-Aware Answers**: Get accurate responses based on your document content
- **Hybrid Search**: Combines semantic and keyword search for better results
- **Conversation Memory**: Maintain context across multiple questions

### 📝 **Quiz Generation**
- **AI-Generated Quizzes**: Create custom quizzes based on document content
- **Multiple Choice Questions**: Interactive quiz format with explanations
- **Score Tracking**: Monitor your learning progress

### 💬 **Conversation History**
- **Chat History**: View all your Q&A interactions
- **Export Functionality**: Download conversation history as JSON
- **Learning Analytics**: Track your engagement and progress

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- OpenAI API key

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

3. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Run the application**
   ```bash
   streamlit run upload_screen.py
   ```

## 🎯 Usage

### 1. **Upload Document**
- Navigate to the upload screen
- Click "Choose a PDF document" or drag and drop
- Click "🚀 Process Document" to start processing

### 2. **Ask Questions**
- Go to the Q&A section
- Type your question about the document
- Get AI-powered answers with source context

### 3. **Generate Quizzes**
- Visit the Quiz section
- Specify a topic and number of questions
- Take the generated quiz and see your score

### 4. **View History**
- Check the History section for:
  - Conversation history
  - Quiz results
  - Learning analytics

## 🏗️ Project Structure

```
radical_ai/
├── upload_screen.py          # Main upload interface
├── pages/
│   ├── qa_screen.py         # Q&A interface
│   ├── quiz_screen.py       # Quiz generation
│   └── history_screen.py    # History and analytics
├── modules/
│   ├── document_processor.py # PDF processing
│   ├── vector_store.py      # ChromaDB operations
│   ├── hybrid_search.py     # Search functionality
│   ├── conversation_buffer.py # Chat memory
│   └── quiz_generator.py    # Quiz generation
├── static/
│   └── style.css           # Professional styling
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key for AI responses

### Customization
- Modify `static/style.css` for custom styling
- Update prompts in individual modules for different AI behaviors
- Adjust chunk sizes in `document_processor.py` for different document types

## 🚀 Deployment

### Local Development
```bash
streamlit run upload_screen.py
```

### Cloud Deployment
The application can be deployed on:
- **Streamlit Cloud**: Connect your GitHub repository
- **Heroku**: Use the provided Procfile
- **AWS/GCP**: Deploy as a containerized application

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for GPT-3.5-turbo API
- **ChromaDB** for vector storage
- **Streamlit** for the web interface
- **SentenceTransformers** for embeddings

## 📞 Support

If you encounter any issues or have questions:
- Open an issue on GitHub
- Check the documentation in the `CONCEPTS_AND_ARCHITECTURE.md` file
- Review the `QUICK_REFERENCE.md` for quick setup

---

**🚀 Radical AI** - Transform your documents into intelligent knowledge bases
