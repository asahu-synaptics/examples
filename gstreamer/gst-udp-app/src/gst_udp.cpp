/*******************************************************************************
 * Copyright (c) 2023-2024 Synaptics Incorporated.

 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:

 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.

 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 ******************************************************************************/

#include <gst/app/gstappsrc.h>
#include <glib.h>
#include <glib-unix.h>
#include <json-glib/json-glib.h>
#include <glib-object.h>
#include "gst_udp.h"
#include "gst_udp_utils.h"

static CustomData udp_data;

/**
 * @brief Handle interrupt signal by sending termination message to pipeline
 */
static gboolean
handle_sigint(GstElement *pipeline) {
    GstBus *bus = gst_element_get_bus (pipeline);
    GstMessage *message = gst_message_new_application (GST_OBJECT (pipeline), gst_structure_new_empty ("GstInterrupt"));
    gst_bus_post (bus, message);
    gst_object_unref (bus);
    return G_SOURCE_REMOVE;
}

/**
 * @brief Bus callback
 */
static gboolean
bus_call (GstBus * bus, GstMessage * msg, gpointer data)
{
  GMainLoop *loop = (GMainLoop *) data;

  switch (GST_MESSAGE_TYPE (msg)) {

    case GST_MESSAGE_EOS:
        g_print ("End of stream, stopping playback\n");
        g_main_loop_quit (loop);
        break;

    case GST_MESSAGE_ERROR:{
        gchar *debug;
        GError *error;

        gst_message_parse_error (msg, &error, &debug);
        g_free (debug);

        g_printerr ("Error: %s\n", error->message);
        g_error_free (error);

        g_main_loop_quit (loop);
        break;
    }
    case GST_MESSAGE_APPLICATION: {
        const GstStructure *s = gst_message_get_structure (msg);
        if (gst_structure_has_name (s, "GstInterrupt")) {
            g_print ("\nCaught Ctrl+C, stopping playback\n");
            g_main_loop_quit (loop);
        }
        break;
    }
    default:
        break;
  }

  return TRUE;
}

/**
 * @brief Initialze UDP socket
 */
static gboolean
init_udp (UdpSocket *udp_socket, const gchar *ip_address, guint port) {
    GError *error = NULL;

    // initialize socket
    udp_socket->socket = g_socket_new (G_SOCKET_FAMILY_IPV4, G_SOCKET_TYPE_DATAGRAM, G_SOCKET_PROTOCOL_UDP, &error);
    if (!udp_socket->socket) {
        g_printerr ("Fatal: Failed to create UDP socket: %s\n", error->message);
        g_clear_error (&error);
        return FALSE;
    }

    // resolve socket address
    udp_socket->address = g_inet_socket_address_new_from_string (ip_address, port);
    if (!udp_socket->address) {
        g_printerr ("Fatal: Invalid IP address or port\n");
        g_object_unref (udp_socket->socket);
        udp_socket->socket = NULL;
        return FALSE;
    }

    return TRUE;
}

/**
 * @brief Appsink callback for new sample
 */
static GstFlowReturn
on_new_sample_from_sink (GstElement *sink, CustomData *appdata)
{
    GstSample *sample;
    GstBuffer *buffer;
    UdpSocket *udp_socket = &(appdata->udp_socket);
    GError *error = NULL;

    g_print ("Got new sample: ");

    /* Retrieve the buffer */
    g_signal_emit_by_name (sink, "pull-sample", &sample);
    if (!sample) {
        return GST_FLOW_ERROR;
    }

    buffer = gst_sample_get_buffer (sample);
    if (!buffer) {
        gst_sample_unref (sample);
        return GST_FLOW_ERROR;
    }

    // Get the JSON result from custom metadata
    GstCustomMeta *meta = gst_buffer_get_custom_meta (buffer, "GstSynapStrMeta");

    if (meta) {
        GstStructure *s = gst_custom_meta_get_structure (meta);
        const gchar *resStr = gst_structure_get_string (s, "result");
        if (resStr) {
            guint64 pts = GST_BUFFER_PTS (buffer);
            JsonParser *parser = json_parser_new ();

            if (json_parser_load_from_data(parser, resStr, -1, &error)) {
                JsonNode *root = json_parser_get_root (parser);
                JsonObject *root_obj = json_node_get_object (root);

                json_object_set_int_member (root_obj, "timestamp", (gint64) pts);

                JsonGenerator *generator = json_generator_new ();
                json_generator_set_root (generator, root);
                gchar *message = json_generator_to_data (generator, NULL);

                g_print ("sending inference results UDP (timestamp: %lu)\n", pts);
                if (g_socket_send_to (udp_socket->socket, udp_socket->address, message, strlen (message), NULL, &error) == -1) {
                    g_printerr ("Error: Failed to send data over UDP: %s\n", error->message);
                    g_clear_error (&error);
                }

                g_free (message);
                g_object_unref (generator);
            } else {
                g_printerr ("Error parsing JSON: %s\n", error->message);
                g_clear_error (&error);
            }

            g_object_unref(parser);
        }
    } else {
        g_print ("couldn't parse inference results\n");
    }

    gst_sample_unref (sample);
    return GST_FLOW_OK;
}

