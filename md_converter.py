import streamlit as st
import markdown
import pdfkit
import os
import PyPDF2
from pathlib import Path
import tempfile
import logging
import re
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_content_structure(md_content):
    """Analyze the content structure and identify different sections."""
    # Identify different types of content
    chapters = re.findall(r'CHAPTER[- ]\w+', md_content)
    sections = re.findall(r'\d{3}[- ][A-Z][^\n]+', md_content)
    subsections = re.findall(r'\d{3}\.\d+[- ][A-Z][^\n]+', md_content)
    
    return {
        'chapters': chapters,
        'sections': sections,
        'subsections': subsections
    }

def format_content(md_content):
    """Format the content based on its structure."""
    # Add proper spacing and formatting for chapters
    md_content = re.sub(
        r'(CHAPTER[- ]\w+)',
        r'<div class="chapter">\n# \1\n</div>',
        md_content
    )
    
    # Format section numbers and titles
    md_content = re.sub(
        r'(\d{3})[- ]([A-Z][^\n]+)',
        r'## \1 \2',
        md_content
    )
    
    # Format subsections
    md_content = re.sub(
        r'(\d{3}\.\d+)[- ]([A-Z][^\n]+)',
        r'### \1 \2',
        md_content
    )
    
    # Format lists and enumerations
    md_content = re.sub(r'(?m)^\s*(\d+\)|\w\))\s*', r'1. ', md_content)
    
    # Add spacing after paragraphs
    md_content = re.sub(r'\n\n', r'\n\n<br>\n\n', md_content)
    
    return md_content

def convert_md_to_pdf(md_content, output_filename):
    try:
        # Analyze content structure
        structure = analyze_content_structure(md_content)
        logger.info(f"Content structure: {structure}")
        
        # Format content
        formatted_content = format_content(md_content)
        
        # Convert markdown to HTML
        html_content = markdown.markdown(formatted_content, extensions=['tables', 'toc'])
        
        # Parse HTML to add additional styling
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Add classes to different elements
        for h1 in soup.find_all('h1'):
            h1['class'] = 'chapter-title'
        for h2 in soup.find_all('h2'):
            h2['class'] = 'section-title'
        for h3 in soup.find_all('h3'):
            h3['class'] = 'subsection-title'
        
        # Wrap the HTML content with proper HTML structure and CSS
        full_html = f"""
        <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    @page {{
                        size: A4;
                        margin: 2.5cm 2cm;
                        @top-center {{
                            content: "Indian Railways Financial Code";
                            font-size: 10pt;
                            color: #666;
                        }}
                        @bottom-right {{
                            content: "Page " counter(page);
                            font-size: 10pt;
                        }}
                    }}
                    
                    body {{
                        font-family: "Times New Roman", Times, serif;
                        line-height: 1.5;
                        font-size: 12pt;
                        text-align: justify;
                    }}
                    
                    .chapter-title {{
                        font-size: 16pt;
                        font-weight: bold;
                        text-align: center;
                        margin-top: 3cm;
                        margin-bottom: 2cm;
                        page-break-before: always;
                        text-transform: uppercase;
                    }}
                    
                    .section-title {{
                        font-size: 14pt;
                        font-weight: bold;
                        margin-top: 1.5cm;
                        margin-bottom: 1cm;
                        color: #2c3e50;
                    }}
                    
                    .subsection-title {{
                        font-size: 12pt;
                        font-weight: bold;
                        margin-top: 1cm;
                        margin-bottom: 0.5cm;
                        color: #34495e;
                    }}
                    
                    p {{
                        margin-bottom: 0.8em;
                        text-align: justify;
                        hyphens: auto;
                    }}
                    
                    ol, ul {{
                        margin-left: 2cm;
                        margin-bottom: 1em;
                    }}
                    
                    li {{
                        margin-bottom: 0.5em;
                    }}
                    
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin: 1cm 0;
                    }}
                    
                    th, td {{
                        border: 1px solid #ddd;
                        padding: 8px;
                        text-align: left;
                    }}
                    
                    th {{
                        background-color: #f5f5f5;
                        font-weight: bold;
                    }}
                    
                    .note {{
                        background-color: #f8f9fa;
                        padding: 1em;
                        margin: 1em 0;
                        border-left: 4px solid #2c3e50;
                    }}
                    
                    .page-break {{
                        page-break-before: always;
                    }}
                </style>
            </head>
            <body>
                {soup.prettify()}
            </body>
        </html>
        """
        
        # Create a temporary HTML file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.html', mode='w', encoding='utf-8') as f:
            f.write(full_html)
            temp_html = f.name
        
        try:
            # Configure wkhtmltopdf path
            config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
            
            # Configure options for better PDF layout
            options = {
                'quiet': '',
                'enable-local-file-access': None,
                'margin-top': '25mm',
                'margin-right': '20mm',
                'margin-bottom': '25mm',
                'margin-left': '20mm',
                'encoding': 'UTF-8',
                'footer-right': '[page]',
                'footer-font-size': '9',
                'header-line': None,
                'header-spacing': '5',
                'enable-smart-shrinking': None,
                'page-size': 'A4',
                'dpi': '300',
                'image-quality': '100',
                'outline': None,
                'outline-depth': '3'
            }
            
            # Convert HTML to PDF
            pdfkit.from_file(temp_html, output_filename, configuration=config, options=options)
            logger.info(f"Successfully converted to PDF: {output_filename}")
            return True
        except Exception as e:
            logger.error(f"Error during PDF conversion: {str(e)}")
            st.error(f"Error converting to PDF: {str(e)}")
            return False
        finally:
            try:
                os.unlink(temp_html)
            except Exception as e:
                logger.warning(f"Error cleaning up temporary file: {str(e)}")
    except Exception as e:
        logger.error(f"Error during markdown conversion: {str(e)}")
        st.error(f"Error converting markdown: {str(e)}")
        return False

