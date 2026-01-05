# Markdown Viewer

A lightweight local Markdown viewer built with Streamlit. Navigate your file system, preview Markdown files, and render Mermaid diagrams with simple SVG download support.

## Features

- **File Explorer**: Navigate your local file system via the sidebar.
- **Markdown Preview**: Instant rendering of selected Markdown files.
- **Mermaid Support**: Automatically renders `mermaid` code blocks as diagrams.
- **Download Charts**: Download your rendered Mermaid diagrams as SVG files.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Unigalactix/MD-VIEWER.git
   cd MD-VIEWER
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`.
