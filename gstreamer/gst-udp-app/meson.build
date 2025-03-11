project('gst-udp', 'cpp',
  version : '1.0',
  meson_version : '>= 0.62',
  default_options : ['warning_level=1', 'buildtype=debugoptimized']
)

gst_dep = dependency('gstreamer-1.0', version : '>= 1.0.0')
gst_json_dep = dependency('json-glib-1.0')
udev_dep = dependency('gudev-1.0')

# Include directories
configinc = include_directories('src')

# Subdirectories
subdir('src')
