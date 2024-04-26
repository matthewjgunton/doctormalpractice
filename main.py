import pandas as pd
import streamlit as st
import anthropic

client = anthropic.Anthropic(
    api_key=st.secrets["CLAUDE_SECRET_KEY"]
)


st.markdown(
    """
        <!-- Global site tag (gtag.js) - Google Analytics -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-DYF57M0YYV"></script>
        <script>
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', 'G-DYF57M0YYV')
        </script>
    """, unsafe_allow_html=True)

def callLLM(translate, doctor, summarize):
    # get relevant documents >> for now that's only the most recent one
    doctor['Date'] = pd.to_datetime(doctor['Date'], format='mixed')
    sorted_df = doctor.sort_values(by='Date', ascending=False)
    values = sorted_df.iloc[0]
    msg = []
    prompt = f'<document>{values["Data"]}</document> Read the document.'

    # Spanish Translation
    if translate:
        prompt += " Then translate the document into Spanish."

    if summarize:
        prompt += " Then summarize the document."

    msg.append(
        {"role": "user", "content": prompt}
    )
    
    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1024,
        messages=msg
    )
    with st.expander("See original text"):
        st.markdown("## See the full source PDF [here](%s)" % values["Link"])
        st.write(values["Data"])
    print(message.content[0])
    st.write(message.content[0].text)

@st.cache_resource
def get_data():
    return pd.read_csv("s3://drmal123/nj3.csv")

df = get_data()
st.title("Doctor Malpractice")
st.subheader("Find out if your New Jersey doctor has had any state medical board actions taken against them")

st.markdown(
    """
    *This AI sources information from the NJ Divison of Consumer Affairs. Its data store reflects the state of that website as of April 14th, 2024.*
    *As a Large Language Model, it is vulnerable to hallucinations, so you should consider verifying information given*
    > the information provided here is provided as is and without guarantees
    """
)

expander = st.expander("See Instructions")
expander.write(
    """
    1. Select a doctor from the drop down menu.
       * If your doctor does not appear, then they have NOT had any NJ State Medical Board actions posted onto the NJ Division of Consumer Affairs website as of 04/14/2024
    2. Decide which actions you want the AI to take:
       * AI can translate the document into Spanish
       * AI can summarize the document so that it is in more accessible language
       * It can both translate into Spanish and summarize the document.
    3. To check the information, click 'See original text' to see the data given to the AI and a link to the PDF on the NJ Divison of Consumer Affairs website
    
    > This bot was partially inspired by the [John Oliver Video on State Medical Boards](https://youtu.be/jVIYbgVks7E?feature=shared)
    """
)

option_arr = df["Name"].unique().tolist().sort()
# option_arr = []
doctor = st.selectbox(placeholder="Choose an option", label="Choose your doctor's name", options=option_arr)
translate = st.checkbox(label="Translate to Spanish", value=False)
summarize = st.checkbox(label="Summarize", value=False)

if st.button("Submit", type="primary"):
    callLLM(translate, df.loc[(df['Name'] == doctor) & (df["Data"].notna())], summarize)
