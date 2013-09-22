REM ******** set the variables ************
REM call both to ensure that one works
call "C:\Program Files\Microsoft Visual Studio 10.0\VC\vcvarsall.bat"
call "C:\Program Files (x86)\Microsoft Visual Studio 10.0\VC\vcvarsall.bat"

REM ******* compile all the sources from CoolProp ***************
cl /c /O2 /I../../CoolProp /MD /EHsc ../../CoolProp/*.cpp
cl /c /O2 /I../../CoolProp /MD /EHsc src/*.cpp

lib CoolProp.obj *.obj /OUT:CoolPropLib.lib
erase *.obj
