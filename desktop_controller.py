import os
import subprocess
import glob
from pathlib import Path

class DesktopController:
    """Manages Windows desktop automation: opening apps, exploring folders, locating files."""

    def __init__(self):
        self.user_home = Path.home()
        self.downloads_dir = self.user_home / "Downloads"
        self.documents_dir = self.user_home / "Documents"

    def open_application(self, app_name: str, argument: str | None = None) -> dict:
        """
        Open common Windows applications such as VS Code, Notepad, Explorer, Calculator.
        """
        app_name_lower = app_name.lower().strip()
        cmd = []

        if "code" in app_name_lower or "vs code" in app_name_lower or "vscode" in app_name_lower:
            cmd = ["code"]
            if argument:
                cmd.append(argument)
            else:
                cmd.append(os.getcwd())
        elif "notepad" in app_name_lower:
            cmd = ["notepad.exe"]
            if argument:
                cmd.append(argument)
        elif "explorer" in app_name_lower or "folder" in app_name_lower:
            target_path = argument or str(self.downloads_dir)
            cmd = ["explorer.exe", target_path]
        elif "calc" in app_name_lower or "calculator" in app_name_lower:
            cmd = ["calc.exe"]
        else:
            # Fallback to Windows 'start'
            cmd = ["cmd", "/c", "start", app_name]
            if argument:
                cmd.append(argument)

        try:
            subprocess.Popen(cmd, shell=False)
            return {
                "status": "success",
                "message": f"Successfully launched {app_name}" + (f" with {argument}" if argument else "")
            }
        except Exception as e:
            return {"status": "error", "error": f"Failed to launch application '{app_name}': {e}"}

    def open_downloads_folder(self) -> dict:
        """Open the user's Downloads directory in Windows Explorer."""
        return self.open_application("explorer", str(self.downloads_dir))

    def find_latest_file(self, directory: str | None = None, extension: str | None = None) -> dict:
        """
        Find the most recently modified file in a directory (default: Downloads folder).
        Optionally filter by extension (e.g., '.pdf', '.docx', '.zip').
        """
        search_dir = Path(directory) if directory else self.downloads_dir
        if not search_dir.exists():
            search_dir = Path(os.getcwd())

        pattern = f"*{extension}" if extension else "*"
        try:
            files = [
                p for p in search_dir.glob(pattern)
                if p.is_file() and not p.name.startswith("~") and not p.name.startswith(".")
            ]
            if not files:
                return {
                    "status": "not_found",
                    "message": f"No files matching '{pattern}' found in {search_dir}"
                }

            # Sort by modification time, descending
            latest_file = max(files, key=lambda f: f.stat().st_mtime)
            return {
                "status": "success",
                "file_path": str(latest_file),
                "file_name": latest_file.name,
                "size_kb": round(latest_file.stat().st_size / 1024, 2),
                "directory": str(search_dir)
            }
        except Exception as e:
            return {"status": "error", "error": f"Failed to search for latest file: {e}"}

    def list_recent_files(self, directory: str | None = None, limit: int = 5) -> dict:
        """List the N most recent files in a directory."""
        search_dir = Path(directory) if directory else self.downloads_dir
        if not search_dir.exists():
            search_dir = Path(os.getcwd())

        try:
            files = [
                p for p in search_dir.iterdir()
                if p.is_file() and not p.name.startswith("~") and not p.name.startswith(".")
            ]
            files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            results = [
                {"name": f.name, "path": str(f), "size_kb": round(f.stat().st_size / 1024, 2)}
                for f in files[:limit]
            ]
            return {"status": "success", "files": results, "directory": str(search_dir)}
        except Exception as e:
            return {"status": "error", "error": f"Failed to list files: {e}"}
