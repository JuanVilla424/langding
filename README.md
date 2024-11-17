# 🗺️ Langding

![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)
![Status](https://img.shields.io/badge/Status-Development-blue.svg)
![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)

Langding is an AI-driven landing page auto-translation tool. It reads HTML files, extracts text content, translates it into multiple languages using OpenAI's GPT models, and generates translated HTML files. This tool is useful for quickly localizing web pages into different languages.

## 📚 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
  - [Initialization](#-initialization)
- [Environment Variables](#-environment-variables)
- [Logging](#-logging)
- [License](#-license)
- [Contact](#-contact)

## ✨ Features

- **Automated Translation**: Translates HTML content into multiple languages using OpenAI's GPT models.
- **Template Generation**: Creates HTML templates with placeholders for easy text replacement.
- **Multi-language Support**: Supports translation into any language specified.
- **Logging**: Detailed logging with rotating file handlers for easy debugging and monitoring.
- **Configuration**: Easily configurable via environment variables and command-line arguments.

## 🛠️ Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/JuanVilla424/langding.git
   cd langding
   ```

2. **Create a Virtual Environment**

   ```bash
   python -m venv venv
   ```

3. **Activate the Virtual Environment**

   On Unix or MacOS:

   ```bash
   source venv/bin/activate
   ```

   On Windows:

   ```bash
    .\venv\Scripts\activate
   ```

   - or

   ```bash
    powershell.exe -ExecutionPolicy Bypass -File .\venv\Scripts\Activate.ps1
   ```

4. **Upgrade pip**

   ```bash
   python -m ensurepip
   pip install --upgrade pip
   ```

5. **Set up your OpenAI API key**:

   Obtain your API key from OpenAI and set it as an environment variable:

   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```

6. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

   - Deactivate the Virtual Environment

   When you're done, deactivate the environment:

   ```bash
    deactivate
   ```

## ⚙️ Configuration

**Environment Variables**:

Create a .env file in the project root directory and populate it with the following variables:

```bash
INPUT_DIR=input
OUTPUT_DIR=output
LANGS=["English","Spanish","French","German"]
OPENAI_MODEL="gpt-3.5-turbo"
```

- Descriptions:
  - INPUT_DIR: Directory containing input HTML files.
  - OUTPUT_DIR: Directory to save output files.
  - LANGS: List of languages to translate into.
  - OPENAI_MODEL: OpenAI model target.

## 🚀 Usage

### 📦 Initialization

1. Prepare Input HTML Files:
   Place your HTML files that you want to translate into the input directory (or your specified input directory).

2. Configure Settings:
   Ensure your environment variables are set, or prepare to pass configurations via command-line arguments.

### Translating HTML Files

Run the main script:

```bash
python langding.py
```

This will process all HTML files in the input directory and generate translated versions in the output directory.

### Command-Line Arguments

You can customize the behavior using the following arguments:

`--input-dir: Specify the input directory containing HTML files.`

```bash
python langding.py --input-dir path/to/your/input
```

`--output-dir: Specify the output directory for the translated files.`

```bash
python langding.py --output-dir path/to/your/output
```

`--languages: List of languages to translate into.`

```bash
python langding.py --languages Spanish,Italian,Japanese
```

`--log-level: Set the logging level (INFO or DEBUG).`

```bash
python langding.py --log-level DEBUG
```

### 📝 Example Usage

```bash
python langding.py --input-dir input_html --output-dir translated_html --languages Spanish,German --log-level INFO
```

### 📜 Environment Variables

Ensure all required environment variables are set in the .env file:

    Global Variables
        INPUT_DIR: Directory containing input HTML files.
        OUTPUT_DIR: Directory to save output files.
        LANGS: List of languages to translate into.
        OPENAI_MODEL: OpenAI Model Target.

## 📊 Logging

Logs are maintained in logs/langding.log with rotating file handlers to prevent excessive file sizes.

    Log Levels:
        INFO: General operational messages.
        DEBUG: Detailed diagnostic information.

## 📫 Contact

For any inquiries or support, please open an issue or contact [r6ty5r296it6tl4eg5m.constant214@passinbox.com](mailto:r6ty5r296it6tl4eg5m.constant214@passinbox.com).

---

## 📜 License

2024 - This project is licensed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html). You are free to use, modify, and distribute this software under the terms of the GPL-3.0 license. For more details, please refer to the [LICENSE](LICENSE) file included in this repository.
