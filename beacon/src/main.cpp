// ============================================================
//  BEACON v1.0 — STEP 1+2+3
//  Architecture + Radio proof of life + Protocol encode/decode.
//
//  What this firmware does:
//   - Boots ESP32 + SX1262 via LoraRadio wrapper
//   - Periodically sends BEACON_HELLO (via Beacon Packet Protocol)
//   - Listens for incoming packets, decodes them, prints RSSI/SNR
//   - Runs a local loopback self-test at boot (encode→decode)
//
//  What it does NOT do yet (STEP 4–7):
//   - ACK / Retry
//   - Routing / Neighbors
//   - Store-and-Forward (LittleFS)
//   - Mission Event generation
// ============================================================
#include <Arduino.h>

#include "config.h"
#include "utils/logger.h"
#include "utils/crc16.h"
#include "protocol/packet.h"
#include "radio/lora_radio.h"

static LoraRadio g_radio;

// ---------- Boot self-test: encode → decode → CRC ----------
static bool self_test_protocol() {
    LOG_PROTO("self-test: encode/decode loopback");

    BeaconPacket tx;
    packet_make_hello(tx, BEACON_ID, 1, 42, 1234567890UL, "SELFTEST");

    uint8_t buf[BEACON_HEADER_SIZE + MAX_PAYLOAD_BYTES + 2];
    size_t n = packet_encode(tx, buf, sizeof(buf));
    if (n == 0) {
        LOG_PROTO("self-test: encode failed");
        return false;
    }

    BeaconPacket rx;
    if (!packet_decode(buf, n, rx)) {
        LOG_PROTO("self-test: decode failed");
        return false;
    }

    if (rx.header.source_id != BEACON_ID ||
        rx.header.sequence_number != 42 ||
        rx.header.payload_length != strlen("SELFTEST")) {
        LOG_PROTO("self-test: field mismatch");
        return false;
    }

    // Corrupt one byte → expect CRC failure
    buf[BEACON_HEADER_SIZE] ^= 0xFF;
    BeaconPacket bad;
    if (packet_decode(buf, n, bad)) {
        LOG_PROTO("self-test: corrupted packet was accepted (BUG)");
        return false;
    }

    LOG_PROTO("self-test: PASS");
    return true;
}

// ---------- State ----------
static uint8_t  g_bootId    = 0;
static uint16_t g_seq       = 0;
static uint32_t g_lastHello = 0;

// ---------- Setup ----------
void setup() {
    Serial.begin(SERIAL_BAUD);
    delay(200);

    Serial.println();
    Serial.println("=================================================");
    Serial.printf( " BEACON v%d.%d.%d  node_id=%u  mission=%u\n",
                   BEACON_FW_VERSION_MAJOR, BEACON_FW_VERSION_MINOR,
                   BEACON_FW_VERSION_PATCH, (unsigned)BEACON_ID,
                   (unsigned)MISSION_ID);
    Serial.println("=================================================");

    // Boot ID = simple pseudo-random from millis + ID; real BSP can use RTC
    g_bootId = (uint8_t)((millis() ^ (BEACON_ID * 31)) & 0xFF);
    LOG_BOOT("boot_id=%u", g_bootId);

    if (!g_radio.begin()) {
        LOG_E("radio init failed — halting");
        while (true) delay(1000);
    }

    if (!self_test_protocol()) {
        LOG_E("protocol self-test failed — halting");
        while (true) delay(1000);
    }

    if (!g_radio.startReceive()) {
        LOG_E("radio RX start failed — halting");
        while (true) delay(1000);
    }
    LOG_BOOT("ready");
}

// ---------- Loop ----------
void loop() {
    // 1) Poll RX
    BeaconPacket rx;
    if (g_radio.pollReceive(rx)) {
        packet_dump(rx);
    }

    // 2) Periodic HELLO
    uint32_t now = millis();
    if (now - g_lastHello >= HELLO_INTERVAL_MS) {
        g_lastHello = now;

        BeaconPacket tx;
        char text[48];
        snprintf(text, sizeof(text),
                 "HELLO from BEACON_%02u", (unsigned)BEACON_ID);

        packet_make_hello(tx, BEACON_ID, g_bootId, g_seq++,
                          (uint32_t)(now / 1000), text);
        packet_dump(tx);

        uint8_t buf[BEACON_HEADER_SIZE + MAX_PAYLOAD_BYTES + 2];
        size_t n = packet_encode(tx, buf, sizeof(buf));
        if (n > 0) {
            LOG_TX("sending %u bytes", (unsigned)n);
            if (g_radio.transmit(buf, n)) {
                LOG_TX("done (RSSI next RX)");
            }
        }
        g_radio.startReceive();
    }

    delay(5);
}