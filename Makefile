NAME:=nexus_autodl

all: build

build: $(NAME).py
	pyinstaller --clean --noconsole -F $<

clean:
	$(RM) -r build dist *.spec

.PHONY: build clean
