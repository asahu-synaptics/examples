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

#ifndef __GST_UDP_H__
#define __GST_UDP_H__

#include <gst/gst.h>
#include <gio/gio.h>
#include "options.h"

/**
 * @brief Structure for parameters in json input
 */
typedef struct _ParameterData
{
    gchar *input;
    gchar *model;
    guint model_width;
    guint model_height;
    gfloat confidence;
    guint skip_frames;
    gchar *postproc_mode;
} ParameterData;

/**
 * @brief UDP socket parameters
 */
typedef struct _UdpSocket
{
    GSocket *socket;
    GSocketAddress *address;
    guint port;
} UdpSocket;

/**
 * @brief Custom application data
 */
typedef struct _CustomData
{
    GstElement *pipeline;
    GstElement *appsink;
    GMainLoop *loop;

    ParameterData params;
    UdpSocket udp_socket;
} CustomData;

int gst_udp (AppOption *pAppOption);

#endif // __GST_UDP_H__
