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

#ifndef __OPTIONS_H__
#define __OPTIONS_H__

#include <float.h>
#include <limits.h>
#include <glib.h>

constexpr const char* DEFAULT_POSTPROC_MODE = "detector";
constexpr gfloat DEFAULT_CONFIDENCE = 0.8;
constexpr guint DEFAULT_SKIP_FRAMES = 3;

constexpr const gchar* NO_STR = "nostr";
constexpr const gfloat NO_FLOAT = FLT_MAX;
constexpr const guint NO_UINT = UINT_MAX;

inline gboolean str_not_provided (const gchar* str) { return str == NULL || g_strcmp0 (str, NO_STR) == 0; }
inline gboolean float_not_provided (const gfloat flt) { return flt == NO_FLOAT; }
inline gboolean uint_not_provided (const guint int_) { return int_ == NO_UINT; }

typedef struct _AppOption {
    // UDP params
    gchar* ip_address;
    guint port;

    // inference params
    gchar* input;
    gchar* model;
    gfloat confidence;
    guint skip_frames;
    gchar* postproc_mode; 
    gchar* param_file;
} AppOption;

#endif // __OPTIONS_H__
