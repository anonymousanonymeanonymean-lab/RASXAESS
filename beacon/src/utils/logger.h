// Lightweight structured logger over Serial.
#pragma once
#include <Arduino.h>
#include "config.h"

#define LOG_E(fmt, ...) do { if (LOG_LEVEL >= LOG_ERROR) Serial.printf("[E] " fmt "\n", ##__VA_ARGS__); } while (0)
#define LOG_W(fmt, ...) do { if (LOG_LEVEL >= LOG_WARN)  Serial.printf("[W] " fmt "\n", ##__VA_ARGS__); } while (0)
#define LOG_I(fmt, ...) do { if (LOG_LEVEL >= LOG_INFO)  Serial.printf("[I] " fmt "\n", ##__VA_ARGS__); } while (0)
#define LOG_D(fmt, ...) do { if (LOG_LEVEL >= LOG_DEBUG) Serial.printf("[D] " fmt "\n", ##__VA_ARGS__); } while (0)

// Tagged loggers (prefixes readable dans le moniteur)
#define LOG_RX(fmt, ...) LOG_I("RX: "  fmt, ##__VA_ARGS__)
#define LOG_TX(fmt, ...) LOG_I("TX: "  fmt, ##__VA_ARGS__)
#define LOG_RADIO(fmt, ...) LOG_I("RADIO: " fmt, ##__VA_ARGS__)
#define LOG_PROTO(fmt, ...) LOG_I("PROTO: " fmt, ##__VA_ARGS__)
#define LOG_BOOT(fmt, ...) LOG_I("BOOT: " fmt, ##__VA_ARGS__)

// Hex dump utility
inline void log_hex(const char* tag, const uint8_t* buf, size_t len) {
    if (LOG_LEVEL < LOG_DEBUG) return;
    Serial.printf("[D] %s (%u bytes):", tag, (unsigned)len);
    for (size_t i = 0; i < len; i++) {
        if (i % 16 == 0) Serial.printf("\n      ");
        Serial.printf("%02X ", buf[i]);
    }
    Serial.println();
}