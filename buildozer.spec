
[app]

title = Thrift Shop Simulator
package.name = thriftshopsim
package.domain = id.pixelstudio

source.dir = .
source.include_exts = py,kv,png,jpg,jpeg,json,ttf,otf,wav,ogg
source.exclude_dirs = .git,.github,bin,__pycache__

version = 0.1.0
requirements = python3==3.12.10,hostpython3==3.12.10,kivy==2.3.1

p4a.branch = master

orientation = landscape
fullscreen = 1

android.accept_sdk_license = True
android.minapi = 24
android.api = 35

[buildozer]

log_level = 2
warn_on_root = 1
