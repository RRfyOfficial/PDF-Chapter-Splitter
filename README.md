# PDF Chapter Splitter

**Split large PDF documents into individual chapter PDFs**

A polished Python application that automatically parses a master PDF's outline (bookmarks) and generates separate PDF files for each chapter. Built to adapt seamlessly to your environment, it uses **CustomTkinter** for a sleek modern GUI when available, or falls back to **Tkinter/ttk** for maximum compatibility.

## Key Features

- **Automatic Outline Parsing**\
  Reads the PDF's embedded bookmarks to detect chapter titles and starting pages.

- **Adaptive GUI**

  - **CustomTkinter Mode**: Modern dark/light themes, smooth hover animations, responsive layout.
  - **ttk Fallback**: Clean, lightweight interface if CustomTkinter isn't installed.

- **Flexible Ordering**\
  Choose **Ascending** (first-to-last chapter) or **Descending** (last-to-first) output.

- **Smart Filenaming**\
  Sanitizes chapter titles into safe filenames, prefixed with a zero-padded index (`01_Introduction.pdf`).

- **Environment-Aware**

  - **Requires**: Python 3.6+, `pypdf` library.
  - **Optional**: `customtkinter` for enhanced UI.

- **Cross-Platform**\
  Works on Windows, macOS, and Linux—just sort your output folder by **Date Modified (ascending)** to view chapters in correct order.

## Installation

```bash
pip install pypdf
# Optional for modern GUI:
pip install customtkinter
```

## Usage

```bash
python pdf_chapter_splitter.py
```

1. Launch the app.
2. Browse for your master PDF.
3. Choose an output folder.
4. Select **Ascending** or **Descending** order.
5. Click **Split Chapters**.
6. Check the output folder (sort by Date Modified ascending).
