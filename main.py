import streamlit as st
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_core.runnables import RunnableConfig
from utils.react_agent import agent

# Set up the Streamlit app configuration
st.set_page_config(page_title="Code Analyzer AI", page_icon="🔍", layout="wide")

# GitHub URL input form
st.write("### Enter the Remote Repository URL for code analysis")
repo_type = st.selectbox("Select the type of repository:", ["Public", "Private"])
github_url = st.text_input("Enter the GitHub URL of the repository:")

# Token input for private repositories
if repo_type == "Private":
    github_token = st.text_input("Enter your GitHub Personal Access Token (PAT):", type="password")
else:
    github_token = ""

# Directory path input within the repository
directory_path = st.text_input("Enter the directory path within the repository (leave empty for root):")

# Select output format and analysis tool
output_format = st.selectbox("Select output format", ["Detailed Report", "Summary", "JSON"])
analysis_tool = st.selectbox("Select analysis tool", ["Python Code Analysis", "SQL Analysis", "Security Vulnerability Analysis"])

# Start the analysis on button click
submit_clicked = st.button("Start Analysis")

if submit_clicked and github_url:
    if repo_type == "Private" and not github_token:
        st.error("GitHub Personal Access Token is required for private repositories.")
    else:
        with st.spinner("Processing..."):
            try:
                # Initialize the agent for each analysis
                agent_executor = agent()
                output_container = st.empty()
                output_container = output_container.container()
                
                # Display the analysis summary
                summary_message = f"""
**Analysis Summary:**

- **Repository URL:** {github_url}
- **Directory Path:** {directory_path if directory_path else 'Root'}
- **Output Format:** {output_format}
- **Analysis Tool:** {analysis_tool}

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
                    "pat": github_token if github_token else ""
                }, cfg)
                
                # Display the response
                output_container.write(response["output"])
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
