import streamlit as st

st.set_page_config(page_title="Dvc + Streamlit = ❤")
st.title("Dvc + Streamlit = ❤️")

#%% Generate the vega in a json file
# dvc plots show data/evaluation/predictions.csv --show-vega > confusion_matrix.vega.json
import json

with open("confusion_matrix.vega.json") as f:
    confusion_matrix = json.load(f)

#%% Separate data and specs
# See https://docs.streamlit.io/en/stable/api.html#streamlit.vega_lite_chart
import pandas as pd

confusion_matrix_data = pd.DataFrame(confusion_matrix["data"]["values"])
confusion_matrix_spec = confusion_matrix["spec"]

#%%
st.vega_lite_chart(
    data=confusion_matrix_data,
    spec=confusion_matrix_spec,
)
