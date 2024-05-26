#include <I2S.h>
#include "FS.h"
#include "SD.h"
#include "SPI.h"
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <WiFi.h>
#include <vector>

// Constants
#define RECORD_TIME   10  // seconds, The maximum value is 240
#define SAMPLE_RATE 16000U
#define SAMPLE_BITS 16
#define WAV_HEADER_SIZE 44
#define VOLUME_GAIN 2

// BLE UUIDs
#define SERVICE_UUID "12345678-1234-5678-1234-56789abcdef0"
#define CHARACTERISTIC_UUID "abcdef01-2345-6789-abcd-ef0123456789"
#define NOTIFY_CHARACTERISTIC_UUID "12345678-1234-5678-1234-56789abcdeff"

// Variables
int fileNumber = 1;
String baseFileName;
bool isRecording = false;
BLEServer* pServer = nullptr;
BLECharacteristic* pCharacteristic = nullptr;
BLECharacteristic* pNotifyCharacteristic = nullptr;
bool deviceConnected = false;

// BLE Callbacks
class MyServerCallbacks: public BLEServerCallbacks {
  void onConnect(BLEServer* pServer) {
    deviceConnected = true;
  }

  void onDisconnect(BLEServer* pServer) {
    deviceConnected = false;
    pServer->startAdvertising();  // Restart advertising on disconnect
  }
};

class MyCallbacks: public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic* pCharacteristic) {
    std::string value = pCharacteristic->getValue();
    if (value == "rec") {
      isRecording = true;
    } else {
      baseFileName = value.c_str();
      fileNumber = 1; // reset file number each time a new base file name is set
      Serial.printf("Send rec for starting recording label \n");
    }
  }
};

// LMS Filter Class
class LMSFilter {
public:
    LMSFilter(size_t filter_order, float mu) : filter_order(filter_order), mu(mu) {
        weights.resize(filter_order, 0.0f);
    }

    float filter(const std::vector<int16_t>& input_signal, size_t index) {
        float y = 0.0f;
        for (size_t i = 0; i < filter_order; ++i) {
            y += weights[i] * input_signal[index - i];
        }
        float e = input_signal[index] - y;
        for (size_t i = 0; i < filter_order; ++i) {
            weights[i] += 2 * mu * e * input_signal[index - i];
        }
        return e;
    }

    size_t get_filter_order() const {
        return filter_order;
    }

private:
    size_t filter_order;
    float mu;
    std::vector<float> weights;
};

// Initialize LMS Filter
LMSFilter lmsFilter(32, 0.01f);

// Function prototypes
void record_wav(String fileName);
void generate_wav_header(uint8_t *wav_header, uint32_t wav_size, uint32_t sample_rate);

void setup() {
  Serial.begin(115200);
  while (!Serial) ;

  I2S.setAllPins(-1, 42, 41, -1, -1);
  if (!I2S.begin(PDM_MONO_MODE, SAMPLE_RATE, SAMPLE_BITS)) {
    Serial.println("Failed to initialize I2S!");
    while (1) ;
  }
  if (!SD.begin(21)){
    Serial.println("Failed to mount SD Card!");
    while (1) ;
  }
  
  BLEDevice::init("ESP32_BLE");
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());

  BLEService *pService = pServer->createService(SERVICE_UUID);
  pCharacteristic = pService->createCharacteristic(
                      CHARACTERISTIC_UUID,
                      BLECharacteristic::PROPERTY_READ |
                      BLECharacteristic::PROPERTY_WRITE
                    );
  pCharacteristic->setCallbacks(new MyCallbacks());

  pNotifyCharacteristic = pService->createCharacteristic(
                           NOTIFY_CHARACTERISTIC_UUID,
                           BLECharacteristic::PROPERTY_NOTIFY
                         );
  pNotifyCharacteristic->addDescriptor(new BLE2902());

  pService->start();

  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->start();
}

void loop() {
  if (deviceConnected) {
    // BLE connection established, commands will be handled by BLE callbacks
  }
  
  if (isRecording && baseFileName != "") {
    String fileName = "/" + baseFileName + "." + String(fileNumber) + ".wav";
    fileNumber++;
    record_wav(fileName);
    delay(1000); // delay to avoid recording multiple files at once
    isRecording = false;

    // Notify the client that recording is complete
    std::string notification = "Recording complete: " + std::string(fileName.c_str());
    pNotifyCharacteristic->setValue(notification);
    pNotifyCharacteristic->notify();
  }
}

void record_wav(String fileName) {
    uint32_t sample_size = 0;
    uint32_t record_size = (SAMPLE_RATE * SAMPLE_BITS / 8) * RECORD_TIME;
    uint8_t *rec_buffer = (uint8_t *)ps_malloc(record_size);
    if (!rec_buffer) {
        Serial.println("Memory allocation failed!");
        return;
    }

    Serial.println("Start recording...");
    esp_i2s::i2s_read(esp_i2s::I2S_NUM_0, rec_buffer, record_size, &sample_size, portMAX_DELAY);

    File file = SD.open(fileName.c_str(), FILE_WRITE);
    if (!file) {
        Serial.println("Failed to open file for writing!");
        free(rec_buffer);
        return;
    }

    uint8_t wav_header[44];
    generate_wav_header(wav_header, record_size, SAMPLE_RATE);
    file.write(wav_header, 44);

    std::vector<int16_t> primary_signal(sample_size / 2);
    memcpy(primary_signal.data(), rec_buffer, sample_size);
    std::vector<int16_t> filtered_signal(sample_size / 2);

    for (size_t i = 0; i < sample_size / 2; i++) {
        if (i >= lmsFilter.get_filter_order()) {
            filtered_signal[i] = lmsFilter.filter(primary_signal, i);
        } else {
            filtered_signal[i] = primary_signal[i];
        }
    }

    for (uint32_t i = 0; i < sample_size; i += SAMPLE_BITS / 8) {
        (*(uint16_t *)(rec_buffer + i)) <<= VOLUME_GAIN;
    }

    Serial.println("Writing to the file...");
    if (file.write((uint8_t*)filtered_signal.data(), sample_size) != sample_size) {
        Serial.println("Write file failed!");
    }

    free(rec_buffer);
    file.close();
    Serial.println("Recording complete.");
}

void generate_wav_header(uint8_t *header, uint32_t size, uint32_t sample_rate) {
    memcpy(header, "RIFF", 4);
    *((uint32_t *)(header + 4)) = size + 36;
    memcpy(header + 8, "WAVEfmt ", 8);
    *((uint32_t *)(header + 16)) = 16;
    *((uint16_t *)(header + 20)) = 1;
    *((uint16_t *)(header + 22)) = 1;
    *((uint32_t *)(header + 24)) = sample_rate;
    *((uint32_t *)(header + 28)) = sample_rate * 2;
    *((uint16_t *)(header + 32)) = 2;
    *((uint16_t *)(header + 34)) = 16;
    memcpy(header + 36, "data", 4);
    *((uint32_t *)(header + 40)) = size;
}
