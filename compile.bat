@echo off
call "F:\Program Files\QGIS 3.10\bin\o4w_env.bat"
call "F:\Program Files\QGIS 3.10\bin\qt5_env.bat"
call "F:\Program Files\QGIS 3.10\bin\py3_env.bat"

@echo on
pyrcc5 -o resources.py resources.qrc