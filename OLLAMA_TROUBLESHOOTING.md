# 🔧 Ollama Troubleshooting Guide

## ⏱️ **Timeout Issues**

### **Problem: "Request timed out" or "Read timed out"**

**Solutions:**

1. **Increase System Resources**
   ```bash
   # Check available RAM
   free -h
   
   # Check CPU usage
   top
   ```

2. **Use a Smaller Model**
   ```bash
   # Download a smaller, faster model
   ollama pull phi-2        # 2.7B parameters
   ollama pull gemma2:2b    # 2B parameters
   ollama pull mistral:7b   # 7B parameters
   ```

3. **Optimize Ollama Settings**
   ```bash
   # Set environment variables for better performance
   export OLLAMA_HOST=0.0.0.0
   export OLLAMA_ORIGINS=*
   
   # Restart Ollama
   ollama serve
   ```

4. **Reduce Context Length**
   - The system now automatically truncates long contexts
   - Try asking shorter, more specific questions
   - Upload smaller documents

## 🚀 **Performance Optimization**

### **For Better Speed:**

1. **Use GPU Acceleration** (if available)
   ```bash
   # Check if CUDA is available
   nvidia-smi
   
   # Install CUDA-enabled Ollama
   # Follow instructions at: https://ollama.ai/docs/gpu
   ```

2. **Optimize Model Selection**
   | Model | Speed | Quality | RAM Usage |
   |-------|-------|---------|-----------|
   | **phi-2** | ⚡ Fastest | ⭐⭐⭐ | 4GB |
   | **gemma2:2b** | ⚡ Fast | ⭐⭐⭐ | 4GB |
   | **mistral:7b** | 🏃 Medium | ⭐⭐⭐⭐ | 8GB |
   | **gemma3:latest** | 🐌 Slower | ⭐⭐⭐⭐⭐ | 8GB+ |

3. **System Recommendations**
   - **RAM**: 16GB+ for optimal performance
   - **CPU**: Modern multi-core processor
   - **Storage**: SSD for faster model loading
   - **GPU**: NVIDIA GPU with 6GB+ VRAM (optional)

## 🔄 **Quick Fixes**

### **Immediate Solutions:**

1. **Restart Ollama Server**
   ```bash
   # Stop current server (Ctrl+C)
   # Then restart
   ollama serve
   ```

2. **Clear Model Cache**
   ```bash
   # Remove and re-download model
   ollama rm gemma3:latest
   ollama pull gemma3:latest
   ```

3. **Use Fallback Provider**
   - Switch to OpenAI in the UI if available
   - This provides instant responses while Ollama loads

4. **Reduce Load**
   - Close other applications using RAM
   - Don't run multiple AI models simultaneously
   - Wait for first response before asking another question

## 📊 **Monitoring**

### **Check System Status:**
```bash
# Monitor Ollama processes
ps aux | grep ollama

# Check memory usage
htop

# Monitor GPU usage (if available)
nvidia-smi -l 1
```

### **Test Model Performance:**
```bash
# Quick test
ollama run gemma3:latest "Hello, how are you?"

# Benchmark test
time ollama run gemma3:latest "Write a short story about a cat."
```

## 🎯 **Best Practices**

### **For Optimal Performance:**

1. **Start Simple**
   - Begin with shorter questions
   - Gradually increase complexity
   - Let the model warm up

2. **Batch Operations**
   - Ask multiple questions at once
   - Use the conversation history feature
   - Avoid rapid-fire questions

3. **Model Management**
   - Keep only the models you need
   - Use smaller models for quick tasks
   - Reserve larger models for complex analysis

4. **System Maintenance**
   - Restart Ollama periodically
   - Monitor system resources
   - Update Ollama regularly

## 🆘 **When All Else Fails**

### **Emergency Solutions:**

1. **Switch to Cloud Provider**
   - Use OpenAI API as fallback
   - Provides instant responses
   - No local resource requirements

2. **Use Smaller Model**
   ```bash
   ollama pull phi-2
   # Update model in UI to phi-2
   ```

3. **Restart Everything**
   ```bash
   # Stop all processes
   pkill ollama
   
   # Restart system
   sudo reboot
   
   # Start fresh
   ollama serve
   ```

4. **Check System Resources**
   ```bash
   # Free up memory
   sudo sync && sudo sysctl -w vm.drop_caches=3
   
   # Check disk space
   df -h
   ```

## 📞 **Getting Help**

### **If problems persist:**

1. **Check Ollama Logs**
   ```bash
   ollama serve --verbose
   ```

2. **Community Support**
   - [Ollama GitHub Issues](https://github.com/ollama/ollama/issues)
   - [Ollama Discord](https://discord.gg/ollama)
   - [Ollama Documentation](https://ollama.ai/docs)

3. **System Requirements**
   - Ensure you meet minimum requirements
   - Consider upgrading hardware if needed

---

**💡 Tip**: The timeout issue is usually resolved by using a smaller model or optimizing system resources. Start with `phi-2` for the fastest experience! 