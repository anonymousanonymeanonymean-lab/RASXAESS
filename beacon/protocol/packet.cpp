#include "protocol/packet.h"
#include "utils/crc16.h"
#include "utils/logger.h"

#include <string.h>

size_t packet_total_length(const BeaconPacket& pkt) {
    return BEACON_HEADER_SIZE + pkt.header.payload_length + 2; // +CRC16
}

size_t packet_encode(const BeaconPacket& pkt, uint8_t* out_buf, size_t out_cap) {
    if (pkt.header.payload_length > MAX_PAYLOAD_BYTES) {
        LOG_PROTO("encode: payload too large (%u)", pkt.header.payload_length);
        return 0;
    }

    const size_t body_len = BEACON_HEADER_SIZE + pkt.header.payload_length;
    const size_t total    = body_len + 2;
    if (total > out_cap) {
        LOG_PROTO("encode: buffer too small (%u < %u)",
                  (unsigned)out_cap, (unsigned)total);
        return 0;
    }

    memcpy(out_buf, &pkt.header, BEACON_HEADER_SIZE);
    if (pkt.header.payload_length > 0) {
        memcpy(out_buf + BEACON_HEADER_SIZE, pkt.payload, pkt.header.payload_length);
    }

    uint16_t crc = crc16_ccitt(out_buf, body_len, 0xFFFF);
    out_buf[body_len + 0] = (uint8_t)(crc & 0xFF);         // little-endian CRC
    out_buf[body_len + 1] = (uint8_t)((crc >> 8) & 0xFF);

    log_hex("ENCODE", out_buf, total);
    return total;
}

bool packet_decode(const uint8_t* raw, size_t raw_len, BeaconPacket& pkt) {
    if (raw_len < BEACON_HEADER_SIZE + 2) {
        LOG_PROTO("decode: too short (%u)", (unsigned)raw_len);
        return false;
    }

    BeaconHeader hdr;
    memcpy(&hdr, raw, BEACON_HEADER_SIZE);

    if (hdr.protocol_version != BEACON_PROTOCOL_VERSION) {
        LOG_PROTO("decode: bad version 0x%02X", hdr.protocol_version);
        return false;
    }
    if (hdr.payload_length > MAX_PAYLOAD_BYTES) {
        LOG_PROTO("decode: payload len invalid (%u)", hdr.payload_length);
        return false;
    }

    const size_t body_len = BEACON_HEADER_SIZE + hdr.payload_length;
    if (raw_len < body_len + 2) {
        LOG_PROTO("decode: truncated");
        return false;
    }

    uint16_t rx_crc = (uint16_t)raw[body_len] | ((uint16_t)raw[body_len + 1] << 8);
    uint16_t calc_crc = crc16_ccitt(raw, body_len, 0xFFFF);
    if (rx_crc != calc_crc) {
        LOG_PROTO("decode: CRC mismatch  rx=0x%04X calc=0x%04X", rx_crc, calc_crc);
        return false;
    }

    pkt.header = hdr;
    if (hdr.payload_length > 0) {
        memcpy(pkt.payload, raw + BEACON_HEADER_SIZE, hdr.payload_length);
    }

    LOG_PROTO("decode: OK type=0x%02X src=%u boot=%u seq=%u",
              hdr.message_type, hdr.source_id, hdr.boot_id, hdr.sequence_number);
    return true;
}

void packet_make_hello(BeaconPacket& pkt,
                       uint8_t source_id,
                       uint8_t boot_id,
                       uint16_t seq,
                       uint32_t timestamp,
                       const char* text) {
    memset(&pkt, 0, sizeof(pkt));
    pkt.header.protocol_version = BEACON_PROTOCOL_VERSION;
    pkt.header.message_type     = MSG_BEACON_HELLO;
    pkt.header.mission_id       = MISSION_ID;
    pkt.header.source_id        = source_id;
    pkt.header.dest_id          = BROADCAST_ID;
    pkt.header.boot_id          = boot_id;
    pkt.header.sequence_number  = seq;
    pkt.header.timestamp        = timestamp;
    pkt.header.hop_count        = 0;
    pkt.header.ttl              = DEFAULT_TTL;
    pkt.header.flags            = 0;
    pkt.header.payload_length   = 0;

    if (text != nullptr) {
        size_t len = strlen(text);
        if (len > MAX_PAYLOAD_BYTES) len = MAX_PAYLOAD_BYTES;
        memcpy(pkt.payload, text, len);
        pkt.header.payload_length = (uint8_t)len;
    }
}

void packet_dump(const BeaconPacket& pkt) {
    if (LOG_LEVEL < LOG_DEBUG) return;
    Serial.printf("[D] PACKET  ver=%u type=0x%02X mid=%u src=%u dst=%u boot=%u seq=%u ts=%lu hop=%u ttl=%u flags=0x%02X len=%u\n",
        pkt.header.protocol_version,
        pkt.header.message_type,
        pkt.header.mission_id,
        pkt.header.source_id,
        pkt.header.dest_id,
        pkt.header.boot_id,
        pkt.header.sequence_number,
        (unsigned long)pkt.header.timestamp,
        pkt.header.hop_count,
        pkt.header.ttl,
        pkt.header.flags,
        pkt.header.payload_length);
    if (pkt.header.payload_length > 0) {
        log_hex("PAYLOAD", pkt.payload, pkt.header.payload_length);
    }
}