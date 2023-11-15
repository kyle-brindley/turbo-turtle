import sys
import argparse

from turbo_turtle import __version__
from turbo_turtle import _settings
from turbo_turtle import _utilities
from turbo_turtle._abaqus_python import parsers


def _docs_parser():
    """Get parser object for docs subcommand command line options

    :return: parser
    :rtype: ArgumentParser
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-p", "--print-local-path",
                        action="store_true",
                        help="Print the path to the locally installed documentation index file. " \
                             "As an alternative to the docs sub-command, open index.html in a web browser " \
                             "(default: %(default)s)")
    return parser


def _docs(print_local_path=False):
    """Open or print the package's installed documentation

    Exits with a non-zero exit code if the installed index file is not found.

    :param bool print_local_path: If True, print the index file path instead of opening with a web browser
    """

    if not _settings._installed_docs_index.exists():
        # This should only be reached if the package installation structure doesn't match the assumptions in
        # _settings.py. It is used by the Conda build tests as a sign-of-life that the assumptions are correct.
        sys.exit("Could not find package documentation HTML index file")

    if print_local_path:
        print(_settings._installed_docs_index, file=sys.stdout)
    else:
        import webbrowser
        webbrowser.open(str(_settings._installed_docs_index))


def add_abaqus_and_cubit(parsers):
    """Add the Abaqus and Cubit command arguments to each parser in the parsers list

    :param list parsers: List of parser to run ``add_argument`` for the abaqus command
    """
    for parser in parsers:
        parser.add_argument("--abaqus-command", nargs="+", default=_settings._default_abaqus_options,
                            help="Abaqus executable options (default: %(default)s)")
        parser.add_argument("--cubit-command", nargs="+", default=_settings._default_cubit_options,
                            help="Cubit executable options (default: %(default)s)")
        parser.add_argument("--cubit", action="store_true",
                            help="Flag to use Cubit instead of Abaqus. " \
                                 "Check subcommand usage/help for implementation status " \
                                 "(default: %(default)s)")


def append_cubit_help(text, append="with Abaqus or Cubit"):
    """Append common short help with optional Cubit text

    :param str text: original text
    :param str append: new text

    :returns: appended text
    :rtype: str
    """
    return f"{text} {append}"


def append_cubit_description(text, append="Defaults to Abaqus, but can optionally run Cubit."):
    """Append common long description with optional Cubit text

    :param str text: original text
    :param str append: new text

    :returns: appended text
    :rtype: str
    """
    return f"{text} {append}"


def get_parser():
    """Get parser object for command line options

    :return: parser
    :rtype: ArgumentParser
    """
    main_description = \
        "Common geometry, partition, and meshing utilities. Currently a thin Python 3 driver for Abaqus CAE utilities."
    main_parser = argparse.ArgumentParser(
        description=main_description,
        prog=_settings._project_name_short
    )
    main_parser.add_argument(
        "-V", "--version",
        action="version",
        version=f"{_settings._project_name_short} {__version__}"
    )

    subparsers = main_parser.add_subparsers(dest="subcommand")

    docs_parser = _docs_parser()
    subparsers.add_parser(
        "docs",
        help=f"Open the {_settings._project_name_short} HTML documentation",
        description=f"Open the packaged {_settings._project_name_short} HTML documentation in the  " \
                     "system default web browser",
        parents=[docs_parser])

    geometry_parser = parsers.geometry_parser(add_help=False)
    cylinder_parser = parsers.cylinder_parser(add_help=False)
    sphere_parser = parsers.sphere_parser(add_help=False)
    partition_parser = parsers.partition_parser(add_help=False)
    mesh_parser = parsers.mesh_parser(add_help=False)
    image_parser = parsers.image_parser(add_help=False)
    merge_parser = parsers.merge_parser(add_help=False)
    export_parser = parsers.export_parser(add_help=False)

    add_abaqus_and_cubit([
        geometry_parser,
        cylinder_parser,
        sphere_parser,
        partition_parser,
        mesh_parser,
        image_parser,
        merge_parser,
        export_parser,
    ])

    subparsers.add_parser(
        "geometry",
        help=append_cubit_help(parsers.geometry_cli_help),
        description=append_cubit_description(parsers.geometry_cli_description),
        parents=[geometry_parser]
    )

    subparsers.add_parser(
        "cylinder",
        help=parsers.cylinder_cli_help,
        description=parsers.cylinder_cli_description,
        parents=[cylinder_parser]
    )

    subparsers.add_parser(
        "sphere",
        help=parsers.sphere_cli_help,
        description=parsers.sphere_cli_description,
        parents=[sphere_parser]
    )

    subparsers.add_parser(
        "partition",
        help=parsers.partition_cli_help,
        description=parsers.partition_cli_description,
        parents=[partition_parser]
    )

    subparsers.add_parser(
        "mesh",
        help=parsers.mesh_cli_help,
        description=parsers.mesh_cli_description,
        parents=[mesh_parser]
    )

    merge_parser = subparsers.add_parser(
        "merge",
        help=parsers.merge_cli_help,
        description=parsers.merge_cli_description,
        parents=[merge_parser]
    )

    subparsers.add_parser(
        "export",
        help=parsers.export_cli_help,
        description=parsers.export_cli_description,
        parents=[export_parser]
    )

    subparsers.add_parser(
        "image",
        help=parsers.image_cli_help,
        description=parsers.image_cli_description,
        parents=[image_parser]
    )

    return main_parser


def main():
    parser = get_parser()
    subcommand_list = parser._subparsers._group_actions[0].choices.keys()
    args = parser.parse_args()

    keys = vars(args).keys()
    if "cubit" in keys and args.cubit:
        command = None
        import importlib.util
        if importlib.util.find_spec("cubit") is None:
            sys.path.append(_utilities.find_cubit_bin(args.cubit_command))
        from turbo_turtle import _cubit_wrappers as _wrappers
    elif "abaqus_command" in vars(args).keys():
        command = _utilities.find_command_or_exit(args.abaqus_command)
        from turbo_turtle import _abaqus_wrappers as _wrappers


    if args.subcommand not in subcommand_list:
        parser.print_help()
    elif args.subcommand == "docs":
        _docs(print_local_path=args.print_local_path)
    else:
        wrapper_command = getattr(_wrappers, args.subcommand)
        wrapper_command(args, command)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
