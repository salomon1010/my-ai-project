import streamlit as st


def render_ai_summary(ai_report: str, on_generate) -> None:
    col1, col2 = st.columns([1, 4])

    with col1:
        if st.button("Generate Report", type="primary"):
            on_generate()

    if not ai_report:
        st.info("Click 'Generate Report' to create an AI-written executive summary.")
    elif ai_report.startswith("[ERROR:"):
        st.error(ai_report)
    elif ai_report.startswith("["):
        st.info("Click 'Generate Report' to create an AI-written executive summary.")
    else:
        from datetime import datetime
        st.caption(f"Generated at {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        st.markdown(ai_report)
