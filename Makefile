NAME := nexus_autodl

ifeq ($(OS),Windows_NT)
    PATHSEP := ;
else
    PATHSEP := :
endif

# Update these paths with the correct paths to your Python executables
PYTHON_EXEC := C:\Py37\python.exe
YAPF_PATH := C:\py37\Scripts\yapf.exe
MYPY_PATH := C:\py37\Scripts\mypy.exe
BUILD_PATH := C:\py37\Scripts\pyinstaller.exe

all: yapf mypy build

build: $(NAME).py
	$(BUILD_PATH) --clean -F --add-data 'templates$(PATHSEP)templates' --icon icon.ico $<

clean:
	$(RM) -r build dist *.spec

mypy: $(NAME).py
	$(MYPY_PATH) $<

yapf: $(NAME).py
	$(PYTHON_EXEC) $(YAPF_PATH) -i --style style.yapf $<

.PHONY: build clean mypy yapf
