#include <json-glib/json-glib.h>
#include <gudev/gudev.h>
#include <fstream>
#include <libudev.h>
#include <glib.h>
#include <glib/gstdio.h>
#include "gst_udp_utils.h"

const gchar* MODEL_META_FILE = "model.json";

static gboolean
run_cmd_no_output (const gchar* cmd, GError* error)
{
    gchar* stdout = NULL;
    gchar* stderr = NULL;
    gboolean status = g_spawn_command_line_sync (cmd, &stdout, &stderr, NULL, &error);
    g_free (stdout);
    g_free (stderr);
    return status;
}

/**
 * @brief Check if model file is valid
 */
gboolean
check_model_file (const gchar* model_path)
{
    if (!g_file_test (model_path, G_FILE_TEST_EXISTS) || !g_str_has_suffix (model_path, ".synap")) {
        g_printerr ("Fatal: Invalid SyNAP model file '%s'\n", model_path);
        return FALSE;
    }

    GError* error = NULL;
    gchar* model_test_cmd = g_strdup_printf ("synap_cli -m %s random", model_path);
    if (!run_cmd_no_output (model_test_cmd, error)) {
        g_printerr ("Fatal: Invalid SyNAP model: %s", error->message);
        g_error_free (error);
        g_free (model_test_cmd);
        return FALSE;
    }
    g_free (model_test_cmd);

    return TRUE;
}

/**
 * @brief Removes all extracted model objects
 */
static void
cleanup_model_metadata (gchar* json_path, JsonParser* parser)
{
    g_object_unref (parser);
    g_remove (json_path);
    g_free (json_path);
}

/**
 * @brief Determine input source type
 */
InputType 
get_inp_type(const gchar* inp_src)
{
    if (g_str_has_prefix(inp_src, "/dev/video")) {
        return InputType::CAMERA;
    }
    else if (g_str_has_prefix(inp_src, "rtsp://")) {
        return InputType::RTSP;
    }

    std::ifstream file(inp_src);
    if (file.good()) {
        return InputType::FILE;
    }

    return InputType::INVALID;
}

/**
 * @brief Get list of connected camera devices
 */
gboolean
get_camera_devices (GArray* device_paths)
{
    gchar *contents = NULL;
    GError *error = NULL;

    const gchar *subsystems[] = { "video4linux", NULL };
    GUdevClient *client = g_udev_client_new (subsystems);
    if (!client) {
        g_printerr ("Error: Failed to create GUdev client\n");
        return FALSE;
    }

    GList *devices = g_udev_client_query_by_subsystem (client, "video4linux");
    for (GList *l = devices; l != NULL; l = l->next) {
        GUdevDevice *device = (GUdevDevice *) l->data;

        if (g_strcmp0 (g_udev_device_get_property (device, "ID_BUS"), "usb") == 0) {
            const gchar *sys_path = g_udev_device_get_sysfs_path (device);
            if (sys_path != NULL) {
                gchar *index_path = g_strdup_printf ("%s/index", sys_path);
                if (g_file_get_contents (index_path, &contents, NULL, &error)) {
                    guint index = (guint) g_ascii_strtoull (contents, NULL, 10);
                    g_free (contents);

                    if (index == 0){
                        const gchar *dev_node = g_udev_device_get_device_file (device);
                        if (dev_node != NULL) {
                            gchar* camera_path = strdup (dev_node);
                            g_array_append_val (device_paths, camera_path);
                        }
                    }
                } else {
                    g_printerr ("Error: Failed to read device file: %s\n", error->message);
                    g_clear_error (&error);
                }
                g_free (index_path);
            }
        }
    }

    g_list_free_full (devices, g_object_unref);
    g_object_unref (client);

    return TRUE;
}

/**
 * @brief Extract model input dimensions
 */
gboolean
get_model_dimensions (ParameterData * params)
{
    GError* error = NULL;

    // extract metadata file "0/model.json" from .synap file
    gchar* command = g_strdup_printf ("unzip -j -o %s 0/%s -d %s", params->model, MODEL_META_FILE, g_get_tmp_dir());
    if (!run_cmd_no_output (command, error)) {
        g_printerr ("Error: Failed to extract model JSON file: %s\n", error->message);
        g_error_free (error);
        g_free (command);
        return FALSE;
    }
    g_free (command);

    gchar* json_path = g_build_path (G_DIR_SEPARATOR_S, g_get_tmp_dir(), MODEL_META_FILE, NULL);
    JsonParser* parser = json_parser_new ();
    if (!json_parser_load_from_file (parser, json_path, &error)) {
        g_printerr ("Error parsing JSON: %s\n", error->message);
        g_error_free (error);
        cleanup_model_metadata (json_path, parser);
        return FALSE;
    }
    
    JsonNode* root = json_parser_get_root (parser);
    JsonObject* metadata = json_node_get_object (root);
    JsonObject* inputs = json_object_get_object_member (metadata, "Inputs");
    if (!inputs || json_object_get_size (inputs) != 1) {
        g_printerr ("Error: Multiple input models not supported.\n");
        cleanup_model_metadata (json_path, parser);
        return FALSE;
    }

    // extract width and height based on format and shape fields
    JsonObject* input_info = json_object_get_object_member (inputs, (gchar*) json_object_get_members (inputs)->data);
    const gchar* format = json_object_get_string_member (input_info, "format");
    JsonArray* shape = json_object_get_array_member (input_info, "shape");

    if (g_strcmp0(format, "nhwc") == 0) {
        params->model_width = (guint) json_array_get_int_element (shape, 2);
        params->model_height = (guint) json_array_get_int_element (shape, 1);
    } else if (g_strcmp0(format, "nchw") == 0) {
        params->model_width = (guint) json_array_get_int_element (shape, 3);
        params->model_height = (guint) json_array_get_int_element (shape, 2);
    } else {
        g_printerr ("Error: Invalid metadata format \"%s\".\n", format);
        cleanup_model_metadata (json_path, parser);
        return FALSE;
    }

    cleanup_model_metadata (json_path, parser);
    
    return TRUE;
}

/**
 * @brief Parse parameters from json file
 */
gboolean 
parse_parameters (const gchar * file_name, ParameterData * params)
{
    JsonParser *parser;
    GError *error = NULL;

    parser = json_parser_new ();
    g_assert (JSON_IS_PARSER (parser));
    if (!json_parser_load_from_file (parser, file_name, &error)) {
        g_printerr ("Fatal: Failed to load JSON file '%s': %s\n", file_name, error->message);
        g_clear_error (&error);
        return FALSE;
    }

    JsonNode *root = json_parser_get_root (parser);
    JsonObject *object = json_node_get_object (root);
    if (!object) {
        g_printerr ("Fatal: Invalid JSON structure\n");
        return FALSE;
    }

    if (str_not_provided (params->input)) params->input = g_strdup (json_object_get_string_member_with_default (object, "input", NO_STR));
    if (str_not_provided (params->model)) params->model = g_strdup (json_object_get_string_member_with_default (object, "model", NO_STR));
    if (float_not_provided (params->confidence)) params->confidence = json_object_get_double_member_with_default (object, "confidence", NO_FLOAT);
    if (uint_not_provided (params->skip_frames)) params->skip_frames = json_object_get_int_member_with_default (object, "skipframes", NO_UINT);
    if (str_not_provided (params->postproc_mode)) params->postproc_mode = g_strdup (json_object_get_string_member_with_default (object, "postprocmode", NO_STR));
    
    g_object_unref (parser);
    return TRUE;
}
