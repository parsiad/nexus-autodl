NAME:=nexus_autodl

all: build

build: $(NAME).py
	pyinstaller --clean -F $<

clean:
	$(RM) -r build dist *.spec

.PHONY: build clean
