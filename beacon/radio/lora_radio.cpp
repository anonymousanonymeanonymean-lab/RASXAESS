#include "radio/lora_radio.h"
#include "utils/logger.h"
#include <SPI.h>

LoraRadio* LoraRadio::_instance = nullptr;

LoraRadio::LoraRadio()
    : _radio(LORA_SPI_NSS_PIN, LORA_DIO1_PIN, LORA_RESET_PIN, LORA_BUSY_PIN) {
    _instance = this;
}

void LoraRadio::_isrThunk() {
    if (LoraRadio::_instance) LoraRadio::_instance->_onDio1();
}

void LoraRadio::_onDio1() {
    _rxFlag = true;
}

bool LoraRadio::begin() {
    SPI.begin(LORA_SPI_SCK_PIN, LORA_SPI_MISO_PIN,
              LORA_SPI_MOSI_PIN, LORA_SPI_NSS_PIN);

    int state = _radio.begin(
        LORA_FREQ_HZ,
        LORA_BANDWIDTH_KHZ,
        LORA_SPREADING_FACTOR,
        LORA_CODING_RATE,
        LORA_SYNC_WORD,
        LORA_TX_POWER_DBM,
        LORA_PREAMBLE_LEN,
        SX1262_USE_TCXO ? SX1262_TCXO_VOLTAGE : 0.0f
    );

    if (state != RADIOLIB_ERR_NONE) {
        LOG_RADIO("begin failed code=%d", state);
        _ready = false;
        return false;
    }

    _radio.setDio2AsRfSwitch(SX1262_USE_DIO2_AS_RF_SWITCH);
    _radio.setCRC(LORA_CRC_ON);

    pinMode(LORA_DIO1_PIN, INPUT);
    attachInterrupt(digitalPinToInterrupt(LORA_DIO1_PIN),
                    LoraRadio::_isrThunk, RISING);

    LOG_RADIO("OK freq=%.1f MHz SF=%d BW=%.1f CR=4/%d tx=%d dBm",
              LORA_FREQ_HZ, LORA_SPREADING_FACTOR,
              LORA_BANDWIDTH_KHZ, LORA_CODING_RATE, LORA_TX_POWER_DBM);
    _ready = true;
    return true;
}

bool LoraRadio::transmit(const uint8_t* data, size_t len) {
    if (!_ready) return false;
    int state = _radio.transmit((uint8_t*)data, len);
    if (state != RADIOLIB_ERR_NONE) {
        LOG_RADIO("TX failed code=%d", state);
        return false;
    }
    return true;
}

bool LoraRadio::startReceive() {
    if (!_ready) return false;
    int state = _radio.startReceive();
    if (state != RADIOLIB_ERR_NONE) {
        LOG_RADIO("startReceive failed code=%d", state);
        return false;
    }
    return true;
}

bool LoraRadio::pollReceive(BeaconPacket& pkt) {
    if (!_rxFlag) return false;
    _rxFlag = false;

    uint8_t buf[BEACON_HEADER_SIZE + MAX_PAYLOAD_BYTES + 2];
    size_t len = _radio.getPacketLength();
    if (len == 0 || len > sizeof(buf)) {
        LOG_RX("invalid length %u", (unsigned)len);
        startReceive();
        return false;
    }

    int state = _radio.readData(buf, len);
    if (state != RADIOLIB_ERR_NONE) {
        if (state == RADIOLIB_ERR_CRC_MISMATCH) LOG_RX("CRC mismatch");
        else                                     LOG_RX("error code=%d", state);
        startReceive();
        return false;
    }

    _rssi = _radio.getRSSI();
    _snr  = _radio.getSNR();

    bool ok = packet_decode(buf, len, pkt);
    if (ok) {
        LOG_RX("len=%u RSSI=%.1f dBm SNR=%.1f dB", (unsigned)len, _rssi, _snr);
    } else {
        LOG_RX("decode rejected (len=%u)", (unsigned)len);
    }
    startReceive();
    return ok;
}