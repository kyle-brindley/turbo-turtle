# Build and install Conda package
$PYTHON -m build --no-isolation
$PYTHON -m pip install dist/$PKG_NAME-$PKG_VERSION.tar.gz --no-deps --ignore-installed -v --no-build-isolation
# Build man page and HTML documentation to bundle in Conda package
scons man html-internal
$PYTHON package_documentation.py
