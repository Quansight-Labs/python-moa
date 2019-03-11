let
  # pin version
  pkgs = import (builtins.fetchTarball {
    url = "https://github.com/NixOS/nixpkgs/archive/2a81eceeba6d9b0499c0a9dc569921765321cdd0.tar.gz";
    sha256 = "0zhg87ialczrz4yb4zy104l8wsw45bivpq33qg8czvnsisq77735";
  }) { };

  pythonPackages = pkgs.python3Packages;
in
rec {
  python-moa = pythonPackages.buildPythonPackage {
    name = "python-moa";
    format = "flit";

    src = builtins.filterSource
      (path: _: !builtins.elem  (builtins.baseNameOf path) [".git" "result" "docs"])
      ./.;

    propagatedBuildInputs = with pythonPackages; [ sly astunparse ];
    checkInputs = with pythonPackages; [ pytest pytestcov graphviz ];

    postConfigure = ''
      # flit requires a home directory...
      export HOME=$(mktemp -d)
    '';

    checkPhase = ''
      pytest --cov=moa
    '';
  };

  docs = pkgs.stdenv.mkDerivation {
     name = "python-moa-docs";

     src = builtins.filterSource
      (path: _: !builtins.elem  (builtins.baseNameOf path) [".git" "result"])
      ./.;

     buildInputs = with pythonPackages; [ python-moa sphinx ];

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
    buildInputs = with pythonPackages; [ python-moa jupyterlab graphviz pkgs.graphviz ];

    shellHook = ''
      cd notebooks; jupyter lab
    '';
  };

  binder = pkgs.mkShell {
    buildInputs = with pythonPackages; [ python-moa jupyterlab graphviz pkgs.graphviz ];
  };
}
