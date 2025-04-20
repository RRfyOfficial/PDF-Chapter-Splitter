#!/usr/bin/env python3
"""
PDF Chapter Splitter with Modern, Polished GUI Using Tkinter and ttk

Requires:
    pip install pypdf

Usage:
    Splits a PDF into chapter-based PDFs by reading its outline/bookmarks.
    After splitting, sort your file explorer by "Date Modified" ascending
    to view chapters in sequence, or select "Descending" for reverse order.
"""
import re
from pathlib import Path
from pypdf import PdfReader, PdfWriter

# Attempt to import Destination for outline items
try:
    from pypdf.generic import Destination
except ImportError:
    try:
        from pypdf._reader import Destination
    except ImportError:
        Destination = None

import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

# ---------- Core Logic ----------
def sanitize_filename(name: str) -> str:
    """Replace illegal filename characters with underscores and strip spaces."""
    return re.sub(r'[\\/*?":"<>|]', "_", name).strip()

def split_pdf_by_chapters(input_pdf: Path, output_dir: Path, reverse_order: bool = False) -> int:
    """
    Split a PDF by its top-level bookmarks into separate chapter PDFs.
    If reverse_order is True, newest chapters appear first.
    """
    reader = PdfReader(str(input_pdf))
    outlines = getattr(reader, 'outlines', None) or getattr(reader, 'outline', None)
    if outlines is None:
        try:
            outlines = reader.get_outlines()
        except Exception:
            raise RuntimeError("No outlines/bookmarks found in PDF.")

    chapters = []
    for item in outlines:
        if Destination and isinstance(item, Destination):
            title, page = item.title, reader.get_destination_page_number(item)
        elif hasattr(item, 'title'):
            title = item.title
            try:
                page = reader.get_destination_page_number(item)
            except Exception:
                continue
        else:
            continue
        chapters.append((title, page))

    if not chapters:
        raise RuntimeError("No valid chapters found in PDF outlines.")

    chapters.sort(key=lambda x: x[1])
    total = len(reader.pages)
    ranges = []
    for i, (title, start) in enumerate(chapters):
        end = chapters[i+1][1] - 1 if i+1 < len(chapters) else total - 1
        ranges.append((title, start, end))
    if reverse_order:
        ranges.reverse()

    for idx, (title, s, e) in enumerate(ranges, 1):
        writer = PdfWriter()
        for p in range(s, e+1): writer.add_page(reader.pages[p])
        fname = f"{idx:02d}_{sanitize_filename(title)}.pdf"
        with open(output_dir / fname, 'wb') as f: writer.write(f)
    return len(ranges)

# ---------- GUI Class ----------
class PDFSplitterApp(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.master.title("PDF Chapter Splitter")
        self.master.geometry("700x280")
        self.master.configure(bg="#f7f8fa")
        self.create_styles()
        self.build_ui()

    def create_styles(self):
        style = ttk.Style(self)
        style.theme_use('clam')
        # Frame and overall
        style.configure('TFrame', background='#f7f8fa')
        # Labels
        style.configure('TLabel', background='#f7f8fa', font=('Helvetica', 11))
        # Entry fields
        style.configure('TEntry', font=('Helvetica', 11), fieldbackground='white', background='white')
        # Combobox
        style.configure('TCombobox', font=('Helvetica', 11), fieldbackground='white')
        # Buttons
        style.configure('Accent.TButton', font=('Helvetica', 11, 'bold'), foreground='white', background='#10A37F', padding=6)
        style.map('Accent.TButton', background=[('active', '#0c7f5a')])

    def build_ui(self):
        self.grid(padx=20, pady=20)
        # Input PDF row
        ttk.Label(self, text="Input PDF:").grid(row=0, column=0, sticky='e', pady=8)
        self.input_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.input_var, width=50).grid(row=0, column=1, sticky='we', padx=8)
        ttk.Button(self, text="Browse", command=self.browse_input, style='Accent.TButton').grid(row=0, column=2)

        # Output folder row
        ttk.Label(self, text="Output Folder:").grid(row=1, column=0, sticky='e', pady=8)
        self.output_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.output_var, width=50).grid(row=1, column=1, sticky='we', padx=8)
        ttk.Button(self, text="Browse", command=self.browse_output, style='Accent.TButton').grid(row=1, column=2)

        # Order selection row
        ttk.Label(self, text="Output Order:").grid(row=2, column=0, sticky='e', pady=8)
        self.order_var = tk.StringVar(value='Ascending')
        order_cb = ttk.Combobox(self, textvariable=self.order_var, values=['Ascending','Descending'], state='readonly', width=18)
        order_cb.grid(row=2, column=1, sticky='w', padx=8)

        # Split button
        ttk.Button(self, text="Split Chapters", command=self.on_split, style='Accent.TButton').grid(row=3, column=1, pady=20)

        # Reminder note
        note = "Sort output folder by Date Modified ascending to view sequence"
        ttk.Label(self, text=note, foreground='#555555', font=('Helvetica', 10)).grid(row=4, column=0, columnspan=3)

        # Adjust grid weights
        self.columnconfigure(1, weight=1)

    def browse_input(self):
        path = filedialog.askopenfilename(filetypes=[("PDF files","*.pdf")])
        if path: self.input_var.set(path)

    def browse_output(self):
        path = filedialog.askdirectory()
        if path: self.output_var.set(path)

    def on_split(self):
        inp = Path(self.input_var.get())
        out = Path(self.output_var.get())
        if not inp.exists() or inp.suffix.lower() != '.pdf':
            messagebox.showerror("Error", "Select a valid PDF file.")
            return
        out.mkdir(parents=True, exist_ok=True)
        rev = (self.order_var.get() == 'Descending')
        try:
            cnt = split_pdf_by_chapters(inp, out, reverse_order=rev)
            messagebox.showinfo("Done", f"Created {cnt} chapter PDFs.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

# ---------- Main ----------
if __name__ == '__main__':
    root = tk.Tk()
    PDFSplitterApp(root)
    root.mainloop()