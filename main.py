import pandas as pd
import streamlit as st
import anthropic

client = anthropic.Anthropic(
    api_key=st.secrets["CLAUDE_SECRET_KEY"]
)


st.markdown(
    """
        <!-- Global site tag (gtag.js) - Google Analytics -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-**********"></script>
        <script>
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', 'G-**********');
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

option_arr = df["Name"].unique().tolist()
doctor = st.selectbox(placeholder="Choose an option", label="Choose your doctor's name", options=option_arr)
translate = st.checkbox(label="Translate to Spanish", value=False)
summarize = st.checkbox(label="Summarize", value=False)

if st.button("Submit", type="primary"):
    callLLM(translate, df.loc[(df['Name'] == doctor) & (df["Data"].notna())], summarize)
