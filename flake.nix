{
  description = ''
    CLI controller for qBittorrent with autocompletion support
  '';

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    inputs:
    inputs.flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import inputs.nixpkgs {
          inherit
            system
            ;
        };
        lib = inputs.nixpkgs.lib;

        py = pkgs.python3;
        pyEnv = py.withPackages (ps: [ ps.requests ]);
        pySite = py.sitePackages;

        completionScripts = {
          bash = ./completions/bash-completion.sh;
          fish = ./completions/fish-completion.fish;
          zsh = ./completions/zsh-completion.zsh;
        };
      in
      {
        packages = {
          rut2qb = pkgs.writeScriptBin "rut2qb" (builtins.readFile ./rut2py.py);
          qbHelper = pkgs.stdenvNoCC.mkDerivation {
            pname = "qbittorrent-helper";
            version = "1.0.0";

            src = ./.;

            nativeBuildInputs = [ pkgs.makeWrapper ];
            buildInputs = [ pkgs.python3 ];

            installPhase = ''
              mkdir -p $out/bin $out/share/bash-completion/completions $out/share/fish/vendor_completions.d $out/share/zsh/site-functions

              # Устанавливаем основной скрипт
              install -Dm755 qbHelper.py $out/bin/qbHelper
              wrapProgram $out/bin/qbHelper \
                --prefix PATH : ${lib.makeBinPath [ py ]} \
                --set PYTHONPATH "${pyEnv}/${pySite}"
              chmod +x $out/bin/qbHelper

              # Устанавливаем completion-скрипты
              install -Dm644 ${completionScripts.bash} $out/share/bash-completion/completions/qbt-controller
              install -Dm644 ${completionScripts.fish} $out/share/fish/vendor_completions.d/qbt-controller.fish
              install -Dm644 ${completionScripts.zsh}  $out/share/zsh/site-functions/_qbt-controller
            '';

            meta = with lib; {
              mainProgram = "torr";
              description = "CLI controller for qBittorrent with autocompletion support";
              homepage = "https://github.com/mctrxnv/qbHelper";
              license = licenses.mit;
              maintainers = with maintainers; [ mctrxnv ];
              platforms = platforms.all;
            };
          };
        };
      }
    );
}
