from flask import Flask, render_template

import os
import json
import time
from google.cloud import texttospeech, translate_v2, texttospeech_v1
import pandas as pd
import requests


app = Flask(__name__)



##################################### UNIVERSITIES CODE #########################################################


status = {'0' : 'Rejected', '1' : 'Accepted', '2' : 'Waiting', '3' : 'Interested'}

####################        MAIN        ##########################


def main():

    result = os.popen("curl -X POST -H \"Authorization: Bearer \"ya29.A0AVA9y1urldH4F29Q7cAaE6SDEChnFFIC2z71wxJXTPIHN7Y3nnbU_5GiI3lDmM6Z1IZdUhpGr27djzTht6Yb7CaIbEgbqwu6cDyc4-QUtQ6JftxhP8LnDW_BLk0aXIv671PBgwgqmUcUzl5zsFUyZidcXthSYSRnHf0n6wYUNnWUtBVEFTQVRBU0ZRRTY1ZHI4cHJ6dU5vNTFzNjJJdU9ZM0x2aF9QUQ0173 -H \"Content-Type: application/json; charset=utf-8\" https://us-central1-aiplatform.googleapis.com/v1/projects/gcp-summer-course-2022/locations/us-central1/endpoints/1442339353316556800:predict -d \"@request_main.json" ).read()
    #time.sleep(10)

    result = json.loads(result)
    print(result)
    
    #print("\nScores:\n")
    scores = result['predictions'][0]['scores']
    #print(scores)
    #print("\nClasses:\n")
    classes = result['predictions'][0]['classes']
    #print(classes)

    print("\n")
    result = dict(zip(classes, scores))
    #print(result)

    result_status = max(zip(result.values(), result.keys()))[1]
    main_result_status = status[str(result_status)]
    print("\nYour Status : " + main_result_status)

    speech = "This is language is what you have desired to hear your results in. We hope you can understand this language well. Your details have been submitted and was run through our model on the Google Cloud Platform. Hope all the details you have submitted are correct. We hope you did not have any difficulties navigating through our form. This prediction is an approximate. Hope this doesn't affect your morale. So, here are your results."
    accepted = "Congragulations. According to our model, we have predicted that you will mostly get accepted into your desired university. Good luck."
    rejected = "So sorry to inform you that our model predicted that you might get rejected from this university. But don't you worry, we have few suggestions on where you can apply so that you could get accepted there. We remind you that this is only a prediction through a model. Here is the list of universities you could apply to."
    waitlisted = "Sorry to tell you that, according to our model, you might not get accepted in this university. But, you might get waitlisted. So, don't lose your hopes. We have a few suggestions on where you can apply so that you could get accepted there. We remind you that this is only a prediction through a model. Here is the list of universities you could apply to."
    end = "Thank you for using our prediction model. Hope you are satisfied with the results. "


    if result_status == '0':
        speech = speech + rejected
    elif result_status == '1':
        speech = speech + accepted
    elif result_status == '2':
        speech = speech + waitlisted



    ####################        OTHERS        ##########################
    unis = []
    if result_status != '1' :
        

        for i in range(35):

            other_result = os.popen("curl -X POST -H \"Authorization: Bearer \"ya29.A0AVA9y1urldH4F29Q7cAaE6SDEChnFFIC2z71wxJXTPIHN7Y3nnbU_5GiI3lDmM6Z1IZdUhpGr27djzTht6Yb7CaIbEgbqwu6cDyc4-QUtQ6JftxhP8LnDW_BLk0aXIv671PBgwgqmUcUzl5zsFUyZidcXthSYSRnHf0n6wYUNnWUtBVEFTQVRBU0ZRRTY1ZHI4cHJ6dU5vNTFzNjJJdU9ZM0x2aF9QUQ0173 -H \"Content-Type: application/json; charset=utf-8\" https://us-central1-aiplatform.googleapis.com/v1/projects/gcp-summer-course-2022/locations/us-central1/endpoints/1442339353316556800:predict -d \"@request_other" + str(i) + ".json" ).read()
            time.sleep(10)

            other_result = json.loads(other_result)

            print(other_result)
            #print("\nScores:\n")
            scores = other_result['predictions'][0]['scores']
            #print(scores)
            #print("\nClasses:\n")
            classes = other_result['predictions'][0]['classes']
            #print(classes)

            print("\n")
            other_result = dict(zip(classes, scores))
            #print(other_result)

            result_status = max(zip(other_result.values(), other_result.keys()))[1]
            print("\nYour Status : " + status[str(result_status)])
            
            if result_status == '1':      
                data = open("request_other" + str(i) + ".json")
                data = json.load(data)
                
                unis.append(data["instances"][0]["university"])
        print(unis)
        
        speech_unis = " ".join(unis)
        speech = speech + speech_unis


    speech = speech + end
    
    return [main_result_status, speech, unis]





####################################################### TRANSLATE + TTS CODE ####################################################


def tts(speech, lang_code, lang_name, target):

    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r"gcp-summer-course-2022-cbd365ff9ce5.json"
    translate_client = translate_v2.Client()

    text = speech


    output = translate_client.translate(text, target_language=target)



    #------------------------------------------------------------------------------------------------------------------------------------------------------


    # Instantiates a client
    tts_client = texttospeech.TextToSpeechClient()
    """
    voice_list = []
    for voice in tts_client.list_voices().voices:
        voice_list.append([voice.name, voice.language_codes[0], voice.ssml_gender, voice.natural_sample_rate_hertz])
    df_voice_list = pd.DataFrame(voice_list, columns=['name', 'language code', 'ssml gender', 'hertz rate']).to_csv('tts_sample.csv', index=False)
    """
    # Set the text input to be synthesized

    synthesis_input = texttospeech.SynthesisInput(text=output['translatedText'])


    #voice = texttospeech.VoiceSelectionParams(language_code=lang_code, ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)

    
    voice = texttospeech.VoiceSelectionParams(
        name=lang_name, language_code=lang_code
        # name='vi-VN-Wavenet-D', language_code="vi-VN"
    )

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        # https://cloud.google.com/text-to-speech/docs/reference/rpc/google.cloud.texttospeech.v1#audioencoding
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = tts_client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    # The response's audio_content is binary.
    with open(r"C:\Users\Sravya Yepuri\Desktop\GCP-Summer-Course-2022\Project\flask app\final\static\audio_"+target+".mp3", "wb") as out:
        # Write the response to the output file.
        out.write(response.audio_content)
        print("Audio content written to file 'audio_"+target+".mp3'")


#------------------------------------------------------------------------------------------------------------------------------------------------------









@app.route('/')

def index():

    print("auth")
    #os.system("""gcloud auth application-default login""")
    #time.sleep(30)

    print("token")
    #token = os.popen("""gcloud auth print-access-token""").read()
    #print(token)

    

    return render_template('index.html')


@app.route('/results')

def result():
    res = main()
    print(res)
    speech = res[1]
    tts(speech, "hi-IN","hi-IN-Standard-A","hi")
    tts(speech, "kn-IN","kn-IN-Standard-A","kn")
    tts(speech, "te-IN","te-IN-Standard-A","te")
    tts(speech, "ta-IN","ta-IN-Standard-A","ta")
    tts(speech, "ml-IN","ml-IN-Standard-A","ml")
    return render_template('result.html', output = res)