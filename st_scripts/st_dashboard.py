import streamlit as st

from st_scripts.st_inference import st_inference
from st_scripts.st_evaluate_single_model import st_evaluate_single_model


#%%
st.title("Dvc + Streamlit = ❤️")


class DashboardActions:
    MODEL_INFERENCE = "Model Inference"
    MODEL_EVALUATION = "Explore Performance on the Test Set"


#%%
selected_dashboard_action = st.sidebar.selectbox(
    "What do you want to do?",
    (
        DashboardActions.MODEL_INFERENCE,
        DashboardActions.MODEL_EVALUATION,
    ),
)


print("Selected dashboard action:", selected_dashboard_action)

if selected_dashboard_action == DashboardActions.MODEL_INFERENCE:
    st_inference()
elif selected_dashboard_action == DashboardActions.MODEL_EVALUATION:
    st_evaluate_single_model()
