import whisper as w

model = w.load_model("base")

file_to_transcribe = "Recordings_DUMP/19_May_SwarmLab_RecordWhileFlying/denoised_audio_left_trim1.wav"

result = model.transcribe(file_to_transcribe)
print(result["text"])
