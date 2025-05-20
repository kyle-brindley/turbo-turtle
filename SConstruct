#! /usr/bin/env python

import os
import inspect
import pathlib
import platform
import warnings

import waves
import setuptools_scm


warnings.filterwarnings(action="ignore", message="tag", category=UserWarning, module="setuptools_scm")


# Project meta data
project_name = "turbo-turtle"
version = setuptools_scm.get_version()
project_configuration = pathlib.Path(inspect.getfile(lambda: None))
project_directory = project_configuration.parent
distribution_name = project_name.replace("-", "_")
package_specification = f"{distribution_name}-{version}"
package_directory = project_directory / distribution_name 
project_variables = {
    "name": project_name,
    "version": version,
    "project_directory": project_directory,
}

# Command line options
AddOption(
    "--build-dir",
    dest="build_directory",
    default="build",
    nargs=1,
    type=str,
    action="store",
    metavar="DIR",
    help="SCons build (variant) root directory. Relative or absolute path. (default: '%default')",
)
AddOption(
    "--prefix",
    dest="prefix",
    default="install",
    nargs=1,
    type="string",
    action="store",
    metavar="DIR",
    help="SCons installation pip prefix ``--prefix``. Relative or absolute path. (default: '%default')",
)
default_abaqus_command = "/apps/abaqus/Commands/abq2024"
AddOption(
    "--abaqus-command",
    dest="abaqus_command",
    nargs=1,
    type="string",
    action="append",
    metavar="COMMAND",
    help=f"Override for the Abaqus command. Repeat to specify more than one (default: '[{default_abaqus_command}]')",
)
default_cubit_command = "/apps/Cubit-16.16/cubit"
AddOption(
    "--cubit-command",
    dest="cubit_command",
    nargs=1,
    type="string",
    action="append",
    metavar="COMMAND",
    help=f"Override for the Cubit command. Repeat to specify more than one (default: '[{default_cubit_command}]')",
)

# Inherit Conda environment from user's active environment and add options
env = waves.scons_extensions.WAVESEnvironment(
    ENV=os.environ.copy(),
    project_directory=project_directory,
    build_directory=pathlib.Path(GetOption("build_directory")),
    prefix=pathlib.Path(GetOption("prefix")),
    abaqus_command=GetOption("abaqus_command"),
    cubit_command=GetOption("cubit_command"),
)
env["abaqus_command"] = env["abaqus_command"] if env["abaqus_command"] is not None else [default_abaqus_command]
env["cubit_command"] = env["cubit_command"] if env["cubit_command"] is not None else [default_cubit_command]
env["ENV"]["PYTHONDONTWRITEBYTECODE"] = 1

# Handle OS-aware tee output
system = platform.system().lower()
if system == "windows":  # Assume PowerShell
    env["tee_suffix"] = "$(| Tee-Object -FilePath ${TARGETS[-1].abspath}$)"
else:  # *Nix style tee
    env["tee_suffix"] = "$(2>&1 | tee ${TARGETS[-1].abspath}$)"

# Find third-party software
abaqus_commands = env["abaqus_command"]
abaqus_environments = dict()
for command in abaqus_commands:
    # TODO: more robust version/name recovery without CI server assumptions
    version = pathlib.Path(command).name
    abaqus_environment = env.Clone()
    abaqus_environment["abaqus"] = abaqus_environment.AddProgram([command])
    abaqus_environments.update({version: abaqus_environment})

cubit_commands = env["cubit_command"]
cubit_environments = dict()
for command in cubit_commands:
    # TODO: more robust version/name recovery without CI server assumptions
    version = pathlib.Path(command).parent.name
    cubit_environment = env.Clone()
    cubit_environment["cubit"] = cubit_environment.AddCubit([command])
    cubit_environments.update({version: cubit_environment})

# Build
installed_documentation = package_directory / "docs"
packages = env.Command(
    target=[
        env["build_directory"] / f"dist/{package_specification}.tar.gz",
        env["build_directory"] / f"dist/{package_specification}-py3-none-any.whl",
    ],
    source=["pyproject.toml"],
    action=[
        Copy(package_directory / "README.rst", "README.rst"),
        Copy(package_directory / "pyproject.toml", "pyproject.toml"),
        Delete(Dir(installed_documentation)),
        Copy(Dir(installed_documentation), Dir(env["build_directory"] / "docs/html")),
        Delete(Dir(installed_documentation / ".doctrees")),
        Delete(installed_documentation / ".buildinfo"),
        Delete(installed_documentation / ".buildinfo.bak"),
        Copy(Dir(installed_documentation), env["build_directory"] / f"docs/man/{project_name}.1"),
        "python -m build --verbose --outdir=${TARGET.dir.abspath} --no-isolation .",
        Delete(Dir(package_specification)),
        Delete(Dir(f"{distribution_name}.egg-info")),
        Delete(Dir(installed_documentation)),
        Delete(package_directory / "README.rst"),
        Delete(package_directory / "pyproject.toml"),
    ],
)
env.Depends(packages, [Alias("html"), Alias("man")])
env.AlwaysBuild(packages)
env.ProjectAlias("build", packages, description="Build pip package in ``--build-dir``")
env.Clean("build", Dir(env["build_directory"] / "dist"))

# Install
install = []
install.extend(
    env.Command(
        target=[env["build_directory"] / "install.log"],
        source=[packages[0]],
        action=[
            (
                "python -m pip install ${SOURCE.abspath} --prefix ${prefix} --log ${TARGET.abspath} "
                "--verbose --no-input --no-cache-dir --disable-pip-version-check --no-deps --ignore-installed "
                "--no-build-isolation --no-warn-script-location --no-index"
            ),
        ],
        prefix=env["prefix"],
    )
)
install.extend(
    env.Install(
        target=[env["prefix"] / "man/man1", env["prefix"] / "share/man/man1"],
        source=[env["build_directory"] / f"docs/man/{project_name}.1"],
    )
)
env.AlwaysBuild(install)
env.ProjectAlias("install", install, description="Install pip package to ``prefix``")

# Documentation
build_dir = env["build_directory"] / "docs"
SConscript(dirs="docs", variant_dir=build_dir, exports=["env", "project_variables"])

# Pytests, style checks, and static type checking
workflow_configurations = ["pytest", "style", "mypy", "cProfile"]
for workflow in workflow_configurations:
    build_dir = env["build_directory"] / workflow
    SConscript(
        build_dir.name,
        variant_dir=build_dir,
        exports=["env", "abaqus_environments", "cubit_environments"],
        duplicate=False,
    )

waves.scons_extensions.project_help()
