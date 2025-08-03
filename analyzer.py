import streamlit as st
from collections import Counter
from textblob import TextBlob
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
from groq import Groq
import re
from transformers import pipeline
import concurrent.futures

nltk.download('vader_lexicon', quiet=True)

class FeedbackAnalyzer:
    def __init__(self, groq_api_key=None, use_roberta=False):
        self.vader_analyzer = SentimentIntensityAnalyzer()
        self.model = Groq(api_key=groq_api_key) if groq_api_key else None
        self.use_roberta = use_roberta
        self.roberta_analyzer = None
        
        if use_roberta:
            try:
                self.roberta_analyzer = pipeline(
                    "sentiment-analysis", 
                    model="cardiffnlp/twitter-roberta-base-sentiment",
                    top_k=None
                )
            except Exception as e:
                st.error(f"Failed to initialize RoBERTa: {str(e)}")
                self.use_roberta = False

    def analyze_feedback(self, feedback_list):
        if not feedback_list:
            return {"error": "No feedback data found"}

        # Filter relevant feedback
        relevant_feedback = self._filter_relevant_feedback(feedback_list)
        
        analysis_results = {
            "total_responses": len(feedback_list),
            "relevant_responses": len(relevant_feedback),
            "sentiment_analysis": self._perform_sentiment_analysis(relevant_feedback),
            "text_analysis": self._perform_text_analysis(relevant_feedback),
            "suggestions": self._extract_suggestions(relevant_feedback),
            "narrative_summary": self._generate_narrative_summary(relevant_feedback),
            "key_takeaways": self._extract_key_takeaways(relevant_feedback)
        }
        return analysis_results

    def _filter_relevant_feedback(self, feedback_list):
        """Filter out irrelevant/short feedback using LLM"""
        if not self.model or len(feedback_list) < 20:
            return feedback_list
            
        chunk_size = 20
        chunks = [feedback_list[i:i + chunk_size] 
                 for i in range(0, len(feedback_list), chunk_size)]
        
        relevant_feedback = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for chunk in chunks:
                futures.append(executor.submit(
                    self._filter_chunk_relevance, 
                    chunk
                ))
            
            for future in concurrent.futures.as_completed(futures):
                relevant_feedback.extend(future.result())
                
        return relevant_feedback or feedback_list

    def _filter_chunk_relevance(self, chunk):
        combined = "\n".join([f"{idx+1}. {fb}" for idx, fb in enumerate(chunk)])
        prompt = f"""
Classify each feedback as relevant (1) or irrelevant (0) based on:
- A feedback item is 'relevant' if it contains specific praise, criticism, or a suggestion.
- Items like "ok",  "no", "n/a", or very short, generic phrases are 'irrelevant'.
- Consider good,great,bad,worst as relevant and empty feedbacks as irrelevant(like 'no','none','ok') which doesn't have much significance
- Mentions specific aspects of the event
- Provides suggestions or criticisms
- Length >= 4 words

Return ONLY a comma-separated list of 1/0 values. Example: 1,0,1,1,0

Feedback:
{combined}
"""
        try:
            response = self.model.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            classifications = response.choices[0].message.content.strip().split(',')
            return [
                fb for idx, fb in enumerate(chunk) 
                if idx < len(classifications) and classifications[idx] == '1'
            ]
        except:
            return chunk

    def professionalize_text(self, text):
        """Use LLM to rewrite text professionally while avoiding instruction echoes"""
        if not text.strip():
            return text.strip()

        protected_acronyms = ["PASC", "PICT", "CP", "DSA", "AI", "ML", "NLP", "UI/UX"]

        prompt = f"""
You are a business writing assistant. Rewrite the following text to be formal, clear, and professional for inclusion in a business report. 
Keep it concise and grammatically correct. 
Do not explain anything, do not include the words "here is the rewritten content", and do not expand or modify acronyms like {', '.join(protected_acronyms)}.

ONLY return the cleaned and improved version. Do not repeat the instructions.

TEXT:
{text.strip()}
        """.strip()

        try:
            response = self.model.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            result = response.choices[0].message.content.strip()

            # Remove unwanted helper or echo phrases (case-insensitive)
            bad_phrases = [
                "here is the rewritten content",
                "i apologize",
                "please provide",
                "note that",
                "the following guidelines",
                "do not expand",
                "sincerely",
                "the revised document will",
                "let me know"
            ]
            result_lower = result.lower()
            if any(phrase in result_lower for phrase in bad_phrases):
                return text.strip()  # Fallback to original clean version
            return result

        except Exception as e:
            st.error(f"Error professionalizing text: {e}")
            return text.strip()

    # ** CORRECTION STARTS HERE **
    def _professionalize_mentions(self, mentions_text):
        """Use LLM to rewrite a list of mentions into a professional bulleted list."""
        if not mentions_text.strip() or not self.model:
            return "- " + "\n- ".join(mentions_text.splitlines())

        prompt = f"""
You are a business writing assistant for a club's event report.
The following are raw notes for the "Special Mentions" section.
Rewrite them into a formal, professional bulleted list suitable for a report.
- For each person or entity, create a separate bullet point.
- Start each bullet point with '- '.
- Ensure the tone is appreciative and formal.
- Do not add any introductory or concluding sentences. Return ONLY the bulleted list.

For example, if the input is "Harsh for mentoring, Prathamesh for attending as chief guest, PICT for providing opportunity", the output should be:
- Acknowledging Harsh for his valuable mentorship.
- Special thanks to Prathamesh for gracing the event as the chief guest.
- Gratitude to PICT for providing this opportunity.

RAW NOTES:
{mentions_text.strip()}
"""
        try:
            response = self.model.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            st.error(f"Error professionalizing mentions: {e}")
            # Fallback to a simple bulleted list
            return "- " + "\n- ".join(mentions_text.strip().splitlines())
    # ** CORRECTION ENDS HERE **
    
    def _perform_sentiment_analysis(self, feedback_list):
        sentiments = {"positive": 0, "negative": 0, "neutral": 0, "scores": [], "detailed_analysis": []}
        
        for feedback in feedback_list:
            if self.use_roberta and self.roberta_analyzer:
                try:
                    roberta_result = self.roberta_analyzer(feedback)[0]
                    roberta_sentiment = max(roberta_result, key=lambda x: x['score'])
                    
                    if roberta_sentiment['label'] == 'LABEL_2':
                        sentiment = "positive"
                        sentiments["positive"] += 1
                    elif roberta_sentiment['label'] == 'LABEL_0':
                        sentiment = "negative"
                        sentiments["negative"] += 1
                    else:
                        sentiment = "neutral"
                        sentiments["neutral"] += 1
                    
                    sentiments["scores"].append({
                        "text": feedback,
                        "roberta_label": roberta_sentiment['label'],
                        "roberta_score": roberta_sentiment['score'],
                        "sentiment": sentiment
                    })
                    
                    sentiments["detailed_analysis"].append({
                        "feedback": feedback,
                        "sentiment": sentiment,
                        "confidence": roberta_sentiment['score']
                    })
                    continue
                except Exception as e:
                    st.warning(f"RoBERTa analysis failed: {str(e)}")
            
            # Fallback to VADER + TextBlob
            vader_scores = self.vader_analyzer.polarity_scores(feedback)
            blob = TextBlob(feedback)
            textblob_polarity = blob.sentiment.polarity

            # ** CORRECTION STARTS HERE **
            # Make thresholds stricter to classify weakly positive/negative comments (potentially sarcastic) as neutral.
            if vader_scores['compound'] >= 0.4 and textblob_polarity > 0.2:
                sentiment = "positive"
                sentiments["positive"] += 1
            elif vader_scores['compound'] <= -0.4 or textblob_polarity < -0.2:
                sentiment = "negative"
                sentiments["negative"] += 1
            else:
                sentiment = "neutral"
                sentiments["neutral"] += 1
            # ** CORRECTION ENDS HERE **

            sentiments["scores"].append({
                "text": feedback,
                "vader_compound": vader_scores['compound'],
                "textblob_polarity": textblob_polarity,
                "sentiment": sentiment
            })

            sentiments["detailed_analysis"].append({
                "feedback": feedback,
                "sentiment": sentiment,
                "confidence": abs(vader_scores['compound'])
            })

        total = len(feedback_list)
        sentiments["percentages"] = {
            "positive": (sentiments["positive"] / total) * 100 if total > 0 else 0,
            "negative": (sentiments["negative"] / total) * 100 if total > 0 else 0,
            "neutral": (sentiments["neutral"] / total) * 100 if total > 0 else 0
        }
        sentiments["overall_score"] = round(
            (1 * sentiments["positive"] + 0 * sentiments["neutral"] + (-1) * sentiments["negative"]) / total, 2
        ) if total > 0 else 0

        return sentiments

    def _perform_text_analysis(self, feedback_list):
        all_text = " ".join(feedback_list)
        clean_text = re.sub(r'[^\w\s]', '', all_text.lower())
        words = clean_text.split()
        stop_words = set(["the", "a", "an", "and", "or", "in", "on", "at", "to", "for", "of", "with", "by", "is", "was", "are", "were"])
        filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
        word_freq = Counter(filtered_words)
        
        # Extract key themes using LLM
        key_themes = self._extract_key_themes(feedback_list)
        
        return {
            "total_words": len(words),
            "unique_words": len(set(words)),
            "most_common_words": word_freq.most_common(20),
            "key_themes": key_themes
        }

    def _extract_key_themes(self, feedback_list):
        combined_feedback = "\n".join(feedback_list[:50])
        prompt = f"""
Identify 3-5 key themes from this feedback. For each theme:
- Provide a short descriptive title
- Summarize the sentiment toward this theme
- Note its significance to the overall feedback

Format as:
### [Theme Title]
[Brief description] (Sentiment: [Positive/Neutral/Negative])

FEEDBACK:
{combined_feedback}

Do not include any diff/patch symbols (like '+', '-') at the start of lines. Use only standard Markdown for headings and lists.
If you want any word or heading to appear bold, start it with ** and end it with ** (Markdown bold).
Do not include any introductory or summary lines. Do not include any output or unnecessary lines like "Here is what you asked for" or similar. Only output the requested content in the specified format.
"""
        try:
            raw = self.model.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}]
            ).choices[0].message.content
            return boldify_with_llm(raw, self.model)
        except Exception as e:
            return f"Error extracting key themes: {e}"

    def _extract_suggestions(self, feedback_list):
        combined_feedback = "\n".join(feedback_list[:50])
        prompt = f"""
You are the club's Event Manager. Review the attendee feedback below and surface the top 5 actionable suggestions.

Instructions:
1. Scan all comments and infer the key themes (for example: "sound setup," "activity flow," "social media buzz," etc.).
2. Create your own headings for each theme—no pre‑defined categories.
3. Under each heading, list recommendations in descending order of frequency.
4. Keep each recommendation to one clear, implementable sentence.

FEEDBACK:
{combined_feedback}

Do not use any numbered bullet points (like 1., 2., 3., etc.) or other bullet marks (like -, *, •) at the start of lines. Only use plain text for list items. Use only standard Markdown for headings and bold.
Do not include any introductory or summary lines. Do not include any output or unnecessary lines like "Here is what you asked for" or similar. Only output the requested content in the specified format.
"""

        try:
            raw = self.model.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}]
            ).choices[0].message.content
            return boldify_with_llm(raw, self.model)
        except Exception as e:
            return f"Error extracting suggestions: {e}"

    def _generate_narrative_summary(self, feedback_list):
        full_text = "\n".join(feedback_list)
        prompt = f"""
You're the club's Event Manager preparing a one‑paragraph wrap‑up for club leadership and sponsors. From the feedback below:

1. State the overall sentiment (positive / neutral / negative).
2. Highlight the two strongest aspects of the event.
4. Mention any patterns that came up repeatedly.

Write in a clear, professional tone that a Club President and Sponsors will appreciate.

FEEDBACK:
{full_text}

Do not include any diff/patch symbols (like '+', '-') at the start of lines. Use only standard Markdown for headings and lists.
If you want any word or heading to appear bold, start it with ** and end it with ** (Markdown bold).
Do not include any introductory or summary lines. Do not include any output or unnecessary lines like "Here is what you asked for" or similar. Only output the requested content in the specified format.
"""

        try:
            raw = self.model.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}]
            ).choices[0].message.content
            return boldify_with_llm(raw, self.model)
        except Exception as e:
            return f"Error generating narrative summary: {e}"

    def _extract_key_takeaways(self, feedback_list):
        combined_feedback = "\n".join(feedback_list[:50])
        prompt = f"""
You are the club's Event Manager. Using the feedback below, generate a "Key Takeaways" section in the following format:

**Key Wins**
- **[Theme 1]:** [One-sentence summary]
- **[Theme 2]:** [One-sentence summary]

**Next Steps**
- **[Theme 3]:** [One-sentence action item]
- **[Theme 4]:** [One-sentence action item]

Only use this format. Do not add any extra commentary or formatting. Use Markdown bold (**...**) for section headings and theme names as shown.

FEEDBACK:
{combined_feedback}

Do not include any introductory or summary lines. Do not include any output or unnecessary lines like "Here is what you asked for" or similar. Only output the requested content in the specified format.
"""

        try:
            raw = self.model.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}]
            ).choices[0].message.content
            return boldify_with_llm(raw, self.model)
        except:
            return "Key takeaways analysis unavailable"
    
def boldify_with_llm(text, model):
    prompt = f'''
You are a formatting assistant. For the text below, identify all headings, section titles, and important phrases (such as the names of key themes, wins, or next steps) and wrap them in Markdown bold (**...**). Do not change the wording or structure of the text. Only add bold formatting where appropriate.

If you want to bold a word or phrase, always use two asterisks at the start and two at the end (e.g., **Heading**). Never use a single asterisk, and never use a single pair of asterisks at only one end of a word or phrase.

If a line or bullet point contains a colon (:), wrap the words before the colon in Markdown bold (**...**). For example, change "Theme Name: description" to "**Theme Name:** description".

TEXT:
{text}

Return only the formatted text.
'''
    response = model.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()