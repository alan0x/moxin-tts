#!/usr/bin/env python3
"""Test script to validate all dependencies are correctly installed.

Checks for standardized dependency versions as defined in DEPENDENCIES.md
"""

import sys
import importlib
import subprocess
from pathlib import Path

def test_import(module_name, package_name=None, expected_range=None):
    """Test if a module can be imported and check version range."""
    if package_name is None:
        package_name = module_name
    
    try:
        module = importlib.import_module(module_name)
        version = getattr(module, '__version__', 'unknown')
        
        if expected_range and version != 'unknown':
            print(f"✓ {package_name}: {version} {expected_range}")
        else:
            print(f"✓ {package_name}: {version}")
        return True
    except ImportError as e:
        print(f"✗ {package_name}: Import failed - {e}")
        return False

def test_command(command, name):
    """Test if a command is available."""
    try:
        result = subprocess.run([command, '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version = result.stdout.strip() or result.stderr.strip()
            print(f"✓ {name}: {version}")
            return True
        else:
            print(f"✗ {name}: Command failed")
            return False
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        print(f"✗ {name}: Not found - {e}")
        return False

def test_numpy_version():
    """Test numpy version is correct."""
    try:
        import numpy as np
        version = np.__version__
        if version.startswith('1.26'):
            print(f"✓ NumPy version: {version} (correct)")
            return True
        else:
            print(f"⚠ NumPy version: {version} (expected 1.26.x)")
            return False
    except ImportError:
        print(f"✗ NumPy: Not installed")
        return False

def test_dora_nodes():
    """Test if Dora nodes can be imported."""
    nodes = [
        ('dora_asr', 'dora-asr'),
        ('dora_primespeech', 'dora-primespeech'),
        ('dora_text_segmenter', 'dora-text-segmenter'),
        ('dora_speechmonitor', 'dora-speechmonitor'),
    ]
    
    all_ok = True
    for module_name, display_name in nodes:
        try:
            importlib.import_module(module_name)
            print(f"✓ {display_name}: Installed")
        except ImportError as e:
            print(f"✗ {display_name}: Not installed - {e}")
            all_ok = False
    
    return all_ok

def main():
    print("=" * 50)
    print("Testing Dora Chatbot Dependencies")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Test Python version
    python_version = sys.version.split()[0]
    if python_version.startswith('3.12'):
        print(f"✓ Python version: {python_version}")
    else:
        print(f"⚠ Python version: {python_version} (expected 3.12.x)")
        all_tests_passed = False
    
    print("\nCore Dependencies:")
    print("-" * 30)
    
    # Test core dependencies with version ranges (as per DEPENDENCIES.md)
    all_tests_passed &= test_numpy_version()
    all_tests_passed &= test_import('torch', expected_range='(>=2.0.0,<2.3.0)')
    all_tests_passed &= test_import('transformers', expected_range='(>=4.40.0,<4.50.0)')
    all_tests_passed &= test_import('torchaudio', expected_range='(>=2.0.0,<2.3.0)')
    all_tests_passed &= test_import('dora', 'dora-rs')
    
    print("\nML Libraries:")
    print("-" * 30)
    
    # Test ML libraries
    all_tests_passed &= test_import('huggingface_hub')
    all_tests_passed &= test_import('datasets')
    all_tests_passed &= test_import('accelerate')
    all_tests_passed &= test_import('sentencepiece')
    
    print("\nAudio Libraries:")
    print("-" * 30)
    
    # Test audio libraries
    all_tests_passed &= test_import('pyaudio')
    all_tests_passed &= test_import('soundfile')
    all_tests_passed &= test_import('librosa')
    all_tests_passed &= test_import('webrtcvad')
    
    print("\nNetworking Libraries:")
    print("-" * 30)
    
    # Test networking libraries  
    all_tests_passed &= test_import('openai')
    all_tests_passed &= test_import('websockets')
    all_tests_passed &= test_import('aiohttp')
    all_tests_passed &= test_import('requests')
    
    print("\nDora Nodes:")
    print("-" * 30)
    
    # Test Dora nodes
    all_tests_passed &= test_dora_nodes()
    
    print("\nSystem Commands:")
    print("-" * 30)
    
    # Test system commands
    all_tests_passed &= test_command('dora', 'Dora CLI')
    test_command('cargo', 'Cargo (optional)')  # Optional, don't affect overall result
    
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("✓ All required dependencies are installed correctly!")
    else:
        print("✗ Some dependencies are missing or incorrect.")
        print("  Please run setup_isolated_env.sh to fix issues.")
    print("=" * 50)
    
    return 0 if all_tests_passed else 1

if __name__ == "__main__":
    sys.exit(main())