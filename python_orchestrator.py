import re
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Any
import docker


class CodeSandbox:
    def __init__(
        self,
        image_name: str = "custom-python-sandbox:latest",
        mem_limit: str = "512m",
        cpu_quota: int = 50000,
        timeout_seconds: int = 120,
    ):
        self.image_name = image_name
        self.mem_limit = mem_limit
        self.cpu_quota = cpu_quota
        self.timeout = timeout_seconds
        self.client = docker.from_env()

    def run_code(self, code_string: str, filename: str = "script.py") -> Dict[str, Any]:
        temp_dir = tempfile.mkdtemp(prefix="agent_sandbox_")
        temp_dir_path = Path(temp_dir)
        result=None
        try:
            # 1. Write the code supplied by the model to the temp workspace
            script_path = temp_dir_path / filename
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(code_string)

            # 2. Run container non-interactively
            container = self.client.containers.run(
                image=self.image_name,
                command=f"python3 /workspace/{filename}",
                volumes={
                    str(temp_dir_path.resolve()): {
                        "bind": "/workspace",
                        "mode": "rw",
                    }
                },
                network_mode="none",  # ❌ Zero Internet access
                mem_limit=self.mem_limit,  # ❌ Memory limit (prevents OOM attacks)
                cpu_quota=self.cpu_quota,  # ❌ CPU capping
                user="sandboxuser",  # ❌ Non-root execution
                cap_drop=["ALL"],  # ❌ Drop all Linux capabilities
                read_only=False,  # Set workspace to writeable, rest of root is locked down
                detach=True,
                stderr=True,
                stdout=True,
            )

            # 3. Wait for process completion
            try:
                result = container.wait(timeout=self.timeout)
                exit_code = result.get("StatusCode", -1)
                logs = container.logs(stdout=True, stderr=True).decode("utf-8")
            except Exception as e:
                container.kill()
                return {
                    "success": False,
                    "exit_code": -1,
                    "output": f"Execution Timed Out after {self.timeout}s.",
                    "error": str(e),
                }
            finally:
                container.remove(force=True)

            return {
                "success": exit_code == 0,
                "exit_code": exit_code,
                "output": logs if logs.strip() else "Code executed silently with no terminal output.",
            }

        except Exception as err:
            return {
                "success": False,
                "exit_code": -1,
                "output": result,
                "error": f"Orchestrator Failure: {str(err)}",
            }
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


def extract_code_blocks(text: str) -> str:
    """Extracts code blocks from markdown backticks if present."""
    match = re.search(r"```python(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    match_generic = re.search(r"```(.*?)```", text, re.DOTALL)
    if match_generic:
        return match_generic.group(1).strip()
    return text.strip()