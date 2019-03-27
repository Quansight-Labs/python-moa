{ benchmark ? false }:

let
  # pin version
  pkgs = import (builtins.fetchTarball {
    url = "https://github.com/costrouc/nixpkgs/archive/14775a074cfacc59482d1adf0446801d38c08216.tar.gz";
    sha256 = "152dflinv7a0nk267nc1i3ldvrx5fwxm7cf3igxc0qnd92n82phf";
  }) { };

  pythonPackages = pkgs.python3Packages;

  buildInputs = with pythonPackages; [ sly astunparse ];
  docsInputs = with pythonPackages; [ sphinx sphinxcontrib-tikz ];
  testInputs = with pythonPackages; [ pytest pytestcov graphviz ];
  benchmarkInputs = with pythonPackages; [ pytest-benchmark numpy numba pytorch tensorflow ];
in
rec {
  python-moa = pythonPackages.buildPythonPackage {
    name = "python-moa";

    src = builtins.filterSource
      (path: _: !builtins.elem  (builtins.baseNameOf path) [".git" "result" "docs"])
      ./.;

    propagatedBuildInputs = buildInputs;
    checkInputs = if benchmark then testInputs ++ benchmarkInputs else testInputs;

    checkPhase = ''
      # pytest tests ${if benchmark then "benchmarks" else ""} --cov=moa
      pytest tests/test_ast.py tests/test_visualize.py
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

     buildInputs = [ python-moa ] ++ docsInputs;

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

  # docker load < result
  docker = pkgs.dockerTools.buildLayeredImage {
    name = "python-moa";
    tag = "latest";
    contents = [
      (pythonPackages.python.withPackages (ps: with ps; [ python-moa ipython ]))
    ];
    config.Cmd = [ "ipython" ];
    maxLayers = 120;
  };

  ipython-shell = pkgs.mkShell {
    buildInputs = with pythonPackages; [ python-moa ipython ];

    shellHook = ''
      cd notebooks; ipython
    '';
  };

  jupyter-shell = pkgs.mkShell {
    buildInputs = with pythonPackages; [ python-moa jupyterlab graphviz numpy numba];

    shellHook = ''
      cd notebooks; jupyter lab
    '';
  };

  binder = pkgs.mkShell {
    buildInputs = with pythonPackages; [ python-moa jupyterlab graphviz numpy numba];
  };
}
