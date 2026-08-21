LATEXMK ?= latexmk

all: main.pdf

main.pdf: main.tex chapters/*.tex chapters/*.md
	$(LATEXMK) -pdf -shell-escape -interaction=nonstopmode -halt-on-error main.tex

clean:
	$(LATEXMK) -C
