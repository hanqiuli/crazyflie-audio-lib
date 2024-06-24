#include <crazyflie-demo-swarmlab_inferencing.h>
#include <I2S.h>
#include <ArduinoBLE.h>

#define SAMPLE_RATE 16000U
#define SAMPLE_BITS 16
#define LED_BUILT_IN 21

/** Audio buffers, pointers and selectors */
typedef struct {
    int16_t *buffer;
    uint8_t buf_ready;
    uint32_t buf_count;
    uint32_t n_samples;
} inference_t;

static inference_t inference;
static const uint32_t sample_buffer_size = 2048;
static signed short sampleBuffer[sample_buffer_size];
static bool debug_nn = false; // Set this to true to see e.g. features generated from the raw signal
static bool record_status = true;

/* Function to send BLE notifications */
void sendBLENotification(const char* label);

BLEService inferenceService("1101");
BLECharacteristic labelCharacteristic("2101", BLERead | BLENotify, 20);

/**
 * @brief      Arduino setup function
 */
void setup() {
    Serial.begin(115200);
    while (!Serial);
    Serial.println("Edge Impulse Inferencing Demo");

    pinMode(LED_BUILT_IN, OUTPUT); // Set the pin as output
    digitalWrite(LED_BUILT_IN, HIGH); // Turn off
    
    I2S.setAllPins(-1, 42, 41, -1, -1);
    if (!I2S.begin(PDM_MONO_MODE, SAMPLE_RATE, SAMPLE_BITS)) {
        Serial.println("Failed to initialize I2S!");
        while (1);
    }
    
    ei_printf("Inferencing settings:\n");
    ei_printf("\tInterval: ");
    ei_printf_float((float)EI_CLASSIFIER_INTERVAL_MS);
    ei_printf(" ms.\n");
    ei_printf("\tFrame size: %d\n", EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE);
    ei_printf("\tSample length: %d ms.\n", EI_CLASSIFIER_RAW_SAMPLE_COUNT / 16);
    ei_printf("\tNo. of classes: %d\n", sizeof(ei_classifier_inferencing_categories) / sizeof(ei_classifier_inferencing_categories[0]));

    ei_printf("\nStarting continuous inference in 2 seconds...\n");
    ei_sleep(2000);

    if (microphone_inference_start(EI_CLASSIFIER_RAW_SAMPLE_COUNT) == false) {
        ei_printf("ERR: Could not allocate audio buffer (size %d), this could be due to the window length of your model\r\n", EI_CLASSIFIER_RAW_SAMPLE_COUNT);
        return;
    }

    ei_printf("Recording...\n");

    // Initialize BLE
    if (!BLE.begin()) {
        Serial.println("Starting BLE failed!");
        while (1);
    }

    BLE.setLocalName("InferenceDevice");
    BLE.setAdvertisedService(inferenceService);
    inferenceService.addCharacteristic(labelCharacteristic);
    BLE.addService(inferenceService);

    BLE.advertise();
    Serial.println("Bluetooth device active, waiting for connections...");
}

/**
 * @brief      Arduino main function. Runs the inferencing loop.
 */
