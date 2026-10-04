// Thin wrapper over RadioLib SX1262, exposing an ONA-friendly API.
#pragma once
#include <Arduino.h>
#include <RadioLib.h>
#include "config.h"
#include "protocol/packet.h"

class LoraRadio {
public:
    LoraRadio();

    // Initialize SPI + SX1262. Returns true on success.
    bool begin();

    // Blocking transmit of raw bytes. Returns true on success.
    bool transmit(const uint8_t* data, size_t len);

    // Enter continuous RX mode (non-blocking).
    bool startReceive();

    // Called from ISR or polled: if a full packet has been received,
    // decode it into `pkt`. Returns true if a valid packet was processed.
    bool pollReceive(BeaconPacket& pkt);

    // Last received RSSI / SNR (valid after pollReceive returns true).
    float lastRssi() const { return _rssi; }
    float lastSnr()  const { return _snr;  }

    bool isReady() const { return _ready; }

private:
    SX1262  _radio;
    bool    _ready = false;
    volatile bool _rxFlag = false;
    float   _rssi = 0.0f;
    float   _snr  = 0.0f;

    static void _isrThunk();
    static LoraRadio* _instance;
    void _onDio1();
};