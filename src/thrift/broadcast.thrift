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
namespace c_glib edu.rice.bold.service
namespace cpp edu.rice.bold.service
namespace java edu.rice.bold.service


/**
 * thrift lets you do typedefs to get pretty names for your types. standard
 * c style here.
 */
typedef string ServerID

typedef string BcdID
typedef i32 BcdSize


/**
 * thrift also lets you define constants for use across languages. complex
 * types and structs are specified using json notation.
 */

/**
 * you can define enums, which are just 32 bit integers. values are optional
 * and start at 1 if not supplied, c style again.
 */
enum PushReplyCmd {
  PUSH, POSTPONE, DENY
}


/**
 * structs are the basic complex data structures. they are comprised of fields
 * which each have an integer identifier, a type, a symbolic name, and an
 * optional default value.
 *
 * fields can be declared "optional", which ensures they will not be included
 * in the serialized output if they aren't set.  note that this requires some
 * manual management in some languages.
 */
struct BcdInfo {
  1:BcdID id,
  2:BcdSize size
}

struct PushReply {
  1:i32 xid,
  2:PushReplyCmd cmd
}


/**
 * structs can also be exceptions, if they are nasty.
 */


/**
 * ahh, now onto the cool part, defining a service. services just need a name
 * and can optionally inherit from another service using the extends keyword.
 */
service BcdService {

  /**
   * a method definition looks like c code. it has a return type, arguments,
   * and optionally a list of exceptions that it may throw. note that argument
   * lists and exception lists are specified using the exact same syntax as
   * field lists in struct or exception definitions.
   */
   PushReply push(1:ServerID master, 2:set<ServerID> slaves, 3:BcdInfo data)

   /**
    * this method has a oneway modifier. that means the client only makes
    * a request and does not listen for any response at all. oneway methods
    * must be void.
    */
    oneway void unpush(1:i32 xid)
}

/**
 * that just about covers the basics. take a look in the test/ folder for more
 * detailed examples. after you run this file, your generated code shows up
 * in folders with names gen-<language>. the generated code isn't too scary
 * to look at. it even has pretty indentation.
 */