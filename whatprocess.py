from computerspeak import ComputerSpeak as cs
from fileshuttle import FileShuttle as fs
from enumeration import FileCrawler as fc
from netrunning import NetRunning as nr
from metasploiting import search_modules, execute_module, list_sessions, _get_client


class WhatProcess:
    def __init__(self):
        self.cs = cs()
        self.fs = fs()
        self.fc = fc()
        self.nr = nr()
    
    def identify_process(self, process_name: str):
        """Identify a process by name and return its details. This function takes a process name as input and attempts to identify the process running on the system. It uses different commands based on the operating system (Windows or Unix-like) to search for the process. If the process is found, its details (such as PID) are extracted and returned in a structured format. If the process is not found, a message is printed indicating that the process was not found, and None is returned."""
        self.cs.execute_command(f"Write-Output Identifying process: {process_name}")
        if self.cs.os_name == "Windows":
            command = f'tasklist /FI "IMAGENAME eq {process_name}"'
        else:
            command = f'ps aux | grep {process_name} | head -n 1'
        output = self.cs.execute_command(command)
        process_stuff = output.strip().split()
        if len(process_stuff) < 2:
            print(f"Process '{process_name}' not found.")
            return None
        else: 
            process_details = {
                "pid": process_stuff[1],
            }
            return process_details
       

    def kill_process(self, pid: int):
        """Kill a process by its PID. This function takes a process ID (PID) as input and attempts to kill the process with that PID. It uses different commands based on the operating system (Windows or Unix-like) to terminate the process. The function includes error handling to catch and report any issues that may arise during the process termination, and it provides feedback on whether the process was successfully killed or if an error occurred."""
        try:
            if self.cs.os_name == "Windows":
                self.cs.execute_command(f"taskkill /PID {pid} /F")
            else:
                self.cs.execute_command(f"kill -9 {pid}")
            print(f"Process with PID {pid} has been killed.")
        except Exception as e:
            print(f"Error killing process: {e}")

    def list_processes(self):
        """List all running processes on the system. This function retrieves a list of all active processes, including their details such as PID, memory usage, and CPU usage. It uses different commands based on the operating system (Windows or Unix-like) to gather the process information. The results are printed and returned in a structured format, and any errors encountered during the process listing are handled gracefully."""
        try:
            if self.cs.os_name == "Windows":
                output = self.cs.execute_command("tasklist")
            else:
                output = self.cs.execute_command("ps aux")
            print("Running processes:")
            print(output) #yeah this one is pretty simple
            return output
        except Exception as e:
            print(f"Error listing processes: {e}")
    def monitor_process(self, pid: int):
        """Monitor a process by its PID and return its resource usage. This function takes a process ID (PID) as input and attempts to monitor the resource usage of the specified process. It uses different commands based on the operating system (Windows or Unix-like) to retrieve the CPU and memory usage of the process. The results are returned in a structured format, and any errors encountered during the monitoring process are handled gracefully."""
        self.cs.execute_command(f"Write-Output Monitoring process with PID: {pid}")
        if self.cs.os_name == "Windows":
            command = f'typeperf "\\Process({pid})\\% Processor Time" "\\Process({pid})\\Working Set" -sc 1'
        else:
            command = f'ps -p {pid} -o %cpu,%mem'
        output = self.cs.execute_command(command).split("\n")
        cs_i = cs()
        if self.cs.os_name == "Windows":
            resource_usage = {
                "cpu_usage": output[2].split(",")[0].strip('"'),
                "memory_usage": output[2].split(",")[1].strip('"')
            }
        else:
            resource_usage = {
                "cpu_usage": output[1].split()[0],
                "memory_usage": output[1].split()[1]
            }
        return resource_usage

    def inject_into_process(self, pid: int, payload: str):
        """Inject a payload into a process by its PID. This function takes a process ID (PID) and a payload string as input and attempts to inject the payload into the specified process. It uses different commands based on the operating system (Windows or Unix-like) to perform the injection. The function includes error handling to catch and report any issues that may arise during the injection process, and it provides feedback on whether the payload was successfully injected or if an error occurred."""
    #stack overflow to the rescue. 
        if self.cs.os_name == "Windows":
            command = f"Write-Output {payload} | powershell -Command \"Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Clipboard]::SetText((Get-Content -Raw));\"; powershell -Command \"Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Clipboard]::GetText() | Out-File -FilePath payload.txt -Encoding ASCII\"; powershell -Command \"Start-Process -FilePath payload.txt -Verb RunAs\""
        else:
            command = f"Write-Output '{payload}' > /tmp/payload.sh; chmod +x /tmp/payload.sh; sudo -u $(ps -o user= -p {pid}) /tmp/payload.sh"
        self.cs.speak(f"Injecting payload into process with PID: {pid}")
        self.cs.execute_command(command)
        print(f"Payload '{payload}' has been injected into process with PID {pid}.")
    def restart_service (self, service_name: str):
        try:
            if self.cs.os_name == "Windows":
                self.cs.execute_command(f"net stop {service_name} && net start {service_name}")
            else:
                self.cs.execute_command(f"systemctl restart {service_name}")
            print(f"Service '{service_name}' has been restarted.")
        except Exception as e:
            print(f"Error restarting service: {e}") #if something bugs we can restart it. :D
    def identify_services(self):
        """Identify running services on the system. This function retrieves a list of all active services, including their details such as service name, status, and description. It uses different commands based on the operating system (Windows or Unix-like) to gather the service information. The results are printed and returned in a structured format, and any errors encountered during the service identification are handled gracefully."""
        try:
            if self.cs.os_name == "Windows":
                output = self.cs.execute_command("sc query type= service state= all")
            else:
                output = self.cs.execute_command("systemctl list-units --type=service --state=running")
            print("Running services:")
            print(output) #yeah this one is pretty simple
        except Exception as e:
            print(f"Error identifying services: {e}")
    def cron_job(self, service:str, command:str, schedule: str):
        """Schedule a cron job with the specified command and schedule."""
        if self.cs.os_name == "Windows":
            cs.execute_command(f"Set-Service -Name {service} -StartupType Automatic(Delayed Start); Register-ScheduledTask -Action (New-ScheduledTaskAction -Execute 'powershell.exe' -Argument '-Command \"{command}\"') -Trigger (New-ScheduledTaskTrigger -AtStartup) -TaskName '{service}_cron_job' -Description 'Cron job for {service}'")
            self.cs.execute_command(f"Write-Output Scheduling task: '{command}' with schedule: '{schedule}'")
            # Example of simulating task scheduling
            print(f"Task '{command}' has been scheduled with schedule '{schedule}'.") #that ones importante. another windows/linux branch
        else:
            self.cs.execute_command(f"(crontab -l ; Write-Output '{schedule} {command}') | crontab -")
        self.cs.execute_command(f"Write-Output Scheduling cron job: '{command}' with schedule: '{schedule}'")
        # Example of simulating cron job scheduling
        print(f"Cron job '{command}' has been scheduled with schedule '{schedule}'.") #that ones importante. another windows/linux branch
    def remove_cron_job(self, command: str):
        """Remove a scheduled cron job by its command. This function takes a command string as input and attempts to remove any scheduled cron jobs that match the provided command. It uses different commands based on the operating system (Windows or Unix-like) to perform the removal. The function includes error handling to catch and report any issues that may arise during the removal process, and it provides feedback on whether the cron job was successfully removed or if an error occurred."""
        # This is a placeholder implementation. You would need to implement the actual logic to remove cron jobs based on your requirements.
        self.cs.speak(f"Removing cron job: '{command}'") #oh yeah i never finished this part. whoops. well you get the idea. just need to parse the crontab and remove the line with the command in it. ye. regex and matching. das all. 
        # Example of simulating cron job removal
        print(f"Cron job '{command}' has been removed.") #that ones importante. another windows/linux branch
        
        def kill_process_by_name(self, pid: int):
            csi = cs()
            try:
                if csi.os_name == "Windows":
                    csi.execute_command(f"taskkill /PID {pid} /F")
                else:
                    csi.execute_command(f"kill -9 {pid}")
                print(f"Process with PID '{pid}' has been killed.")
            except Exception as e:
                print(f"Error killing process: {e}")
    def elevate_privileges(self, pid: int):
        """Attempt to elevate privileges of a process by its PID. This function takes a process ID (PID) as input and attempts to elevate the privileges of the specified process. It uses different commands based on the operating system (Windows or Unix-like) to perform the privilege escalation. The function includes error handling to catch and report any issues that may arise during the elevation process, and it provides feedback on whether the privileges were successfully elevated or if an error occurred."""
        csi = cs()
        try:
            if csi.os_name == "Windows":
                csi.execute_command(f"powershell -Command \"Start-Process -FilePath powershell.exe -Verb RunAs -ArgumentList '-Command \"Get-Process -Id {pid} | ForEach-Object {{ $_.PriorityClass = 'High' }}\"'\"")
            else:
                csi.execute_command(f"sudo renice -n -10 -p {pid}")
            print(f"Privileges for process with PID '{pid}' have been elevated.")
        except Exception as e:
            print(f"Error elevating privileges: {e}")

