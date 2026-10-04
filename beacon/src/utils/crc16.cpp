#include "crc16.h"

uint16_t crc16_ccitt(const uint8_t* data, size_t length, uint16_t initial) {
    uint16_t crc = initial;
    for (size_t i = 0; i < length; i++) {
        crc ^= (uint16_t)data[i] << 8;
        for (uint8_t b = 0; b < 8; b++) {
            if (crc & 0x8000) crc = (crc << 1) ^ 0x1021;
            else              crc = (crc << 1);
        }
    }
    return crc;
}