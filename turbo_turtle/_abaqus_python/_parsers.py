"""Python 2/3 compatible parsers for use in both the Abaqus Python scripts and the Turbo-Turtle Python 3 wrappers

Content *must* be compatible with Python 2 and 3. Content should be limited to those things necessary to construct the
CLI parser(s). Other content, such as project/package settings type variables, can be included to minimize the required
``sys.path`` modifications required in the Abaqus Python package/scripts. For now, that means this file does double duty
as the Abaqus Python package settings file and the parsers file.
"""
import argparse


sphere_default_input_file = None
sphere_default_quadrant = "both"
sphere_default_angle = 360.
sphere_default_center = (0., 0.)
sphere_default_model_name = "Model-1"
sphere_default_part_name = "sphere"


def sphere_parser(basename="_sphere.py", add_help=True):

    prog = "abaqus cae -noGui {} --".format(basename)
    cli_description = "Create a hollow, spherical geometry from a sketch in the X-Y plane with upper (+X+Y), lower " \
                      "(+X-Y), or both quadrants."

    if add_help:
        parser = argparse.ArgumentParser(description=cli_description, prog=prog)
    else:
        parser = argparse.ArgumentParser(add_help=add_help)

    requiredNamed = parser.add_argument_group('Required Named Arguments')
    requiredNamed.add_argument('--inner-radius', type=float, required=True,
                               help="Inner radius (hollow size)")
    requiredNamed.add_argument('--outer-radius', type=float, required=True,
                               help="Outer radius (sphere size)")
    requiredNamed.add_argument('--output-file', type=str, required=True,
                               help="Abaqus model database to create")

    parser.add_argument('--input-file', type=str, default=sphere_default_input_file,
                        help="Abaqus model database to open (default: %(default)s)")
    parser.add_argument("--quadrant", type=str, choices=("both", "upper", "lower"), default=sphere_default_quadrant,
                        help="XY plane quadrant: both, upper (I), lower (IV) (default: %(default)s)")
    parser.add_argument('--angle', type=float, default=sphere_default_angle,
                        help="Angle of revolution about the +Y axis (default: %(default)s)")
    parser.add_argument('--center', nargs=2, type=float, default=sphere_default_center,
                        help="Center of the sphere (default: %(default)s)")
    parser.add_argument('--model-name', type=str, default=sphere_default_model_name,
                        help="Abaqus model name (default: %(default)s)")
    parser.add_argument('--part-name', type=str, default=sphere_default_part_name,
                        help="Abaqus part name (default: %(default)s)")

    return parser


# TODO: These CLI lists will fail if a user tries to provide a negative number
partition_default_center = [0.0, 0.0, 0.0]
partition_default_xpoint = [1.0, 0.0, 0.0]
partition_default_zpoint = [0.0, 0.0, 1.0]
partition_default_plane_angle = 45.0
partition_default_partitions_x = [0.0, 0.0]
partition_default_partitions_y = [0.0, 0.0]
partition_default_partitions_z = [0.0, 0.0]


def partition_parser(basename="_partition.py", add_help=True):

    prog = "abaqus cae -noGui {} --".format(basename)
    cli_description = "Partition a spherical shape into a turtle shell given a small number of locating parameters."

    if add_help:
        parser = argparse.ArgumentParser(description=cli_description, prog=prog)
    else:
        parser = argparse.ArgumentParser(add_help=add_help)

    requiredNamed = parser.add_argument_group('Required Named Arguments')
    requiredNamed.add_argument('--model-name', type=str, required=True,
                        help="Abaqus model name")
    requiredNamed.add_argument('--part-name', type=str, required=True,
                        help="Abaqus part name")
    requiredNamed.add_argument('--input-file', type=str, required=True,
                        help="Abaqus model database to open")

    parser.add_argument('--output-file', type=str, default=None,
                        help="Abaqus model database to save to. Defaults to the specified --input-file")
    parser.add_argument('--xpoint', nargs=3, type=float, default=partition_default_xpoint,
                        help="Point on the x-axis (default: %(default)s)")
    parser.add_argument('--center', nargs=3, type=float, default=partition_default_center,
                        help="Center of the sphere (default: %(default)s)")
    parser.add_argument('--zpoint', nargs=3, type=float, default=partition_default_zpoint,
                        help="Point on the z-axis (default: %(default)s)")
    parser.add_argument('--plane-angle', type=float, default=partition_default_plane_angle,
                        help="Angle for non-principal partitions (default: %(default)s)")
    parser.add_argument('--x-partitions', type=float, nargs='+', default=partition_default_partitions_x,
                        help="Create a partition offset from the x-principal-plane (default: %(default)s)")
    parser.add_argument('--y-partitions', type=float, nargs='+', default=partition_default_partitions_y,
                        help="Create a partition offset from the y-principal-plane (default: %(default)s)")
    parser.add_argument('--z-partitions', type=float, nargs='+', default=partition_default_partitions_z,
                        help="Create a partition offset from the z-principal-plane (default: %(default)s)")

    return parser
