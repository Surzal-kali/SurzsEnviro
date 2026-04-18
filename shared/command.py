#this code automates the git pull/push process so that conquer is a simple button press to upload and download changes. it should handle errors gracefully, and having branching logic dependent on the precense of bash/pwsh on the machine :D
from computerspeak import ComputerSpeak as cs
import time
import asyncio

async def automate_git():
    csi = cs()
    csi.speak("Starting Git automation...")
    csi.execute_command("git pull")
    await asyncio.sleep(1)
    csi.execute_command("git push")
    csi.speak("Git automation completed.")
    await asyncio.sleep(300)



if __name__ == "__main__":
    asyncio.run(automate_git())


#so do we need anything else to keep it running repeatedly? i don't think so.. just a manifest and we can use conquer for that. :D a one time script ill throw in randomcode to run. 