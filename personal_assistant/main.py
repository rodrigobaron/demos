import streamlit as st
from litellm import completion
from dotenv import load_dotenv

load_dotenv()

PROMPT = """
You are an expecional assistant, think while giving the answer. Your thinkg process should be inside of <thinking> tag. Can have multiple thinking tags. 

<thinking>
Think step by step and reflect your thoughts.
</thinking>
"""

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": PROMPT}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask me anything!")
assistant_response = ""

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        c = st.empty()

        stream = completion(
            model="groq/llama-3.1-70b-versatile",
            messages=st.session_state.messages,
            stream=True,
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                assistant_response += chunk.choices[0].delta.content
                c.markdown(assistant_response)

        st.session_state.messages.append(
            {"role": "assistant", "content": st.session_state.messages[-1]["content"]}
        )
