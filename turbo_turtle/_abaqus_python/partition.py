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
         output_file=parsers.partition_defaults["output_file"],
         center=parsers.partition_defaults["center"],
         xvector=parsers.partition_defaults["xvector"],
         zvector=parsers.partition_defaults["zvector"],
         model_name=parsers.partition_defaults["model_name"],
         part_name=parsers.partition_defaults["part_name"],
         big_number=parsers.partition_defaults["big_number"]):
    """Wrap  partition function with file open and file write operations

    :param str input_file: Abaqus CAE model database to open
    :param str output_file: Abaqus CAE model database to write. If none is provided, use the input file.
    :param list center: center location of the geometry
    :param list xvector: Local x-axis vector defined in global coordinates
    :param list zvector: Local z-axis vector defined in global coordinates
    :param str model_name: model to query in the Abaqus model database (only applies when used with ``abaqus cae -nogui``)
    :param list part_name: list of parts to query in the specified Abaqus model (only applies when used with ``abaqus cae -nogui``)
    :param float big_number: Number larger than the outer radius of the part to partition.

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
        partition(center, xvector, zvector, model_name, part_name, big_number=big_number)
        abaqus.mdb.saveAs(pathName=output_file)


def datum_axis(center, vector, part):
    """Return an Abaqus DataAxis object by center and normal axis

    :param numpy.array center: center location of the axis
    :param numpy.array vector: axis vector
    :param abaqus.mdb.models[].parts[] part: Abaqus part object

    :returns: Abaqus datum axis object
    :rtype: DatumAxis
    """
    point = center + vector
    return part.datums[part.DatumAxisByTwoPoint(point1=tuple(center), point2=tuple(point)).id]


def datum_plane(center, normal, part):
    """Return an Abaqus DataPlane object by center and normal axis

    :param numpy.array center: center location of the plane
    :param numpy.array normal: plane normal vector
    :param abaqus.mdb.models[].parts[] part: Abaqus part object

    :returns: Abaqus Datum Plane object
    :rtype: DatumPlane
    """
    axis = datum_axis(center, normal, part)
    return part.datums[part.DatumPlaneByPointNormal(point=tuple(center), normal=axis).id]


def partition(center, xvector, zvector, model_name, part_name, big_number=parsers.partition_defaults["big_number"]):
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
    :param list part_name: list of parts to query in the specified Abaqus model (only applies when used with ``abaqus cae -nogui``)
    :param float big_number: Number larger than the outer radius of the part to partition.
    """
    import abaqus
    import caeModules
    import abaqusConstants

    # Process input and calculate local coordinate system properties
    xvector = vertices.normalize_vector(xvector)
    zvector = vertices.normalize_vector(zvector)
    yvector = numpy.cross(zvector, xvector)
    center = numpy.array(center)
    plane_normals = vertices.datum_planes(xvector, zvector)

    angle = numpy.pi / 2. - numpy.arccos(numpy.sqrt(2.0/3.0))
    big_number_coordinates = vertices.rectalinear_coordinates([big_number], [angle])[0]
    # TODO: This depends on the :meth:`turbo_turtle._abaqus_python.vertices.datum_planes` tuple order. Find a way to
    # programmatically calculate (or return) the paired positive sketch edge instead of hardcoding the matching order.
    positive_sketch_axis = (yvector, yvector, zvector, zvector, xvector, xvector)
    sketch_vertex_pairs = (
        ((-big_number_coordinates[0],  big_number_coordinates[1]),
         ( big_number_coordinates[0],  big_number_coordinates[1])),
        ((-big_number_coordinates[0], -big_number_coordinates[1]),
         ( big_number_coordinates[0], -big_number_coordinates[1]))
    )

    model = abaqus.mdb.models[model_name]
    for current_part in part_name:
        part = model.parts[current_part]

        # Create local coordinate system primary partition planes
        partition_planes = [datum_plane(center, normal, part) for normal in plane_normals]

        # Partition by three (3) local coordinate system x/y/z planes
        for plane in partition_planes[0:3]:
            try:
                part.PartitionCellByDatumPlane(datumPlane=plane, cells=part.cells[:])
            except:
                pass

        # Partition by sketch on the six (6) 45 degree planes
        for edge, plane in zip(positive_sketch_axis, partition_planes[3:]):
            axis = datum_axis(center, edge, part)
            # TODO: Move to a dedicated partition function
            for vertex_1, vertex_2 in sketch_vertex_pairs:
                transform = part.MakeSketchTransform(
                    sketchPlane=plane,
                    sketchUpEdge=axis,
                    sketchPlaneSide=abaqusConstants.SIDE1,
                    origin=center
                )
                sketch = model.ConstrainedSketch(
                    name='__profile__',
                    sheetSize=91.45,
                    gridSpacing=2.28,
                    transform=transform
                )
                sketch.setPrimaryObject(option=abaqusConstants.SUPERIMPOSE)
                part.projectReferencesOntoSketch(sketch=sketch, filter=abaqusConstants.COPLANAR_EDGES)
                sketch.Line(point1=(0.0, 0.0), point2=vertex_1)
                sketch.Line(point1=(0.0, 0.0), point2=vertex_2)
                sketch.Line(point1=vertex_1, point2=vertex_2)
                try:
                    part.PartitionCellBySketch(
                        sketchPlane=plane,
                        sketchUpEdge=axis,
                        cells=part.cells[:],
                        sketch=sketch
                    )
                # TODO: Is is possible to distinguish between expected failures (operating on an incomplete sphere, so
                # sketch doesn't intersect) and unexpected failures (bad options, missing geometry, etc)?
                except AbaqusException as err:
                    pass

        abaqus.mdb.models[model_name].parts[current_part].checkGeometry()


