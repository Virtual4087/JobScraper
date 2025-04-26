{ pkgs }:

{
  packages = with pkgs; [
    python311
    python311Packages.pip
    python311Packages.flask
    python311Packages.requests
    python311Packages.beautifulsoup4
  ];
}