def analyze_pdf(pdf_file):
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        num_pages = len(reader.pages)
        
        # Extract text from first page for preview
        first_page_text = reader.pages[0].extract_text()
        
        # Analyze PDF structure
        structure = {
            'num_pages': num_pages,
            'preview': first_page_text[:500] + "..." if len(first_page_text) > 500 else first_page_text,
            'has_toc': hasattr(reader, 'outline') and bool(reader.outline),
            'has_images': any('Image' in page.keys() for page in reader.pages)
        }
        
        return structure
    except Exception as e:
        logger.error(f"Error during PDF analysis: {str(e)}")
        st.error(f"Error analyzing PDF: {str(e)}")
        return None

def main():
    st.title("Document Converter & Analyzer")
    
    tab1, tab2 = st.tabs(["Convert to PDF", "Analyze PDF"])
    
    with tab1:
        st.header("Convert to PDF")
        
        # File uploader
        md_file = st.file_uploader("Upload document file", type=['md', 'txt'], key="md_uploader")
        
        if md_file is not None:
            md_content = md_file.getvalue().decode()
            
            # Show content structure
            structure = analyze_content_structure(md_content)
            with st.expander("Document Structure"):
                st.write("Chapters:", len(structure['chapters']))
                st.write("Sections:", len(structure['sections']))
                st.write("Subsections:", len(structure['subsections']))
            
            st.text_area("Preview Content", md_content, height=200)
            
            # Place convert button right after the preview
            if st.button("Convert to PDF", key="convert_button"):
                with st.spinner("Converting to PDF..."):
                    output_filename = "output.pdf"
                    if convert_md_to_pdf(md_content, output_filename):
                        with open(output_filename, "rb") as pdf_file:
                            pdf_bytes = pdf_file.read()
                            st.success("Conversion successful!")
                            st.download_button(
                                label="Download PDF",
                                data=pdf_bytes,
                                file_name=output_filename,
                                mime="application/pdf"
                            )
                        try:
                            os.remove(output_filename)
                        except Exception as e:
                            logger.warning(f"Error cleaning up generated PDF file: {str(e)}")
    
    with tab2:
        st.header("Analyze PDF")
        pdf_file = st.file_uploader("Upload PDF file", type=['pdf'], key="pdf_uploader")
        
        if pdf_file is not None:
            # Place analyze button right after the upload
            if st.button("Analyze PDF", key="analyze_button"):
                with st.spinner("Analyzing PDF..."):
                    analysis = analyze_pdf(pdf_file)
                    if analysis is not None:
                        st.write(f"Number of pages: {analysis['num_pages']}")
                        st.write(f"Has table of contents: {'Yes' if analysis['has_toc'] else 'No'}")
                        st.write(f"Contains images: {'Yes' if analysis['has_images'] else 'No'}")
                        st.write("Preview of first page:")
                        st.text_area("Content", analysis['preview'], height=200)

if __name__ == "__main__":
    main()
