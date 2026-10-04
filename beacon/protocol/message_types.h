#pragma once
#include <stdint.h>

enum MessageType : uint8_t {
    MSG_BEACON_HELLO         = 0x01,
    MSG_BEACON_STATUS        = 0x02,
    MSG_ROUTE_ADVERTISEMENT  = 0x03,
    MSG_ROUTE_REQUEST        = 0x04,
    MSG_ROUTE_REPLY          = 0x05,
    MSG_DATA_EVENT           = 0x10,
    MSG_FORWARD_DATA         = 0x11,
    MSG_DATA_ACK             = 0x12,
    MSG_E2E_ACK              = 0x13,
    MSG_HEARTBEAT            = 0x20,
    MSG_UNKNOWN              = 0xFF
};

// Message flag bits
#define FLAG_ACK_REQ        (1 << 0)
#define FLAG_PRIORITY       (1 << 1)
#define FLAG_RETRANSMIT     (1 << 2)

// Priority levels
enum Priority : uint8_t {
    PRIO_LOW       = 0,
    PRIO_NORMAL    = 1,
    PRIO_HIGH      = 2,
    PRIO_CRITICAL  = 3
};