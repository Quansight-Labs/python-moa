# ARRAY 2019

A two page extended abstract was written for the [PLDI
ARRAY](https://pldi19.sigplan.org/series/ARRAY) series.

## Requirements

Submissions are welcome in two categories: full papers and extended
abstracts. All submissions should be formatted in conformance with the
ACM SIGPLAN proceedings style. Accepted submissions in either category
will be presented at the workshop.

Extended abstracts may be up to 2pp; they may describe work in
progress, tool demonstrations, and summaries of work published in full
elsewhere. The focus of the extended abstract should be to explain why
the proposed presentation will be of interest to the ARRAY
audience. Submissions will be lightly reviewed only for relevance to
the workshop, and will not published in the DL.

Whether full papers or extended abstracts, submissions must be in PDF
format, printable in black and white on US Letter sized paper. Papers
must adhere to the standard SIGPLAN conference format: two columns,
nine-point font on a ten-point baseline, with columns 20pc (3.33in)
wide and 54pc (9in) tall, with a column gutter of 2pc (0.33in). A
suitable document template for LaTeX is available at
http://www.sigplan.org/Resources/Author/.

Papers must be submitted using EasyChair.

Authors take note: The official publication date of full papers is the
date the proceedings are made available in the ACM Digital
Library. This date may be up to two weeks prior to the workshop. The
official publication date affects the deadline for any patent filings
related to published work.

## Development

Simply use [nix](https://nixos.org/nix/download.html) for building.

```shell
nix-build
okular result # open pdf with viewer
```

Or build it manually you will need texlive and xelatex installed.

```shell
latexmk -xelatex paper.tex
```

