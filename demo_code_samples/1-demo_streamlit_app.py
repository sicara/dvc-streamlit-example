import streamlit as st

st.set_page_config(page_title="Dvc + Streamlit = ❤")
st.title("Dvc + Streamlit = ❤️")

st.write("Hello !")

#%%
import numpy as np
import pandas as pd


df = pd.DataFrame(columns=["a", "b", "c"], data=np.random.random((10, 3)))

st.write(df)

#%% It can visualize any kind of data, e.g., images, videos
st.video("https://youtu.be/EE7Gk84OZY8")

#%% It is interactive
selected_option = st.selectbox(label="Select an option bla bla", options=["foo", "bar"])

st.write("My selected option:", selected_option)
