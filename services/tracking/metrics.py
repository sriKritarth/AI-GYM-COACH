import streamlit as st
from services.config.workout_config import METRICS_FIELDS

def sync_metric_context(context):
    if not context or not hasattr(context , "state") or not context.state.playing:
        return
    
    processor = getattr(context , "video_processor" , None)


    if not processor:
        return
    
    exercise = st.session_state.get("exercise_type")

    if not exercise:
        return 
    
    processor.set_exercise(exercise)

    latest_metrics = processor.get_latest_metrics()

    if not latest_metrics:
        return
    
    reps = latest_metrics.get("reps")

    st.session_state.reps = reps

    fields = METRICS_FIELDS.get(exercise)

    if not fields:
        return
    
    for key , default in fields.items():
        st.session_state[key] = latest_metrics.get(key , default)