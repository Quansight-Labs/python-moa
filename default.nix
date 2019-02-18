let
  # pin version
  pkgs = import (builtins.fetchGit {
    url = "https://github.com/nixos/nixpkgs.git";
    rev = "36f316007494c388df1fec434c1e658542e3c3cc";
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
