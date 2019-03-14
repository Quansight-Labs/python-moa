let
  # pin version
  pkgs = import (builtins.fetchTarball {
    url = "https://github.com/costrouc/nixpkgs/archive/14775a074cfacc59482d1adf0446801d38c08216.tar.gz";
    sha256 = "152dflinv7a0nk267nc1i3ldvrx5fwxm7cf3igxc0qnd92n82phf";
  }) { };

  pythonPackages = pkgs.python3Packages;
in
rec {
  python-moa = pythonPackages.buildPythonPackage {
    name = "python-moa";

    src = builtins.filterSource
      (path: _: !builtins.elem  (builtins.baseNameOf path) [".git" "result" "docs"])
      ./.;

    propagatedBuildInputs = with pythonPackages; [ sly astunparse ];
    checkInputs = with pythonPackages; [ pytest pytestcov pytest-benchmark graphviz ];

    postConfigure = ''
      # flit requires a home directory...
      export HOME=$(mktemp -d)
    '';

    checkPhase = ''
      pytest --cov=moa -k "not benchmark"
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

     buildInputs = with pythonPackages; [ python-moa sphinx sphinxcontrib-tikz ];

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
    buildInputs = with pythonPackages; [ python-moa jupyterlab graphviz pkgs.graphviz numpy numba];

    shellHook = ''
      cd notebooks; jupyter lab
    '';
  };

  binder = pkgs.mkShell {
    buildInputs = with pythonPackages; [ python-moa jupyterlab graphviz pkgs.graphviz numpy numba];
  };
}
