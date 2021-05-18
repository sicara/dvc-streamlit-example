import streamlit as st

from st_scripts.st_evaluate_single_model import st_evaluate_single_model
from st_scripts.st_inference import st_inference
from st_scripts.st_list_model import st_list_model


#%%
st.set_page_config(
    page_title="Dvc + Streamlit = ❤",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Dvc + Streamlit = ❤️")


class DashboardActions:
    MODEL_LIST = "See All Models"
    MODEL_INFERENCE = "Model Inference"
    MODEL_EVALUATION = "Explore Performance on the Test Set"


#%%
selected_dashboard_action = st.sidebar.selectbox(
    "What do you want to do?",
    (
        DashboardActions.MODEL_LIST,
        DashboardActions.MODEL_INFERENCE,
        DashboardActions.MODEL_EVALUATION,
    ),
)


print("Selected dashboard action:", selected_dashboard_action)

if selected_dashboard_action == DashboardActions.MODEL_LIST:
    st_list_model()
elif selected_dashboard_action == DashboardActions.MODEL_INFERENCE:
    st_inference()
elif selected_dashboard_action == DashboardActions.MODEL_EVALUATION:
    st_evaluate_single_model()
