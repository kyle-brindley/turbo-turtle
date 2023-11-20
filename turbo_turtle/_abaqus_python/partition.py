import ast
import os
import sys
import math
import shutil
import inspect
import argparse
import tempfile

import numpy


filename = inspect.getfile(lambda: None)
basename = os.path.basename(filename)
parent = os.path.dirname(filename)
sys.path.insert(0, parent)
import parsers
import vertices


def main(input_file,
         output_file=parsers.partition_default_output_file,
         center=parsers.partition_default_center,
         xvector=parsers.partition_default_xvector,
         zvector=parsers.partition_default_zvector,
         model_name=parsers.partition_default_model_name,
         part_name=parsers.partition_default_part_name):
    """Wrap  partition function with file open and file write operations

    :param str input_file: Abaqus CAE model database to open
    :param str output_file: Abaqus CAE model database to write. If none is provided, use the input file.
    :param list center: center location of the geometry
    :param list xvector: Local x-axis vector defined in global coordinates
    :param list zvector: Local z-axis vector defined in global coordinates
    :param str model_name: model to query in the Abaqus model database (only applies when used with ``abaqus cae -nogui``)
    :param str part_name: part to query in the specified Abaqus model (only applies when used with ``abaqus cae -nogui``)

    :returns: Abaqus CAE database named ``{output_file}.cae``
    """
    import abaqus

    if output_file is None:
        output_file = input_file
    input_file = os.path.splitext(input_file)[0] + ".cae"
    output_file = os.path.splitext(output_file)[0] + ".cae"
    with tempfile.NamedTemporaryFile(suffix=".cae", dir=".") as copy_file:
        shutil.copyfile(input_file, copy_file.name)
        abaqus.openMdb(pathName=copy_file.name)
        partition(center, xvector, zvector, model_name, part_name)
        abaqus.mdb.saveAs(pathName=output_file)


def datum_plane(center, normal, part):
    """Return an Abaqus DataPlane object by center and normal axis

    :param numpy.array center: center location of the geometry
    :param numpy.array normal: plane normal vector
    :param abaqus.mdb.models[].parts[] part: Abaqus part object

    :returns: Abaqus Datum Plane object
    :rtype: DatumPlane
    """
    point = center + normal
    axis = part.datums[part.DatumAxisByTwoPoint(point1=tuple(center), point2=tuple(point)).id]
    return part.datums[part.DatumPlaneByPointNormal(point=tuple(center), normal=axis).id]


