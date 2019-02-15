{ pkgs ? import <nixpkgs> { }, pythonPackages ? pkgs.python3Packages }:

{
  python-moa = pythonPackages.buildPythonPackage {
    name = "python-moa";
    format = "flit";

    src = builtins.filterSource
      (path: _: !builtins.elem  (builtins.baseNameOf path) [".git"])
      ./.;

    propagatedBuildInputs = with pythonPackages; [ sly ];
    checkInputs = with pythonPackages; [ pytest ];

    checkPhase = ''
      pytest moa
    '';
  };

}
