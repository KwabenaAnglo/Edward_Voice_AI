#!/usr/bin/env python3
"""
Simple GUI test to identify specific errors.
"""
import sys
import traceback
import tkinter as tk

def test_gui_imports():
    """Test GUI-related imports."""
    print("Testing GUI imports...")
    
    try:
        from gui import EdwardGUI
        print("✓ GUI module imported successfully")
        return True
    except Exception as e:
        print(f"✗ GUI import failed: {e}")
        traceback.print_exc()
        return False

def test_gui_creation():
    """Test GUI creation without showing."""
    print("\nTesting GUI creation...")
    
    try:
        import tkinter as tk
        from gui import EdwardGUI
        
        # Create root window but don't show it
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Create GUI instance
        gui = EdwardGUI(root)
        print("✓ GUI created successfully")
        
        # Clean up
        root.destroy()
        return True
    except Exception as e:
        print(f"✗ GUI creation failed: {e}")
        traceback.print_exc()
        return False

def test_missing_modules():
    """Check for missing optional modules."""
    print("\nChecking optional modules...")
    
    modules = {
        'elevenlabs': 'ElevenLabs TTS',
        'pyaudio': 'Audio recording',
        'wave': 'Audio file handling',
        'openai': 'OpenAI API',
        'dotenv': 'Environment variables'
    }
    
    missing = []
    for module, description in modules.items():
        try:
            __import__(module)
            print(f"✓ {module} - {description}")
        except ImportError:
            print(f"✗ {module} - {description} (missing)")
            missing.append(module)
    
    return len(missing) == 0

def main():
    """Run GUI tests."""
    print("Edward Voice AI - GUI Error Detection")
    print("=" * 50)
    
    tests = [
        test_missing_modules,
        test_gui_imports,
        test_gui_creation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            traceback.print_exc()
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All GUI tests passed!")
        return 0
    else:
        print("✗ Some GUI tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
