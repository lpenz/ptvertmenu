{
  description =
    ''
      Vertical menu widget for prompt-toolkit with optional fzf-inspired search
    '';
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.05";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages."${system}";
        python = pkgs.python3Packages;
        ptvertmenu = pkgs.python3Packages.buildPythonPackage {
          pname = "ptvertmenu";
          version = "0.1.0";
          src = self;
          requirements = builtins.readFile ./requirements.txt;
          propagatedBuildInputs = [
            python.prompt-toolkit
          ];
        };
      in
      rec {
        packages.default = ptvertmenu;
      }
    );
}
