import streamlit as st
from groq import Groq
import torch
from transformers import pipeline
import textwrap

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

# ========== PROMPT BUILDER ========== #
def build_linkedin_prompt(data, use_roberta):
    overview = roberta_summarize(data['overview']) if use_roberta else data['overview']
    
    prompt = f"""
Generate a pre-event promotional content for LinkedIn in the EXACT format below. Use proper line spacing and emojis:

Event details:
Title: {data['title']}
Overview: {overview}
Staff & Team: {data['staff']}
Date: {data['date']}
Platform/Venue: {data['platform']}
{('Link: ' + data['link']) if data['link'] else ''}
Time: {data['time']}
ACM Head: {data['acm_head']}

Format the LinkedIn content EXACTLY like this structure:
🚀 PASC presents: [Event Title] 🚀 

[Catchy opening line related to the event]

[Main body paragraph about what the event offers, who's conducting it, and why people should attend]

📅 Date: [Date]
📍 Venue/Platform: [Venue/Platform]
{('🔗 Link: ' + data['link']) if data['link'] else ''}
🕓 Time: [Time]

📌 [Brief description of what will be covered or why to attend]

[Motivational closing line]

{data['acm_head']}
Head of PICT ACM Student Chapter

Use these hashtags at the end: {' '.join(PREDEFINED_HASHTAGS)} and add 3-4 relevant ones based on the event topic.
"""
    return prompt

def build_whatsapp_prompt(data, use_roberta):
    overview = roberta_summarize(data['overview']) if use_roberta else data['overview']
    
    prompt = f"""
Generate a pre-event promotional content for WhatsApp in the EXACT format below:

Event details:
Title: {data['title']}
Overview: {overview}
Staff & Team: {data['staff']}
Date: {data['date']}
Platform/Venue: {data['platform']}
{('Link: ' + data['link']) if data['link'] else ''}
Time: {data['time']}
ACM Head: {data['acm_head']}

Format the WhatsApp content EXACTLY like this structure:
🚀 [Event Title with PASC] 🚀

[Engaging opening question or statement]

[Main body paragraph about the event, speaker/team, and what participants will learn]

📅 Date: [Date]
📍 Platform/Venue: [Platform/Venue]
{('🔗 Link: ' + data['link']) if data['link'] else ''}
🕓 Time: [Time]

[Motivational closing line about not missing the opportunity]

Keep it conversational and use emojis appropriately.
"""
    return prompt

def build_instagram_prompt(data, use_roberta):
    overview = roberta_summarize(data['overview']) if use_roberta else data['overview']
    
    prompt = f"""
Generate a pre-event promotional content for Instagram with a fun, witty, and casual tone.

Event details:
Title: {data['title']}
Overview: {overview}
Staff & Team: {data['staff']}
Date: {data['date']}
Platform/Venue: {data['platform']}
{('Link: ' + data['link']) if data['link'] else ''}
Time: {data['time']}
ACM Head: {data['acm_head']}

Make it fun and engaging with:
- Fun emojis and casual language
- Catchy opening
- Brief but exciting description
- Event details
- Call to action
- Include these hashtags: {' '.join(PREDEFINED_HASHTAGS)} and add relevant fun ones
"""
    return prompt

