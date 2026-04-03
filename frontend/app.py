import requests
import streamlit as st

st.set_page_config(page_title="Max AI", page_icon="🏟️", layout="wide")
API_BASE = st.sidebar.text_input("API Base URL", value="http://localhost:8000")

st.title("🏟️ Max AI")
st.caption("Internal Sports Agency AI for chat, analytics, and sponsorship strategy.")

tab1, tab2, tab3 = st.tabs(["Chat", "Analytics", "Athletes"])

with tab1:
    st.subheader("Ask Max AI")
    question = st.text_area("Your question", placeholder="Which athletes should we prioritize for premium sponsors next quarter?")
    use_llm = st.toggle("Use LLM API", value=True)
    if st.button("Run Query", type="primary"):
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            try:
                r = requests.post(f"{API_BASE}/chat/query", json={"question": question, "use_llm": use_llm}, timeout=60)
                r.raise_for_status()
                st.success("Response generated")
                st.markdown(r.json()["answer"])
            except Exception as e:
                st.error(f"Request failed: {e}")

with tab2:
    st.subheader("Agency Performance Snapshot")
    if st.button("Refresh Analytics"):
        try:
            data = requests.get(f"{API_BASE}/analytics/overview", timeout=30).json()
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Athletes", data["total_athletes"])
            c2.metric("Agents", data["total_agents"])
            c3.metric("Sponsors", data["total_sponsors"])
            c4.metric("Avg Perf Score", data["avg_performance_score"])

            st.write("#### Sport Mix")
            st.bar_chart(data["sport_mix"])
            st.write("#### Top Athletes")
            for name in data["top_athletes"]:
                st.write(f"- {name}")
        except Exception as e:
            st.error(f"Failed to load analytics: {e}")

with tab3:
    st.subheader("Athlete Explorer + Sponsor Fit")
    sport_filter = st.selectbox("Sport", ["all", "football", "tennis", "f1", "indy", "basketball"])
    params = {} if sport_filter == "all" else {"sport": sport_filter}

    try:
        athletes = requests.get(f"{API_BASE}/athletes", params=params, timeout=30).json()
    except Exception as e:
        athletes = []
        st.error(f"Could not fetch athletes: {e}")

    if athletes:
        selected = st.selectbox("Select athlete", athletes, format_func=lambda x: f"{x['full_name']} ({x['sport']})")
        st.json(selected)
        if st.button("Get Sponsor Recommendations"):
            try:
                recs = requests.get(f"{API_BASE}/suggestions/sponsor-fit", params={"athlete_id": selected["id"]}, timeout=30).json()
                st.write("#### Top Sponsor Fits")
                st.dataframe(recs["recommendations"])
            except Exception as e:
                st.error(f"Failed to fetch recommendations: {e}")
    else:
        st.info("No athletes found.")
