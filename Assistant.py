import openai
import speech_recognition as sr
import requests
from pydub import AudioSegment
from pydub.playback import play
from io import BytesIO

# Configure your API keys
openai_api_key = 'YOUR OPENAI API KEY'
elevenlabs_api_key = 'YOUR ELEVENLABS API KEY'

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

conversation1 = []  
# context file can be freely edited
chatbot1 = open_file('context.txt') 

# Function to capture voice input and transcribe it into text
def transcribe_voice():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Speak now...")
        recognizer.adjust_for_ambient_noise(source)  # Adjust for ambient noise
        audio_data = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio_data)
        return text
    except sr.UnknownValueError:
        print("Speech Recognition could not understand audio")
        return ""
    except sr.RequestError as e:
        print("Could not request results from Speech Recognition service; {0}".format(e))
        return ""

# Function to generate a response using OpenAI ChatGPT 3.5
def generate_response(api_key, conversation, chatbot, user_input, temperature=0.9, frequency_penalty=0.2, presence_penalty=0):
    openai.api_key = api_key
    conversation.append({"role": "user","content": user_input})
    messages_input = conversation.copy()
    prompt = [{"role": "system", "content": chatbot}]
    messages_input.insert(0, prompt[0])
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0125",
        temperature=temperature,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        messages=messages_input)
    chat_response = completion['choices'][0]['message']['content']
    conversation.append({"role": "assistant", "content": chat_response})
    return chat_response

# Function to send text to Elevenlabs API for voice processing
def send_to_elevenlabs(text, voice_id, api_key):
    url = f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}'
    headers = {
        'Accept': 'audio/mpeg',
        'xi-api-key': api_key,
        'Content-Type': 'application/json'
    }
    data = {
        'text': text,
        'model_id': 'eleven_monolingual_v1',
        'voice_settings': {
            'stability': 0.6,
            'similarity_boost': 0.85
        }
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("Text successfully sent to Elevenlabs API")
        # Convert response content to AudioSegment
        audio = AudioSegment.from_file(BytesIO(response.content))
        # Play the audio
        play(audio)
    else:
        print("Error sending text to Elevenlabs API:", response.text)


voice_id1 = 'ENTER VOICEID FROM ELEVENLABS' 

# Main function
def main():
    # Capture voice input and transcribe it into text
    transcribed_text = transcribe_voice()
    
    if transcribed_text:
        print("User:", transcribed_text)
        
        # Generate response based on transcribed text
        conversation = []
        response = generate_response(openai_api_key, conversation, chatbot1, transcribed_text)
        
        if response:
            print("AI:", response)
            # Send text to Elevenlabs API for voice processing
            send_to_elevenlabs(response, voice_id1, elevenlabs_api_key )
        else:
            print("Failed to generate response from OpenAI")
    else:
        print("Failed to transcribe audio")

if __name__ == "__main__":
    main()
