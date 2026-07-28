import streamlit as st
# streamlit: Web based app making
# lite python framework

st.title("AI Resume Maker")

st.markdown("""## User can create or
download AI created Resume based on high ATS
Score""")


#==========AGENT CODE==================

import os
import time
import langchain
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
import pytesseract as pyt
from tavily import TavilyClient
from langchain.messages import SystemMessage, HumanMessage
import numpy as np
import streamlit as st
from langchain_community.document_loaders import PyMuPDFLoader
from PIL import Image

#===============API KEY LOAD==========

GOOGLE_API_KEY = st.sidebar.text_input("GOOGLE_API_KEY",type="password")
GROQ_API_KEY = st.sidebar.text_input("GROQ_API_KEY",type="password")
TAVILY_API_KEY = st.sidebar.text_input("TAVILY_API_KEY",type="password")

if not (GOOGLE_API_KEY) and not (GROQ_API_KEY) and not (TAVILY_API_KEY):
    st.sidebar.warning("PASS API KEYS")
    st.stop()
else:
    st.success("API KEYS LOADED")

# ==============MODEL BUILDING=============
model = ChatGoogleGenerativeAI(
    model = "gemini-3.5-flash-lite",
    google_api_key = GOOGLE_API_KEY
)

# tool
def search_recent_news_jobs(query):
  """This function helps to search
  recent news or recent jobs
  related to given search query
  suppose user write a Python Developer Jobs
  It should return trending news and jobs link"""
  client = TavilyClient(
      api_key = TAVILY_API_KEY
  )
  return client.search(query)


# agent creation
from langchain.agents import create_agent
agent = create_agent(
    model = model,
    tools = [search_recent_news_jobs]
)


#========PROMPT GENERATOR=========
def prompt_generator(agent):
  """This function help to give detailed prompt
  followed by  chain of thoughts and
  persona based prompting, main task is to give
  detailed prompt to build Resume for
  Students or experienced person
  Based on their given personal information
  """

  prompt = """You are senior HR resume analyzer,
  main task is to give
  detailed prompt to build Resume for
  Students or experienced person
  Based on their given personal information
  System Instruction I want model to generate resume
  in HTML format include that in prompt"""

  response = agent.invoke(prompt)
  file_name = 'prompt.py'
  with open(file_name,'w') as f:
    f.write(response.content[-1]['text'])
  return "Prompt file generated Successfully,agent can read it"

prompt_generator(model)
# Tool 2:
def resume_maker_prompt():
  """This function just gives
  updated prompt for model"""

  with open('prompt.py','r') as f:
    prompt = f.read()
  return prompt

resume_maker_prompt()

#===========UPLOAD IMAGE==============
uploaded_file = st.sidebar.file_uploader(
    "Choose an image file", 
    type=["jpg", "jpeg", "png", "webp"]
)
if uploaded_file is not None:
    try:
        image = Image.open(uploaded_file)
        
        st.sidebar.image(image, caption="Uploaded Image", use_container_width=True)
        
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        base_name = os.path.splitext(uploaded_file.name)[0]
        save_path = f"{base_name}.jpg"
        
        
        image.save(save_path, "JPEG")  
        st.sidebar.success(f"🎉 Image successfully saved as {save_path}!")
        
    except Exception as e:
        st.error(f"Error processing image: {e}")

#============GENERATE RESUME===========
prompt = """You are a helpful AI assistant
with job resume marker, your task is to give
HTML format resume, with proper designing using recent CSS snd JS
code, with  professional design format.
Uer will upload data and return HTML format resume
always use different color or styling and the information written below heading and sub-heading in black colour
IMPORTANT: wherever the profile photo goes in the resume, output exactly this tag and nothing else:
<img src="PROFILE_IMAGE_PLACEHOLDER" style="width:100px;height:100px;border-radius:50%;">
do not draw or generate any other image tag or placeholder circle yourself"""

final_prompt = prompt + resume_maker_prompt()

user_info = st.text_area("Enter your information")

user_details = f"""user details: given below:
Resume info: {user_info}
Photo: {uploaded_file}
Photo present in current directory with name as
uploaded_file, and once resume generated give
download button in same html code.
Default if not given: Give Python Developer Resume"""

query = final_prompt + user_details

import base64

OPTIONS = ['DELHI','NOIDA','GURGAON','PUNE','KANPUR','BENGALURU']

LOCATION = st.sidebar.multiselect('Select Location:', options = OPTIONS)

JOB_PROFILE = ['PYTHON DEVELOPER','GEN AI','FULL-STACK DEVELOPER','DATA ANALYST']

PROFILE = st.sidebar.multiselect("Select your Job role:", options = JOB_PROFILE)

job_prompt = f"""Based on {PROFILE} Jobs in {LOCATION},I
want latest job news in using tavily,
try top 10 search or whatever available
and give result like naukri theme design with
jon name, job desc, salary,
apply link, OUTPUT must be in HTML no markdowns"""

if st.button("Generate Resume"):
  with st.spinner("Running Agent....."):

    response = agent.invoke({'messages':[{'role':'user',"content":query}]})
    code = response['messages'][-1].content[-1]['text']

      # swap in the actual uploaded photo instead of the placeholder tag
    if uploaded_file is not None:
        with open(save_path, "rb") as img_file:
            b64_image = base64.b64encode(img_file.read()).decode()
        data_uri = f"data:image/jpeg;base64,{b64_image}"
        code = code.replace("PROFILE_IMAGE_PLACEHOLDER", data_uri)
    #st.markdown(code)
    st.html(code,width="stretch", unsafe_allow_javascript=True)

    st.divider()
    response = agent.invoke({'messages':[{'role':'user',"content":job_prompt}]})
    job_code = response['messages'][-1].content[-1]['text']
    st.html(job_code,width="stretch", unsafe_allow_javascript=True)
