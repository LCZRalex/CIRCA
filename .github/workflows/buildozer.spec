[app]

# (str) Title of your application
title = Circa

# (str) Package name
package.name = circa

# (str) Package domain (needed for android/ios packaging)
package.domain = org.circa

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,wav

# (list) List of inclusions using pattern matching
source.include_patterns = license,data/*.json

# (str) Application versioning (method 1)
version = 0.1

# (list) Application requirements
requirements = python3,kivy,numpy,opencv-python-headless,face_recognition,playsound,pyjnius

# (list) Permissions
android.permissions = WRITE_EXTERNAL_STORAGE

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

#
# iOS specific
#

# (str) Name of the certificate to use for signing the debug version
ios.codesign.debug = "iPhone Developer: <lastname> <firstname> (<hexstring>)"

# (str) Name of the certificate to use for signing the release version
ios.codesign.release = "iPhone Distribution: <lastname> <firstname> (<hexstring>)"

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .ipa) storage
bin_dir = ./bin
