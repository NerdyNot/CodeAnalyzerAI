import os
import shutil
import subprocess
import uuid
import faiss
import numpy as np
from pydantic import BaseModel
from git import Repo
from typing import Type
from langchain_core.tools import BaseTool
from langchain.docstore import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from utils.config_llm import config_llm

# Initialize LLM and embedding model
config_llm.initialize_llm_from_env()
config_llm.initialize_embedding_from_env()
embedding = config_llm.get_embedding()

def get_embedding_size(embedding_model, sample_text="test query"):
    sample_embedding = embedding_model.embed_query(sample_text)
    return len(sample_embedding)

# Initialize embedding and vectorstore
embedding_size = get_embedding_size(embedding)
index = faiss.IndexFlatL2(embedding_size)
vectorstore = FAISS(embedding.embed_query, index, InMemoryDocstore({}), {})
metadata_store = {}

class PythonCodeAnalysisConfig(BaseModel):
    input_data: str

class PythonCodeAnalysisTool(BaseTool):
    name = "python_code_analysis"
    description = "Clone a GitHub repository and perform Bandit and pycodestyle analysis. Takes GitHub URL and optional directory path as input in the format 'github_url|directory_path'."
    args_schema: Type[BaseModel] = PythonCodeAnalysisConfig
    return_direct: bool = True

    def _run(self, input_data: str) -> str:
        github_url, directory_path = (input_data.split('|') + [""])[:2]
        result = self.analyze_python(github_url.strip(), directory_path.strip())
        identifier = str(uuid.uuid4())
        self.save_to_vectorstore(identifier, result)
        return f"Analysis results saved. Identifier: {identifier}"

    async def _arun(self, input_data: str) -> str:
        github_url, directory_path = (input_data.split('|') + [""])[:2]
        result = self.analyze_python(github_url.strip(), directory_path.strip())
        identifier = str(uuid.uuid4())
        self.save_to_vectorstore(identifier, result)
        return f"Analysis results saved. Identifier: {identifier}"

    def analyze_python(self, github_url: str, directory_path: str = "") -> str:
        clone_dir = f"cloned_repo_{uuid.uuid4()}"
        if os.path.exists(clone_dir):
            shutil.rmtree(clone_dir)
        os.makedirs(clone_dir)

        try:
            # Clone the repository
            Repo.clone_from(github_url, clone_dir)
        except Exception as e:
            return f"Error cloning the repository: {e}"

        analysis_dir = os.path.join(clone_dir, directory_path)

        try:
            # Run Bandit analysis
            bandit_result = subprocess.run(['bandit', '-r', analysis_dir], capture_output=True, text=True)
            bandit_output = bandit_result.stdout
        except Exception as e:
            return f"Error running Bandit: {e}"

        try:
            # Run pycodestyle analysis
            pycodestyle_result = subprocess.run(['pycodestyle', analysis_dir], capture_output=True, text=True)
            pycodestyle_output = pycodestyle_result.stdout
        except Exception as e:
            return f"Error running pycodestyle: {e}"

        shutil.rmtree(clone_dir)  # Clean up the cloned repository

        return f"Cloned the repository to {clone_dir}.\n\nBandit analysis results:\n{bandit_output}\n\npycodestyle analysis results:\n{pycodestyle_output}"

    def save_to_vectorstore(self, identifier, result):
        embedding_vector = embedding.embed_query(result)
        vectorstore.index.add(np.array([embedding_vector]))
        metadata_store[identifier] = {"identifier": identifier, "result": result, "embedding": embedding_vector}

class SQLAnalysisConfig(BaseModel):
    input_data: str

