#!/bin/bash

# Quick install script for macOS dependencies
# Run this before setup_isolated_env.sh

echo "Installing macOS dependencies via Homebrew..."
brew install portaudio ffmpeg git-lfs openblas libomp

echo ""
echo "✓ All dependencies installed!"
echo ""
echo "Next steps:"
echo "  cd models/setup-local-models"
echo "  ./setup_isolated_env.sh"
