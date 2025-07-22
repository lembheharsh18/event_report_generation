import streamlit as st
from charts import create_sentiment_chart
import pandas as pd
import matplotlib.pyplot as plt
from analyzer import FeedbackAnalyzer
from report_generator import create_docx_report
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def display_analysis_results(analysis):
    """Display analysis results in Streamlit"""
    if not analysis:
        return
        
    st.subheader("📊 Analysis Results")
    
    with st.expander("📌 Event Summary", expanded=True):
        st.write(analysis.get("narrative_summary", ""))
    
    sentiment_data = analysis.get("sentiment_analysis", {})
    if sentiment_data:
        with st.expander("😃 Sentiment Analysis"):
            st.write(f"**Total Responses:** {analysis.get('total_responses', 0)}")
            col1, col2, col3 = st.columns(3)
            col1.metric("Positive", f"{sentiment_data.get('positive', 0)} ({sentiment_data.get('percentages', {}).get('positive', 0):.1f}%)")
            col2.metric("Neutral", f"{sentiment_data.get('neutral', 0)} ({sentiment_data.get('percentages', {}).get('neutral', 0):.1f}%)")
            col3.metric("Negative", f"{sentiment_data.get('negative', 0)} ({sentiment_data.get('percentages', {}).get('negative', 0):.1f}%)")
            st.write(f"**Overall Sentiment Score:** {sentiment_data.get('overall_score', 0):.2f}")
            
            sentiment_chart = create_sentiment_chart({
                "Positive": sentiment_data.get('positive', 0),
                "Neutral": sentiment_data.get('neutral', 0),
                "Negative": sentiment_data.get('negative', 0)
            })
            st.image(sentiment_chart, caption="Sentiment Distribution", width=400)
    
    # Text analysis
    text_analysis = analysis.get("text_analysis", {})
    if text_analysis:
        with st.expander("📝 Text Analysis"):
            col1, col2 = st.columns(2)
            col1.metric("Total Words", text_analysis.get('total_words', 0))
            col2.metric("Unique Words", text_analysis.get('unique_words', 0))
            
            if text_analysis.get('most_common_words'):
                st.subheader("Top 20 Most Common Words")
                words, frequencies = zip(*text_analysis['most_common_words'])
                plt.figure(figsize=(10, 6))
                plt.barh(words, frequencies, color='#2196F3')
                plt.xlabel('Frequency')
                plt.title('Top 20 Most Common Words')
                plt.gca().invert_yaxis()
                st.pyplot(plt)
            
            if text_analysis.get('key_themes'):
                st.subheader("Key Themes")
                st.markdown(text_analysis['key_themes'])
    
    with st.expander("💡 Key Takeaways"):
        st.markdown(analysis.get("key_takeaways", ""))
    
    with st.expander("✨ Suggestions"):
        st.markdown(analysis.get("suggestions", ""))

    # Detailed sentiment analysis
    if sentiment_data and sentiment_data.get('detailed_analysis'):
        with st.expander("🔍 Detailed Sentiment Analysis"):
            for i, item in enumerate(sentiment_data['detailed_analysis'][:20]):  # Show first 20
                st.write(f"**Feedback {i+1}:**")
                st.caption(f"Sentiment: {item.get('sentiment', '')} (Confidence: {item.get('confidence', 0):.2f})")
                st.write(item.get('feedback', ''))
                st.divider()


