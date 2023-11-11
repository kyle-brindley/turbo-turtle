import sys
import shutil
import pathlib
import inspect
import functools


def search_commands(options):
    """Return the first found command in the list of options. Return None if none are found.

    :param list options: executable path(s) to test

    :returns: command absolute path
    :rtype: str
    """
    command_search = (shutil.which(command) for command in options)
    command_abspath = next((command for command in command_search if command is not None), None)
    return command_abspath


def find_command(options):
    """Return first found command in list of options.

    Raise a FileNotFoundError if none is found.

    :param list options: alternate command options

    :returns: command absolute path
    :rtype: str
    """
    command_abspath = search_commands(options)
    if command_abspath is None:
        raise FileNotFoundError(f"Could not find any executable on PATH in: {', '.join(options)}")
    return command_abspath


def print_exception_message(function):
    """Decorate a function to catch any exception, print the message and call sys.exit

    :param function: function to decorate
    """
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        try:
            output = function(*args, **kwargs)
        except Exception as err:
            sys.exit(str(err))
        return output
    return wrapper


@print_exception_message
def find_command_or_exit(*args, **kwargs):
    return find_command(*args, **kwargs)


def find_cubit_bin(options="cubit"):
    """Look for the Cubit bin via direct import and by executable search in options

    If the Cubit bin directory is not found, raise a FileNotFoundError.

    :param list options: Cubit command options

    :returns: Cubit bin directory absolute path
    :rtype: pathlib.Path
    """
    message = "Could not import Cubit. Cound not find a Cubit bin directory. Please ensure the cubit executable " \
              "is on PATH or the cubit bin directory is on PYTHONPATH."

    try:
        import cubit
        pathlib.Path(inspect.getfile(cubit)).parent
    except ModuleNotFoundError:
        pass

    try:
        cubit_command = find_command(options)
    except FileNotFoundError as err:
        raise FileNotFoundError(f"{message} {err}")

    cubit_bin = pathlib.Path(cubit_command)
    if "bin" in cubit_bin.parts:
        while cubit_bin.name != "bin":
            cubit_bin = cubit_bin.parent
    else:
        search = cubit_bin.glob("bin")
        cubit_bin = next((path for path in search if path.name == "bin"), None)
    if cubit_bin is None:
        raise FileNotFoundError(message)
    return cubit_bin
