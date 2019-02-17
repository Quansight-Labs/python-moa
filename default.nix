{ pkgs ? import <nixpkgs> { }, pythonPackages ? pkgs.python3Packages }:

rec {
  python-moa = pythonPackages.buildPythonPackage {
    name = "python-moa";
    format = "flit";

    src = builtins.filterSource
      (path: _: !builtins.elem  (builtins.baseNameOf path) [".git"])
      ./.;

    propagatedBuildInputs = with pythonPackages; [ sly astunparse ];
    checkInputs = with pythonPackages; [ pytest pytestcov graphviz ];

    checkPhase = ''
      pytest --cov=moa
    '';
  };

  shell = pkgs.mkShell {
    buildInputs = with pythonPackages; [ python-moa jupyterlab graphviz pkgs.graphviz ];

    shellHook = ''
      cd notebooks; jupyter lab
    '';
  };

}
