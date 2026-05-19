# webToDoc

## Overview

`webToDoc` is a Python project designed to convert web links into documentation formats. The primary goal is to automate the extraction and conversion of web content into structured documents, such as Markdown or text files. While the project aims to support PDF generation in the future, its current functionality focuses on converting web pages—specifically API documentation—into Markdown and text documents.

## Current Features

- **Web to Markdown/Text Conversion:**
  - Converts web pages (such as API documentation) into Markdown (`.md`) and text (`.txt`) files.
  - Currently, the project has been used to convert Dhan API documentation into organized Markdown files.
- **Dhan Docs Integration:**
  - The `dhan_docs/` directory contains structured documentation for Dhan APIs, including:
    - Individual Markdown files for each API endpoint or topic
    - Combined documentation files
    - Metadata for documentation management

## Project Structure

```
webToDoc.py            # Main script for conversion
requirements.txt       # Python dependencies

dhan_docs/
  metadata.json        # Metadata for documentation
  combined/            # Combined documentation files
  markdown/            # Individual Markdown files for Dhan APIs
  raw_html/            # (Optional) Raw HTML files
  txt/                 # (Optional) Text files
```

## Usage

1. **Install Dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```
2. **Run the Conversion Script:**
   ```powershell
   python webToDoc.py
   ```
   - The script will process web links (currently configured for Dhan APIs) and generate documentation in the `dhan_docs/` directory.

## Future Plans

- Add support for direct web-to-PDF conversion
- Enhance support for more websites and documentation formats
- Improve metadata and search capabilities

## Contributing

Contributions are welcome! Please open issues or submit pull requests for improvements, bug fixes, or new features.

## License

This project is licensed under the MIT License.
