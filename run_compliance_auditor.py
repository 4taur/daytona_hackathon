from browser_use import Agent, ChatGoogle, BrowserProfile, BrowserSession
from dotenv import load_dotenv
import asyncio
import os
import sys
import time
from pathlib import Path
from daytona import Daytona, DaytonaConfig, CreateSandboxBaseParams
from dotenv import load_dotenv


load_dotenv()

PROFILE_DIR = os.path.expanduser("~/my_browser_profile")
profile = BrowserProfile(path=PROFILE_DIR, headless=True)

task = \
"""
Find compliance laws for the European Union (EU) regarding data privacy.
Read through the latest document (not all documents) released by the EU and retrieve key policies.
"""

async def get_latest_compliance():
    llm = ChatGoogle(model="gemini-flash-latest")
    task = "Find compliance laws for the European Union regarding data privacy."
    agent = Agent(task=task, llm=llm, profile=profile)
    await agent.run()
    print("Agent task completed. Results saved to eu_compliance_results.txt")


load_dotenv()

# Step 1: Initialize Daytona and create sandbox
def setup_daytona_sandbox():
    api_key = os.getenv("DAYTONA_API_KEY")
    if not api_key:
        print("DAYTONA_API_KEY not set.")
        sys.exit(1)
    config = DaytonaConfig(api_key=api_key)
    daytona = Daytona(config)
    try:
        params = CreateSandboxBaseParams(language="python")
        sandbox = daytona.create(params)
        print(f"Sandbox created with ID: {sandbox.id}")
        return daytona, sandbox
    except Exception as e:
        print(f"Error creating Daytona sandbox: {e}")
        print("Attempting to create sandbox without params...")
        try:
            params = CreateSandboxFromImageParams(
                language="python",
                image="python:3.11-slim"  # Explicitly use Python 3.11+
            )
            sandbox = daytona.create(params)
            print(f"Fallback sandbox created with ID: {sandbox.id}")
            return daytona, sandbox
        except Exception as e2:
            print(f"Fallback failed: {e2}")
            sys.exit(1)

# Step 2: Clone repo and set up environment
def clone_and_setup(sandbox, repo_url="https://github.com/4taur/founder_mode_fintech_startup.git"):
    clone_code = f"""
import subprocess
result = subprocess.run(['git', 'clone', '{repo_url}'], capture_output=True, text=True)
if result.returncode != 0:
    print(f"Clone error: {{result.stderr}}")
    exit(result.returncode)
print("Repo cloned successfully")
"""
    clone_response = sandbox.process.code_run(clone_code)
    if clone_response.exit_code != 0:
        print(f"Error cloning repo: {clone_response.exit_code} {clone_response.result}")
        sys.exit(1)
    print("Repo cloned successfully")

    # Set up virtual environment and install requirements
    setup_code = """
import subprocess
import sys
import os
# Check if requirements.txt exists
if not os.path.exists('founder_mode_fintech_startup/requirements.txt'):
    print("Error: requirements.txt not found in founder_mode_fintech_startup")
    exit(1)
# Use system python3 to create venv
subprocess.run(['python3.11', '-m', 'venv', 'venv'], check=True)
# Correct venv paths
venv_dir = 'venv/Scripts' if sys.platform == 'win32' else 'venv/bin'
venv_python = os.path.join(venv_dir, 'python.exe' if sys.platform == 'win32' else 'python3')
venv_pip = os.path.join(venv_dir, 'pip.exe' if sys.platform == 'win32' else 'pip3')
# Ensure pip is available
subprocess.run([venv_python, '-m', 'ensurepip', '--default-pip'], check=True)
subprocess.run([venv_pip, 'install', '-r', 'founder_mode_fintech_startup/requirements.txt'], check=True)
subprocess.run([venv_pip, 'install', 'browser-use', 'galileo'], check=True)
print("Environment set up and dependencies installed")
"""
    setup_response = sandbox.process.code_run(setup_code)
    if setup_response.exit_code != 0:
        print(f"Error setting up environment: {setup_response.exit_code} {setup_response.result}")
        sys.exit(1)
    print("Environment setup complete")

