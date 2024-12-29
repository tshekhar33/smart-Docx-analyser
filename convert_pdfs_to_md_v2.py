import os
import pdfplumber

# Directory containing PDF files
pdf_directory = 'c:/Users/Sekhar/Documents/Finance rule/'

# Loop through all files in the directory
for filename in os.listdir(pdf_directory):
    if filename.endswith('.pdf'):
        pdf_path = os.path.join(pdf_directory, filename)
        md_filename = filename.replace('.pdf', '.md')
        md_path = os.path.join(pdf_directory, md_filename)

        # Extract text from PDF
        with pdfplumber.open(pdf_path) as pdf:
            with open(md_path, 'w', encoding='utf-8') as md_file:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        md_file.write(text + '\n\n')

print('Conversion completed!')
