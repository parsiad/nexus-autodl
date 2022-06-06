NAME:=nexus_autodl

ifeq ($(OS),Windows_NT)
	PATHSEP:=;
else
	PATHSEP:=:
endif

all: yapf lint mypy build

build: $(NAME).py
	pyinstaller --clean -F --add-data 'templates$(PATHSEP)templates' $<

clean:
	$(RM) -r build dist *.spec

lint: $(NAME).py
	pylint --max-line-length 120 $<

mypy: $(NAME).py
	mypy $<

yapf: $(NAME).py
	yapf -i --style style.yapf $<

.PHONY: build clean lint mypy yapf
