
[app]

title = Thrift Shop Simulator
package.name = thriftshopsim
package.domain = id.pixelstudio
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf,otf,wav,ogg,json
source.exclude_dirs = .git,.github,bin,.buildozer,__pycache__

version = 0.1.0
requirements = python3,kivy==2.3.1

android.accept_sdk_license = True

orientation = landscape
fullscreen = 1

[buildozer]

log_level = 2
warn_on_root = 1

[app:android]

