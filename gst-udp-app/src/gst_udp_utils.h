#ifndef __GST_UDP_UTILS_H__
#define __GST_UDP_UTILS_H__

#include <glib.h>
#include "gst_udp.h"

enum class InputType {
    CAMERA,
    FILE,
    RTSP,
    INVALID
};

gboolean check_model_file (const gchar* model_path);
InputType get_inp_type (const gchar* inp_src);
gboolean get_camera_devices (GArray* device_paths);
gboolean get_model_dimensions (ParameterData * params);
gboolean parse_parameters (const gchar * file_name, ParameterData * params);

#endif // __GST_UDP_UTILS_H__
