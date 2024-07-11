from pocketsphinx import AudioFile

#Create audiofile instance


file_to_transcribe = "Recordings_DUMP/19_May_SwarmLab_RecordWhileFlying/Keyword_LEFT_Proper_clipped.wav"

audio = AudioFile(file_to_transcribe)

for phrase in audio:
    print(phrase)

