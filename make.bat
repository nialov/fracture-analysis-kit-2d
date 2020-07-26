@ECHO OFF
ECHO Running tests
pytest

ECHO Updating requirements_dev.txt
python -m pip freeze > requirements_dev.txt

ECHO Building documentation into .\docs
sphinx-build -b html docs_src\source docs
ECHO Documentation built.

ECHO Archiving plugin to .\zip_build\fracture_analysis_2d.zip
pb_tool zip

if %1%==deploy pb_tool deploy --no-confirm