LATEXMK ?= latexmk

all: main.pdf

main.pdf: main.tex gobble.sty sections/*.tex sections/*.md
	$(LATEXMK) -pdf -shell-escape -interaction=nonstopmode -halt-on-error main.tex

clean:
	$(LATEXMK) -C
