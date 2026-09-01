# JAIR author-kit subset

These five files are the unmodified class and BibLaTeX support files from the
official **JAIR Author Kit** downloaded from
`https://www.jair.org/index.php/jair/libraryFiles/downloadPublic/6` on
2026-08-31. The upstream ZIP labels the template files 2026-02-16.

Only the files required to compile an article are vendored; the example paper,
sample image, sample bibliography, macOS metadata and rendered example are
omitted. The SHA-256 values of the copied upstream bytes are:

```text
b174b1003076b63285ef5fcbc0469ce26206b70f6259922be82f96425d227693  acmart.cls
267dc31eb08af3524b12ac76d4e95fa6604022c2ae171eaa13b3af2220749f34  acmauthoryear.bbx
cb22394f982fcaf8ed7f0df34234696f45fc130afcf9ee3cd1260805ad2170d1  acmauthoryear.cbx
a5bab6fed4585780632607ef2790ee8797864244a4b80bc0c4e3bfcb76b0c2bc  acmdatamodel.dbx
b203f8fe198a82afececa5fc5c2641fa529e3aa05b82b329bcf5891be339fc68  jair.cls
```

These files govern publication formatting only and carry no scientific
authority.

`ccicons.sty` is a local text-only compatibility shim for the minimal TeX
installation used by the clean-build audit. The JAIR class renders the official
CC-BY PDF artwork through `doclicenseImage`; the shim only supplies fallback
commands required when the full `ccicons` package is absent.
