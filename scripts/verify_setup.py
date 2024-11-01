# scripts/verify_setup.py
import os
import importlib.util
import sys

def verify_extension_setup():
    results = []
    
    # Check directory structure
    base_dir = os.path.dirname(os.path.dirname(__file__))
    required_files = [
        'install.py',
        'requirements.txt',
        'scripts/hf_backup.py',
        'scripts/settings.py'
    ]
    
    for file in required_files:
        if os.path.exists(os.path.join(base_dir, file)):
            results.append(f"✓ Found {file}")
        else:
            results.append(f"✗ Missing {file}")
    
    # Check dependencies
    dependencies = {
        'huggingface_hub': '4.30.2',
        'glob2': '0.7'
    }
    
    for package, version in dependencies.items():
        try:
            imported = importlib.import_module(package)
            actual_version = getattr(imported, '__version__', 'unknown')
            if actual_version == version:
                results.append(f"✓ {package} version {version} installed correctly")
            else:
                results.append(f"! {package} version mismatch. Expected {version}, got {actual_version}")
        except ImportError:
            results.append(f"✗ {package} not installed")
    
    # Check HF token (if set)
    from modules import shared
    if hasattr(shared.opts, 'data') and shared.opts.data.get("hf_write_key"):
        results.append("✓ HF Write token is set")
    else:
        results.append("! HF Write token not set in settings")
    
    return "\n".join(results)

# You can run this directly to test:
if __name__ == "__main__":
    print(verify_extension_setup())
