#!/bin/bash

set -xe

if command -v apt-get &> /dev/null; then
  sudo apt-get install python3-launchpadlib
  sudo apt-get update
  sudo apt-get install -y xvfb libnvidia-egl-wayland1 mesa-utils libgl1-mesa-dri
fi

. $HOME/.cargo/env

ulimit -n 4096

if command -v Xvfb &> /dev/null; then
  if ! test "$ZEN_CROSS_COMPILING"; then
    Xvfb :2 -nolisten tcp -noreset -screen 0 1024x768x24 &
    XVFB_PID=$!
    export LLVM_PROFDATA=$HOME/.mozbuild/clang/bin/llvm-profdata
    export DISPLAY=:2
    
    # Wait for Xvfb to be ready
    echo "Waiting for Xvfb to start..."
    for i in {1..10}; do
      if xdpyinfo -display :2 >/dev/null 2>&1; then
        echo "Xvfb is ready"
        break
      fi
      echo "Waiting for Xvfb... ($i/10)"
      sleep 1
    done
    
    # Verify Xvfb is running
    if ! xdpyinfo -display :2 >/dev/null 2>&1; then
      echo "ERROR: Xvfb failed to start properly"
      exit 1
    fi
  fi
  export ZEN_RELEASE=1
  npm run build
else
  echo "Xvfb could not be found, running without it"
  echo "ASSUMING YOU ARE RUNNING THIS ON MACOS"

  set -v
  export ZEN_RELEASE=1
  npm run build
fi
