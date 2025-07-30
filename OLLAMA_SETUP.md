# 🦙 Ollama Setup Guide

This guide will help you set up Ollama (local AI) for your document intelligence platform.

## 🚀 Quick Start

### 1. Install Ollama

**Windows:**
```bash
# Using winget (recommended)
winget install Ollama.Ollama

# Or download from https://ollama.ai/download
```

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### 2. Start Ollama Server
```bash
ollama serve
```

### 3. Download Models
```bash
# For document Q&A (recommended)
ollama pull llama2:13b

# For coding/technical documents
ollama pull codellama

# For lightweight use
ollama pull mistral
```

### 4. Test Installation
```bash
# Test if Ollama is working
ollama run llama2:13b "Hello, how are you?"
```

## 🔧 System Requirements

### Minimum Requirements:
- **RAM**: 8GB (16GB recommended)
- **Storage**: 4GB per model
- **OS**: Windows 10+, macOS 10.15+, Linux
- **GPU**: Optional but recommended

### Recommended Setup:
- **RAM**: 16GB+
- **Storage**: 20GB+ for multiple models
- **GPU**: NVIDIA GPU with 6GB+ VRAM
- **CPU**: Modern multi-core processor

## 📊 Model Comparison

| Model | Size | Best For | RAM Usage | Performance |
|-------|------|----------|-----------|-------------|
| **Llama 2** | 7B | General use | 8GB | ⭐⭐⭐⭐ |
| **Llama 2** | 13B | Better reasoning | 16GB | ⭐⭐⭐⭐⭐ |
| **Mistral** | 7B | Fast, efficient | 8GB | ⭐⭐⭐⭐ |
| **CodeLlama** | 7B | Programming | 8GB | ⭐⭐⭐⭐⭐ |
| **Phi-2** | 2.7B | Lightweight | 4GB | ⭐⭐⭐ |

## 🎯 Integration with Your Platform

### Automatic Detection
Your document intelligence platform will automatically detect if Ollama is running and use it as the primary AI provider.

### Manual Configuration
1. Start your Streamlit app: `streamlit run main_simplified.py`
2. Go to the sidebar → AI Provider Configuration
3. Select "ollama" from the dropdown
4. Click "Switch Provider"
5. Test the connection

### Provider Priority
The platform will automatically choose providers in this order:
1. **Ollama (Local)** - Privacy-focused, free
2. **OpenAI** - Cloud-based, requires API key

## 🔒 Privacy Benefits

### ✅ What Ollama Provides:
- **Complete privacy**: Your data never leaves your computer
- **No API costs**: Free after initial setup
- **Offline operation**: Works without internet
- **No usage tracking**: No external monitoring
- **Compliance friendly**: Perfect for sensitive documents

### 🎯 Perfect For:
- Legal documents
- Medical records
- Financial reports
- Confidential business documents
- Research papers
- Personal documents

## 🛠️ Troubleshooting

### Common Issues:

**1. "Ollama server is not available"**
```bash
# Start Ollama server
ollama serve
```

**2. "Model not found"**
```bash
# Download the model
ollama pull llama2:13b
```

**3. "Out of memory"**
```bash
# Use a smaller model
ollama pull mistral
# or
ollama pull phi-2
```

**4. Slow responses**
- Ensure you have enough RAM
- Consider using a smaller model
- Check if GPU acceleration is available

### Performance Tips:

**1. Use GPU acceleration (if available):**
```bash
# Check if CUDA is available
nvidia-smi
```

**2. Optimize model selection:**
- Use 7B models for general use
- Use 13B models for better quality
- Use 2.7B models for speed

**3. Monitor resource usage:**
```bash
# Check Ollama processes
ps aux | grep ollama
```

## 🔄 Switching Between Providers

Your platform supports multiple AI providers:

### Ollama (Local)
- ✅ Privacy-focused
- ✅ No costs
- ✅ Always available
- ⚠️ Requires local setup

### OpenAI (Cloud)
- ✅ Easy setup
- ✅ Latest models
- ⚠️ Requires API key
- ⚠️ Usage costs
- ⚠️ Data sent to external servers

## 📈 Performance Comparison

| Aspect | Ollama (Local) | OpenAI API |
|--------|----------------|------------|
| **Privacy** | 🔒 Perfect | ⚠️ External |
| **Cost** | 💰 Free | 💸 Pay-per-use |
| **Speed** | ⚡ Fast | 🐌 Network dependent |
| **Reliability** | ✅ Always available | 🌐 Internet required |
| **Setup** | 🔧 One-time | ✅ Instant |

## 🎉 Next Steps

1. **Install Ollama** using the commands above
2. **Start the server**: `ollama serve`
3. **Download a model**: `ollama pull llama2:13b`
4. **Run your platform**: `streamlit run main_simplified.py`
5. **Select Ollama** in the AI Provider dropdown
6. **Test with your documents**!

## 📞 Support

If you encounter issues:
1. Check the [Ollama documentation](https://ollama.ai/docs)
2. Visit the [Ollama GitHub](https://github.com/ollama/ollama)
3. Check system requirements and troubleshooting tips above

---

**Enjoy your privacy-focused, cost-effective AI document intelligence platform! 🚀🔒** 