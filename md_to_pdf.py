import tkinter as tk
from tkinter import filedialog, messagebox
import pdfkit
import markdown

def convert_md_to_pdf(md_file, pdf_file):
    try:
        # Read the Markdown file
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Add CSS for styling
        css = '''
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }
                h1 { color: #2c3e50; text-align: center; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
                .question { background-color: #f9f9f9; padding: 15px; margin: 15px 0; border-left: 5px solid #3498db; }
                .options { margin-left: 20px; }
                .answer { color: #27ae60; font-weight: bold; margin-top: 10px; }
                .explanation { background-color: #edf7ff; padding: 10px; margin-top: 10px; border-radius: 5px; }
            </style>
        '''
        
        # Convert Markdown to HTML with extensions
        html_content = markdown.markdown(md_content, extensions=['tables'])
        
        # Combine everything
        final_html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            {css}
        </head>
        <body>
            {html_content}
        </body>
        </html>
        '''
        
        # Configure path to wkhtmltopdf
        config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
        
        # Convert HTML to PDF with options for better formatting and suppress warnings
        options = {
            'page-size': 'A4',
            'margin-top': '20mm',
            'margin-right': '20mm',
            'margin-bottom': '20mm',
            'margin-left': '20mm',
            'encoding': 'UTF-8',
            'no-outline': None,
            'quiet': ''  # This will suppress some warnings
        }
        
        # Convert HTML to PDF using the configuration
        pdfkit.from_string(final_html, pdf_file, configuration=config, options=options)
        messagebox.showinfo("Success", f"Converted '{md_file}' to '{pdf_file}' successfully!")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def select_md_file():
    md_file = filedialog.askopenfilename(title="Select Markdown File", filetypes=[("Markdown Files", "*.md")])
    md_file_entry.delete(0, tk.END)
    md_file_entry.insert(0, md_file)

def select_pdf_file():
    pdf_file = filedialog.asksaveasfilename(title="Save PDF As", defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
    pdf_file_entry.delete(0, tk.END)
    pdf_file_entry.insert(0, pdf_file)

def convert():
    md_file = md_file_entry.get()
    pdf_file = pdf_file_entry.get()
    if md_file and pdf_file:
        convert_md_to_pdf(md_file, pdf_file)
    else:
        messagebox.showwarning("Warning", "Please select both Markdown and PDF files.")

# Create the main window
root = tk.Tk()
root.title("Markdown to PDF Converter")

# Create and place the widgets
tk.Label(root, text="Markdown File:").grid(row=0, column=0, padx=10, pady=10)
md_file_entry = tk.Entry(root, width=50)
md_file_entry.grid(row=0, column=1, padx=10, pady=10)
tk.Button(root, text="Browse", command=select_md_file).grid(row=0, column=2, padx=10, pady=10)

tk.Label(root, text="Save as PDF:").grid(row=1, column=0, padx=10, pady=10)
pdf_file_entry = tk.Entry(root, width=50)
pdf_file_entry.grid(row=1, column=1, padx=10, pady=10)
tk.Button(root, text="Browse", command=select_pdf_file).grid(row=1, column=2, padx=10, pady=10)

tk.Button(root, text="Convert", command=convert).grid(row=2, column=1, pady=20)

# Run the application
root.mainloop()