/**
 * @brief Cleanup Gstreamer objects
 */
static void
cleanup (guint bus_watch_id)
{
    if (bus_watch_id > 0) {
        g_source_remove (bus_watch_id);
    }
    if (udp_data.pipeline) {
        gst_object_unref (GST_OBJECT (udp_data.pipeline));
        udp_data.pipeline = NULL;
    }
    if (udp_data.loop) {
        g_main_loop_unref (udp_data.loop);
        udp_data.loop = NULL;
    }
    g_free (udp_data.params.input);
    g_free (udp_data.params.model);
    g_free (udp_data.params.postproc_mode);
}

/**
 * @brief Main function for UDP streaming
 */
int
gst_udp (AppOption *pAppOptions)
{
    GstBus *bus = NULL;
    guint bus_watch_id = 0;
    gchar *str_pipeline = NULL;
    gchar *input_elems = NULL;

    udp_data.params.input = pAppOptions->input;
    udp_data.params.model = pAppOptions->model;
    udp_data.params.confidence = pAppOptions->confidence;
    udp_data.params.skip_frames = pAppOptions->skip_frames;
    udp_data.params.postproc_mode = pAppOptions->postproc_mode;

    /* parse parameters from json input file */
    if (!str_not_provided (pAppOptions->param_file)) {
        if (!parse_parameters (pAppOptions->param_file, &udp_data.params)) {
            cleanup (bus_watch_id);
            return -1;
        }
    }

    if (str_not_provided (pAppOptions->ip_address) || uint_not_provided (pAppOptions->port) || str_not_provided (udp_data.params.input) || str_not_provided (udp_data.params.model)) {
        if (str_not_provided (pAppOptions->ip_address)) g_printerr ("Error: IP address not provided\n");
        if (uint_not_provided (pAppOptions->port)) g_printerr ("Error: port not provided\n");
        if (str_not_provided (udp_data.params.input)) g_printerr ("Error: input source not provided\n");
        if (str_not_provided (udp_data.params.model)) g_printerr ("Error: inference model not provided\n");
        g_printerr ("Missing input parameters, re-run with --help\n");
        cleanup (bus_watch_id);
        return -1;
    }

    if (str_not_provided (udp_data.params.postproc_mode)) udp_data.params.postproc_mode = g_strdup (DEFAULT_POSTPROC_MODE);
    if (float_not_provided (udp_data.params.confidence)) udp_data.params.confidence = DEFAULT_CONFIDENCE;
    if (uint_not_provided (udp_data.params.skip_frames)) udp_data.params.skip_frames = DEFAULT_SKIP_FRAMES;

    if (g_strcmp0 (g_ascii_strdown (udp_data.params.input, -1), "cam") == 0) {
        GArray *camera_paths = g_array_new (FALSE, FALSE, sizeof(gchar *));
        if (!get_camera_devices (camera_paths)) {
            g_array_free (camera_paths, TRUE);
            cleanup (bus_watch_id);
            return -1;
        }
        udp_data.params.input = g_strdup (g_array_index (camera_paths, gchar *, 0));
        for (guint i = 0; i < camera_paths->len; i++) {
            gchar *element = g_array_index (camera_paths, gchar *, i);
            g_free (element);
        }
        g_array_free (camera_paths, TRUE);
    }

    /* check if model is valid */
    if (!check_model_file (udp_data.params.model)) {
        cleanup (bus_watch_id);
        return -1;
    }

    /* extract input dimensions from model file */
    if (!get_model_dimensions (&udp_data.params)) {
        cleanup (bus_watch_id);
        return -1;
    }
    
    g_print ("\n---------------------------------------\n");
    g_print ("Application Parameters\n");
    g_print ("---------------------------------------\n");
    g_print ("Receiver address:     %s:%d\n", pAppOptions->ip_address, pAppOptions->port);
    g_print ("Input source:         %s\n", udp_data.params.input);
    g_print ("Inference Model:      %s (%dx%d)\n", udp_data.params.model, udp_data.params.model_width, udp_data.params.model_height);
    g_print ("Confidence:           %.1f\n", udp_data.params.confidence);
    g_print ("Skip frames:          %d\n", udp_data.params.skip_frames);
    g_print ("Post Processing Mode: %s\n", udp_data.params.postproc_mode);
    g_print ("---------------------------------------\n\n");

    /* initialize UDP socket*/
    if (!init_udp (&udp_data.udp_socket, pAppOptions->ip_address, pAppOptions->port)) {
        cleanup (bus_watch_id);
        return -1;
    }

    /* initialize gstreamer */
    gst_init (NULL, NULL);

    /* main loop */
    udp_data.loop = g_main_loop_new (NULL, FALSE);

    switch (get_inp_type (udp_data.params.input)) {
        case InputType::CAMERA:
            input_elems = g_strdup_printf (
                "v4l2src device=%s ! video/x-raw,framerate=30/1,format=YUY2,width=640,height=480",
                udp_data.params.input
            );
            break;
        case InputType::FILE:
            input_elems = g_strdup_printf (
                "filesrc location=%s ! qtdemux name=demux demux.video_0 ! h264parse ! avdec_h264",
                udp_data.params.input
            );
            break;
        case InputType::RTSP:
            input_elems = g_strdup_printf (
                "rtspsrc location=%s latency=2000 ! rtpjitterbuffer ! rtph264depay wait-for-keyframe=true ! video/x-h264",
                udp_data.params.input
            );
            break;
        case InputType::INVALID:
        default:
            g_printerr ("Error: Invalid input source: %s\n", udp_data.params.input);
            cleanup (bus_watch_id);
            return -1;
    }

    /* Create the pipeline for udp transmission */
    str_pipeline = g_strdup_printf (
        "%s ! videoconvert ! videoscale ! video/x-raw,width=%d,height=%d,format=RGB "
        "! queue ! synapinfer model=%s mode=%s frameinterval=%d output=json "
        "! appsink name=synap_sink ",
        input_elems, udp_data.params.model_width, udp_data.params.model_height, udp_data.params.model, udp_data.params.postproc_mode, udp_data.params.skip_frames
    );
    g_free (input_elems);

    udp_data.pipeline = gst_parse_launch (str_pipeline, NULL);
    g_assert (udp_data.pipeline);
    g_free (str_pipeline);

    /* we add a message handler */
    bus = gst_pipeline_get_bus (GST_PIPELINE (udp_data.pipeline));
    bus_watch_id = gst_bus_add_watch (bus, bus_call, udp_data.loop);
    gst_object_unref (bus);

    /* Configure signals */
    g_print ("Configure appsink\n");
    udp_data.appsink =
        gst_bin_get_by_name (GST_BIN (udp_data.pipeline), "synap_sink");
    g_assert (udp_data.appsink);
    g_object_set (G_OBJECT (udp_data.appsink), "emit-signals", TRUE, "sync", TRUE,
        NULL);
    g_signal_connect (udp_data.appsink, "new-sample",
        G_CALLBACK (on_new_sample_from_sink), &udp_data);
    g_unix_signal_add (SIGINT, (GSourceFunc) handle_sigint, udp_data.pipeline);

    /* Set pipeline to playing state */
    gst_element_set_state (udp_data.pipeline, GST_STATE_PLAYING);
    GstStateChangeReturn ret;
    GstState state;
    GstState pending;
    ret = gst_element_get_state (udp_data.pipeline, &state, &pending, 5 * GST_SECOND);
    if (ret == GST_STATE_CHANGE_FAILURE || state != GST_STATE_PLAYING) {
        g_printerr ("Failed to set pipeline to PLAYING. Current state: %d\n", state);
        cleanup(bus_watch_id);
        return -1;
    }

    /* Run loop */
    g_print ("Running...\n");
    g_main_loop_run (udp_data.loop);

    /* Clean-up */
    gst_element_set_state (udp_data.pipeline, GST_STATE_NULL);
    cleanup(bus_watch_id);

    return 0;
}
