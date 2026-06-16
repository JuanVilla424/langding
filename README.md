<div align="center">

# 🗺️ Langding

_AI-Powered Landing Page Translation Tool_

![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)
![AI](https://img.shields.io/badge/AI-OpenAI%20%7C%20Anthropic-green.svg)
![Status](https://img.shields.io/badge/Status-Development-yellow.svg)
![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)
![Automation](https://img.shields.io/badge/Automation-Translation-orange.svg)

</div>

---

## 🌐 Overview

Langding is an AI-driven landing page auto-translation tool designed for developers who need to localize their websites efficiently. It extracts meaningful content from HTML files, translates it using advanced AI models (OpenAI GPT or Anthropic Claude), and generates complete multilingual versions with automatic language detection.

### 🎯 Core Translation Features

- **🤖 AI-Powered Translation**: Leverages OpenAI GPT or Anthropic Claude for context-aware translations
- **🌍 Multi-Language Support**: Supports 10+ languages with automatic browser detection
- **📄 Smart Template System**: Generates reusable templates with intelligent placeholder mapping
- **🔄 Auto-Redirect Generation**: Creates language detection and redirect pages
- **⚡ Batch Processing**: Efficiently processes multiple HTML files
- **🎛️ Flexible Configuration**: Environment-based and CLI configuration options

---

<div align="center">

## 📚 Table of Contents

|        🎯 **Core Sections**         |                📖 **Technical Docs**                |               🚀 **Advanced Usage**               |
| :---------------------------------: | :-------------------------------------------------: | :-----------------------------------------------: |
|      [✨ Features](#-features)      | [🔧 Environment Variables](#-environment-variables) | [📁 Processing Templates](#-processing-templates) |
|  [🛠️ Installation](#️-installation)  |  [🎛️ Command Line Options](#-command-line-options)  |    [🤖 AI Provider Setup](#-ai-provider-setup)    |
| [⚙️ Configuration](#️-configuration) |               [📊 Logging](#-logging)               |             [📝 Examples](#-examples)             |
|         [🚀 Usage](#-usage)         |               [📜 License](#-license)               |              [📫 Contact](#-contact)              |

</div>

---

## ✨ Features

```mermaid
graph TD
    A[HTML Input] --> B[Content Extraction]
    B --> C{AI Translation}
    C -->|OpenAI GPT| D[Context-Aware Translation]
    C -->|Anthropic Claude| D
    D --> E[Template Generation]
    E --> F[Multi-Language Output]
    F --> G[Auto-Redirect Pages]

    H[Configuration] --> C
    H --> I[Environment Variables]
    H --> J[CLI Arguments]

    K[Logging System] --> L[Rotation & Monitoring]

    style A fill:#e1f5fe
    style F fill:#f3e5f5
    style G fill:#fff3e0
    style C fill:#e8f5e8
```

### 🔧 Core Translation Engine

- **Smart Content Extraction**: Prioritizes headings, paragraphs, and meta content
- **Context Preservation**: Maintains technical accuracy and professional tone
- **Template Generation**: Creates reusable placeholders for efficient processing

### 🌐 Multi-AI Support

- **OpenAI GPT Integration**: Support for GPT-3.5-turbo and GPT-4 models
- **Anthropic Claude Integration**: Claude-3-haiku and Claude-3-sonnet support
- **Provider Switching**: Easy configuration between AI providers

### 📄 Output Management

- **Structured File Generation**: Organized output with language-specific files
- **Auto-Redirect System**: Browser language detection with fallback support
- **GitHub Pages Ready**: Direct deployment compatibility

---

## 🛠️ Installation

### Prerequisites

- **Python 3.12+**
- **Git**
- **AI API Key** (OpenAI OR Anthropic)

### Quick Setup

```bash
# Clone repository
git clone https://github.com/JuanVilla424/langding.git
cd langding

# Setup virtual environment (always .venv)
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 🔑 AI Provider Setup

Choose **ONE** provider:

**Option A: OpenAI**

```bash
export OPENAI_API_KEY='sk-your-openai-key-here'
export AI_PROVIDER='openai'
```

**Option B: Anthropic Claude**

```bash
export ANTHROPIC_API_KEY='sk-ant-your-anthropic-key-here'
export AI_PROVIDER='anthropic'
```

---

## ⚙️ Configuration

### Environment Configuration

Create `.env` file:

```env
# Output Configuration
OUTPUT_DIR=output

# Language Selection (JSON format)
LANGS=["English","Spanish","French","German","Portuguese","Italian","Japanese","Korean","Chinese","Arabic"]

# AI Provider Selection
AI_PROVIDER=openai  # Options: openai, anthropic

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-3.5-turbo

# Anthropic Configuration
ANTHROPIC_API_KEY=your-anthropic-api-key-here
ANTHROPIC_MODEL=claude-3-haiku-20240307
```

### 📋 Configuration Variables

| Variable            | Description                          | Default                                   | Required                |
| :------------------ | :----------------------------------- | :---------------------------------------- | :---------------------- |
| `OUTPUT_DIR`        | Output directory for generated files | `output`                                  | ❌                      |
| `LANGS`             | Target languages (JSON array)        | `["English","Spanish","French","German"]` | ❌                      |
| `AI_PROVIDER`       | AI service provider                  | `openai`                                  | ❌                      |
| `OPENAI_API_KEY`    | OpenAI API key                       | -                                         | ✅ (if using OpenAI)    |
| `ANTHROPIC_API_KEY` | Anthropic API key                    | -                                         | ✅ (if using Anthropic) |
| `OPENAI_MODEL`      | OpenAI model name                    | `gpt-3.5-turbo`                           | ❌                      |
| `ANTHROPIC_MODEL`   | Anthropic model name                 | `claude-3-haiku-20240307`                 | ❌                      |

---

## 🚀 Usage

### Basic Commands

```bash
# Process templates directory
python langding.py --process-templates

# Process custom input directory
python langding.py --input-dir input_html --output-dir translated_html

# Specify target languages
python langding.py --process-templates --languages Spanish French German

# Enable debug logging
python langding.py --process-templates --log-level DEBUG
```

### 📁 Processing Templates

**Input Structure:**

```
templates/
├── index.html          # Main landing page
├── about.html          # Additional pages
└── contact.html        # More pages
```

**Command:**

```bash
python langding.py --process-templates
```

**Generated Output:**

```
output/
├── index.html                    # Auto-redirect page
├── english_index.html           # English version
├── spanish_index.html           # Spanish version
├── french_index.html            # French version
├── template_index.html          # Template with placeholders
└── index_translations.json     # Translation metadata
```

---

## 🎛️ Command Line Options

```bash
python langding.py [OPTIONS]

Options:
  --input-dir TEXT        Input directory containing HTML files
  --output-dir TEXT       Output directory for generated files
  --template-dir TEXT     Template directory (default: templates)
  --languages TEXT...     Target languages for translation
  --log-level CHOICE      Logging level [DEBUG|INFO|WARNING|ERROR]
  --process-templates     Process files from templates directory
  --help                  Show help message and exit
```

---

## 📝 Examples

### Example 1: Basic Translation

```bash
# Translate templates to Spanish and French
python langding.py --process-templates --languages Spanish French
```

### Example 2: Custom Workflow

```bash
# Custom directories with specific languages
python langding.py \
  --input-dir my_website \
  --output-dir translations \
  --languages English Spanish Portuguese Italian \
  --log-level INFO
```

### Example 3: Development Mode

```bash
# Debug mode with detailed logging
python langding.py --process-templates --log-level DEBUG
```

---

## 🤖 AI Provider Setup

### OpenAI Configuration

1. Get API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Set environment variables:

```bash
export OPENAI_API_KEY='sk-your-key-here'
export AI_PROVIDER='openai'
```

### Anthropic Claude Configuration

1. Get API key from [Anthropic Console](https://console.anthropic.com/)
2. Set environment variables:

```bash
export ANTHROPIC_API_KEY='sk-ant-your-key-here'
export AI_PROVIDER='anthropic'
```

---

## 📊 Logging

Logs are stored in `logs/langding.log` with automatic rotation:

- **File Size Limit**: 5MB per file
- **Backup Count**: 5 files maximum
- **Format**: `timestamp - logger - level - message`

### Log Levels

- **`DEBUG`**: Detailed diagnostic information
- **`INFO`**: General operational messages
- **`WARNING`**: Warning messages for potential issues
- **`ERROR`**: Error messages for failed operations

---

## 📫 Contact

For any inquiries or support, please open an issue or contact [r6ty5r296it6tl4eg5m.constant214@passinbox.com](mailto:r6ty5r296it6tl4eg5m.constant214@passinbox.com).

---

## 📜 License

<div align="center">

2026 — This project is licensed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html). You are free to use, modify, and distribute this software under the terms of the GPL-3.0 license. For more details, please refer to the [LICENSE](LICENSE) file included in this repository.

</div>
