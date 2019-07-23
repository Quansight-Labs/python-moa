let pkgs = import (builtins.fetchTarball {
      url = "https://github.com/costrouc/nixpkgs/archive/14775a074cfacc59482d1adf0446801d38c08216.tar.gz";
      sha256 = "152dflinv7a0nk267nc1i3ldvrx5fwxm7cf3igxc0qnd92n82phf";
    }) { };

    build = import ./build.nix {
      inherit pkgs;
      pythonPackages = pkgs.python3Packages;
    };
in {
  python-moa = build.package;
  python-moa-docs = build.docs;
  python-moa-sdist = build.sdist;
  python-moa-docker = build.docker;
}