def build_twitter_prompt(data, use_roberta):
    overview = roberta_summarize(data['overview']) if use_roberta else data['overview']
    
    prompt = f"""
Generate a pre-event promotional content for Twitter (X) - MUST be under {TWITTER_CHAR_LIMIT} characters.

Event details:
Title: {data['title']}
Overview: {overview}
Staff & Team: {data['staff']}
Date: {data['date']}
Platform/Venue: {data['platform']}
{('Link: ' + data['link']) if data['link'] else ''}
Time: {data['time']}

Keep it short, punchy, and include:
- Event title with PASC
- Date and time
- Venue/platform
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
st.set_page_config(page_title="PASC Content Generator", layout="centered", page_icon="🚀")
st.title("🚀 PASC Pre-Event Content Generator")
st.markdown("""
Generate engaging pre-event promotional content for LinkedIn, WhatsApp, Instagram, and Twitter (X) using AI.
""")

# API Key Input
api_key = st.text_input("🔑 Groq API Key", type="password", help="Enter your Groq API key to generate content")

# RoBERTa Option
use_roberta = st.checkbox("Use RoBERTa summarization for Overview", value=True, help="Summarize long overviews using RoBERTa model")

st.header("📋 Enter Event Details")

# Event Details Form
with st.form("event_details"):
    col1, col2 = st.columns(2)
    
    with col1:
        title = st.text_input("Event Title*", placeholder="e.g., CP SIG Workshop")
        date = st.date_input("Event Date*")
        time = st.text_input("Event Time*", placeholder="e.g., 4:00 PM – 6:00 PM")
    
    with col2:
        platform_type = st.selectbox("Event Type*", ["Online", "Offline"])
        venue_or_platform = st.text_input("Venue/Platform Name*", placeholder="e.g., A1-311 or MS Teams")
        acm_head = st.text_input("ACM Head Name*", placeholder="e.g., Dr. Geetanjali Kale")
    
    overview = st.text_area("Event Overview*", placeholder="Describe what the event is about, topics to be covered, etc.", height=100)
    staff = st.text_area("Staff & Team Conducting*", placeholder="Names of instructors/speakers conducting the event", height=80)
    
    link = ""
    if platform_type == "Online":
        link = st.text_input("Event Link", placeholder="https://...")
    
    submit = st.form_submit_button("✨ Generate Content", use_container_width=True)

if submit:
    if not api_key:
        st.error("🔑 Please provide your Groq API Key.")
    elif not all([title, overview, staff, time, venue_or_platform, acm_head]):
        st.warning("⚠️ Please fill all required fields marked with *")
    else:
        # Prepare data
        data = {
            "title": title,
            "overview": overview,
            "staff": staff,
            "date": date.strftime("%d %B %Y"),
            "time": time,
            "platform": venue_or_platform,
            "link": link,
            "acm_head": acm_head
        }

        # Generate content for each platform
        platforms = {
            "LinkedIn": build_linkedin_prompt,
            "WhatsApp": build_whatsapp_prompt,
            "Instagram": build_instagram_prompt,
            "Twitter": build_twitter_prompt
        }
        
        results = {}
        
        with st.spinner("🤖 Generating content using Groq API..."):
            for platform_name, prompt_builder in platforms.items():
                try:
                    prompt = prompt_builder(data, use_roberta)
                    result = call_groq_api(api_key, prompt)
                    
                    # Special handling for Twitter character limit
                    if platform_name == "Twitter" and len(result) > TWITTER_CHAR_LIMIT:
                        result = result[:TWITTER_CHAR_LIMIT - 3] + "..."
                    
                    results[platform_name] = result
                    
                except Exception as e:
                    results[platform_name] = f"⚠️ Error generating content: {str(e)}"

        # Display results
        st.success("🎉 Content generated successfully!")
        
        # Create tabs for each platform
        tab1, tab2, tab3, tab4 = st.tabs(["📱 LinkedIn", "💬 WhatsApp", "📸 Instagram", "🐦 Twitter (X)"])
        
        with tab1:
            st.subheader("📱 LinkedIn Content")
            st.text_area("", value=results["LinkedIn"], height=400, key="linkedin")
            st.download_button(
                label="📥 Download LinkedIn Content",
                data=results["LinkedIn"],
                file_name=f"linkedin_{title.replace(' ', '_')}.txt",
                mime="text/plain"
            )
        
        with tab2:
            st.subheader("💬 WhatsApp Content")
            st.text_area("", value=results["WhatsApp"], height=300, key="whatsapp")
            st.download_button(
                label="📥 Download WhatsApp Content",
                data=results["WhatsApp"],
                file_name=f"whatsapp_{title.replace(' ', '_')}.txt",
                mime="text/plain"
            )
        
        with tab3:
            st.subheader("📸 Instagram Content")
            st.text_area("", value=results["Instagram"], height=300, key="instagram")
            st.download_button(
                label="📥 Download Instagram Content",
                data=results["Instagram"],
                file_name=f"instagram_{title.replace(' ', '_')}.txt",
                mime="text/plain"
            )
        
        with tab4:
            st.subheader("🐦 Twitter (X) Content")
            char_count = len(results["Twitter"])
            if char_count > TWITTER_CHAR_LIMIT:
                st.error(f"⚠️ Content is {char_count} characters (limit: {TWITTER_CHAR_LIMIT})")
            else:
                st.success(f"✅ Character count: {char_count}/{TWITTER_CHAR_LIMIT}")
            
            st.text_area("", value=results["Twitter"], height=200, key="twitter")
            st.download_button(
                label="📥 Download Twitter Content",
                data=results["Twitter"],
                file_name=f"twitter_{title.replace(' ', '_')}.txt",
                mime="text/plain"
            )

# Footer
st.markdown("---")
