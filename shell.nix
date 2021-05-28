{ pkgs ? import <nixpkgs> {} }:
  pkgs.mkShell {
    buildInputs = [
      pkgs.python37
      pkgs.python37Packages.virtualenv
      pkgs.python37Packages.pip
      pkgs.python37Packages.tkinter
      pkgs.python37Packages.pygobject3
      pkgs.python37Packages.matplotlib
      pkgs.python37Packages.numpy
      pkgs.python37Packages.scipy
      # pkgs.python37Packages.tensorflow
      pkgs.python37Packages.tensorflow-tensorboard
      # pkgs.python37Packages.pytorch

      pkgs.gobjectIntrospection
      pkgs.gtk3
      pkgs.poppler_utils

      pkgs.cmake
      pkgs.libGLU
      pkgs.libGL
      pkgs.curl
      pkgs.patchelf
      pkgs.glfw3
      pkgs.bzip2
      pkgs.swig
      pkgs.gcc9
      pkgs.libglvnd
      pkgs.xorg.libX11
      pkgs.xorg.libXext
      pkgs.xorg.libXft
      pkgs.xorg.libXcursor
      pkgs.xorg.libXrender
      pkgs.xorg.libXrandr
      pkgs.xorg.libXfixes
      pkgs.glib
    ];

    shellHook = ''
    unset SOURCE_DATE_EPOCH

    if [[ ! -d ".venv" ]]
      then
        python3 -m venv .venv;
    fi

    source .venv/bin/activate

    export TMPDIR="$(pwd)/.tmp" # torch refuses to install if we use the default tmp dir
    mkdir -p $TMPDIR
    pip install -r requirements.txt
    '';
    
    LD_LIBRARY_PATH = "/run/opengl-driver/lib:${with pkgs; lib.makeLibraryPath [
      fox_1_6
      proj
      xercesc
      xorg.libX11
      xorg.libXext
      libglvnd
      gcc-unwrapped
      glib
      gl2ps
      gnome2.pango
    ]}";
    
    SUMO_HOME = "/home/drusu/src/sumo";
}
