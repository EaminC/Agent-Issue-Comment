import subprocess
import os
import time
import re

# List of tags to process
TAGS = [
    "agixt_1026", "crewai_1370",
    "agixt_1030", "crewai_1463",
    "agixt_1253", "crewai_1532",
    "agixt_1256", "crewai_1723",
    "agixt_1369", "crewai_1753",
    "agixt_1371", "crewai_1824",
    "ai_2705", "crewai_1934",
    "ai_3953", "crewai_2102",
    "ai_4411", "crewai_2127",
    "ai_4412", "crewai_2150",
    "ai_4446", "crewai_2237",
    "ai_4619", "evoninja_445",
    "ai_4761", "evoninja_504",
    "ai_5365", "evoninja_515",
    "ai_5380", "evoninja_525",
    "ai_5628", "evoninja_594",
    "ai_6510", "evoninja_652",
    "autogen_4733", "haystack_9487",
    "autogen_4785", "haystack_9523",
    "autogen_5007", "lagent_239",
    "autogen_5012", "lagent_244",
    "autogen_5124", "lagent_279",
    "beeai_framework_55", "langgraphjs_1217",
    "camel_1145", "mastra_4331",
    "camel_1273", "metagpt_1313",
    "camel_1309", "mle_agent_173",
    "camel_1614", "openmanus_1140",
    "camel_88", "openmanus_1143",
    "chatdev_318", "pythagora_55",
    "chatdev_413", "superagent_953",
    "chatdev_465", "sweagent_333",
    "crewai_1270", "sweagent_362",
    "crewai_1323", "sweagent_741",
]

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

def clean_ansi(text):
    return ANSI_ESCAPE.sub('', text)

def run_command(command, logfile, timeout=None, skip_on_fail=False):
    print(f"\n>>> Running: {command}\n")
    logfile.write(f"\n>>> Running: {command}\n")
    try:
        process = subprocess.Popen(
            command, shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True,
            stdin=subprocess.DEVNULL
        )
        for line in process.stdout:
            print(line, end="")
            logfile.write(clean_ansi(line))
        process.wait(timeout=timeout)
        logfile.write(f"\n--- Exit code: {process.returncode} ---\n")
    except subprocess.TimeoutExpired:
        print(f"\n⚠️ Timeout! Skipping command: {command}\n")
        logfile.write(f"\n⚠️ Timeout! Skipped command: {command}\n")
        process.kill()
    except subprocess.CalledProcessError:
        if skip_on_fail:
            print(f"\n⚠️ Error! Skipping command: {command}\n")
            logfile.write(f"\n⚠️ Error! Skipped command: {command}\n")
        else:
            raise

if __name__ == "__main__":
    print(">>> Removing all existing Docker images...\n")
    subprocess.run("sudo docker rmi -f $(sudo docker images -q) || true", shell=True)
    print("\n>>> All existing images removed.\n")
    time.sleep(2)

    for idx, tag in enumerate(TAGS, start=1):
        print(f"\n===== [{idx}/{len(TAGS)}] Processing {tag} =====\n")
        log_path = os.path.join(LOG_DIR, f"{tag}.log")
        with open(log_path, "w", encoding="utf-8") as logfile:
            image = f"alfin06/agentissue-bench:{tag}"
            run_command(f"sudo docker pull {image}", logfile, timeout=600, skip_on_fail=True)
            run_command(f"sudo docker run --rm \"{image}\" test_buggy", logfile, timeout=600, skip_on_fail=True)
            run_command(f"sudo docker run --rm \"{image}\" test_fixed", logfile, timeout=600, skip_on_fail=True)

        print(f"\n>>> Finished {tag}. Log saved to: {log_path}\n")
        time.sleep(1)

    print("\n✅ All tasks completed. Check logs/ folder for clean outputs.")