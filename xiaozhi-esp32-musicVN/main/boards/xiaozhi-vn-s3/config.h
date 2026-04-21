#ifndef _BOARD_CONFIG_H_
#define _BOARD_CONFIG_H_

#include <driver/gpio.h>

// ============================================================
// Board: ESP32-S3 N16R8
// Sơ đồ đấu nối: Xiaozhi AI-IoT Việt Nam
// ============================================================

#define AUDIO_INPUT_SAMPLE_RATE  16000
#define AUDIO_OUTPUT_SAMPLE_RATE 16000

// Dùng chế độ Simplex: Mic (INMP441) và Loa (MAX98357A) dùng I2S riêng
#define AUDIO_I2S_METHOD_SIMPLEX

// --- Mic INMP441 (I2S Input) ---
// SCK  → GPIO 5
// WS   → GPIO 4
// SD   → GPIO 6
#define AUDIO_I2S_MIC_GPIO_SCK  GPIO_NUM_5
#define AUDIO_I2S_MIC_GPIO_WS   GPIO_NUM_4
#define AUDIO_I2S_MIC_GPIO_DIN  GPIO_NUM_6

// --- Loa MAX98357A (I2S Output) ---
// BCLK → GPIO 15
// LRC  → GPIO 16
// DIN  → GPIO 7
#define AUDIO_I2S_SPK_GPIO_BCLK GPIO_NUM_15
#define AUDIO_I2S_SPK_GPIO_LRCK GPIO_NUM_16
#define AUDIO_I2S_SPK_GPIO_DOUT GPIO_NUM_7

// --- Nút bấm ---
// Wakeup (gọi robot) → GPIO 0
// Volume (+)         → GPIO 40
// Volume (-)         → GPIO 39
// Power              → GPIO 38
#define BOOT_BUTTON_GPIO        GPIO_NUM_0
#define VOLUME_UP_BUTTON_GPIO   GPIO_NUM_40
#define VOLUME_DOWN_BUTTON_GPIO GPIO_NUM_39
#define POWER_BUTTON_GPIO       GPIO_NUM_38

// --- LED tích hợp: board này không có LED, GetLed() trả về nullptr ---

// --- Màn hình TFT 1.54 inch ST7789 240x240 (SPI) ---
// SCL (Clock) → GPIO 9
// SDA (MOSI)  → GPIO 10
// RES (Reset) → GPIO 18
// DC          → GPIO 8
// CS          → GPIO 14
// BL          → GPIO 13
#define DISPLAY_CLK_PIN         GPIO_NUM_9
#define DISPLAY_MOSI_PIN        GPIO_NUM_10
#define DISPLAY_RST_PIN         GPIO_NUM_18
#define DISPLAY_DC_PIN          GPIO_NUM_8
#define DISPLAY_CS_PIN          GPIO_NUM_14
#define DISPLAY_BACKLIGHT_PIN   GPIO_NUM_13

// --- Thông số màn hình ST7789 240x240 ---
#define DISPLAY_WIDTH           240
#define DISPLAY_HEIGHT          240
#define DISPLAY_MIRROR_X        false
#define DISPLAY_MIRROR_Y        false
#define DISPLAY_SWAP_XY         false
#define DISPLAY_INVERT_COLOR    true
#define DISPLAY_OFFSET_X        0
#define DISPLAY_OFFSET_Y        0
#define DISPLAY_BACKLIGHT_OUTPUT_INVERT false

#endif // _BOARD_CONFIG_H_
