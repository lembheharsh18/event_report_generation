# Event Report Generation System

A comprehensive Streamlit-based application for generating professional event reports and social media content using AI-powered analysis.

## 🚀 Features

### 📊 **Event Analysis & Reporting**
- **Event Analyzer** (`analyzer.py`): AI-powered analysis of event feedback and data
- **Report Generator** (`report_generator.py`): Generate comprehensive event reports
- **Charts Generation** (`charts.py`): Create visual representations of event data

### 📱 **Social Media Content Generation**
- **Post-Event Content Generator** (`post_event.py`): Create engaging social media posts for multiple platforms
- **Pre-Event Content Generator** (`pre_event_content_gen.py`): Generate promotional content before events

### 🎯 **Supported Platforms**
- LinkedIn (Professional posts with structured format)
- Instagram (Visual, emoji-rich captions)
- WhatsApp (Friendly, celebratory messages)
- Twitter/X (Concise, character-limited posts)

### 🔧 **Advanced Capabilities**
- Multi-format file support (DOCX, PDF, Excel)
- AI-powered content refinement
- Professional tone adaptation
- Automatic hashtag generation
- Two-step content optimization process

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Groq API key for AI content generation

### Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/event_report_generation.git
cd event_report_generation

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download required NLTK data
python -m nltk.downloader vader_lexicon
python -m nltk.downloader punkt
python -m nltk.downloader stopwords
```

## 🔑 Configuration

1. **Get API Keys**:
   - **Groq API Key**: Sign up at [Groq Console](https://console.groq.com/)

2. **Environment Variables** (optional):
   ```bash
   export GROQ_API_KEY="your_groq_api_key_here"
   ```

## 🚀 Usage

### Main Application
```bash
streamlit run app.py
```

### Individual Components
```bash
# Post-Event Content Generator
streamlit run post_event.py

# Pre-Event Content Generator
streamlit run pre_event_content_gen.py

# Event Analyzer
streamlit run analyzer.py

# Report Generator
streamlit run report_generator.py

# Charts Generation
streamlit run charts.py
```

## 📋 How It Works

### 1. **Post-Event Content Generation**
- Upload event reports (DOCX/PDF format)
- AI analyzes the content and extracts key information
- Generates platform-specific social media posts
- Two-step refinement process for professional quality
- Automatic hashtag generation and optimization

### 2. **Event Analysis**
- Process event feedback and data
- Generate insights and recommendations
- Create visual charts and graphs
- Sentiment analysis of feedback

### 3. **Report Generation**
- Compile comprehensive event reports
- Include analytics and visualizations
- Export in multiple formats
- Professional formatting and styling

### 4. **Content Optimization**
- Platform-specific tone adaptation
- Character limit compliance
- Professional language refinement
- Engagement optimization

## 📁 Project Structure

```
event_report_generation/
├── app.py                      # Main Streamlit application
├── post_event.py              # Post-event social media content generator
├── pre_event_content_gen.py   # Pre-event promotional content
├── analyzer.py                # Event feedback analyzer
├── report_generator.py        # Event report generator
├── charts.py                  # Data visualization and charts
├── requirements.txt           # Python dependencies
└── README.md                 # This file
```

## 🔧 Dependencies

### **Core Framework**
- `streamlit` - Web application framework
- `streamlit-option-menu` - Enhanced UI components

### **Data Processing**
- `pandas` - Data manipulation and analysis
- `numpy` - Numerical computing
- `openpyxl` - Excel file processing

### **Data Visualization**
- `matplotlib` - Basic plotting library
- `seaborn` - Statistical data visualization
- `plotly` - Interactive plotting

### **AI and NLP**
- `groq` - AI content generation API
- `transformers` - Advanced NLP models
- `torch` - Deep learning framework
- `nltk` - Natural language processing
- `textblob` - Text processing

### **File Processing**
- `python-docx` - DOCX file processing
- `pymupdf` - PDF file processing
- `python-dotenv` - Environment variable management

### **Utilities**
- `requests` - HTTP library
- `pillow` - Image processing

## 🎨 Features in Detail

### **AI-Powered Content Generation**
- Uses Groq's Llama3-70B model for high-quality content
- Platform-specific tone and formatting
- Automatic hashtag generation
- Professional refinement process
- Multi-language support capabilities

### **Multi-Format Support**
- **DOCX**: Microsoft Word documents
- **PDF**: Portable Document Format
- **Excel**: Spreadsheet data processing
- Automatic text extraction and parsing
- Table and chart data extraction

### **Smart Content Analysis**
- Extracts key event information
- Identifies highlights and achievements
- Generates appropriate acknowledgments
- Maintains professional tone across platforms
- Sentiment analysis and feedback processing

### **Advanced Visualization**
- Interactive charts and graphs
- Statistical analysis visualization
- Professional report formatting
- Export capabilities

## 🚀 Performance Features

- **Fast Processing**: Optimized for quick content generation
- **Memory Efficient**: Handles large documents efficiently
- **Scalable**: Supports multiple concurrent users
- **Caching**: Intelligent caching for improved performance




