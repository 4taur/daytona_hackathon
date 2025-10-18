from browser_use import Agent, ChatGoogle, BrowserProfile
from dotenv import load_dotenv
import asyncio
import os

load_dotenv()

PROFILE_DIR = os.path.expanduser("~/my_browser_profile")
profile = BrowserProfile(path=PROFILE_DIR, headless=True)

async def main():
    llm = ChatGoogle(model="gemini-flash-latest")
    task = "Find compliance laws for the European Union regarding data privacy."
    agent = Agent(task=task, llm=llm, profile=profile)
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())
