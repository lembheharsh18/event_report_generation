import matplotlib.pyplot as plt
from io import BytesIO

def create_sentiment_chart(sentiment_data):
    labels = list(sentiment_data.keys())
    sizes = list(sentiment_data.values())
    colors = ['#4CAF50', '#FFC107', '#F44336']
    
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', 
           startangle=90, textprops={'fontsize': 10})
    ax.axis('equal')
    
    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return buf

def create_attendance_chart(students, faculty, guests):
    labels = ['Students', 'Faculty', 'Guests']
    sizes = [students, faculty, guests]
    colors = ['#66b3ff','#99ff99','#ffcc99']
    
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
           startangle=90, textprops={'fontsize': 10})
    ax.axis('equal')
    
    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return buf

def create_word_frequency_chart(word_freq_data):
    words, frequencies = zip(*word_freq_data)
    plt.figure(figsize=(10, 6))
    plt.barh(words, frequencies, color='#2196F3')
    plt.xlabel('Frequency')
    plt.title('Top 20 Most Common Words')
    plt.gca().invert_yaxis()
    
    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return buf