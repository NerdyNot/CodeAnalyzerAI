import streamlit as st
import pdfkit
from markdown2 import markdown
from io import BytesIO
from datetime import datetime
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_core.runnables import RunnableConfig
from utils.react_agent import agent
import tempfile

# Function to create a PDF from markdown text
def create_pdf(md_content):
    # Convert markdown to HTML
    html_content = markdown(md_content)
    
    # Add a style to include Korean font
    style = """
    <style>
        @font-face {
            font-family: 'Noto Sans KR';
            src: url('https://fonts.gstatic.com/ea/notosanskr/v2/NotoSansKR-Regular.woff2') format('woff2');
        }
        body {
            font-family: 'Noto Sans KR', sans-serif;
        }
    </style>
    """
    
    html_content = style + html_content

    # Create a temporary HTML file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as temp_html:
        temp_html.write(html_content.encode('utf-8'))
        temp_html_path = temp_html.name

    # Convert the HTML file to PDF and save it to a BytesIO object
    options = {
        'encoding': 'UTF-8',
        'quiet': ''
    }
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        pdfkit.from_file(temp_html_path, temp_pdf.name, options=options)
        temp_pdf_path = temp_pdf.name

    with open(temp_pdf_path, "rb") as f:
        pdf_output = BytesIO(f.read())

    return pdf_output


# Set up the Streamlit app configuration
st.set_page_config(page_title="Code Analyzer AI", page_icon="🔍", layout="wide")

st.markdown(
    """
    <h1>
        <a href="https://github.com/NerdyNot/CodeAnalyzerAI" target="_blank" style="text-decoration: none;">
            <span style="font-size: 1em;">🔍</span>
            Code Analyzer AI
        </a>
    </h1>
    """,
    unsafe_allow_html=True
)

# GitHub URL input form
st.write("### Enter the Remote Repository URL for code analysis")
repo_type = st.selectbox("Select the type of repository:", ["Public", "Private"], key="repo_type")
github_url = st.text_input("Enter the GitHub URL of the repository:", key="github_url")

# Token input for private repositories
if repo_type == "Private":
    github_token = st.text_input("Enter your GitHub Personal Access Token (PAT):", type="password", key="github_token")
else:
    github_token = ""

# Branch input within the repository
branch = st.text_input("Enter the branch within the repository (default is 'main'):", key="branch")

# Directory path input within the repository
directory_path = st.text_input("Enter the directory path within the repository (leave empty for root):", key="directory_path")

# Select output format and analysis tool
output_format = st.selectbox("Select output format", ["Detailed Report", "Simpled Report", "JSON"], key="output_format")
output_language = st.selectbox("Select output Language", ["English", "Korean"], key="output_language")
analysis_tool = st.selectbox("Select analysis tool", ["Python Code Analysis", "SQL Analysis", "Security Vulnerability Analysis"], key="analysis_tool")

# Start the analysis on button click
submit_clicked = st.button("Start Analysis")

# Check if the analysis should be performed
if submit_clicked:
    st.session_state['submit_clicked'] = True
    st.session_state['analysis_completed'] = False  # Reset analysis completion state

if 'submit_clicked' in st.session_state and st.session_state.submit_clicked:
    if repo_type == "Private" and not github_token:
        st.error("GitHub Personal Access Token is required for private repositories.")
    elif not st.session_state.get('analysis_completed', False):
        with st.spinner("Processing..."):
            try:
                # Initialize the agent for each analysis
                agent_executor = agent()
                output_container = st.empty()
                output_container = output_container.container()

                # Capture the current timestamp
                report_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Display the analysis summary
                summary_message = f"""
**Analysis Summary:**

- **Repository URL:** {github_url}
- **Directory Path:** {directory_path if directory_path else 'Root'}
- **Branch:** {branch if branch else 'main'}
- **Output Format:** {output_format}
- **Analysis Tool:** {analysis_tool}
- **Report Generated At:** {report_timestamp}

Please wait while the analysis is being performed...
"""
                output_container.write(summary_message)

                st_callback = StreamlitCallbackHandler(output_container)
                cfg = RunnableConfig()
                cfg["callbacks"] = [st_callback]

                # Invoke the agent with the prepared input
                response = agent_executor.invoke({
                    "input": github_url,
                    "directory_path": directory_path if directory_path else "",
                    "analysis_tool": analysis_tool,
                    "pat": github_token if github_token else "",
                    "branch": branch if branch else "main",
                    "output_format": output_format,
                    "output_language": output_language
                }, cfg)

                # Display the response
                analysis_output = response["output"]
                output_container.write(analysis_output)

                # Prepare markdown content
                md_content = f"""
# Analysis Report

**Repository URL:** {github_url}
**Directory Path:** {directory_path if directory_path else 'Root'}
**Branch:** {branch if branch else 'main'}
**Output Format:** {output_format}
**Analysis Tool:** {analysis_tool}
**Report Generated At:** {report_timestamp}

---

{analysis_output}
"""
                st.session_state['md_content'] = md_content  # Store the markdown content in session state
                st.session_state['analysis_completed'] = True  # Mark analysis as completed

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

if st.session_state.get('analysis_completed', False):
    # Buttons for download and copy to clipboard
        # PDF download button
        pdf_output = create_pdf(st.session_state['md_content'])
        st.download_button(
            label="Download Report to PDF",
            data=pdf_output,
            file_name="analysis_report.pdf",
            mime="application/pdf"
        )
        # Markdown download button
        st.download_button(
            label="Download Report to Markdown",
            data=st.session_state['md_content'],
            file_name="analysis_report.md",
            mime="text/markdown"
        )
