/*
 * licensed to the apache software foundation (asf) under one
 * or more contributor license agreements. see the notice file
 * distributed with this work for additional information
 * regarding copyright ownership. the asf licenses this file
 * to you under the apache license, version 2.0 (the
 * "license"); you may not use this file except in compliance
 * with the license. you may obtain a copy of the license at
 *
 *   http://www.apache.org/licenses/license-2.0
 *
 * unless required by applicable law or agreed to in writing,
 * software distributed under the license is distributed on an
 * "as is" basis, without warranties or conditions of any
 * kind, either express or implied. see the license for the
 * specific language governing permissions and limitations
 * under the license.
 */

# thrift tutorial
# mark slee (mcslee@facebook.com)
#
# this file aims to teach you how to use thrift, in a .thrift file. neato. the
# first thing to notice is that .thrift files support standard shell comments.
# this lets you make your thrift file executable and include your thrift build
# step on the top line. and you can place comments like this anywhere you like.
#
# before running this file, you will need to have installed the thrift compiler
# into /usr/local/bin.

/**
 * the first thing to know about are types. the available types in thrift are:
 *
 *  bool        boolean, one byte
 *  i8 (byte)   signed 8-bit integer
 *  i16         signed 16-bit integer
 *  i32         signed 32-bit integer
 *  i64         signed 64-bit integer
 *  double      64-bit floating point value
 *  string      string
 *  binary      blob (byte array)
 *  map<t1,t2>  map from one type to another
 *  list<t1>    ordered list of one type
 *  set<t1>     set of unique elements of one type
 *
 * did you also notice that thrift supports c style comments?
 */

// just in case you were wondering... yes. we support simple c comments too.

/**
 * thrift files can reference other thrift files to include common struct
 * and service definitions. these are found using the current path, or by
 * searching relative to any paths specified with the -i compiler flag.
 *
 * included objects are accessed using the name of the .thrift file as a
 * prefix. i.e. shared.sharedobject
 */

/**
 * thrift files can namespace, package, or prefix their output in various
 * target languages.
 */
namespace c_glib edu.rice.republic.amif
namespace cpp edu.rice.republic.amif
namespace java edu.rice.republic.amif

typedef i64 Bytes
typedef string AppID
typedef string DataID
typedef string ServerID

typedef string RequestID // locally generated id for each each transfer
typedef i32 ResponseID // unique number for each request

enum ResponseType {
    ACCEPT, DENY
}

typedef i64 ResponseCode

struct Request {
    1:RequestID rqid,
    2:AppID aid,
    3:DataID did,
    4:Bytes datasize,
    5:Bytes remainingsize,
    6:ServerID sender,
    7:set<ServerID> receivers
}

struct Response {
    1:RequestID rqid,
    2:ResponseID rpid,
    3:ResponseType type,
    4:ResponseCode code,
    5:Bytes acceptedsize
}

struct Release {
    1:RequestID rqid,
    2:ResponseID rpid
}

service AgentManagerInterface {
    Response request(1:Request rq)
    oneway void release(1:Release rl)
}