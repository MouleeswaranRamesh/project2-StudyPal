import os
from dotenv import load_dotenv
import streamlit as st
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain.chains import ConversationalRetrievalChain
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.memory import ConversationBufferMemory
from chatbot_utility import get_chapter_list
from get_yt_video import get_yt_video_link

load_dotenv()

working_dir=os.path.dirname(os.path.abspath(__file__))
parent_dir=os.path.dirname(working_dir)

pdfs_list=['Some_BrandNew_Doc.pdf','Some_BrandNew_Doc copy.pdf']


def get_vector_db_path(chapter,subject):
    if chapter=="All":
        return f"{parent_dir}/vector_db/Books_vector_DB"
    return f"{parent_dir}/chapters_vector_db"


def setup_chain(selected_pages_pdf,selected_pdf):
    vector_db_path=get_vector_db_path(selected_pages_pdf,selected_pdf)
    embeddings=HuggingFaceEmbeddings(model_kwargs={"device":"cpu"})
    vectorstore=Chroma(persist_directory=vector_db_path,embedding_function=embeddings)
    #vectorstore=Chroma(embedding_function=embeddings)
    llm=ChatGroq(model="llama-3.3-70b-versatile",temperature=0.92)
    memory=ConversationBufferMemory(llm=llm,output_key='answer',memory_key='chat_history',return_messages=True)
    chain=ConversationalRetrievalChain.from_llm(
        llm=llm,
        memory=memory,
        chain_type='stuff',
        retriever=vectorstore.as_retriever(search_type='mmr',search_kwargs={"k":3}),
        return_source_documents=True,
        get_chat_history=lambda h: h,
        #verbose=True,
    )
    return chain

st.set_page_config(
    page_title="StudyPal",
    page_icon="🌐",
)

st.title("💯✍️🧠📚 StudyPal")

if "chat_history" not in st.session_state:
    st.session_state.chat_history=[]
if "video_history" not in st.session_state:
    st.session_state.video_history=[]

#selected_pdf = st.selectbox("Select Subject", pdfs_list)

selected_pdf=st.selectbox(
    label="Select a pdf from the the 2 present",
    options=pdfs_list,
    index=None
)


if selected_pdf:
    pages_list=get_chapter_list(selected_pdf)

    selected_pages_pdf=st.selectbox(
        label="Select the number",
        options=pdfs_list,
        index=0
    )


    if selected_pages_pdf:
        #Reset chat_chain if chapter changes
        if st.session_state.get("selected_pages_pdf")!=selected_pages_pdf:
            st.session_state.chat_chain=setup_chain(selected_pages_pdf,selected_pdf)
        st.session_state.selected_pages_pdf=selected_pages_pdf

#Display previous messages
for idx,message in enumerate(st.session_state.chat_history):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        #Show video references if present for assistant messages
        if message["role"]=="assistant" and idx<len(st.session_state.video_history):
            video_refs=st.session_state.video_history[idx]
            if video_refs:
                st.subheader("Video reference")
                for title,link in video_refs:
                    st.info(f"{title}\n \n Link:{link}")

#Input field for users message
user_input= st.chat_input("Ask AI")

if user_input:
    st.session_state.chat_history.append({"role":"user","content":user_input})
    st.session_state.video_history.append(None) #No video refs for user

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        response=st.session_state.chat_chain({"question":user_input})
        st.markdown(response['answer'])

        search_query=' , '.join([item["content"] for item in st.session_state.chat_history if item["role"] == "user"])
        video_titles,video_links= get_yt_video_link(search_query)
        st.subheader("Video Reference")
        video_refs=[]
        for i in range(3):
            st.info(f"{video_titles[i]} \n \n Link:{video_links[i]}")
            video_refs.append((video_titles[i],video_links[i]))

        st.session_state.chat_history.append({"role":"assistant","content":response['answer']})
        st.session_state.video_history.append(video_refs)

#print("end")