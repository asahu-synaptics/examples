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

#include <gst/gst.h>
#include <glib.h>
#include "gst_udp.h"
#include "gst_udp_utils.h"
#include "options.h"

static gboolean parse_options (int argc, char *argv[], AppOption *pAppOptions)
{
    GOptionContext *ctx;
    GError *err = NULL;

    GOptionEntry entries[] = {
        { "ipaddress", 'a', 0, G_OPTION_ARG_STRING, &pAppOptions->ip_address,
            "Receiver UDP IP addresss", "STRING" },
        { "port", 'p', 0, G_OPTION_ARG_INT, &pAppOptions->port,
            "Receiver UDP port", "INT" },
        { "input", 'i', 0, G_OPTION_ARG_STRING, &pAppOptions->input,
            "Video input (camera/file/RTSP)", "STRING" },
        { "model", 'm', 0, G_OPTION_ARG_STRING, &pAppOptions->model,
            "Inference model (.synap)", "STRING" },
        { "confidence", 'c', 0, G_OPTION_ARG_DOUBLE, &pAppOptions->confidence,
            "Detection confidence level (default: 0.8)", "FLOAT"},
        { "skipframes", 's', 0, G_OPTION_ARG_INT, &pAppOptions->skip_frames,
            "How many frames to skip between each inference (default: 3)", "INT" },
        { "postproc", 'r', 0, G_OPTION_ARG_STRING, &pAppOptions->postproc_mode,
            "Postprocessing mode: classifier/detector (default: detector)", "STRING" },
        { "paramfile", 'f', 0, G_OPTION_ARG_STRING, &pAppOptions->param_file,
            "Parameters JSON file", "STRING" },
        { NULL },
    };

    ctx = g_option_context_new ("GStreamer Synaptics UDP Demo");
    g_option_context_add_main_entries (ctx, entries, NULL);
    g_option_context_add_group (ctx, gst_init_get_option_group ());
    if (!g_option_context_parse (ctx, &argc, &argv, &err)) {
        g_print ("Failed to initialize: %s\n", err->message);
        g_clear_error (&err);
        g_option_context_free (ctx);
        return FALSE;
    }

    g_option_context_free (ctx);
    return TRUE;
}

static void cleanup(AppOption *pAppOptions) {
    g_free (pAppOptions->param_file);
    g_free (pAppOptions->input);
    g_free (pAppOptions->model);
    g_free (pAppOptions->ip_address);
}

int main (int argc, char *argv[])
{
    AppOption appOptions;

    // Initialize options
    appOptions.ip_address       = g_strdup (NO_STR);
    appOptions.port             = NO_UINT;
    appOptions.input            = g_strdup (NO_STR);
    appOptions.model            = g_strdup (NO_STR);
    appOptions.confidence       = NO_FLOAT;
    appOptions.skip_frames      = NO_UINT;
    appOptions.postproc_mode    = g_strdup (NO_STR);
    appOptions.param_file       = g_strdup (NO_STR);

    if (!parse_options (argc, argv, &appOptions)) {
        g_print ("Invalid Options - Please run with --help\n");
        cleanup (&appOptions);
        return -1;
    }

    gst_udp (&appOptions);
    return 0;
}

