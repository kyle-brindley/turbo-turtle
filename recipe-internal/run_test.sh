cd $SP_DIR/$PKG_NAME
pytest -vvv -n 4 --ignore=_abaqus_python -m "" --abaqus-command=/apps/abaqus/Commands/abq2024 --cubit-command=/apps/Cubit-16.16/cubit
pytest -vvv -n 4 --ignore=_abaqus_python -m "systemtest and abaqus" --abaqus-command=/apps/abaqus/Commands/abq2023
/apps/abaqus/Commands/abq2024 python -m unittest discover _abaqus_python/turbo_turtle_abaqus --verbose
/apps/abaqus/Commands/abq2023 python -m unittest discover _abaqus_python/turbo_turtle_abaqus --verbose