class SQLAnalysisTool(BaseTool):
    name = "sql_analysis"
    description = "Analyze SQL content from a GitHub repository using SQLCheck. Takes GitHub URL and optional directory path as input in the format 'github_url|directory_path'."
    args_schema: Type[BaseModel] = SQLAnalysisConfig
    return_direct: bool = True

    def _run(self, input_data: str) -> str:
        github_url, directory_path = (input_data.split('|') + [""])[:2]
        result = self.analyze_sql(github_url.strip(), directory_path.strip())
        identifier = str(uuid.uuid4())
        self.save_to_vectorstore(identifier, result)
        return f"Analysis results saved. Identifier: {identifier}"

    async def _arun(self, input_data: str) -> str:
        github_url, directory_path = (input_data.split('|') + [""])[:2]
        result = self.analyze_sql(github_url.strip(), directory_path.strip())
        identifier = str(uuid.uuid4())
        self.save_to_vectorstore(identifier, result)
        return f"Analysis results saved. Identifier: {identifier}"

    def analyze_sql(self, github_url: str, directory_path: str = "") -> str:
        clone_dir = f"cloned_repo_{uuid.uuid4()}"
        if os.path.exists(clone_dir):
            shutil.rmtree(clone_dir)
        os.makedirs(clone_dir)

        try:
            # Clone the repository
            Repo.clone_from(github_url, clone_dir)
        except Exception as e:
            return f"Error cloning the repository: {e}"

        sql_path = os.path.join(clone_dir, directory_path)
        sqlcheck_output = ""
        try:
            # Find all SQL files in the directory
            sql_files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(sql_path) for f in filenames if f.endswith('.sql')]

            if not sql_files:
                return "No SQL files found in the specified directory."

            # Run SQLCheck analysis on each SQL file
            for sql_file in sql_files:
                sqlcheck_result = subprocess.run(['sqlcheck', '-f', sql_file], capture_output=True, text=True)
                sqlcheck_output += f"\n\nResults for {sql_file}:\n{sqlcheck_result.stdout}"

        except Exception as e:
            return f"Error running SQLCheck: {e}"

        shutil.rmtree(clone_dir)  # Clean up the cloned repository

        return f"SQLCheck analysis results:\n{sqlcheck_output}"

    def save_to_vectorstore(self, identifier, result):
        embedding_vector = embedding.embed_query(result)
        vectorstore.index.add(np.array([embedding_vector]))
        metadata_store[identifier] = {"identifier": identifier, "result": result, "embedding": embedding_vector}

class SecurityVulnerabilityAnalysisConfig(BaseModel):
    input_data: str

class SecurityVulnerabilityAnalysisTool(BaseTool):
    name = "security_vulnerability_analysis"
    description = "Clone a GitHub repository and perform security analysis using Horusec. Takes GitHub URL and optional directory path as input in the format 'github_url|directory_path'."
    args_schema: Type[BaseModel] = SecurityVulnerabilityAnalysisConfig
    return_direct: bool = True

    def _run(self, input_data: str) -> str:
        github_url, directory_path = (input_data.split('|') + [""])[:2]
        result = self.analyze_security_vulnerability(github_url.strip(), directory_path.strip())
        identifier = str(uuid.uuid4())
        self.save_to_vectorstore(identifier, result)
        return f"Analysis results saved. Identifier: {identifier}"

    async def _arun(self, input_data: str) -> str:
        github_url, directory_path = (input_data.split('|') + [""])[:2]
        result = self.analyze_security_vulnerability(github_url.strip(), directory_path.strip())
        identifier = str(uuid.uuid4())
        self.save_to_vectorstore(identifier, result)
        return f"Analysis results saved. Identifier: {identifier}"

    def analyze_security_vulnerability(self, github_url: str, directory_path: str = "") -> str:
        clone_dir = f"cloned_repo_{uuid.uuid4()}"

        if os.path.exists(clone_dir):
            shutil.rmtree(clone_dir)
        os.makedirs(clone_dir)

        try:
            # Clone the repository
            Repo.clone_from(github_url, clone_dir)
        except Exception as e:
            return f"Error cloning the repository: {e}"

        analysis_directory_path = os.path.join(clone_dir, directory_path)

        try:
            analyze_result = subprocess.run(
                ['horusec', 'start', '-p', analysis_directory_path, '--disable-docker'],
                capture_output=True, text=True)
            analyze_output = analyze_result.stdout
            analyze_error = analyze_result.stderr

        except Exception as e:
            return f"Error running Horusec: {e}"

        if "level=error" in analyze_error.lower():
            return f"Error in Horusec analysis: {analyze_error}"

        shutil.rmtree(clone_dir)  # Clean up the cloned repository

        return f"Cloned the repository to {clone_dir}.\n\nHorusec analysis results:\n{analyze_output}"

    def save_to_vectorstore(self, identifier, result):
        embedding_vector = embedding.embed_query(result)
        vectorstore.index.add(np.array([embedding_vector]))
        metadata_store[identifier] = {"identifier": identifier, "result": result, "embedding": embedding_vector}

class ReportConfig(BaseModel):
    identifier: str

class ReportTool(BaseTool):
    name = "generate_report"
    description = "Generate a report based on the identifier value by searching related results in the vector store. Takes identifier value as input."
    args_schema: Type[BaseModel] = ReportConfig
    return_direct: bool = True

    def _run(self, identifier: str) -> str:
        return self.generate_report(identifier)

    async def _arun(self, identifier: str) -> str:
        return self.generate_report(identifier)

    def generate_report(self, identifier: str) -> str:
        identifier = identifier.strip()

        result = metadata_store.get(identifier)
        if not result:
            return f"No results found for Identifier: {identifier}"

        report = f"Query Identifier: {identifier}\n"
        report += f"Query Result: {result['result']}\n\n"

        return report