def main():
    st.set_page_config(
        page_title="Event Feedback Analyzer", 
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📊 Event Feedback Analyzer")
    st.caption("Analyze event feedback and generate professional reports")
    
    # Initialize session state
    if "report_data" not in st.session_state:
        st.session_state.report_data = {}
    if "analysis" not in st.session_state:
        st.session_state.analysis = {}
    
    # Get API key from environment
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        st.error("⚠️ GROQ_API_KEY not found in environment variables. Please add it to your .env file.")
        st.stop()
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        use_roberta = st.checkbox("Use RoBERTa for sentiment analysis (more accurate)")
        st.divider()
        
        st.header("📤 Data Import")
        feedback_option = st.radio("Feedback Input Method", 
                                   ["Upload CSV", "Manual Input"])
        feedback_list = []
        
        if feedback_option == "Upload CSV":
            uploaded_file = st.file_uploader("Upload feedback CSV", type="csv")
            if uploaded_file:
                try:
                    df = pd.read_csv(uploaded_file)
                    
                    # Find feedback columns
                    feedback_cols = []
                    for col in df.columns:
                        col_lower = col.lower()
                        if ('feedback' in col_lower or 
                            'comment' in col_lower or 
                            'suggestion' in col_lower or 
                            'review' in col_lower or 
                            'response' in col_lower):
                            feedback_cols.append(col)
                    
                    # Process feedback
                    if feedback_cols:
                        for col in feedback_cols:
                            feedback_list.extend(df[col].dropna().astype(str).tolist())
                    else:
                        # Fallback to all text columns
                        for col in df.columns:
                            if df[col].dtype == 'object':
                                feedback_list.extend(df[col].dropna().astype(str).tolist())
                    
                    st.success(f"Loaded {len(feedback_list)} feedback entries")
                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")
        
        else:  # Manual Input
            num_entries = st.number_input("Number of Feedback Entries", 
                                          min_value=1, max_value=50, value=5, step=1)
            for i in range(num_entries):
                feedback = st.text_input(f"Feedback #{i+1}", key=f"fb_{i}")
                if feedback:
                    feedback_list.append(feedback)
    
    # Main content area
    with st.expander("📋 Event Details", expanded=True):
        event_name = st.text_input("Event Name")
        col1, col2 = st.columns(2)
        event_date = col1.date_input("Date")
        
        # Time range input
        st.subheader("Event Time")
        time_col1, time_col2 = st.columns(2)
        start_time = time_col1.time_input("Start Time")
        end_time = time_col2.time_input("End Time")
        
        event_venue = st.text_input("Venue")
        
        st.subheader("Attendance (Approximate)")
        total_attendees = st.text_input("Total Attendees (e.g., '50+', 'Around 100', '75-80')", placeholder="e.g., 50+")
        col1, col2, col3 = st.columns(3)
        students = col1.text_input("Students (e.g., '30+', 'Around 25')", placeholder="e.g., 30+")
        faculty = col2.text_input("Faculty (e.g., '10+', 'Around 15')", placeholder="e.g., 10+")
        guests = col3.text_input("Guests (e.g., '5+', 'Around 10')", placeholder="e.g., 5+")
        
        st.subheader("Topics Covered")
        topics = st.text_area("Enter topics (one per line)", 
                              placeholder="Topic 1\nTopic 2\nTopic 3",
                              height=100)
        
        st.subheader("Challenges & Solutions")
        num_challenges = st.number_input("Number of Challenges", 
                                         min_value=0, max_value=5, value=1, step=1)
        challenges = []
        solutions = []
        
        for i in range(num_challenges):
            st.write(f"Challenge {i+1}")
            challenge = st.text_input(f"Description {i+1}", key=f"ch_{i}")
            solution = st.text_input(f"Solution {i+1}", key=f"sol_{i}")
            if challenge:  # Only add if not empty
                challenges.append(challenge)
            if solution:  # Only add if not empty
                solutions.append(solution)
        
        st.subheader("Special Mentions")
        special_mentions = st.text_area("People to acknowledge (one per line)", 
                                        height=80, placeholder="Name 1\nName 2")
        
        st.subheader("Additional Information")
        relevant_links = st.text_area("Relevant Links (one per line)", 
                                      placeholder="https://example.com/photos\nhttps://example.com/recording",
                                      height=80)
        prepared_by = st.text_input("Prepared By")
        report_date = st.date_input("Report Date")
        
        # Save event details
        if st.button("💾 Save Event Details"):
            # Create time range string
            time_range = ""
            if start_time and end_time:
                time_range = f"{start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}"
            elif start_time:
                time_range = start_time.strftime('%I:%M %p')
            elif end_time:
                time_range = f"Until {end_time.strftime('%I:%M %p')}"
            
            # Process topics
            topics_list = []
            if topics.strip():
                topics_list = [t.strip() for t in topics.split("\n") if t.strip()]
            
            # Process special mentions
            mentions_list = []
            if special_mentions.strip():
                mentions_list = [m.strip() for m in special_mentions.split("\n") if m.strip()]
            
            # Process relevant links
            links_list = []
            if relevant_links.strip():
                links_list = [l.strip() for l in relevant_links.split("\n") if l.strip()]
            
            # Only include non-empty fields in report data
            report_data = {}
            
            if event_name.strip():
                report_data["event_name"] = event_name.strip()
            if event_date:
                report_data["event_date"] = event_date.strftime("%B %d, %Y")
            if event_venue.strip():
                report_data["event_venue"] = event_venue.strip()
            if time_range:
                report_data["event_time"] = time_range
            
            # ** CORRECTION STARTS HERE **
            # Always include attendance fields to prevent KeyErrors, defaulting to '0' if empty.
            if total_attendees.strip():
                report_data["total_attendees"] = total_attendees.strip()
            report_data["students"] = students.strip() or "0"
            report_data["faculty"] = faculty.strip() or "0"
            report_data["guests"] = guests.strip() or "0"
            # ** CORRECTION ENDS HERE **
            
            if topics_list:
                report_data["topics"] = topics_list
            if challenges:
                report_data["challenges"] = challenges
            if solutions:
                report_data["solutions"] = solutions
            if mentions_list:
                report_data["special_mentions"] = mentions_list
            if links_list:
                report_data["relevant_links"] = links_list
            if prepared_by.strip():
                report_data["prepared_by"] = prepared_by.strip()
            if report_date:
                report_data["report_date"] = report_date.strftime("%B %d, %Y")
            
            st.session_state.report_data = report_data
            st.success("Event details saved!")
    
    # Analysis and report generation
    if not feedback_list:
        st.warning("Please add feedback data to analyze")
        st.stop()
    
    # Analysis buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔍 Analyze Feedback Only", use_container_width=True):
            with st.spinner("Analyzing feedback..."):
                analyzer = FeedbackAnalyzer(groq_api_key, use_roberta=use_roberta)
                analysis = analyzer.analyze_feedback(feedback_list)
                st.session_state.analysis = analysis
                st.session_state.analyzer = analyzer
                st.success("✅ Analysis completed!")
    
    with col2:
        if st.button("✨ Generate Full Report", use_container_width=True):
            if not st.session_state.report_data:
                st.warning("Please save event details first")
                st.stop()
                
            with st.spinner("Analyzing feedback and generating report..."):
                analyzer = FeedbackAnalyzer(groq_api_key, use_roberta=use_roberta)
                analysis = analyzer.analyze_feedback(feedback_list)
                st.session_state.analysis = analysis
                st.session_state.analyzer = analyzer
                
                # Generate DOCX report
                docx_bytes = create_docx_report(
                    st.session_state.report_data, 
                    analysis,
                    analyzer
                )
                
                st.success("✅ Report generated successfully!")
                st.download_button(
                    label="📥 Download DOCX Report",
                    data=docx_bytes,
                    file_name=f"{st.session_state.report_data.get('event_name', 'event').replace(' ', '_')}_report.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
    
    # Display analysis results if available
    if st.session_state.get("analysis"):
        display_analysis_results(st.session_state.analysis)

if __name__ == "__main__":
    main()
