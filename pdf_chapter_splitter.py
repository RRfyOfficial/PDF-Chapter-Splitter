#!/usr/bin/env python3
"""
PDF Chapter Splitter with Manual Chapter Selection & Enhanced UI


Requires:
    pip install pypdf
Optional GUI:
    pip install customtkinter
"""
import re
from pathlib import Path
from pypdf import PdfReader, PdfWriter
import sys


# ---------------- Core Logic ----------------
def sanitize_filename(name: str) -> str:
    """Sanitize chapter title for filesystem."""
    return re.sub(r'[\\/*?:"<>|]', '_', name).strip()




def get_chapter_ranges(input_pdf: Path):
    """Return list of (title, start, end) from PDF bookmarks."""
    reader = PdfReader(str(input_pdf))
    outlines = getattr(reader, 'outlines', None) or getattr(reader, 'outline', None)
    if outlines is None:
        outlines = reader.get_outlines()


    raw = []
    for item in outlines:
        title = getattr(item, 'title', None)
        if not title:
            continue
        try:
            page = reader.get_destination_page_number(item)
        except Exception:
            continue
        raw.append((title, page))


    raw.sort(key=lambda x: x[1])
    total = len(reader.pages)
    ranges = []
    for i, (title, start) in enumerate(raw):
        end = raw[i+1][1] - 1 if i+1 < len(raw) else total - 1
        ranges.append((title, start, end))
    return ranges




def write_chapters(ranges, reader, output_dir: Path, selected_idx=None):
    """Write specified chapters to PDF files."""
    if selected_idx is None:
        selected = list(range(len(ranges)))
    else:
        selected = selected_idx
    count = 0
    for num, idx in enumerate(selected, start=1):
        title, start, end = ranges[idx]
        writer = PdfWriter()
        for p in range(start, end+1): writer.add_page(reader.pages[p])
        fname = f"{num:02d}_{sanitize_filename(title)}.pdf"
        with open(output_dir / fname, 'wb') as f:
            writer.write(f)
        count += 1
    return count


# -------- GUI SELECTION --------
try:
    import customtkinter as ctk
    from tkinter import filedialog, messagebox
    GUI_LIB = 'custom'
except ImportError:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
    GUI_LIB = 'ttk'


