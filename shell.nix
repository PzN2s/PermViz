{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  packages = [
    pkgs.python313
    pkgs.python313Packages.textual
  ];
}
