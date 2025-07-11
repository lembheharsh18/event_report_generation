import streamlit as st
from groq import Groq
import torch
from transformers import pipeline
import textwrap
from docx import Document
import io

# ========== CONFIG ========== #
TWITTER_CHAR_LIMIT = 280
PREDEFINED_HASHTAGS = [
    "#PASC", "#PICT", "#ACM", "#coding", "#tech", "#event", "#learning"
]

# ========== ROBERTA SUMMARIZER ========== #
@st.cache_resource(show_spinner=False)
def load_summarizer():
    return pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

def roberta_summarize(text, max_len=130):
    summarizer = load_summarizer()
    summary = summarizer(text, max_length=max_len, min_length=30, do_sample=False)
    return summary[0]['summary_text']

# ========== DOCX PARSER ========== #
def parse_docx(uploaded_file):
    """Extract text from uploaded DOCX file"""
    doc = Document(io.BytesIO(uploaded_file.read()))
    full_text = []
    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)
    return '\n'.join(full_text)

# ========== PROMPT BUILDERS ========== #
def build_linkedin_post_event_prompt(data, report_content, use_roberta):
    if use_roberta and len(report_content) > 200:
        summarized_content = roberta_summarize(report_content)
    else:
        summarized_content = report_content
    
    prompt = f"""
Generate a post-event content for LinkedIn in the EXACT format below. Use proper line spacing and emojis:

Event details:
Title: {data['title']}
Report Content: {summarized_content}
Date: {data['date']}
Platform/Venue: {data['platform']}
Organizing Team: {data['organizing_team']}
Speakers: {data['speakers']}
ACM Head: {data['acm_head']}
Attendance: {data['attendance']}

Format the LinkedIn post-event content EXACTLY like this structure:

🎉 {data['title']} - Event Wrap Up! 🎉

📊 Short Report:
[2-3 lines about attendance, participation, and overall success]

🚀 What Happened:
[Paragraph about what took place during the event, key highlights, and main activities]

📚 Topics Covered:
[Brief overview of the topics/skills covered during the event]

💡 Future Impact:
[How this event will help participants in their future careers/studies]

📖 Resources: [If any resources were shared, mention them briefly]

🙏 Special Thanks:
Huge appreciation to our organizing team: {data['organizing_team']}
And our amazing speakers: {data['speakers']}

🎊 Thank You Attendees:
[Grateful message to all participants who made this event successful]

🌟 [Motivational slogan or closing message about learning and growth]

{data['acm_head']}
Head of PICT ACM Student Chapter

Use these hashtags at the end: {' '.join(PREDEFINED_HASHTAGS)} and add 3-4 relevant ones based on the event topic.
"""
    return prompt

def build_whatsapp_post_event_prompt(data, report_content, use_roberta):
    if use_roberta and len(report_content) > 200:
        summarized_content = roberta_summarize(report_content)
    else:
        summarized_content = report_content
    
    prompt = f"""
Generate a post-event content for WhatsApp in the EXACT format below:

Event details:
Title: {data['title']}
Report Content: {summarized_content}
Date: {data['date']}
Platform/Venue: {data['platform']}
Organizing Team: {data['organizing_team']}
Speakers: {data['speakers']}
ACM Head: {data['acm_head']}
Attendance: {data['attendance']}

Format the WhatsApp post-event content EXACTLY like this structure:

🎉 {data['title']} - Successfully Completed! 🎉

📊 [2-3 lines about attendance and event success]

✨ Event Highlights:
[What happened during the event and key moments]

📚 We covered: [Topics/skills covered]

🚀 This will help participants in: [Future benefits]

🙏 Big thanks to:
• Organizing team: {data['organizing_team']}
• Our speakers: {data['speakers']}

💫 Thank you to all attendees for making this event amazing!

[Motivational closing message]

Keep it conversational and use emojis appropriately.
"""
    return prompt