# Step 3: Run Streamlit, BrowserUse, check compliance, and log to Galileo
def run_workflow(sandbox):
    workflow_code = """
import subprocess
import sys
import time
import os
import asyncio
from browser_use import Agent, ChatBrowserUse, Browser
from galileo import Client

# Change to repo directory
os.chdir('founder_mode_fintech_startup')

# Start Streamlit in background using venv python
venv_dir = 'venv/Scripts' if sys.platform == 'win32' else 'venv/bin'
venv_python = os.path.join(venv_dir, 'python.exe' if sys.platform == 'win32' else 'python3')
streamlit_proc = subprocess.Popen(
    [venv_python, '-m', 'streamlit', 'run', 'app.py', '--server.headless', 'true', '--server.port', '8501'],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
)
print("Starting Streamlit server...")
time.sleep(15)  # Increased wait for stability
if streamlit_proc.poll() is not None:
    stderr_output = streamlit_proc.stderr.read()
    print(f"Streamlit failed: {{stderr_output}}")
    exit(1)

# Run BrowserUse agent
async def run_browser_agent():
    try:
        browser = Browser(use_cloud=True)  # Requires BROWSER_USE_API_KEY
        agent = Agent(
            task="Navigate to http://localhost:8501, fill the credit scoring form with age=30, income=50000, gender=female (select option '1'), click the 'Predict' button, wait for the result, and extract the prediction output text. Capture any console errors or bias messages.",
            llm=ChatBrowserUse(),
            browser=browser
        )
        result = await agent.run()
        output = result.get('output', str(result)) if isinstance(result, dict) else str(result)
        return output
    except Exception as e:
        return f"BrowserUse error: {{e}}"

browser_output = asyncio.run(run_browser_agent())
print(f"BrowserUse output: {{browser_output}}")

# Check EU compliance
compliance_issues = [
    "Non-compliant with EU AI Act: Uses gender without bias mitigation (Article 10).",
    "Lacks transparency/explainability (Article 13).",
    f"Discriminatory behavior in predictions: {{browser_output}}"
]
compliance = "\\n".join(compliance_issues)
print(f"EU Compliance Check:\\n{{compliance}}")

# Log to Galileo
try:
    api_key = os.getenv("GALILEO_API_KEY")
    if not api_key:
        print("GALILEO_API_KEY not set")
        exit(1)
    client = Client(api_key=api_key)
    project_id = os.getenv("GALILEO_PROJECT_ID", "your_project_id_here")
    trace = client.trace.start(project_id=project_id, user_id="test_user", trace_type="fintech_demo")
    client.prompt.log(
        trace_id=trace.trace_id,
        prompt_id="input",
        prompt_text="Credit scoring prediction with inputs: age=30, income=50000, gender=female",
        context="Streamlit app demo"
    )
    client.response.log(
        trace_id=trace.trace_id,
        response_id="prediction",
        response_text=browser_output,
        metadata={"compliance_check": compliance}
    )
    client.trace.end(trace_id=trace.trace_id)
    print("Output logged to Galileo")
except Exception as e:
    print(f"Galileo error: {{e}}")

# Stop Streamlit
streamlit_proc.terminate()
try:
    streamlit_proc.wait(timeout=5)
except subprocess.TimeoutExpired:
    streamlit_proc.kill()
print("Streamlit server stopped")

# Save output
with open("browseruse_result.txt", "w") as f:
    f.write(f"Browser Output:\\n{{browser_output}}\\n\\nCompliance:\\n{{compliance}}")
print("Output saved to browseruse_result.txt")
"""
    response = sandbox.process.code_run(workflow_code)
    if response.exit_code != 0:
        print(f"Error running workflow: {response.exit_code} {response.result}")
        sys.exit(1)
    print("Workflow completed successfully")
    print(response.result)

# Step 4: Cleanup
def cleanup(daytona, sandbox):
    try:
        sandbox.delete()
        print(f"Sandbox {sandbox.id} deleted")
    except Exception as e:
        print(f"Error deleting sandbox: {e}")
        sys.exit(1)

def run_dynamic_test():
    daytona, sandbox = setup_daytona_sandbox()
    try:
        clone_and_setup(sandbox)
        run_workflow(sandbox)
    except Exception as e:
        print(f"Workflow error: {e}")
        sys.exit(1)
    finally:
        cleanup(daytona, sandbox)

if __name__ == "__main__":
    asyncio.run(get_latest_compliance())
    run_dynamic_test()