import pathlib
import datetime


_project_name = "Turbo Turtle"
_project_name_short = "turbo-turtle"
_project_root_abspath = pathlib.Path(__file__).parent.resolve()
_abaqus_python_abspath = _project_root_abspath / "_abaqus_python"
_installed_docs_index = _project_root_abspath / "docs/index.html"
_default_abaqus_options = ["abaqus", "abq2023"]
