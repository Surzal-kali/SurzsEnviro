import asyncio
import json
import os
import shutil
import time
from pathlib import Path
from threading import Lock

from computerspeak import ComputerSpeak as cs

"""FOR THE HORDE"""


class Tenfold:
    """Watch a local source folder, stage approved scripts, and run them on schedule."""

    MANIFEST_NAME = "execution.json"
    DEFAULT_POLL_INTERVAL = 60

    DEFAULT_CORE_DEPS = (
        "computerspeak.py",
        "fileshuttle.py",
        "enumeration.py",
        "shellwalking.py",
        "netrunning.py",
        "dacore.py",
        "whatprocess.py",
        "conquer.py",
    )

    def __init__(
        self,
        source_dir: str | Path | None = None,
        working_dir: str | Path | None = None,
        execution_file: str | Path | None = None,
        poll_interval: int = DEFAULT_POLL_INTERVAL,
        approved_extensions: tuple[str, ...] | None = None,
        core_deps: tuple[str, ...] | None = None,
        core_deps_dir: str | Path | None = None,
    ):
        self.cs = cs()
        self.source_dir = self._resolve_path(source_dir, self._default_source_dir())
        self.working_dir = self._resolve_path(working_dir, self._default_working_dir())
        self.execution_file = (
            self._resolve_path(execution_file, self.working_dir / self.MANIFEST_NAME)
            if execution_file is not None
            else self.working_dir / self.MANIFEST_NAME
        )
        self.poll_interval = int(poll_interval)
        self.allowed_extensions = tuple(
            extension.lower() for extension in (approved_extensions or self._default_extensions())
        )
        self.core_deps = tuple(core_deps if core_deps is not None else self.DEFAULT_CORE_DEPS)
        self.core_deps_dir = self._resolve_path(
            core_deps_dir, Path(__file__).resolve().parent
        )
        self._manifest_lock = Lock()

    @staticmethod
    def _resolve_path(value: str | Path | None, fallback: Path) -> Path:
        if value is None:
            return fallback
        return Path(value).expanduser().resolve()

    @staticmethod
    def _base_directory() -> Path:
        if os.name == "nt":
            program_data = Path(os.environ.get("PROGRAMDATA", r"C:\ProgramData"))
            return program_data / "Conquer"
        return Path.home() / ".conquer"

    @classmethod
    def _default_source_dir(cls) -> Path:
        override = os.environ.get("CONQUER_SOURCE_DIR")
        if override:
            return Path(override).expanduser().resolve()
        return cls._base_directory() / "source"

    @classmethod
    def _default_working_dir(cls) -> Path:
        override = os.environ.get("CONQUER_WORKING_DIR")
        if override:
            return Path(override).expanduser().resolve()
        return cls._base_directory() / "working"

    @staticmethod
    def _default_extensions() -> tuple[str, ...]:
        if os.name == "nt":
            return (".ps1", ".py")
        return (".sh", ".py")

    def _log(self, message: str):
        self.working_dir.mkdir(parents=True, exist_ok=True)
        log_path = self.working_dir / "debug_log.txt"
        with log_path.open("a", encoding="utf-8") as log_file:
            log_file.write(f"{time.ctime()} - {message}\n")

    def _ensure_runtime_paths(self):
        self.source_dir.mkdir(parents=True, exist_ok=True)
        self.working_dir.mkdir(parents=True, exist_ok=True)
        if not self.execution_file.exists():
            self._write_manifest({"scripts": []})

    def _load_manifest(self, manifest_path: Path | None = None) -> dict:
        path = manifest_path or self.execution_file
        if not path.exists():
            return {"scripts": []}

        with path.open("r", encoding="utf-8") as exec_file:
            payload = json.load(exec_file)

        if not isinstance(payload, dict):
            raise ValueError(f"{path} must contain a JSON object")

        scripts = payload.get("scripts", [])
        if not isinstance(scripts, list):
            raise ValueError(f"{path} must contain a 'scripts' list")

        normalized_scripts = []
        for entry in scripts:
            if not isinstance(entry, dict):
                raise ValueError(f"{path} contains a non-object script entry")

            script_name = Path(str(entry.get("name", ""))).name
            if not script_name:
                raise ValueError(f"{path} contains a script entry without a valid name")

            repeat = bool(entry.get("repeat", True))
            repeat_interval = entry.get("repeat_interval")
            if repeat_interval is None:
                repeat_interval = 0

            repeat_interval = int(repeat_interval)
            if repeat_interval < 0:
                raise ValueError(f"{path} contains a negative repeat_interval")

            last_executed = entry.get("last_executed")
            if last_executed is not None:
                last_executed = float(last_executed)

            normalized_scripts.append(
                {
                    "name": script_name,
                    "repeat_interval": repeat_interval,
                    "repeat": repeat,
                    "last_executed": last_executed,
                }
            )

        return {"scripts": normalized_scripts}

    def _write_manifest(self, manifest: dict, manifest_path: Path | None = None):
        path = manifest_path or self.execution_file
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as exec_file:
            json.dump(manifest, exec_file, indent=4)

    @staticmethod
    def _needs_copy(source: Path, destination: Path) -> bool:
        if not destination.exists():
            return True
        source_stat = source.stat()
        destination_stat = destination.stat()
        return (
            source_stat.st_mtime > destination_stat.st_mtime
            or source_stat.st_size != destination_stat.st_size
        )

    def _source_manifest_path(self) -> Path:
        return self.source_dir / self.MANIFEST_NAME

    def _merge_source_manifest(self):
        source_manifest_path = self._source_manifest_path()
        source_manifest = self._load_manifest(source_manifest_path)
        local_manifest = self._load_manifest(self.execution_file)
        local_scripts = {entry["name"]: entry for entry in local_manifest["scripts"]}

        merged_scripts = []
        seen = set()
        for source_entry in source_manifest["scripts"]:
            merged_entry = dict(source_entry)
            existing = local_scripts.get(source_entry["name"])
            if existing and existing.get("last_executed") is not None:
                merged_entry["last_executed"] = existing["last_executed"]
            merged_scripts.append(merged_entry)
            seen.add(source_entry["name"])

        for local_name, local_entry in local_scripts.items():
            if local_name not in seen:
                merged_scripts.append(local_entry)

        self._write_manifest({"scripts": merged_scripts})

    def _sync_once(self):
        self._ensure_runtime_paths()
        with self._manifest_lock:
            self._merge_source_manifest()

        for source_file in self.source_dir.iterdir():
            if not source_file.is_file():
                continue
            if source_file.name == self.MANIFEST_NAME:
                continue
            if source_file.suffix.lower() not in self.allowed_extensions:
                continue

            destination_file = self.working_dir / source_file.name
            if self._needs_copy(source_file, destination_file):
                shutil.copy2(source_file, destination_file)
                self._log(f"Staged script {source_file.name} to {destination_file}")

        for dep_name in self.core_deps:
            dep_source = self.core_deps_dir / dep_name
            if not dep_source.exists():
                self._log(f"Core dep not found, skipping: {dep_source}")
                continue
            dep_dest = self.working_dir / dep_name
            if self._needs_copy(dep_source, dep_dest):
                shutil.copy2(dep_source, dep_dest)
                self._log(f"Synced core dep {dep_name} to {dep_dest}")

    async def sync_local_scripts(self, destiny: str | Path | None = None):
        """Continuously stage approved scripts from the local source folder."""
        if destiny is not None:
            self.working_dir = self._resolve_path(destiny, self.working_dir)
            self.execution_file = self.working_dir / self.MANIFEST_NAME

        while True:
            try:
                self._sync_once()
            except Exception as error:
                self._log(f"Error syncing scripts: {type(error).__name__}: {error}")
            await asyncio.sleep(self.poll_interval)

    async def download_from_tailscale_drive(self, destiny: str | Path | None = None):
        """Backward-compatible alias for local staging."""
        await self.sync_local_scripts(destiny=destiny)

    async def execute_scripts(self):
        """Run staged scripts whose repeat interval says they are due."""
        self._ensure_runtime_paths()

        while True:
            try:
                with self._manifest_lock:
                    execution_data = self._load_manifest(self.execution_file)

                manifest_updated = False
                for script_info in execution_data.get("scripts", []):
                    if await self.should_execute_script(
                        repeat_interval=script_info["repeat_interval"],
                        last_executed=script_info.get("last_executed"),
                        repeat=script_info.get("repeat", True),
                    ):
                        if await self.execute_script(script_info["name"]):
                            script_info["last_executed"] = time.time()
                            manifest_updated = True

                if manifest_updated:
                    with self._manifest_lock:
                        self._write_manifest(execution_data)
            except Exception as error:
                self._log(f"Error executing scripts: {type(error).__name__}: {error}")
            await asyncio.sleep(self.poll_interval)

    async def should_execute_script(
        self, repeat_interval: int, last_executed: float | None, repeat: bool = True
    ) -> bool:
        """Determine whether a script should run on this scheduler pass."""
        if last_executed is None:
            return True
        if not repeat:
            return False
        return (time.time() - last_executed) >= repeat_interval

    def _build_command(self, script_path: Path) -> str:
        suffix = script_path.suffix.lower()
        if os.name == "nt":
            if suffix == ".ps1":
                return (
                    "powershell -NoProfile -NonInteractive -ExecutionPolicy Bypass "
                    f'-File "{script_path}"'
                )
            if suffix == ".py":
                return f'python "{script_path}"'
        else:
            if suffix == ".sh":
                return f'bash "{script_path}"'
            if suffix == ".py":
                return f'python3 "{script_path}"'
        raise ValueError(f"Unsupported script type for this host: {script_path.name}")

    async def execute_script(self, script_name: str) -> bool:
        """Run an approved staged script and report whether it succeeded."""
        script_file = self.working_dir / Path(script_name).name
        if not script_file.exists():
            self._log(f"Skipped missing script {script_name}")
            return False

        if script_file.suffix.lower() not in self.allowed_extensions:
            self._log(f"Skipped unapproved script type for {script_name}")
            return False

        try:
            command = self._build_command(script_file)
            result = self.cs.execute_command(command)
            return result is not None
        except Exception as error:
            self._log(f"Error executing script {script_name}: {type(error).__name__}: {error}")
            return False

    @staticmethod
    def ten(file: str, interval: int | None, repeat: bool):
        """Register a local script in the source manifest for scheduled execution."""
        runner = Tenfold()
        runner._ensure_runtime_paths()

        provided_path = Path(file).expanduser()
        if provided_path.exists():
            if not provided_path.is_file():
                raise ValueError(f"{file} is not a file")
            script_name = provided_path.name
            target_path = runner.source_dir / script_name
            if provided_path.resolve() != target_path.resolve():
                shutil.copy2(provided_path, target_path)
        else:
            script_name = Path(file).name
            target_path = runner.source_dir / script_name

        if target_path.suffix.lower() not in runner.allowed_extensions:
            raise ValueError(f"Unsupported script type for this host: {script_name}")

        if repeat and interval is None:
            raise ValueError("repeat_interval is required when repeat is enabled")

        if not target_path.exists():
            raise FileNotFoundError(f"Script not found in source folder: {target_path}")

        manifest_path = runner._source_manifest_path()
        manifest = runner._load_manifest(manifest_path)
        entry = {
            "name": script_name,
            "repeat_interval": int(interval or 0),
            "repeat": bool(repeat),
            "last_executed": None,
        }

        manifest["scripts"] = [
            script for script in manifest["scripts"] if script["name"] != script_name
        ]
        manifest["scripts"].append(entry)
        runner._write_manifest(manifest, manifest_path=manifest_path)
        runner._sync_once()


async def main():
    """Run the local staging loop and the execution loop together."""
    ten = Tenfold()
    await asyncio.gather(ten.sync_local_scripts(), ten.execute_scripts())


if __name__ == "__main__":
    asyncio.run(main())
