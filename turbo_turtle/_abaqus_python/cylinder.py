import os
import sys
import inspect

import numpy

filename = inspect.getfile(lambda: None)
basename = os.path.basename(filename)
parent = os.path.dirname(filename)
sys.path.insert(0, parent)
import parsers
import vertices
import geometry


def main(inner_radius, outer_radius, height, output_file,
         model_name=parsers.geometry_defaults["model_name"],
         part_name=parsers.cylinder_default_part_name,
         revolution_angle=parsers.geometry_defaults["revolution_angle"],
         y_offset=parsers.cylinder_default_y_offset):
    """Accept dimensions of a right circular cylinder and generate an axisymmetric revolved geometry

    Centroid of cylinder is located on the global coordinate origin by default.

    :param float inner_radius: Radius of the hollow center
    :param float outer_radius: Outer radius of the cylinder
    :param float height: Height of the cylinder
    :param str output_file: Abaqus CAE database to save the part(s)
    :param str model_name: name of the Abaqus model in which to create the part
    :param list part_name: name(s) of the part(s) being created
    :param float revolution_angle: angle of solid revolution for ``3D`` geometries
    :param float y_offset: vertical offset along the global Y-axis
    """
    import abaqus
    import abaqusConstants

    abaqus.mdb.Model(name=model_name, modelType=abaqusConstants.STANDARD_EXPLICIT)
    output_file = os.path.splitext(output_file)[0] + ".cae"

    coordinates = vertices.cylinder(inner_radius, outer_radius, height, y_offset=y_offset)
    geometry.draw_part_from_splines(coordinates, planar=False, model_name=model_name, part_name=part_name,
                                    revolution_angle=revolution_angle)

    abaqus.mdb.saveAs(pathName=output_file)


if __name__ == "__main__":

    parser = parsers.cylinder_parser(basename=basename)
    try:
        args, unknown = parser.parse_known_args()
    except SystemExit as err:
        sys.exit(err.code)

    sys.exit(main(
        inner_radius=args.inner_radius,
        outer_radius=args.outer_radius,
        height=args.height,
        output_file=args.output_file,
        model_name=args.model_name,
        part_name=args.part_name,
        revolution_angle=args.revolution_angle,
        y_offset=args.y_offset
    ))
