import streamlit as st
from scraper_script import scrape_google_search, enrich_with_groq, save_to_database, fetch_from_database, delete_all_data, delete_single_entry
import pandas as pd

def load_css():
    st.markdown("""
        <style>
        .block-container {
            max-width: 1200px;
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* Button styling */
        .stButton button {
            width: 100%;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            background-color: #262730;
            border: 1px solid #555;
            color: white;
            transition: all 0.2s;
        }
        
        .stButton button:hover {
            background-color: #363940;
            border-color: #666;
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            background-color: #1E1E1E;
            border-radius: 4px;
            margin-bottom: 0.5rem;
        }
        
        /* Input area styling */
        .stTextArea textarea {
            background-color: #262730;
            color: white;
            border: 1px solid #555;
        }
        
        .stTextArea textarea:focus {
            border-color: #666;
        }
        </style>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="Lead Generation Tool",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    load_css()
    
    # Initialize session state
    if 'pipeline_running' not in st.session_state:
        st.session_state.pipeline_running = False
    
    # Header
    st.title("🎯 Lead Generation Tool")
    st.markdown("Scrape emails and gather insights from URLs or Google search queries.")
    
    # Input Query
    st.markdown("### Input Query")
    
    # Input area and Pipeline controls
    col1, col2 = st.columns([3, 1])
    
    with col1:
        input_text = st.text_area(
            "Enter URL or Google Search Query",
            height=100,
            placeholder="Enter a URL or search query here..."
        )
    
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        if not st.session_state.pipeline_running:
            if st.button("▶️ Start Pipeline", key="start_button", use_container_width=True):
                if input_text.strip():
                    st.session_state.pipeline_running = True
                    st.rerun()
                else:
                    st.error("Please enter a query first.")
        else:
            if st.button("⏹️ Stop Pipeline", key="stop_button", use_container_width=True):
                st.session_state.pipeline_running = False
                st.rerun()
    
    # Database Controls
    st.markdown("### Database Controls")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Database", use_container_width=True):
            delete_all_data()
            st.success("Database cleared successfully!")
            st.rerun()
    
    with col2:
        data = fetch_from_database()
        if not data.empty:
            csv_data = data.to_csv(index=False)
            st.download_button(
                "📥 Download All Data",
                data=csv_data,
                file_name="lead_generation_data.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    # Pipeline Execution
    if st.session_state.pipeline_running and input_text.strip():
        try:
            with st.spinner("Running pipeline..."):
                scraped_data = scrape_google_search(input_text)
                enriched_data = enrich_with_groq(scraped_data)
                save_to_database(enriched_data)
                st.success("✅ Pipeline completed successfully!")
                st.session_state.pipeline_running = False
                st.rerun()
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.session_state.pipeline_running = False
            st.rerun()
    
    # Results Display
    st.markdown("### Results")
    data = fetch_from_database()
    
    if data.empty:
        st.info("No data available in the database.")
    else:
        for idx, row in data.iterrows():
            # Only open first item by default
            is_first = idx == 0
            with st.expander(f"Entry #{row['id']} - {row['title']}", expanded=is_first):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Query:** {row['query']}")
                    st.markdown(f"**URL:** [{row['url']}]({row['url']})")
                    st.markdown(f"**Description:** {row['description']}")
                    st.markdown(f"**Emails:** {row['emails']}")
                    if 'ai_insights' in row:
                        st.markdown(f"**AI Insights:** {row['ai_insights']}")
                
                with col2:
                    st.markdown("##### Actions")
                    if st.button("🗑️ Delete", key=f"del_{row['id']}", use_container_width=True):
                        delete_single_entry(row['id'])
                        st.success(f"Entry {row['id']} deleted.")
                        st.rerun()
                    
                    csv_row = pd.DataFrame([row]).to_csv(index=False)
                    st.download_button(
                        "📥 Download",
                        data=csv_row,
                        file_name=f"lead_data_{row['id']}.csv",
                        mime="text/csv",
                        key=f"down_{row['id']}",
                        use_container_width=True
                    )

if __name__ == "__main__":
    main()