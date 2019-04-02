{ pkgs ? import <nixpkgs> { }}:

pkgs.stdenv.mkDerivation {
  name = "python-moa-array-2019";

  src = ./.;

  buildInputs = with pkgs; [
    texlive.combined.scheme-full
  ];

  buildPhase = ''
    latexmk -xelatex paper.tex
  '';

  installPhase = ''
    cp paper.pdf $out
  '';
}
