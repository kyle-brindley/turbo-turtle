import subprocess

from turbo_turtle import _settings


def geometry(args, command):
    """Python 3 wrapper around the Abaqus Python :meth:`turbo_turtle._abaqus_python.parsers.geometry_parser` CLI

    :param argparse.Namespace args: namespace of parsed arguments
    :param str command: abaqus executable path
    """
    script = _settings._abaqus_python_abspath / "geometry.py"

    command = f"{command} cae -noGui {script} -- "
    command += f"--input-file {' '.join(map(str, args.input_file))} "
    command += f"--output-file {args.output_file} "
    command += f"--unit-conversion {args.unit_conversion} "
    command += f"--euclidean-distance {args.euclidean_distance} "
    if args.planar:
        command += f"--planar "
    command += f"--model-name {args.model_name} "
    if args.part_name[0] is not None:
        command += f"--part-name {' '.join(map(str, args.part_name))} "
    command += f"--delimiter {args.delimiter} "
    command += f"--header-lines {args.header_lines} "
    command += f"--revolution-angle {args.revolution_angle}"
    command = command.split()
    stdout = subprocess.check_output(command)


def cylinder(args, command):
    """Python 3 wrapper around the Abaqus Python :meth:`turbo_turtle._abaqus_python.parsers.cylinder_parser` CLI

    :param argparse.Namespace args: namespace of parsed arguments
    :param str command: abaqus executable path
    """
    script = _settings._abaqus_python_abspath / "cylinder.py"

    command = f"{command} cae -noGui {script} -- "
    command += f"--inner-radius {args.inner_radius} "
    command += f"--outer-radius {args.outer_radius} "
    command += f"--height {args.height} "
    command += f"--output-file {args.output_file} "
    command += f"--model-name {args.model_name} "
    command += f"--part-name {args.part_name} "
    command += f"--revolution-angle {args.revolution_angle}"
    command = command.split()
    stdout = subprocess.check_output(command)


def sphere(args, command):
    """Python 3 wrapper around the Abaqus Python :meth:`turbo_turtle._abaqus_python.parsers.sphere_parser` CLI

    :param argparse.Namespace args: namespace of parsed arguments
    :param str command: abaqus executable path
    """
    script = _settings._abaqus_python_abspath / "sphere.py"

    command = f"{command} cae -noGui {script} -- "
    command += f"--inner-radius {args.inner_radius} --outer-radius {args.outer_radius} "
    command += f"--output-file {args.output_file} "
    if args.input_file is not None:
        command += f"--input-file {args.input_file} "
    command += f"--quadrant {args.quadrant} --angle {args.angle} "
    command += f"--center {' '.join(map(str, args.center))} "
    command += f"--model-name {args.model_name} --part-name {args.part_name}"
    command = command.split()
    stdout = subprocess.check_output(command)


def partition(args, command):
    """Python 3 wrapper around the Abaqus Python :meth:`turbo_turtle._abaqus_python.parsers.partition_parser` CLI

    :param argparse.Namespace args: namespace of parsed arguments
    :param str command: abaqus executable path
    """
    script = _settings._abaqus_python_abspath / "partition.py"

    command = f"{command} cae -noGui {script} -- "
    command += f"--input-file {args.input_file} "
    if args.output_file is not None:
        command += f"--output-file {args.output_file} "
    command += f"--model-name {args.model_name} --part-name {args.part_name} "
    command += f"--xpoint {' '.join(map(str, args.xpoint))} "
    command += f"--center {' '.join(map(str, args.center))} "
    command += f"--zpoint {' '.join(map(str, args.zpoint))} "
    command += f"--plane-angle {args.plane_angle} "
    command += f"--x-partitions {' '.join(map(str, args.x_partitions))} "
    command += f"--y-partitions {' '.join(map(str, args.y_partitions))} "
    command += f"--z-partitions {' '.join(map(str, args.z_partitions))} "
    command = command.split()
    stdout = subprocess.check_output(command)


def mesh(args, command):
    """Python 3 wrapper around the Abaqus Python :meth:`turbo_turtle._abaqus_python.parsers.mesh_parser` CLI

    :param argparse.Namespace args: namespace of parsed arguments
    :param str command: abaqus executable path
    """
    script = _settings._abaqus_python_abspath / "mesh.py"

    command = f"{command} cae -noGui {script} -- "
    command += f"--input-file {args.input_file} "
    command += f"--element-type {args.element_type} "
    if args.output_file is not None:
        command += f"--output-file {args.output_file} "
    command += f"--model-name {args.model_name} --part-name {args.part_name} "
    command += f"--global-seed {args.global_seed}"
    command = command.split()
    stdout = subprocess.check_output(command)


def merge(args, command):
    """Python 3 wrapper around the Abaqus Python :meth:`turbo_turtle._abaqus_python.parsers.merge_parser` CLI

    :param argparse.Namespace args: namespace of parsed arguments
    :param str command: abaqus executable path
    """
    script = _settings._abaqus_python_abspath / "merge.py"

    command = f"{command} cae -noGui {script} -- "
    command += f"--input-file {' '.join(map(str, args.input_file))} "
    command += f"--output-file {args.output_file} "
    command += f"--merged-model-name {args.merged_model_name} "
    if args.model_name[0] is not None:
        command += f"--model-name {' '.join(map(str, args.model_name))} "
    if args.part_name[0] is not None:
        command += f"--part-name {' '.join(map(str, args.part_name))}"
    command = command.split()
    stdout = subprocess.check_output(command)


def export(args, command):
    """Python 3 wrapper around the Abaqus Python :meth:`turbo_turtle._abaqus_python.parsers.export_parser` CLI

    :param argparse.Namespace args: namespace of parsed arguments
    :param str command: abaqus executable path
    """
    script = _settings._abaqus_python_abspath / "export.py"

    command = f"{command} cae -noGui {script} -- "
    command += f"--input-file {args.input_file} "
    command += f"--model-name {args.model_name} --part-name {' '.join(map(str, args.part_name))} "
    if args.element_type[0] is not None:
        command += f"--element-type {' '.join(map(str, args.element_type))} "
    command += f"--destination {args.destination} "
    if args.assembly is not None:
        command += f"--assembly {args.assembly}"
    command = command.split()
    stdout = subprocess.check_output(command)


def image(args, command):
    """Python 3 wrapper around the Abaqus Python :meth:`turbo_turtle._abaqus_python.parsers.image_parser` CLI

    :param argparse.Namespace args: namespace of parsed arguments
    :param str command: abaqus executable path
    """
    script = _settings._abaqus_python_abspath / "image.py"

    command = f"{command} cae -noGui {script} -- "
    command += f"--input-file {args.input_file} "
    command += f"--output-file {args.output_file} "
    command += f"--x-angle {args.x_angle} "
    command += f"--y-angle {args.y_angle} "
    command += f"--z-angle {args.z_angle} "
    command += f"--image-size {' '.join(map(str, args.image_size))} "
    command += f"--model-name {args.model_name} --part-name {args.part_name}"
    command = command.split()
    stdout = subprocess.check_output(command)