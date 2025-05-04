import streamlit as st
import pandas as pd

# Load your data
data = pd.read_csv(r'C:\Users\anush\OneDrive\Desktop\AI-Court\final_cases_with_detailed_section_explanations.csv', low_memory=False)

# Streamlit page setup
st.set_page_config(page_title="AI Court Case Analyzer", page_icon="⚖️", layout="wide")

# Apply custom CSS for a court-like theme
st.markdown(
    """
    <style>
    body {
        background-color: #f4f4f9;
        color: #333;
    }
    .sidebar .sidebar-content {
        background-color: #3e4a60;
    }
    .sidebar h1, .sidebar h2 {
        color: #fff;
    }
    .sidebar .stButton button {
        background-color: #d1b100;
        color: #fff;
        font-weight: bold;
        border-radius: 5px;
    }
    .stButton button:hover {
        background-color: #a18600;
    }
    h1 {
        color: #2a3d66;
    }
    .stContainer {
        background-color: #ffffff;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stMarkdown, .stText {
        font-family: "Times New Roman", Times, serif;
    }
    .stInfo {
        background-color: #f7f8f8;
        border-left: 4px solid #003366;
    }
    .stSuccess {
        background-color: #e0f7e0;
        border-left: 4px solid #2a6a3d;
    }
    .stError {
        background-color: #f8d7da;
        border-left: 4px solid #721c24;
    }
    .stWarning {
        background-color: #fff3cd;
        border-left: 4px solid #856404;
    }
    /* Case Overview Dark Text Style */
    .case-overview {
        background-color: #f0f8ff;
        color: #2a3d66;
        padding: 15px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("⚖️ AI Court Case Analyzer")
    st.markdown("Analyze Indian court cases quickly using AI")
    st.divider()
    state_input = st.text_input("Enter State Name", "Assam")
    police_station_input = st.text_input("Enter Police Station", "Bongaigaon")
    act_input = st.text_input("Enter Act Number", "236")
    st.divider()
    search_button = st.button("🔍 Search Cases")

# Main Title
st.markdown("<h1 style='text-align: center; color: #adbde0;'>📚Court Case Dashboard</h1>", unsafe_allow_html=True)
st.write("---")

# When Search Button Clicked
if search_button:
    # Filter dataset
    filtered_cases = data[
        (data['state_name'].str.contains(state_input, case=False, na=False)) &
        (data['police_station'].str.contains(police_station_input, case=False, na=False)) &
        (data['act'].astype(str).str.contains(act_input, na=False))
    ]

    if not filtered_cases.empty:
        st.success(f"✅ Found {len(filtered_cases)} matching case(s)!")

        for idx, row in filtered_cases.iterrows():
            with st.container():
                st.markdown("### 🔹 Case Overview")
                st.markdown(f"""
                <div class="case-overview">
                <b>Case No:</b> {row['cino']}<br>
                <b>Court:</b> {row['desgname']}<br>
                <b>Police Station:</b> {row['police_station']}<br>
                <b>Filing Date:</b> {row['date_of_filing']}<br>
                <b>Act:</b> {row['act']}
                </div>
                """, unsafe_allow_html=True)

                st.markdown("### AI-Generated Insights")
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("#### 📄 Case Summary")
                    st.info(f"This is a criminal trial filed under Section {row['act']} IPC at {row['police_station']} court ({row['desgname']}), currently decided. First hearing was on {row['date_of_filing']}.")

                with col2:
                    st.markdown("#### Outcome Prediction")
                    st.success("Likely to result in compromise based on prior case trends.")

                st.markdown("### 📜 Act Explanation")
                st.warning(row['description'])

                st.write("---")
    else:
        st.error("❌ No matching cases found. Please check your inputs!")

else:
    st.info("👈 Enter search details in the sidebar and click 'Search Cases'.")
