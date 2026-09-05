from .server import __name__ as _  # noqa: F401
import runpy
runpy.run_module("twa_curriculum_mcp.server", run_name="__main__")
