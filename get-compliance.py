from browser_use import Agent, ChatGoogle, BrowserProfile, BrowserSession
from dotenv import load_dotenv
import asyncio
import os

load_dotenv()

PROFILE_DIR = os.path.expanduser("~/my_browser_profile")
profile = BrowserProfile(path=PROFILE_DIR, headless=True)

task = \
"""
Find compliance laws for the European Union (EU) regarding data privacy.
Read through the latest document (not all documents) released by the EU and retrieve key policies.
"""

async def main():
    llm = ChatGoogle(model="gemini-flash-latest")
    task = "Find compliance laws for the European Union regarding data privacy."
    agent = Agent(task=task, llm=llm, profile=profile)
    await agent.run()
    print("Agent task completed. Results saved to eu_compliance_results.txt")

if __name__ == "__main__":
    asyncio.run(main())