def _partition_gui_get_inputs():
    """Interactive Inputs

    Prompt the user for inputs with this interactive data entry function. When called, this function opens an Abaqus CAE
    GUI window with text boxes to enter the following values:
    
    GUI-INPUTS
    ==========
    * Center - center location of the geometry
    * X-Vector - location on the x-axis local to the geometry
    * Z-Vector - location on the z-axis local to the geometry
    * Loop Through Parts - Yes/No value to loop through all parts in the current model
    * Copy and Paste Parameters - copy and paste the parameters printed to the Abaqus Python terminal to make 
      re-use of previous partition parameters easier

    **IMPORTANT** - this function must return values in the same order as the ``partition`` function

    :return: ``center`` - center location of the geometry
    :rtype: list

    :return: ``xvector`` - location on the x-axis local to the geometry
    :rtype: list

    :return: ``zvector`` - location on the z-axis local to the geometry
    :rtype: list

    :return ``model_name`` - name of the model in the current viewport
    :rtype: str

    :return ``part_name`` - name of the part in the current viewport, or a list of all part names in the model
    :rtype: list
    """
    from abaqus import getInputs

    model_name = None  # Set defaults in case the user cancels turbo-turtle
    part_name = []
    fields = (('Center:','0.0, 0.0, 0.0'),
              ('X-Vector:', '1.0, 0.0, 0.0'),
              ('Z-Vector:', '0.0, 0.0, 1.0'),
              ('Loop Through Parts:', 'No (or Yes/y)'),
              ('Copy and Paste Parameters', 'ctrl+c ctrl+v printed parameters'), )
    center, xvector, zvector, loop_through_parts, cp_parameters = getInputs(fields=fields,
        dialogTitle='Turbo Turtle', )
    if center is not None:  # Center will be None if the user hits the "cancel/esc" button
        if cp_parameters != fields[-1][-1]:
            cp_param = [x.replace('\n', '') for x in cp_parameters.split('\n')]
            center = ast.literal_eval(cp_param[0].replace('Center: ', ''))
            xvector = ast.literal_eval(cp_param[1].replace('X-Vector: ', ''))
            zvector = ast.literal_eval(cp_param[2].replace('Z-Vector: ', ''))
        else:
            center = list(ast.literal_eval(center))
            xvector = list(ast.literal_eval(xvector))
            zvector = list(ast.literal_eval(zvector))
        print('\nPartitioning Parameters Entered By User:')
        print('----------------------------------------')
        print('Only copy the three lines below to use "Copy and Paste Parameters"\n')
        print('Center: {}'.format(center))
        print('X-Vector: {}'.format(xvector))
        print('Z-Vector: {}'.format(zvector))
        print('')
        if loop_through_parts.upper() == "YES" or loop_through_parts.upper() == "Y":
            part_name = abaqus.mdb.models[model_name].parts.keys()
        else:  # Accept anything other than yes/y as No
            part_name = [session.viewports[session.currentViewportName].displayedObject.name]
        model_name = session.viewports[session.currentViewportName].displayedObject.modelName
    return center, xvector, zvector, model_name, part_name


def _partition_gui_post_action(center, xvector, zvector, model_name, part_name):
    """Action performed after running partition

    After partitioning, this funciton resets the viewport - if the last partition action hits the an AbaqusException
    except statement in the ``partition`` function, the user will otherwise be left in a sketch view that is hard to
    exit from. An example of this is partioning a half-sphere; half of the partitioning actions are expected to fail,
    since there is no geometry to partition on the open-end of the half-sphere.

    This function is designed to have the exact same arguments as 
    :meth:`turbo_turtle._abaqus_python.partition.partition`
    """
    import abaqus

    part_object = abaqus.mdb.models[model_name].parts[part_name[-1]]
    session.viewports['Viewport: 1'].setValues(displayedObject=part_object)
    session.viewports['Viewport: 1'].view.setValues(session.views['Iso'])
    session.viewports['Viewport: 1'].view.fitView()


def gui_wrapper(inputs_function, subcommand_function, post_action_function=None):
    """Wrapper around the abaqus.getInputs function and calls a turbo_turtle._abaqus_python module

    ``inputs_function`` cannot have any function arguments. ``inputs_function`` must return
    values to match the arguments of the ``subcommand_function``. ``post_action_function`` must have identical
    arguments to ``subcommand_function`` or the ability to ignore provided arguments. Any return values from 
    ``post_action_function`` will have no affect.
    
    :param func inputs_function: function to get user inputs through the Abaqus CAE GUI
    :param func subcommand_function: function with arguments matching the return values from ``inputs_function``
    :param func post_action_function: function to call for script actions after calling ``subcommand_function``
    """
    import abaqus

    user_inputs = inputs_function()  # Tuple of user inputs, if the user Cancels, all will be None
    if user_inputs[0] is None:
        print('\nTurboTurtle was canceled\n')  # Do not sys.exit, that will kill Abaqus CAE
    else:
        subcommand_function(*user_inputs)  # Assumes inputs_function returns same arguments expected by subcommand_function
        if post_action_function is not None:
            post_action_function(*user_inputs)


if __name__ == "__main__":
    if 'caeModules' in sys.modules:  # All Abaqus CAE sessions immediately load caeModules
        gui_wrapper(inputs_function=_partition_gui_get_inputs,
                    subcommand_function=partition,
                    post_action_function=_partition_gui_post_action)
    else:
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
            part_name=args.part_name,
            big_number=args.big_number
        ))