void loop() {
    BLEDevice central = BLE.central();
    if (central) {
        bool m = microphone_inference_record();
        if (!m) {
            ei_printf("ERR: Failed to record audio...\n");
            return;
        }

        signal_t signal;
        signal.total_length = EI_CLASSIFIER_RAW_SAMPLE_COUNT;
        signal.get_data = &microphone_audio_signal_get_data;
        ei_impulse_result_t result = { 0 };

        EI_IMPULSE_ERROR r = run_classifier(&signal, &result, debug_nn);
        if (r != EI_IMPULSE_OK) {
            ei_printf("ERR: Failed to run classifier (%d)\n", r);
            return;
        }

        int pred_index = 0;     // Initialize pred_index
        float pred_value = 0;   // Initialize pred_value
        String pred_label = ""; // Initialize pred_label

        // print the predictions
        ei_printf("Predictions ");
        ei_printf("(DSP: %d ms., Classification: %d ms., Anomaly: %d ms.)",
            result.timing.dsp, result.timing.classification, result.timing.anomaly);
        ei_printf(": \n");
        for (size_t ix = 0; ix < EI_CLASSIFIER_LABEL_COUNT; ix++) {
            ei_printf("    %s: ", result.classification[ix].label);
            ei_printf_float(result.classification[ix].value);
            ei_printf("\n");

            if (result.classification[ix].value > pred_value){
               pred_index = ix;
               pred_value = result.classification[ix].value;
               pred_label = result.classification[ix].label;
          }
        }
        // // Display inference result
        // if (pred_label == "left" && pred_value > 0.97){
        //     digitalWrite(LED_BUILT_IN, HIGH); // Turn on
        // }
        // else if(pred_label == "right" && pred_value > 0.97){
        //     digitalWrite(LED_BUILT_IN, LOW); // Turn off
        // }
        // else{
        //     digitalWrite(LED_BUILT_IN, LOW); // Turn off
        // }

        sendBLENotification(pred_label.c_str());

    #if EI_CLASSIFIER_HAS_ANOMALY == 1
        ei_printf("    anomaly score: ");
        ei_printf_float(result.anomaly);
        ei_printf("\n");
    #endif
    }
}

void sendBLENotification(const char* label) {
    if (labelCharacteristic.subscribed()) {
        labelCharacteristic.writeValue(label);
    }
}

static void audio_inference_callback(uint32_t n_bytes) {
    for(int i = 0; i < n_bytes>>1; i++) {
        inference.buffer[inference.buf_count++] = sampleBuffer[i];

        if(inference.buf_count >= inference.n_samples) {
            inference.buf_count = 0;
            inference.buf_ready = 1;
        }
    }
}

static void capture_samples(void* arg) {
    const int32_t i2s_bytes_to_read = (uint32_t)arg;
    size_t bytes_read = i2s_bytes_to_read;

    while (record_status) {
        esp_i2s::i2s_read(esp_i2s::I2S_NUM_0, (void*)sampleBuffer, i2s_bytes_to_read, &bytes_read, 100);

        if (bytes_read <= 0) {
            ei_printf("Error in I2S read : %d", bytes_read);
        } else {
            if (bytes_read < i2s_bytes_to_read) {
                ei_printf("Partial I2S read");
            }

            // scale the data (otherwise the sound is too quiet)
            for (int x = 0; x < i2s_bytes_to_read/2; x++) {
                sampleBuffer[x] = (int16_t)(sampleBuffer[x]) * 2;
            }

            if (record_status) {
                audio_inference_callback(i2s_bytes_to_read);
            } else {
                break;
            }
        }
    }
    vTaskDelete(NULL);
}

static bool microphone_inference_start(uint32_t n_samples) {
    inference.buffer = (int16_t *)malloc(n_samples * sizeof(int16_t));

    if(inference.buffer == NULL) {
        return false;
    }

    inference.buf_count  = 0;
    inference.n_samples  = n_samples;
    inference.buf_ready  = 0;

    ei_sleep(100);

    record_status = true;

    xTaskCreate(capture_samples, "CaptureSamples", 1024 * 32, (void*)sample_buffer_size, 10, NULL);

    return true;
}

static bool microphone_inference_record(void) {
    bool ret = true;

    while (inference.buf_ready == 0) {
        delay(10);
    }

    inference.buf_ready = 0;
    return ret;
}

static int microphone_audio_signal_get_data(size_t offset, size_t length, float *out_ptr) {
    numpy::int16_to_float(&inference.buffer[offset], out_ptr, length);
    return 0;
}

static void microphone_inference_end(void) {
    free(sampleBuffer);
    ei_free(inference.buffer);
}

#if !defined(EI_CLASSIFIER_SENSOR) || EI_CLASSIFIER_SENSOR != EI_CLASSIFIER_SENSOR_MICROPHONE
#error "Invalid model for current sensor."
#endif