# ------------------ CUSTOMTKINTER MODE ------------------
if GUI_LIB == 'custom':
    class PDFSplitterApp(ctk.CTk):
        def __init__(self):
            super().__init__()
            ctk.set_appearance_mode('System')
            ctk.set_default_color_theme('dark-blue')
            self.title('PDF Chapter Splitter')
            self.geometry('700x350')
            self.grid_columnconfigure(1, weight=1)


            # Variables
            self.input_var = ctk.StringVar()
            self.output_var = ctk.StringVar()
            self.order_var = ctk.StringVar(value='Ascending')
            self.manual_var = ctk.BooleanVar(value=False)


            # Input PDF row
            ctk.CTkLabel(self, text='Input PDF:').grid(row=0, column=0, sticky='e', padx=10, pady=5)
            ctk.CTkEntry(self, textvariable=self.input_var).grid(row=0, column=1, sticky='we', padx=5)
            ctk.CTkButton(self, text='Browse', command=self.browse_inp).grid(row=0, column=2, padx=10)


            # Output folder row
            ctk.CTkLabel(self, text='Output Folder:').grid(row=1, column=0, sticky='e', padx=10, pady=5)
            ctk.CTkEntry(self, textvariable=self.output_var).grid(row=1, column=1, sticky='we', padx=5)
            ctk.CTkButton(self, text='Browse', command=self.browse_out).grid(row=1, column=2, padx=10)


            # Order selection row
            ctk.CTkLabel(self, text='Output Order:').grid(row=2, column=0, sticky='e', padx=10, pady=5)
            ctk.CTkComboBox(self, variable=self.order_var,
                             values=['Ascending', 'Descending'], state='readonly').grid(row=2, column=1, sticky='w', padx=5)


            # Manual selection toggle
            ctk.CTkCheckBox(self, text='Manual Chapter Selection',
                            variable=self.manual_var).grid(row=3, column=1,
                            sticky='w', padx=5, pady=5)


            # Split button
            ctk.CTkButton(self, text='Split Chapters', fg_color='#10A37F',
                          hover_color='#0c7f5a', command=self.on_split).grid(row=4, column=1, pady=15)


        def browse_inp(self):
            path = filedialog.askopenfilename(filetypes=[('PDF','*.pdf')])
            if path:
                self.input_var.set(path)


        def browse_out(self):
            path = filedialog.askdirectory()
            if path:
                self.output_var.set(path)


        def on_split(self):
            inp = Path(self.input_var.get())
            out = Path(self.output_var.get())
            if not inp.exists() or inp.suffix.lower() != '.pdf':
                messagebox.showerror('Error','Invalid PDF')
                return
            out.mkdir(parents=True, exist_ok=True)


            # Get chapter ranges and optionally reverse
            ranges = get_chapter_ranges(inp)
            reader = PdfReader(str(inp))
            if self.order_var.get() == 'Descending':
                ranges.reverse()


            if self.manual_var.get():
                self.show_manual_dialog(ranges, reader, out)
            else:
                count = write_chapters(ranges, reader, out)
                messagebox.showinfo('Done', f'Created {count} PDFs')


        def show_manual_dialog(self, ranges, reader, out_dir):
            win = ctk.CTkToplevel(self)
            win.title('Select Chapters')
            win.geometry('400x500')


            # Initialize toggle state
            toggle_flag = {'all': True}


            # Toggle button: alternates select/deselect all
            def toggle():
                for var in checks:
                    var.set(toggle_flag['all'])
                toggle_flag['all'] = not toggle_flag['all']


            ctk.CTkButton(win, text='Toggle All', command=toggle).pack(pady=5)


            # Scrollable checkbox frame
            frame = ctk.CTkScrollableFrame(win)
            frame.pack(expand=True, fill='both', pady=5)
            checks = []
            for i, (title, _, _) in enumerate(ranges):
                var = ctk.BooleanVar(value=True)
                ctk.CTkCheckBox(frame, text=f'{i+1:02d} - {title}', variable=var)
                checks.append(var)


            def confirm():
                selected = [i for i, var in enumerate(checks) if var.get()]
                count = write_chapters(ranges, reader, out_dir, selected_idx=selected)
                messagebox.showinfo('Done', f'Created {count} PDFs')
                win.destroy()


            ctk.CTkButton(win, text='Confirm', fg_color='#10A37F',
                          hover_color='#0c7f5a', command=confirm).pack(pady=10)


    def main():
        PDFSplitterApp().mainloop()


