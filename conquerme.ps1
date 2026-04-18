Start-Job -Name WatchRunner -ScriptBlock {
    watchexec -r -e py -- python conquer.py
}
//ok so this script is to embed conquer .\conquer.py into a PowerShell job that watches for changes and automatically runs the script. we also need to add logic to ADD watcher. consider this my first payload, to distribute the dev enviroment and start automation with it :D