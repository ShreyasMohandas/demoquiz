import streamlit as st
import llm
import time
import random
import asyncio

student_id = st.query_params.get("student_id")
student_name = st.query_params.get("student_name")

def gen_respose(res:str):
    for i in res:
        time.sleep(random.randrange(0,3,1)*0.01)
        yield i

async def async_chat_with_me(prompt: str):
    # Ensure you await the coroutine to get the result
    response = await llm.chat_with_me(prompt)
    return response

async def async_greeting(student_id):
    response = await llm.greeting(student_id)
    return response



st.title(f"Welcome, {student_name}")
if "messages" not in st.session_state:
    response = asyncio.run(async_greeting(student_id))
    st.session_state["messages"] = [{"role": "assistant", "content": response}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write_stream(gen_respose(msg["content"]))

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    response = asyncio.run(async_chat_with_me(prompt+f" my student id is {student_id}"))
    msg = response
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write_stream(gen_respose(msg))