# ------------------ TKINTER/TTK MODE ------------------
else:
    class PDFSplitterApp(ttk.Frame):
        def __init__(self, master):
            super().__init__(master, padding=20)
            master.title('PDF Chapter Splitter')
            master.geometry('700x350')
            master.grid_columnconfigure(0, weight=1)
            master.grid_rowconfigure(0, weight=1)
            self.grid(row=0, column=0, sticky='nsew')


            # Variables
            self.inp = tk.StringVar()
            self.outd = tk.StringVar()
            self.order = tk.StringVar(value='Ascending')
            self.manual = tk.BooleanVar(value=False)


            # Input PDF
            ttk.Label(self, text='Input PDF:').grid(row=0, column=0, sticky='e')
            ttk.Entry(self, textvariable=self.inp, width=50).grid(row=0, column=1, sticky='we', padx=5, pady=5)
            ttk.Button(self, text='Browse', command=self.browse_inp).grid(row=0, column=2, padx=5)


            # Output folder
            ttk.Label(self, text='Output Folder:').grid(row=1, column=0, sticky='e')
            ttk.Entry(self, textvariable=self.outd, width=50).grid(row=1, column=1, sticky='we', padx=5, pady=5)
            ttk.Button(self, text='Browse', command=self.browse_out).grid(row=1, column=2, padx=5)


            # Order
            ttk.Label(self, text='Output Order:').grid(row=2, column=0, sticky='e')
            ttk.Combobox(self, textvariable=self.order,
                         values=['Ascending','Descending'], state='readonly').grid(row=2, column=1,
                         sticky='w', padx=5, pady=5)


            # Manual toggle
            ttk.Checkbutton(self, text='Manual Chapter Selection', variable=self.manual).grid(
                row=3, column=1, sticky='w', padx=5, pady=5
            )


            # Split button
            ttk.Button(self, text='Split Chapters', command=self.on_split).grid(row=4, column=1, pady=15)


        def browse_inp(self):
            path = filedialog.askopenfilename(filetypes=[('PDF','*.pdf')])
            if path:
                self.inp.set(path)


        def browse_out(self):
            path = filedialog.askdirectory()
            if path:
                self.outd.set(path)


        def on_split(self):
            inp_path = Path(self.inp.get())
            out_dir = Path(self.outd.get())
            if not inp_path.exists() or inp_path.suffix.lower() != '.pdf':
                messagebox.showerror('Error', 'Invalid PDF')
                return
            out_dir.mkdir(parents=True, exist_ok=True)
            ranges = get_chapter_ranges(inp_path)
            reader = PdfReader(str(inp_path))
            if self.order.get() == 'Descending':
                ranges = list(reversed(ranges))


            if self.manual.get():
                self.popup_manual(ranges, reader, out_dir)
            else:
                count = write_chapters(ranges, reader, out_dir)
                messagebox.showinfo('Done', f'Created {count} PDFs')


        def popup_manual(self, ranges, reader, out_dir):
            win = tk.Toplevel(self)
            win.title('Select Chapters')
            win.geometry('400x500')


            # Toggle state
            toggle_flag = {'all': True}
            vars = []


            # Single toggle button
            def toggle():
                for v in vars:
                    v.set(toggle_flag['all'])
                toggle_flag['all'] = not toggle_flag['all']


            ttk.Button(win, text='Toggle All', command=toggle).pack(pady=5)


            # Scrollable list
            frame = ttk.Frame(win)
            frame.pack(fill='both', expand=True)
            canvas = tk.Canvas(frame)
            sb = ttk.Scrollbar(frame, orient='vertical', command=canvas.yview)
            scroll_frame = ttk.Frame(canvas)
            scroll_frame.bind(
                '<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
            )
            canvas.create_window((0,0), window=scroll_frame, anchor='nw')
            canvas.configure(yscrollcommand=sb.set)


            # Mousewheel scrolling
            def _on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), 'units')
            canvas.bind_all('<MouseWheel>', _on_mousewheel)


            canvas.pack(side='left', fill='both', expand=True)
            sb.pack(side='right', fill='y')


            for i, (title, _, _) in enumerate(ranges):
                v = tk.BooleanVar(value=True)
                ttk.Checkbutton(scroll_frame, text=f'{i+1:02d} - {title}', variable=v).pack(anchor='w')
                vars.append(v)


            def confirm():
                sel = [i for i, v in enumerate(vars) if v.get()]
                count = write_chapters(ranges, reader, out_dir, selected_idx=sel)
                messagebox.showinfo('Done', f'Created {count} PDFs')
                win.destroy()


            ttk.Button(win, text='Confirm', command=confirm).pack(pady=10)


    def main(): PDFSplitterApp().mainloop()


# -------- Application Entry Point --------
if __name__ == '__main__':
    # Launch appropriate GUI based on available library
    if GUI_LIB == 'custom':
        app = PDFSplitterApp()
        app.mainloop()
    else:
        root = tk.Tk()
        PDFSplitterApp(root)
        root.mainloop()