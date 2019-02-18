let
  # pin version
  pkgs = import (builtins.fetchTarball {
    url = "https://github.com/NixOS/nixpkgs/archive/36f316007494c388df1fec434c1e658542e3c3cc.tar.gz";
    sha256 = "1w1dg9ankgi59r2mh0jilccz5c4gv30a6q1k6kv2sn8vfjazwp9k";
  }) { };

  pythonPackages = pkgs.python3Packages;

  src = builtins.filterSource
      (path: _: !builtins.elem  (builtins.baseNameOf path) [".git" "result"])
      ./.;
in
rec {
  python-moa = pythonPackages.buildPythonPackage {
    name = "python-moa";
    format = "flit";

    inherit src;

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

     inherit src;

     buildInputs = with pythonPackages; [ python-moa sphinx ];

     buildPhase = ''
       cd docs;
       sphinx-apidoc -f -o source/ ../moa
       sphinx-build -b html . _build/html
     '';

     installPhase = ''
       mkdir $out
       cp -r _build/html/* $out
     '';
   };

  shell = pkgs.mkShell {
    buildInputs = with pythonPackages; [ python-moa jupyterlab graphviz pkgs.graphviz ];

    shellHook = ''
      cd notebooks; jupyter lab
    '';
  };
}
