#include <I2S.h>
#include "FS.h"
#include "SD.h"
#include "SPI.h"
#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <WebSerial.h>
#include <Filters.h>
#include <Filters/IIRFilter.hpp>
#include <AH/Containers/Array.hpp>

#define RECORD_TIME   3  // seconds
#define WAV_FILE_NAME "data"
#define SAMPLE_RATE 44100U
#define SAMPLE_BITS 16
#define WAV_HEADER_SIZE 44
#define VOLUME_GAIN 2

int fileNumber = 1;
String baseFileName;
bool isRecording = false;

// Define the filter coefficients
AH::Array<float, 3> b1 = {0.98644104, -1.9542765 ,  0.98644104}; //350Hz
AH::Array<float, 3> a1 = {1.0, -1.9542765 ,  0.97288208};
AH::Array<float, 3> b2 = {0.97323993, -1.87339973,  0.97323993}; //700Hz
AH::Array<float, 3> a2 = {1.0, -1.87339973,  0.94647986};
AH::Array<float, 3> b3 = {0.94783735, -1.61632839,  0.94783735}; //1400Hz
AH::Array<float, 3> a3 = {1.0, -1.61632839,  0.89567471};


// Create IIR filter objects
IIRFilter<3, 3, float> filter1(b1, a1);
IIRFilter<3, 3, float> filter2(b2, a2);
IIRFilter<3, 3, float> filter3(b3, a3);


AsyncWebServer server(80);

void setup() {
  Serial.begin(115200);
  while (!Serial);

  // Initialize WiFi connection
  WiFi.begin("yourSSID", "yourPassword"); // Replace with your WiFi credentials
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("WiFi Connected");
  Serial.println(WiFi.localIP());

  // Initialize WebSerial with the server
  WebSerial.begin(&server);
  WebSerial.msgCallback(webSerialReceived);
  server.begin();

  I2S.setAllPins(-1, 42, 41, -1, -1);
  if (!I2S.begin(PDM_MONO_MODE, SAMPLE_RATE, SAMPLE_BITS)) {
    Serial.println("Failed to initialize I2S!");
    while (1);
  }
  if (!SD.begin(21)) {
    Serial.println("Failed to mount SD Card!");
    while (1);
  }
  Serial.println("Setup done, enter 'start <filename>' to record.");
}

void loop() {
  // Empty loop since everything is event-driven now
}

void webSerialReceived(uint8_t *data, size_t len) {
  String command = "";
  for(size_t i = 0; i < len; i++) {
    command += (char)data[i];
  }
  command.trim();
  
  if (command == "r") {
    isRecording = true;
    if (baseFileName != "") {
      String fileName = "/" + baseFileName + "." + String(fileNumber) + ".wav";
      fileNumber++;
      record_wav(fileName);
      delay(1000); // delay to avoid recording multiple files at once
      isRecording = false;
      WebSerial.println("Recording finished");
    } else {
      WebSerial.println("Set a label name before recording.");
    }
  } else {
    baseFileName = command;
    fileNumber = 1; // reset file number each time a new base file name is set
    WebSerial.println("New label set. Send 'r' to start recording.");
  }
}

void record_wav(String fileName)
{
  uint32_t sample_size = 0;
  uint32_t record_size = (SAMPLE_RATE * SAMPLE_BITS / 8) * RECORD_TIME;
  uint8_t *rec_buffer = NULL;
  Serial.printf("Start recording ...\n");
   
  File file = SD.open(fileName.c_str(), FILE_WRITE);
  // Write the header to the WAV file
  uint8_t wav_header[WAV_HEADER_SIZE];
  generate_wav_header(wav_header, record_size, SAMPLE_RATE);
  file.write(wav_header, WAV_HEADER_SIZE);

  // PSRAM malloc for recording
  rec_buffer = (uint8_t *)ps_malloc(record_size);
  if (rec_buffer == NULL) {
    Serial.printf("malloc failed!\n");
    while(1) ;
  }
  Serial.printf("Buffer: %d bytes\n", ESP.getPsramSize() - ESP.getFreePsram());

  // Start recording
  esp_i2s::i2s_read(esp_i2s::I2S_NUM_0, rec_buffer, record_size, &sample_size, portMAX_DELAY);
  if (sample_size == 0) {
    Serial.printf("Record Failed!\n");
  } else {
    Serial.printf("Record %d bytes\n", sample_size);
  }

  // Increase volume
  for (uint32_t i = 0; i < sample_size; i += SAMPLE_BITS/8) {
    (*(uint16_t *)(rec_buffer+i)) <<= VOLUME_GAIN;
  }

  // Apply filters
  for (uint32_t i = 0; i < sample_size; i += SAMPLE_BITS / 8) {
      int16_t sample = (*(int16_t *)(rec_buffer + i));
      sample = apply_notch_filters(sample);
      (*(int16_t *)(rec_buffer + i)) = sample;
  }

  // Write data to the WAV file
  WebSerial.println("Writing to the file ...\n");
  if (file.write(rec_buffer, record_size) != record_size)
    WebSerial.println("Write file Failed!\n");

  free(rec_buffer);
  file.close();
}

void generate_wav_header(uint8_t *wav_header, uint32_t wav_size, uint32_t sample_rate)
{
  // See this for reference: http://soundfile.sapp.org/doc/WaveFormat/
  uint32_t file_size = wav_size + WAV_HEADER_SIZE - 8;
  uint32_t byte_rate = SAMPLE_RATE * SAMPLE_BITS / 8;
  const uint8_t set_wav_header[] = {
    'R', 'I', 'F', 'F', // ChunkID
    file_size, file_size >> 8, file_size >> 16, file_size >> 24, // ChunkSize
    'W', 'A', 'V', 'E', // Format
    'f', 'm', 't', ' ', // Subchunk1ID
    0x10, 0x00, 0x00, 0x00, // Subchunk1Size (16 for PCM)
    0x01, 0x00, // AudioFormat (1 for PCM)
    0x01, 0x00, // NumChannels (1 channel)
    sample_rate, sample_rate >> 8, sample_rate >> 16, sample_rate >> 24, // SampleRate
    byte_rate, byte_rate >> 8, byte_rate >> 16, byte_rate >> 24, // ByteRate
    0x02, 0x00, // BlockAlign
    0x10, 0x00, // BitsPerSample (16 bits)
    'd', 'a', 't', 'a', // Subchunk2ID
    wav_size, wav_size >> 8, wav_size >> 16, wav_size >> 24, // Subchunk2Size
  };
  memcpy(wav_header, set_wav_header, sizeof(set_wav_header));
}

int16_t apply_notch_filters(int16_t input_sample) {

    float output_sample = input_sample;

    output_sample = filter1(output_sample);
    output_sample = filter2(output_sample);
    output_sample = filter3(output_sample);

    return (int16_t)output_sample;
}

float apply_notch_filter(float input_sample, const float b[], const float a[], float x[], float y[]) {
    // Shift the old samples
    for (int i = 2; i > 0; i--) {
        x[i] = x[i-1];
        y[i] = y[i-1];
    }

    // Update the current sample
    x[0] = input_sample;

    // Calculate the new output
    float output = b[0] * x[0] + b[1] * x[1] + b[2] * x[2] - a[1] * y[1] - a[2] * y[2];

    // Update the output history
    y[0] = output;

    return output;
}