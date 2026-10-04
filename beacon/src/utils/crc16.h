// CRC-16/CCITT-FALSE (poly 0x1021, init 0xFFFF).
// Compatible with ONA Python implementation (crc16_ccitt).
#pragma once
#include <stdint.h>
#include <stddef.h>

uint16_t crc16_ccitt(const uint8_t* data, size_t length, uint16_t initial = 0xFFFF);