from daytona import Daytona, DaytonaConfig
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("DAYTONA_API_KEY")
config = DaytonaConfig(api_key=api_key)
daytona = Daytona(config)
sandbox = daytona.create()

repo_url = "https://github.com/4taur/founder_mode_fintech_startup.git"

cloned = sandbox.process.code_run(
f"""
import subprocess
result = subprocess.run(['git', 'clone', '{repo_url}'], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)
exit(result.returncode)
""")

if cloned.exit_code != 0:
  print(f"Error: {cloned.exit_code} {cloned.result}")
else:
    print("Repo cloned successfully!")

repo_folder = "founder_mode_fintech_startup"
ls_response = sandbox.process.code_run(f"""
import subprocess
result = subprocess.run(['ls', '-la', '{repo_folder}'], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)
exit(result.returncode)
""")

if ls_response.exit_code != 0:
  print(f"Error: {ls_response.exit_code} {ls_response.result}")
else:
    print(ls_response.result)

sandbox.delete()
