import requests
import logging
import re
import os

# Configure logging format
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] - %(message)s",
    level=logging.INFO
)

OLLAMA_API_URL = "http://ollama:11434/api/generate"

def analyze_logs_and_act(context):
    """
    Analyze logs using the AI agent and determine the next action.
    """
    task_instance = context['task_instance']
    
    logging.info(f"Fetching logs for DAG: {task_instance.dag_id}, Task: {task_instance.task_id}, Run ID: {task_instance.run_id}")

    log_content = fetch_logs(
        task_instance.dag_id, 
        task_instance.task_id, 
        task_instance.run_id, 
        task_instance.try_number
    )

    logging.info(f"Logs fetched successfully. Sending logs to AI agent for analysis.")

    # Query AI for suggested action
    action = query_ai_agent(log_content)

    logging.info(f"✅ AI Agent Decision: {action.upper()}")
    
    return action

def fetch_logs(dag_id, task_id, dag_run_id, attempt=1):
    """
    Read logs directly from the local log file.
    """
    log_file_path = f"/opt/airflow/logs/dag_id={dag_id}/run_id={dag_run_id}/task_id={task_id}/attempt={attempt}.log"

    if not os.path.exists(log_file_path):
        logging.error(f"❌ Log file NOT found: {log_file_path}")
        return f"Error: Log file not found at {log_file_path}"

    try:
        with open(log_file_path, "r") as log_file:
            logs = log_file.read()
        logging.info(f"📄 Successfully read {len(logs)} characters from log file.")
        return logs
    except Exception as e:
        logging.error(f"⚠️ Failed to read log file: {e}")
        return "Error: Unable to read log file."

def query_ai_agent(logs):
    """
    Query the AI agent via Ollama and get its suggested action.
    """
    prompt = f"""
    You are an AI assistant helping with ETL pipeline failures. A failure occurred, and here are the last logs:
    
    ```
    {logs}
    ```
    
    What should be done? Choose one of the following actions: 
    - "restart" (if it's a temporary issue)
    - "ignore" (if it's not a critical failure)
    - "escalate" (if a human should investigate).
    
    Reply with only one word.
    """

    logging.info("🧠 Sending logs to AI agent for processing...")

    data = {
        "model": "deepseek-r1:7b",
        "prompt": prompt,
        "stream": False,
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=data)
        response.raise_for_status()
        result = response.json()

        raw_response = result.get("response", "").strip().lower()

        # 🛠️ Extract only the last word AFTER </think>
        decision_match = re.search(r"</think>\s*\n*\s*(\w+)", raw_response)

        if decision_match:
            action = decision_match.group(1)
        else:
            logging.warning(f"⚠️ AI response format unexpected: {raw_response}")
            action = "escalate"  # Default fallback

        if action not in ["restart", "ignore", "escalate"]:
            logging.warning(f"⚠️ AI response unclear ('{action}'). Defaulting to 'escalate'.")
            action = "escalate"

        logging.info(f"🎯 AI Agent suggested: {action.upper()}")
        return action

    except Exception as e:
        logging.error(f"🚨 Failed to query AI agent: {e}")
        return "escalate"
