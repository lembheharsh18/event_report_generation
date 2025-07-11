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
Generate a LinkedIn post-event content in the EXACT format below. Use proper line spacing and include emojis as indicated.

Event details:
Title: {data['title']}
Report Content: {summarized_content}
Date: {data['date']}
Platform/Venue: {data['platform']}
Organizing Team: {data['organizing_team']}
Speakers: {data['speakers']}
ACM Head: {data['acm_head']}
Attendance: {data['attendance']}

Format the LinkedIn post EXACTLY like this structure:

🎉 {data['title']} - Event Wrap Up! 🎉

📊 Short Report:  
[Write 2-3 lines about attendance, participation, and overall success of the event]

🚀 What Happened:  
[Write a paragraph describing what took place during the event, key highlights, and main activities]

📚 Topics Covered:  
[Briefly overview the topics or skills covered during the event]

💡 Future Impact:  
[Explain how this event will help participants in their future careers or studies]

📖 Resources:  
[Mention if any resources were shared, briefly]

🙏 Special Thanks:  
Huge appreciation to our organizing team: {data['organizing_team']}  
And our amazing speakers: {data['speakers']}

🎊 Thank You Attendees:  
[Write a grateful message to all participants who made the event successful]

🌟 [Write a motivational slogan or closing message about learning and growth]

{data['acm_head']}  
Head of PICT ACM Student Chapter

At the end, add these hashtags: {' '.join(PREDEFINED_HASHTAGS)} plus 3-4 relevant hashtags based on the event topic.

Important:  
- Keep the tone professional, positive, and engaging.  
- Use clear, concise language suitable for LinkedIn.  
- Maintain the exact line breaks and emoji placements as shown.  
- Do NOT add or remove any sections.  
- Avoid generic or repetitive phrases; make it specific and lively.

Generate the full post content only, without any explanations or extra text.

"""
    return prompt

def build_whatsapp_post_event_prompt(data, report_content, use_roberta):
    if use_roberta and len(report_content) > 200:
        summarized_content = roberta_summarize(report_content)
    else:
        summarized_content = report_content
    
    prompt = f"""
Generate a WhatsApp post-event message using the EXACT structure below, with appropriate emojis and a conversational tone.

Event details:
Title: {data['title']}
Report Content: {summarized_content}
Date: {data['date']}
Platform/Venue: {data['platform']}
Organizing Team: {data['organizing_team']}
Speakers: {data['speakers']}
ACM Head: {data['acm_head']}
Attendance: {data['attendance']}

Format the WhatsApp post-event message EXACTLY like this:

🎉 {data['title']} - Successfully Completed! 🎉

📊 [Write 2-3 lines about attendance and the overall success of the event. Make it upbeat and positive.]

✨ Event Highlights:
[Briefly describe what happened during the event and mention any key or memorable moments.]

📚 We covered: [List the main topics or skills covered, separated by commas.]

🚀 This will help participants in: [Explain in 1-2 lines how the event benefits participants in their future studies, careers, or personal growth.]

🙏 Big thanks to:
• Organizing team: {data['organizing_team']}
• Our speakers: {data['speakers']}

💫 Thank you to all attendees for making this event amazing!

[End with a short, motivational closing message about learning, growth, or community.]

Important instructions:
- Keep the tone friendly, conversational, and celebratory.
- Use emojis as shown and add more if it feels natural.
- Maintain the exact structure, order, and line breaks.
- Do NOT add or remove any sections.
- Output only the WhatsApp message content, nothing else.

"""
    return prompt

def build_instagram_post_event_prompt(data, report_content, use_roberta):
    if use_roberta and len(report_content) > 200:
        summarized_content = roberta_summarize(report_content)
    else:
        summarized_content = report_content
    
    prompt = f"""
Generate a fun, celebratory, and engaging Instagram post-event caption using the event details below.

Event details:
Title: {data['title']}
Report Content: {summarized_content}
Date: {data['date']}
Platform/Venue: {data['platform']}
Organizing Team: {data['organizing_team']}
Speakers: {data['speakers']}
ACM Head: {data['acm_head']}
Attendance: {data['attendance']}

Your Instagram caption MUST include:

🎉 Celebratory emojis and casual, friendly language to create excitement  
📋 A brief, catchy recap of the event highlighting attendance and key moments  
📚 What was learned or covered during the event, in a fun and simple way  
🙌 A warm thank you to the organizing team, speakers, and attendees  
💪 A motivational closing line encouraging growth, learning, or community spirit  
#️⃣ Include these hashtags: {' '.join(PREDEFINED_HASHTAGS)} plus 3-4 relevant, fun, and trending hashtags related to the event topic or audience  

Additional instructions:  
- Keep the tone light, upbeat, and relatable, suitable for Instagram’s audience  
- Use emojis generously but naturally to enhance engagement  
- Keep it concise but impactful (around 150-250 words)  
- Avoid formal language or jargon; make it feel like a friendly celebration post  
- Output only the Instagram caption text, no extra explanations or formatting  

Generate the full caption now.

"""
    return prompt

def build_twitter_post_event_prompt(data, report_content, use_roberta):
    if use_roberta and len(report_content) > 200:
        summarized_content = roberta_summarize(report_content)
    else:
        summarized_content = report_content
    
    prompt = f"""
Generate a celebratory, concise Twitter (X) post (max {TWITTER_CHAR_LIMIT} characters) about the successful completion of the event below. The post MUST:

- Start with an energetic phrase and event title.
- Highlight a key achievement or memorable moment.
- Thank the organizing team and speakers by name.
- Mention attendance (if notable).
- End with 4 required hashtags: {' '.join(PREDEFINED_HASHTAGS[:4])} and 2-3 relevant trending or event-specific hashtags.
- Be positive, engaging, and suitable for a public audience.
- Do NOT include apologies or promises for improvement—focus on celebration and gratitude.
- Keep it under {TWITTER_CHAR_LIMIT} characters.

Event details:
Title: {data['title']}
Summary: {summarized_content}
Date: {data['date']}
Organizing Team: {data['organizing_team']}
Speakers: {data['speakers']}
Attendance: {data['attendance']}

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
