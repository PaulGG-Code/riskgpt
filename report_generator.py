import markdown # pip install markdown
from weasyprint import HTML # pip install weasyprint
import streamlit as st # pip install streamlit

# --------- Report Generation --------- #

# This file contains the functions to generate the security report and convert it to PDF.
# Function to generate the report.
def generate_report():
    report = "# Security Report\n\n"
    
    # Repository Analysis & Application Description
    if "github_analysis" in st.session_state:
        report += "## Repository Analysis\n"
        report += st.session_state["github_analysis"] + "\n\n"
    if "app_input" in st.session_state:
        report += "## Application Description\n"
        report += st.session_state["app_input"] + "\n\n"
    
    # Threat Model
    report += "## Threat Model\n\n"
    if st.session_state.get("threat_model"):
        # Here we call your existing conversion function from threat_model.py.
        from threat_model import json_to_markdown
        improvement_suggestions = st.session_state.get("improvement_suggestions", [])
        report += json_to_markdown(st.session_state["threat_model"], improvement_suggestions)
    else:
        report += "Threat model not generated.\n"
    report += "\n\n"
    
    # Attack Tree
    report += "## Attack Tree\n\n"
    if st.session_state.get("attack_tree"):
        report += "```mermaid\n" + st.session_state["attack_tree"] + "\n```\n"
    else:
        report += "Attack tree not generated.\n"
    report += "\n\n"
    
    # Mitigations
    report += "## Mitigations\n\n"
    if st.session_state.get("mitigations"):
        report += st.session_state["mitigations"] + "\n"
    else:
        report += "Mitigations not generated.\n"
    report += "\n\n"
    
    # DREAD Assessment
    report += "## DREAD Risk Assessment\n\n"
    if st.session_state.get("dread_assessment"):
        from dread import dread_json_to_markdown
        report += dread_json_to_markdown(st.session_state["dread_assessment"])
    else:
        report += "DREAD risk assessment not generated.\n"
    report += "\n\n"
    
    # Test Cases
    report += "## Test Cases\n\n"
    if st.session_state.get("test_cases"):
        report += st.session_state["test_cases"] + "\n"
    else:
        report += "Test cases not generated.\n"
    
    return report

# Function to generate the PDF.
def generate_pdf(report_md):
    # Convert Markdown to HTML with fenced code and table support
    html_content = markdown.markdown(report_md, extensions=['fenced_code', 'tables'])

    # Example CSS to control the table layout
    # Note: Adjust the nth-of-type widths to match the number of columns you have and how wide each should be.
    full_html = f"""
    <html>
    <head>
        <meta charset='utf-8'>
        <style>
            body {{
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                margin: 20px;
                font-size: 10px;
                line-height: 1.6;
                color: #333;
            }}
            h1 {{
                font-size: 2em;
                margin-bottom: 0.5em;
                border-bottom: 2px solid #333;
                padding-bottom: 0.3em;
            }}
            h2 {{
                font-size: 1.75em;
                margin-bottom: 0.75em;
                border-bottom: 1px solid #ccc;
                padding-bottom: 0.3em;
            }}
            h3 {{
                font-size: 1.5em;
                margin-bottom: 0.75em;
            }}
            p {{
                margin-bottom: 1em;
            }}
            pre {{
                background: #f7f7f7;
                border: 1px solid #ddd;
                padding: 10px;
                border-radius: 4px;
                overflow-x: auto;
            }}
            code {{
                font-family: 'Courier New', Courier, monospace;
                background: #f7f7f7;
                padding: 2px 4px;
                border-radius: 3px;
            }}

            /* --- TABLE LAYOUT STYLING --- */
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
                table-layout: fixed; /* Important for fixed-width columns */
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
                vertical-align: top;
                word-wrap: break-word; /* Ensure text wraps within cells */
            }}
            th {{
                background-color: #f2f2f2;
            }}

            /* Example: If we have 7 columns (as in DREAD table), we should define widths with nth-of-type */
            /* Adjust these as needed for your actual column count and widths */
            th:nth-of-type(1), td:nth-of-type(1) {{ width: 12%; }}
            th:nth-of-type(2), td:nth-of-type(2) {{ width: 25%; }}
            th:nth-of-type(3), td:nth-of-type(3) {{ width: 10%; }}
            th:nth-of-type(4), td:nth-of-type(4) {{ width: 10%; }}
            th:nth-of-type(5), td:nth-of-type(5) {{ width: 10%; }}
            th:nth-of-type(6), td:nth-of-type(6) {{ width: 10%; }}
            th:nth-of-type(7), td:nth-of-type(7) {{ width: 10%; }}

        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    pdf_bytes = HTML(string=full_html).write_pdf()
    return pdf_bytes