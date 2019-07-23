{ pkgs ? import <nixpkgs> {}, pythonPackages ? pkgs.python3Packages, benchmark ? false }:

rec {
  package = pythonPackages.buildPythonPackage rec {
    name = "python-moa";

    src = builtins.filterSource
      (path: _: !builtins.elem  (builtins.baseNameOf path) [".git" "result" "docs"])
      ./.;

    propagatedBuildInputs = with pythonPackages; [
      sly
      astunparse
    ];

    checkInputs = with pythonPackages; [
      pytest
      pytestcov
      graphviz
    ] ++ (if benchmark then [
      pytest-benchmark
      numpy
      numba
      pytorch
      tensorflow
    ] else [ ]);

    checkPhase = ''
      pytest tests ${if benchmark then "benchmarks" else ""} --cov=moa
    '';
  };

  sdist = pkgs.stdenv.mkDerivation {
    name = "python-moa-sdist";

    buildInputs = [ package ];

    src = builtins.filterSource
        (path: _: !builtins.elem  (builtins.baseNameOf path) [".git" "result"])
        ./.;

    buildPhase = ''
      python setup.py sdist
    '';

    installPhase = ''
      mkdir -p $out
      cp dist/* $out
    '';
  };

  docs = pkgs.stdenv.mkDerivation {
    name = "python-moa-docs";

    src = builtins.filterSource
      (path: _: !builtins.elem  (builtins.baseNameOf path) [".git" "result"])
      ./.;

     postPatch = ''
      # readthedocs makes the default GhostScript
      substituteInPlace docs/conf.py \
        --replace "'GhostScript'" "'pdf2svg'"
    '';

    buildInputs = with pythonPackages; [
      package
      sphinx
      # sphinxcontrib-tikz
    ];

    buildPhase = ''
      cd docs;
      sphinx-apidoc -f -o source/ ../moa
      sphinx-build -b doctest . _build/doctest
      sphinx-build -b html . _build/html
    '';

    installPhase = ''
      mkdir $out
      cp -r _build/html/* $out
    '';
  };

  docker = pkgs.dockerTools.buildLayeredImage {
    name = "python-moa";
    tag = "latest";
    contents = [
      (pythonPackages.python.withPackages (ps: with ps; [ package ipython ]))
    ];
    config.Cmd = [ "ipython" ];
    maxLayers = 120;
  };
}