def build_instagram_post_event_prompt(data, report_content, use_roberta):
    if use_roberta and len(report_content) > 200:
        summarized_content = roberta_summarize(report_content)
    else:
        summarized_content = report_content
    
    prompt = f"""
Generate a post-event content for Instagram with a fun, celebratory, and engaging tone.

Event details:
Title: {data['title']}
Report Content: {summarized_content}
Date: {data['date']}
Platform/Venue: {data['platform']}
Organizing Team: {data['organizing_team']}
Speakers: {data['speakers']}
ACM Head: {data['acm_head']}
Attendance: {data['attendance']}

Make it fun and engaging with:
- Celebratory emojis and casual language
- Brief event recap
- What was learned/covered
- Thanks to team and attendees
- Motivational closing
- Include these hashtags: {' '.join(PREDEFINED_HASHTAGS)} and add relevant fun ones
"""
    return prompt

def build_twitter_post_event_prompt(data, report_content, use_roberta):
    if use_roberta and len(report_content) > 200:
        summarized_content = roberta_summarize(report_content)
    else:
        summarized_content = report_content
    
    prompt = f"""
Generate a post-event content for Twitter (X) - MUST be under {TWITTER_CHAR_LIMIT} characters.

Event details:
Title: {data['title']}
Report Content: {summarized_content}
Date: {data['date']}
Organizing Team: {data['organizing_team']}
Speakers: {data['speakers']}
Attendance: {data['attendance']}

Keep it short, celebratory, and include:
- Event title completion
- Brief success note
- Thanks to team/speakers
- Key hashtags: {' '.join(PREDEFINED_HASHTAGS[:4])} and 2-3 relevant ones
- Must be under {TWITTER_CHAR_LIMIT} characters total
"""
    return prompt

# ========== GROQ API CALL ========== #
def call_groq_api(api_key, prompt):
    client = Groq(api_key=api_key)
    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return completion.choices[0].message.content.strip()

# ========== STREAMLIT UI ========== #
st.set_page_config(page_title="PASC Post-Event Content Generator", layout="centered", page_icon="🎉")
st.title("🎉 PASC Post-Event Content Generator")
st.markdown("""
Generate engaging post-event content for LinkedIn, WhatsApp, Instagram, and Twitter (X) by uploading your event report document.
""")

# API Key Input
api_key = st.text_input("🔑 Groq API Key", type="password", help="Enter your Groq API key to generate content")

# RoBERTa Option
use_roberta = st.checkbox("Use RoBERTa summarization for long reports", value=True, help="Summarize long reports using RoBERTa model")

st.header("📄 Upload Event Report")

# File Upload
uploaded_file = st.file_uploader("Upload Event Report (DOCX)", type=['docx'], help="Upload your event report document")

if uploaded_file is not None:
    # Parse the document
    with st.spinner("📖 Reading document..."):
        report_content = parse_docx(uploaded_file)
    
    st.success("✅ Document uploaded successfully!")
    
    # Show preview of content
    with st.expander("📋 Preview Document Content"):
        st.text_area("Document Text", report_content, height=200, disabled=True)

st.header("📋 Enter Additional Event Details")

# Event Details Form
with st.form("post_event_details"):
    col1, col2 = st.columns(2)
    
    with col1:
        title = st.text_input("Event Title*", placeholder="e.g., CP SIG Workshop")
        date = st.date_input("Event Date*")
        attendance = st.text_input("Attendance*", placeholder="e.g., 50+ participants")
    
    with col2:
        platform = st.text_input("Venue/Platform*", placeholder="e.g., A1-311 or MS Teams")
        acm_head = st.text_input("ACM Head Name*", placeholder="e.g., Dr. Geetanjali Kale")
    
    organizing_team = st.text_area("Organizing Team*", placeholder="Names of team members who organized the event", height=80)
    speakers = st.text_area("Speakers/Instructors*", placeholder="Names of speakers/instructors who conducted the event", height=80)
    
    submit = st.form_submit_button("✨ Generate Post-Event Content", use_container_width=True)

