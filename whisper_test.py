import whisper as w

model = w.load_model("medium")

file_to_transcribe = "Recordings_DUMP/19_May_SwarmLab_RecordWhileFlying/Keyword_LEFT_Proper_clipped.wav"

result = model.transcribe(file_to_transcribe)
print(result["text"])