def partition(center, xvector, zvector, model_name, part_name):
    """Partition the model/part with the turtle shell method, also know as the soccer ball method.

    If the body is modeled with fractional symmetry (e.g. quater or half symmetry), this code will attempt all
    partitioning and face removal actions anyways. If certain aspects of the code fail, the code will move on and give no
    errors.

    **Note:** It is possible to create strange looking partitions if inputs are not defined properly. Always check your
    partitions visually after using this tool.

    :param list center: center location of the geometry
    :param list xvector: Local x-axis vector defined in global coordinates
    :param list zvector: Local z-axis vector defined in global coordinates
    :param str model_name: model to query in the Abaqus model database (only applies when used with ``abaqus cae -nogui``)
    :param str part_name: part to query in the specified Abaqus model (only applies when used with ``abaqus cae -nogui``)
    """
    import abaqus
    import caeModules


    if center is None:
        print('\nTurboTurtle was canceled\n')
        return

    part = abaqus.mdb.models[model_name].parts[part_name]

    center = numpy.array(center)
    plane_normals = vertices.datum_planes(xvector, zvector)
    partition_planes = [datum_plane(center, normal, part) for normal in plane_normals]
    for plane in partition_planes:
        try:
            part.PartitionCellByDatumPlane(datumPlane=plane, cells=part.cells[:])
        except:
            pass

    # Step 19 - Find the vertices intersecting faces to remove for the x-axis
    # TODO: Clean this up. Maybe march along local primary axes? Maybe remove all the surface guessing and save surfaces
    # from partition command?
    zvector = plane_normals[0]
    xvector = plane_normals[1]
    yvector = plane_normals[2]
    plane_angle = math.radians(45.)
    found_face = True

    vector_rotation = [[xvector, zvector], [yvector, xvector], [zvector, yvector]]
    for pointOnIDX, (first_vector, second_vector) in enumerate(vector_rotation):
        while found_face:
            x_vectors = ()
            for v in part.vertices:
                pointOn = numpy.asarray(v.pointOn[0])
                this_vector = vertices.normalize_vector(pointOn - center)
                if numpy.abs(numpy.abs(numpy.dot(this_vector, first_vector)) - 1.0) < 0.01:
                    x_vectors += ((v), )
            x_points = numpy.asarray([v.pointOn[0][pointOnIDX] for v in x_vectors])
            x_points.sort()
            x_vectors_grabbed = ()
            for xp in x_points:
                for v in x_vectors:
                    pointOn = v.pointOn[0]
                    if pointOn[pointOnIDX] == xp:
                        x_vectors_grabbed += ((v), )
            x_vectors_grabbed_idxs = [v.index for v in x_vectors_grabbed]

            # Step 20 - locate faces with a normal at the plane_angle to the local coordinate system
            # Step 21 - recursively remove the faces and redundant enties as a result of removed faces
            for II, face in enumerate(part.faces):
                this_vert_idxs = face.getVertices()
                try:
                    if x_vectors_grabbed_idxs[1] in this_vert_idxs or x_vectors_grabbed_idxs[2] in this_vert_idxs:
                        this_normal = normalize_vector(face.getNormal())
                        if numpy.abs(numpy.abs(numpy.dot(this_normal, second_vector))-numpy.abs(numpy.cos(plane_angle))) < 0.001:
                            part.RemoveFaces(faceList=part.faces[face.index:(face.index+1)], deleteCells=False)
                            part.RemoveRedundantEntities(vertexList = part.vertices[:], edgeList = part.edges[:])
                            found_face = True
                            break
                except:
                    pass
            if II == (len(part.faces)-1):
                found_face = False
            else:
                pass

    # Step 29 - validate geometry
    abaqus.mdb.models[model_name].parts[part_name].checkGeometry()


def get_inputs():
    """Interactive Inputs

    Prompt the user for inputs with this interactive data entry function. When called, this function opens an Abaqus CAE
    GUI window with text boxes to enter values for the outputs listed below:

    :return: ``center`` - center location of the geometry
    :rtype: list

    :return: ``xvector`` - location on the x-axis local to the geometry
    :rtype: list

    :return: ``zvector`` - location on the z-axis local to the geometry
    :rtype: list
    """
    from abaqus import getInputs


    fields = (('Center:','0.0, 0.0, 0.0'),
              ('X-Vector:', '1.0, 0.0, 0.0'),
              ('Z-Vector:', '0.0, 0.0, 1.0'),
              ('Copy and Paste Parameters', 'ctrl+c ctrl+v printed parameters'), )
    center, xvector, zvector, cp_parameters = getInputs(fields=fields,
        label='Specify Geometric Parameters:',
        dialogTitle='Turbo Turtle', )
    if center is not None:
        if cp_parameters != fields[-1][-1]:
            cp_param = [x.replace('\n', '') for x in cp_parameters.split('\n')]
            center = ast.literal_eval(cp_param[0].replace('Center: ', ''))
            xpoint = ast.literal_eval(cp_param[1].replace('X-Vector: ', ''))
            zpoint = ast.literal_eval(cp_param[2].replace('Z-Vector: ', ''))
        else:
            center = list(ast.literal_eval(center))
            xvector = list(ast.literal_eval(xvector))
            zvector = list(ast.literal_eval(zvector))
        print('\nPartitioning Parameters Entered By User:')
        print('----------------------------------------')
        print('Center: {}'.format(center))
        print('X-Vector: {}'.format(xvector))
        print('Z-Vector: {}'.format(zvector))
        print('')
    return center, xpoint, zpoint


if __name__ == "__main__":
    try:
        center, xvector, zvector = get_inputs()
        model_name=None
        part_name=None
        partition(center, xvector, zvector, model_name, part_name)

    except:
        parser = parsers.partition_parser(basename=basename)
        try:
            args, unknown = parser.parse_known_args()
        except SystemExit as err:
            sys.exit(err.code)

        sys.exit(main(
            input_file=args.input_file,
            output_file=args.output_file,
            center=args.center,
            xvector=args.xvector,
            zvector=args.zvector,
            model_name=args.model_name,
            part_name=args.part_name
        ))
