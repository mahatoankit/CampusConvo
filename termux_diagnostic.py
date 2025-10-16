#!/usr/bin/env python3
"""
Termux Audio Diagnostic Tool
Checks what's missing for voice mode to work
"""

import os
import subprocess
import sys

def check(description, condition, fix=""):
    """Print check result"""
    if condition:
        print(f"[OK] {description}")
        return True
    else:
        print(f"[ERROR] {description}")
        if fix:
            print(f"        Fix: {fix}")
        return False

print("=" * 60)
print("Termux Audio Diagnostic Tool")
print("=" * 60)
print()

all_good = True

# Check 1: Termux environment
print("1. Checking Termux environment...")
is_termux = os.path.exists("/data/data/com.termux")
all_good &= check("Running in Termux", is_termux)
print()

if not is_termux:
    print("This diagnostic is for Termux only!")
    print("Run on your Android device in Termux app.")
    sys.exit(1)

# Check 2: termux-api package
print("2. Checking termux-api package...")
result = subprocess.run("pkg list-installed | grep -q termux-api", 
                       shell=True, capture_output=True)
has_package = result.returncode == 0
all_good &= check("termux-api package installed", has_package, 
                 "pkg install termux-api")
print()

# Check 3: termux-microphone-record command
print("3. Checking termux-microphone-record command...")
result = subprocess.run("which termux-microphone-record", 
                       shell=True, capture_output=True)
has_command = result.returncode == 0

if has_command:
    location = result.stdout.decode().strip()
    print(f"[OK] termux-microphone-record found at: {location}")
else:
    print("[ERROR] termux-microphone-record command NOT found")
    print("        This means Termux:API APP is NOT installed!")
    print()
    print("        REQUIRED: Install Termux:API app from F-Droid:")
    print("        https://f-droid.org/en/packages/com.termux.api/")
    print()
    print("        Steps:")
    print("        1. Open browser on your phone")
    print("        2. Go to the URL above")
    print("        3. Download and install Termux:API app")
    print("        4. Grant microphone permission")
    print("        5. Restart Termux and run this script again")

all_good &= has_command
print()

# Check 4: Storage access
print("4. Checking storage access...")
can_write = os.access("/sdcard", os.W_OK)
all_good &= check("Can write to /sdcard", can_write,
                 "Run: termux-setup-storage")
print()

# Check 5: Test recording (only if command exists)
if has_command:
    print("5. Testing actual recording...")
    print("   Recording 3 seconds of audio, please speak...")
    
    test_file = "/sdcard/Download/termux_diagnostic_test.wav"
    
    # Clean up old test file
    if os.path.exists(test_file):
        os.remove(test_file)
    
    # Try recording
    result = subprocess.run(
        f"termux-microphone-record -f {test_file} -d 3",
        shell=True,
        capture_output=True
    )
    
    if result.returncode == 0:
        import time
        print("   Please speak now...")
        time.sleep(3)
        
        # Stop recording
        subprocess.run("termux-microphone-record -q", shell=True)
        
        # Check file
        if os.path.exists(test_file):
            size = os.path.getsize(test_file)
            if size > 1000:
                print(f"[OK] Recording successful! ({size:,} bytes)")
                all_good &= True
            else:
                print(f"[WARNING] File created but very small ({size} bytes)")
                print("           Microphone permission may not be granted")
                print("           Settings -> Apps -> Termux:API -> Permissions -> Microphone")
                all_good &= False
        else:
            print("[ERROR] Recording file was not created")
            print("        Check storage permissions")
            all_good &= False
    else:
        error = result.stderr.decode() if result.stderr else "Unknown error"
        print(f"[ERROR] Recording failed: {error}")
        print("        Check microphone permission for Termux:API app")
        all_good &= False
    print()

# Summary
print("=" * 60)
if all_good:
    print("SUCCESS! Voice mode should work!")
    print()
    print("You can now run:")
    print("  python client.py")
    print("  Choose: v (voice mode)")
else:
    print("ISSUES FOUND - Voice mode will NOT work yet")
    print()
    print("Most Common Fix:")
    print("1. Install Termux:API app from F-Droid:")
    print("   https://f-droid.org/en/packages/com.termux.api/")
    print()
    print("2. Grant microphone permission:")
    print("   Settings -> Apps -> Termux:API -> Permissions -> Microphone")
    print()
    print("3. Restart Termux completely")
    print()
    print("4. Run this diagnostic again")

print("=" * 60)
