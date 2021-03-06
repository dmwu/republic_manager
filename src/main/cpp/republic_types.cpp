/**
 * Autogenerated by Thrift Compiler (0.9.3)
 *
 * DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
 *  @generated
 */
#include "republic_types.h"

#include <algorithm>
#include <ostream>

#include <thrift/TToString.h>

namespace edu { namespace rice { namespace republic { namespace amif {

int _kResponseTypeValues[] = {
  ResponseType::ACCEPT,
  ResponseType::DENY
};
const char* _kResponseTypeNames[] = {
  "ACCEPT",
  "DENY"
};
const std::map<int, const char*> _ResponseType_VALUES_TO_NAMES(::apache::thrift::TEnumIterator(2, _kResponseTypeValues, _kResponseTypeNames), ::apache::thrift::TEnumIterator(-1, NULL, NULL));


Request::~Request() throw() {
}


void Request::__set_rid(const RequestID& val) {
  this->rid = val;
}

void Request::__set_aid(const AppID& val) {
  this->aid = val;
}

void Request::__set_did(const DataID& val) {
  this->did = val;
}

void Request::__set_datasize(const Bytes val) {
  this->datasize = val;
}

void Request::__set_remainingsize(const Bytes val) {
  this->remainingsize = val;
}

void Request::__set_sender(const ServerID& val) {
  this->sender = val;
}

void Request::__set_receivers(const std::set<ServerID> & val) {
  this->receivers = val;
}

uint32_t Request::read(::apache::thrift::protocol::TProtocol* iprot) {

  apache::thrift::protocol::TInputRecursionTracker tracker(*iprot);
  uint32_t xfer = 0;
  std::string fname;
  ::apache::thrift::protocol::TType ftype;
  int16_t fid;

  xfer += iprot->readStructBegin(fname);

  using ::apache::thrift::protocol::TProtocolException;


  while (true)
  {
    xfer += iprot->readFieldBegin(fname, ftype, fid);
    if (ftype == ::apache::thrift::protocol::T_STOP) {
      break;
    }
    switch (fid)
    {
      case 1:
        if (ftype == ::apache::thrift::protocol::T_STRING) {
          xfer += iprot->readString(this->rid);
          this->__isset.rid = true;
        } else {
          xfer += iprot->skip(ftype);
        }
        break;
      case 2:
        if (ftype == ::apache::thrift::protocol::T_STRING) {
          xfer += iprot->readString(this->aid);
          this->__isset.aid = true;
        } else {
          xfer += iprot->skip(ftype);
        }
        break;
      case 3:
        if (ftype == ::apache::thrift::protocol::T_STRING) {
          xfer += iprot->readString(this->did);
          this->__isset.did = true;
        } else {
          xfer += iprot->skip(ftype);
        }
        break;
      case 4:
        if (ftype == ::apache::thrift::protocol::T_I64) {
          xfer += iprot->readI64(this->datasize);
          this->__isset.datasize = true;
        } else {
          xfer += iprot->skip(ftype);
        }
        break;
      case 5:
        if (ftype == ::apache::thrift::protocol::T_I64) {
          xfer += iprot->readI64(this->remainingsize);
          this->__isset.remainingsize = true;
        } else {
          xfer += iprot->skip(ftype);
        }
        break;
      case 6:
        if (ftype == ::apache::thrift::protocol::T_STRING) {
          xfer += iprot->readString(this->sender);
          this->__isset.sender = true;
        } else {
          xfer += iprot->skip(ftype);
        }
        break;
      case 7:
        if (ftype == ::apache::thrift::protocol::T_SET) {
          {
            this->receivers.clear();
            uint32_t _size0;
            ::apache::thrift::protocol::TType _etype3;
            xfer += iprot->readSetBegin(_etype3, _size0);
            uint32_t _i4;
            for (_i4 = 0; _i4 < _size0; ++_i4)
            {
              ServerID _elem5;
              xfer += iprot->readString(_elem5);
              this->receivers.insert(_elem5);
            }
            xfer += iprot->readSetEnd();
          }
          this->__isset.receivers = true;
        } else {
          xfer += iprot->skip(ftype);
        }
        break;
      default:
        xfer += iprot->skip(ftype);
        break;
    }
    xfer += iprot->readFieldEnd();
  }

  xfer += iprot->readStructEnd();

  return xfer;
}

uint32_t Request::write(::apache::thrift::protocol::TProtocol* oprot) const {
  uint32_t xfer = 0;
  apache::thrift::protocol::TOutputRecursionTracker tracker(*oprot);
  xfer += oprot->writeStructBegin("Request");

  xfer += oprot->writeFieldBegin("rid", ::apache::thrift::protocol::T_STRING, 1);
  xfer += oprot->writeString(this->rid);
  xfer += oprot->writeFieldEnd();

  xfer += oprot->writeFieldBegin("aid", ::apache::thrift::protocol::T_STRING, 2);
  xfer += oprot->writeString(this->aid);
  xfer += oprot->writeFieldEnd();

  xfer += oprot->writeFieldBegin("did", ::apache::thrift::protocol::T_STRING, 3);
  xfer += oprot->writeString(this->did);
  xfer += oprot->writeFieldEnd();

  xfer += oprot->writeFieldBegin("datasize", ::apache::thrift::protocol::T_I64, 4);
  xfer += oprot->writeI64(this->datasize);
  xfer += oprot->writeFieldEnd();

  xfer += oprot->writeFieldBegin("remainingsize", ::apache::thrift::protocol::T_I64, 5);
  xfer += oprot->writeI64(this->remainingsize);
  xfer += oprot->writeFieldEnd();

  xfer += oprot->writeFieldBegin("sender", ::apache::thrift::protocol::T_STRING, 6);
  xfer += oprot->writeString(this->sender);
  xfer += oprot->writeFieldEnd();

  xfer += oprot->writeFieldBegin("receivers", ::apache::thrift::protocol::T_SET, 7);
  {
    xfer += oprot->writeSetBegin(::apache::thrift::protocol::T_STRING, static_cast<uint32_t>(this->receivers.size()));
    std::set<ServerID> ::const_iterator _iter6;
    for (_iter6 = this->receivers.begin(); _iter6 != this->receivers.end(); ++_iter6)
    {
      xfer += oprot->writeString((*_iter6));
    }
    xfer += oprot->writeSetEnd();
  }
  xfer += oprot->writeFieldEnd();

  xfer += oprot->writeFieldStop();
  xfer += oprot->writeStructEnd();
  return xfer;
}

void swap(Request &a, Request &b) {
  using ::std::swap;
  swap(a.rid, b.rid);
  swap(a.aid, b.aid);
  swap(a.did, b.did);
  swap(a.datasize, b.datasize);
  swap(a.remainingsize, b.remainingsize);
  swap(a.sender, b.sender);
  swap(a.receivers, b.receivers);
  swap(a.__isset, b.__isset);
}

Request::Request(const Request& other7) {
  rid = other7.rid;
  aid = other7.aid;
  did = other7.did;
  datasize = other7.datasize;
  remainingsize = other7.remainingsize;
  sender = other7.sender;
  receivers = other7.receivers;
  __isset = other7.__isset;
}
Request& Request::operator=(const Request& other8) {
  rid = other8.rid;
  aid = other8.aid;
  did = other8.did;
  datasize = other8.datasize;
  remainingsize = other8.remainingsize;
  sender = other8.sender;
  receivers = other8.receivers;
  __isset = other8.__isset;
  return *this;
}
void Request::printTo(std::ostream& out) const {
  using ::apache::thrift::to_string;
  out << "Request(";
  out << "rid=" << to_string(rid);
  out << ", " << "aid=" << to_string(aid);
  out << ", " << "did=" << to_string(did);
  out << ", " << "datasize=" << to_string(datasize);
  out << ", " << "remainingsize=" << to_string(remainingsize);
  out << ", " << "sender=" << to_string(sender);
  out << ", " << "receivers=" << to_string(receivers);
  out << ")";
}


Response::~Response() throw() {
}


void Response::__set_rid(const ResponseID& val) {
  this->rid = val;
}

void Response::__set_type(const ResponseType::type val) {
  this->type = val;
}

void Response::__set_code(const ResponseCode val) {
  this->code = val;
}

void Response::__set_acceptedsize(const Bytes val) {
  this->acceptedsize = val;
}

uint32_t Response::read(::apache::thrift::protocol::TProtocol* iprot) {

  apache::thrift::protocol::TInputRecursionTracker tracker(*iprot);
  uint32_t xfer = 0;
  std::string fname;
  ::apache::thrift::protocol::TType ftype;
  int16_t fid;

  xfer += iprot->readStructBegin(fname);

  using ::apache::thrift::protocol::TProtocolException;


  while (true)
  {
    xfer += iprot->readFieldBegin(fname, ftype, fid);
    if (ftype == ::apache::thrift::protocol::T_STOP) {
      break;
    }
    switch (fid)
    {
      case 1:
        if (ftype == ::apache::thrift::protocol::T_STRING) {
          xfer += iprot->readString(this->rid);
          this->__isset.rid = true;
        } else {
          xfer += iprot->skip(ftype);
        }
        break;
      case 2:
        if (ftype == ::apache::thrift::protocol::T_I32) {
          int32_t ecast9;
          xfer += iprot->readI32(ecast9);
          this->type = (ResponseType::type)ecast9;
          this->__isset.type = true;
        } else {
          xfer += iprot->skip(ftype);
        }
        break;
      case 3:
        if (ftype == ::apache::thrift::protocol::T_I64) {
          xfer += iprot->readI64(this->code);
          this->__isset.code = true;
        } else {
          xfer += iprot->skip(ftype);
        }
        break;
      case 4:
        if (ftype == ::apache::thrift::protocol::T_I64) {
          xfer += iprot->readI64(this->acceptedsize);
          this->__isset.acceptedsize = true;
        } else {
          xfer += iprot->skip(ftype);
        }
        break;
      default:
        xfer += iprot->skip(ftype);
        break;
    }
    xfer += iprot->readFieldEnd();
  }

  xfer += iprot->readStructEnd();

  return xfer;
}

uint32_t Response::write(::apache::thrift::protocol::TProtocol* oprot) const {
  uint32_t xfer = 0;
  apache::thrift::protocol::TOutputRecursionTracker tracker(*oprot);
  xfer += oprot->writeStructBegin("Response");

  xfer += oprot->writeFieldBegin("rid", ::apache::thrift::protocol::T_STRING, 1);
  xfer += oprot->writeString(this->rid);
  xfer += oprot->writeFieldEnd();

  xfer += oprot->writeFieldBegin("type", ::apache::thrift::protocol::T_I32, 2);
  xfer += oprot->writeI32((int32_t)this->type);
  xfer += oprot->writeFieldEnd();

  xfer += oprot->writeFieldBegin("code", ::apache::thrift::protocol::T_I64, 3);
  xfer += oprot->writeI64(this->code);
  xfer += oprot->writeFieldEnd();

  xfer += oprot->writeFieldBegin("acceptedsize", ::apache::thrift::protocol::T_I64, 4);
  xfer += oprot->writeI64(this->acceptedsize);
  xfer += oprot->writeFieldEnd();

  xfer += oprot->writeFieldStop();
  xfer += oprot->writeStructEnd();
  return xfer;
}

void swap(Response &a, Response &b) {
  using ::std::swap;
  swap(a.rid, b.rid);
  swap(a.type, b.type);
  swap(a.code, b.code);
  swap(a.acceptedsize, b.acceptedsize);
  swap(a.__isset, b.__isset);
}

Response::Response(const Response& other10) {
  rid = other10.rid;
  type = other10.type;
  code = other10.code;
  acceptedsize = other10.acceptedsize;
  __isset = other10.__isset;
}
Response& Response::operator=(const Response& other11) {
  rid = other11.rid;
  type = other11.type;
  code = other11.code;
  acceptedsize = other11.acceptedsize;
  __isset = other11.__isset;
  return *this;
}
void Response::printTo(std::ostream& out) const {
  using ::apache::thrift::to_string;
  out << "Response(";
  out << "rid=" << to_string(rid);
  out << ", " << "type=" << to_string(type);
  out << ", " << "code=" << to_string(code);
  out << ", " << "acceptedsize=" << to_string(acceptedsize);
  out << ")";
}


Release::~Release() throw() {
}


void Release::__set_rid(const ResponseID& val) {
  this->rid = val;
}

uint32_t Release::read(::apache::thrift::protocol::TProtocol* iprot) {

  apache::thrift::protocol::TInputRecursionTracker tracker(*iprot);
  uint32_t xfer = 0;
  std::string fname;
  ::apache::thrift::protocol::TType ftype;
  int16_t fid;

  xfer += iprot->readStructBegin(fname);

  using ::apache::thrift::protocol::TProtocolException;


  while (true)
  {
    xfer += iprot->readFieldBegin(fname, ftype, fid);
    if (ftype == ::apache::thrift::protocol::T_STOP) {
      break;
    }
    switch (fid)
    {
      case 1:
        if (ftype == ::apache::thrift::protocol::T_STRING) {
          xfer += iprot->readString(this->rid);
          this->__isset.rid = true;
        } else {
          xfer += iprot->skip(ftype);
        }
        break;
      default:
        xfer += iprot->skip(ftype);
        break;
    }
    xfer += iprot->readFieldEnd();
  }

  xfer += iprot->readStructEnd();

  return xfer;
}

uint32_t Release::write(::apache::thrift::protocol::TProtocol* oprot) const {
  uint32_t xfer = 0;
  apache::thrift::protocol::TOutputRecursionTracker tracker(*oprot);
  xfer += oprot->writeStructBegin("Release");

  xfer += oprot->writeFieldBegin("rid", ::apache::thrift::protocol::T_STRING, 1);
  xfer += oprot->writeString(this->rid);
  xfer += oprot->writeFieldEnd();

  xfer += oprot->writeFieldStop();
  xfer += oprot->writeStructEnd();
  return xfer;
}

void swap(Release &a, Release &b) {
  using ::std::swap;
  swap(a.rid, b.rid);
  swap(a.__isset, b.__isset);
}

Release::Release(const Release& other12) {
  rid = other12.rid;
  __isset = other12.__isset;
}
Release& Release::operator=(const Release& other13) {
  rid = other13.rid;
  __isset = other13.__isset;
  return *this;
}
void Release::printTo(std::ostream& out) const {
  using ::apache::thrift::to_string;
  out << "Release(";
  out << "rid=" << to_string(rid);
  out << ")";
}

}}}} // namespace
