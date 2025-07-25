import streamlit as st
import os
from dotenv import load_dotenv, find_dotenv
import google.generativeai as genai
import time
from gtts import gTTS
from io import BytesIO

load_dotenv(find_dotenv())
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("❌ Gemini API Key not found.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

st.set_page_config(page_title="🔥 AI Debate", layout="centered")
st.markdown("""
<style>
.stApp { background-color: #0e0e0e; color: white; }
.chat-box { padding: 20px; border-radius: 20px; max-width: 400px; margin: auto; }
.message { padding: 12px; margin-bottom: 10px; border-radius: 16px; max-width: 80%; word-wrap: break-word; }
.left { background-color: #1e1e1e; margin-right: auto; text-align: left; color: white; }
.right { background-color: #333333; margin-left: auto; text-align: left; color: white; }
.judge { background-color: #222244; margin: 20px auto; text-align: center; color: #ffffff; padding: 15px; border-radius: 16px; font-style: italic; }
</style>
""", unsafe_allow_html=True)

st.title("🎙️ AI Debate Battle")
st.subheader("2 AIs arguing like humans 😎")

enable_voice = st.checkbox("🔊 Enable Voice Narration")

def speak_and_wait(text):
    if enable_voice:
        tts = gTTS(text, lang='en', slow=False)
        mp3_fp = BytesIO()
        tts.write_to_fp(mp3_fp)
        st.audio(mp3_fp.getvalue(), format='audio/mp3', autoplay=True)
        duration = len(text.split()) // 2 + 1
        time.sleep(duration)

with st.form("debate_form"):
    st.markdown("### 🎯 Debate Setup")
    topic = st.text_input("🗣️ Debate Topic", "Should smartphones be allowed in schools?")

    st.markdown("#### 👤 Debater 1")
    debater_1_name = st.text_input("Name", "Aryan")
    debater_1_style = st.text_input("Speaking Style / Role", "an emotional student")

    st.markdown("#### 👤 Debater 2")
    debater_2_name = st.text_input("Name ", "Kabir")
    debater_2_style = st.text_input("Speaking Style / Role ", "a logical thinker")

    st.markdown("#### 🌀 Debate Length")
    num_rounds = st.slider("How many back-and-forth rounds?", min_value=1, max_value=5, value=2)

    start_btn = st.form_submit_button("🔥 Start Debate")

    debater_1 = f"{debater_1_name}, {debater_1_style}"
    debater_2 = f"{debater_2_name}, {debater_2_style}"

if start_btn:
    with st.spinner("Generating Debate..."):
        chat = []
        st.markdown('<div class="chat-box">', unsafe_allow_html=True)

        # Debater 1 opens
        first_prompt = f"""
You are {debater_1}. Debate in Hinglish with emotions.
Make your argument in a natural, human tone. Always follow this implicit structure:
- Start with a clear opinion/assertion.
- Support it with a reason.
- Add a small real-life example or analogy to back it up.

Topic: "{topic}"
Speak first in 2-3 lines.
"""
        response = model.generate_content(first_prompt).text.strip()
        name1 = debater_1.split(",")[0]
        chat.append(("left", name1, response))
        st.markdown(f'<div class="message left"><strong>{name1}</strong><br>{response}</div>', unsafe_allow_html=True)
        speak_and_wait(response)

        # Rounds of debate
        for _ in range(num_rounds):
            prev_msg = chat[-1][2]
            reply_prompt = f"""
You are {debater_2}. You're a logical thinker.
Debate in Hinglish with real facts, following this format (but don’t say these labels!):
- Clear opinion/assertion
- A logical reason or stat
- A relatable example to support it

Respond in 2-3 lines to: "{prev_msg}"
"""
            response = model.generate_content(reply_prompt).text.strip()
            name2 = debater_2.split(",")[0]
            chat.append(("right", name2, response))
            st.markdown(f'<div class="message right"><strong>{name2}</strong><br>{response}</div>', unsafe_allow_html=True)
            speak_and_wait(response)

            # Debater 1 rebuttal
            prev_msg = chat[-1][2]
            rebuttal_prompt = f"""
You are {debater_1}. Rebut emotionally but follow this thought process:
- Assert your opinion clearly
- Disagree with a solid reason
- Use a personal example or emotional angle

Stay in Hinglish and respond to: "{prev_msg}" in 2-3 lines.
"""
            response = model.generate_content(rebuttal_prompt).text.strip()
            chat.append(("left", name1, response))
            st.markdown(f'<div class="message left"><strong>{name1}</strong><br>{response}</div>', unsafe_allow_html=True)
            speak_and_wait(response)

        # Final wrap-up by debater 2
        final_prompt = f"""
You are {debater_2}. Conclude confidently with 3-4 lines.
Structure your final statement as:
- Strong closing opinion
- Recap your best argument
- End with a clear example or memorable line in Hinglish
"""
        response = model.generate_content(final_prompt).text.strip()
        chat.append(("right", name2, response))
        st.markdown(f'<div class="message right"><strong>{name2}</strong><br>{response}</div>', unsafe_allow_html=True)
        speak_and_wait(response)

        # Judge verdict
        st.markdown('</div>', unsafe_allow_html=True)
        transcript = "\n".join([f"{n}: {m}" for _, n, m in chat])
        judge_prompt = f"""
You are a strict but witty judge. Here's the transcript of a Hinglish debate:

{transcript}

Now, give a decisive final verdict:
- Choose a clear winner (don’t say it's a tie!)
- Explain *why* in 3-4 lines
- Highlight who had stronger reasoning, better examples, or more convincing delivery
"""
        judge_response = model.generate_content(judge_prompt).text.strip()
        st.markdown(f'<div class="judge">⚖️ <strong>Judge\'s Verdict:</strong><br>{judge_response}</div>', unsafe_allow_html=True)
        speak_and_wait(judge_response)

        st.success("✅ Debate Finished!")
