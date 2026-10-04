// ============================================================
//  Beacon Packet Protocol v1.0 — Binary layout
//  Little-endian, packed. Header = 17 bytes + payload + CRC16.
// ============================================================
#pragma once
#include <stdint.h>
#include <stddef.h>

#include "config.h"
#include "protocol/message_types.h"

#pragma pack(push, 1)
struct BeaconHeader {
    uint8_t  protocol_version;   // offset 0
    uint8_t  message_type;       // offset 1
    uint16_t mission_id;         // offset 2
    uint8_t  source_id;          // offset 4
    uint8_t  dest_id;            // offset 5
    uint8_t  boot_id;            // offset 6
    uint16_t sequence_number;    // offset 7
    uint32_t timestamp;          // offset 9
    uint8_t  hop_count;          // offset 13
    uint8_t  ttl;                // offset 14
    uint8_t  flags;              // offset 15
    uint8_t  payload_length;     // offset 16
};                               // total 17 bytes
#pragma pack(pop)

constexpr size_t BEACON_HEADER_SIZE = sizeof(BeaconHeader); // 17

struct BeaconPacket {
    BeaconHeader header;
    uint8_t      payload[MAX_PAYLOAD_BYTES];
};

// ---- Encode ----
// Serialize packet into out_buf. Returns total length in bytes, or 0 on error.
size_t packet_encode(const BeaconPacket& pkt, uint8_t* out_buf, size_t out_cap);

// ---- Decode ----
// Parse raw bytes into pkt. Returns true on success (incl. CRC check).
bool packet_decode(const uint8_t* raw, size_t raw_len, BeaconPacket& pkt);

// ---- Helpers ----
// Build a HELLO packet with a short text payload.
void packet_make_hello(BeaconPacket& pkt,
                       uint8_t source_id,
                       uint8_t boot_id,
                       uint16_t seq,
                       uint32_t timestamp,
                       const char* text);

// Compute total on-wire length of a packet.
size_t packet_total_length(const BeaconPacket& pkt);

// Debug dump
void packet_dump(const BeaconPacket& pkt);