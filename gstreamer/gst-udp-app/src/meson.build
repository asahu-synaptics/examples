gst_udp_sources = [
  'main.cpp',
  'gst_udp.cpp',
  'gst_udp_utils.cpp',
]

executable('gst-udp',
  gst_udp_sources,
  cpp_args: ['-DHAVE_CONFIG_H','-fpermissive'],
  include_directories: [configinc],
  dependencies : [gst_dep, gst_json_dep, udev_dep],
  install : true,
  install_tag : 'bin',
)