if submit:
    if not api_key:
        st.error("🔑 Please provide your Groq API Key.")
    elif uploaded_file is None:
        st.error("📄 Please upload an event report document.")
    elif not all([title, attendance, platform, acm_head, organizing_team, speakers]):
        st.warning("⚠️ Please fill all required fields marked with *")
    else:
        # Prepare data
        data = {
            "title": title,
            "date": date.strftime("%d %B %Y"),
            "attendance": attendance,
            "platform": platform,
            "organizing_team": organizing_team,
            "speakers": speakers,
            "acm_head": acm_head
        }

        # Generate content for each platform
        platforms = {
            "LinkedIn": build_linkedin_post_event_prompt,
            "WhatsApp": build_whatsapp_post_event_prompt,
            "Instagram": build_instagram_post_event_prompt,
            "Twitter": build_twitter_post_event_prompt
        }
        
        results = {}
        
        with st.spinner("🤖 Generating post-event content using Groq API..."):
            for platform_name, prompt_builder in platforms.items():
                try:
                    prompt = prompt_builder(data, report_content, use_roberta)
                    result = call_groq_api(api_key, prompt)
                    
                    # Special handling for Twitter character limit
                    if platform_name == "Twitter" and len(result) > TWITTER_CHAR_LIMIT:
                        result = result[:TWITTER_CHAR_LIMIT - 3] + "..."
                    
                    results[platform_name] = result
                    
                except Exception as e:
                    results[platform_name] = f"⚠️ Error generating content: {str(e)}"

        # Display results
        st.success("🎉 Post-event content generated successfully!")
        
        # Create tabs for each platform
        tab1, tab2, tab3, tab4 = st.tabs(["📱 LinkedIn", "💬 WhatsApp", "📸 Instagram", "🐦 Twitter (X)"])
        
        with tab1:
            st.subheader("📱 LinkedIn Post-Event Content")
            st.text_area("", value=results["LinkedIn"], height=500, key="linkedin_post")
            st.download_button(
                label="📥 Download LinkedIn Content",
                data=results["LinkedIn"],
                file_name=f"linkedin_post_event_{title.replace(' ', '_')}.txt",
                mime="text/plain"
            )
        
        with tab2:
            st.subheader("💬 WhatsApp Post-Event Content")
            st.text_area("", value=results["WhatsApp"], height=400, key="whatsapp_post")
            st.download_button(
                label="📥 Download WhatsApp Content",
                data=results["WhatsApp"],
                file_name=f"whatsapp_post_event_{title.replace(' ', '_')}.txt",
                mime="text/plain"
            )
        
        with tab3:
            st.subheader("📸 Instagram Post-Event Content")
            st.text_area("", value=results["Instagram"], height=400, key="instagram_post")
            st.download_button(
                label="📥 Download Instagram Content",
                data=results["Instagram"],
                file_name=f"instagram_post_event_{title.replace(' ', '_')}.txt",
                mime="text/plain"
            )
        
        with tab4:
            st.subheader("🐦 Twitter (X) Post-Event Content")
            char_count = len(results["Twitter"])
            if char_count > TWITTER_CHAR_LIMIT:
                st.error(f"⚠️ Content is {char_count} characters (limit: {TWITTER_CHAR_LIMIT})")
            else:
                st.success(f"✅ Character count: {char_count}/{TWITTER_CHAR_LIMIT}")
            
            st.text_area("", value=results["Twitter"], height=200, key="twitter_post")
            st.download_button(
                label="📥 Download Twitter Content",
                data=results["Twitter"],
                file_name=f"twitter_post_event_{title.replace(' ', '_')}.txt",
                mime="text/plain"
            )

# Instructions
st.markdown("---")
st.header("📝 Instructions")
st.markdown("""
1. **Upload** your event report DOCX file
2. **Enter** additional event details in the form
3. **Generate** content for all social media platforms
4. **Download** individual platform content as needed

**Report Format Expected:**
- Event overview and what happened
- Topics covered during the event
- Attendance and participation details
- Resources shared (if any)
- Overall event success metrics
""")

# Footer
st.markdown("---")
