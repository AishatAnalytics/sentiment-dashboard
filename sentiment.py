import boto3
import json
import os
from datetime import datetime
from dotenv import load_dotenv
import anthropic

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
ses = boto3.client('ses', region_name=os.getenv('AWS_REGION'))

# Sample data simulating real mentions
SAMPLE_MENTIONS = [
    "AWS Lambda is incredible — deployed my entire backend in minutes with zero server management!",
    "Frustrated with AWS pricing — got a $500 bill and have no idea what caused it",
    "Just passed my AWS Solutions Architect Professional exam! Best certification I've done",
    "AWS outage affecting us-east-1 right now — our entire app is down",
    "The new AWS Bedrock features are game changing for AI applications",
    "AWS support took 3 days to respond to a critical ticket — unacceptable",
    "CloudFormation makes infrastructure deployment so much easier",
    "AWS costs are way too complex to understand — need better tooling",
    "Just migrated to AWS and cut our infrastructure costs by 40 percent",
    "EventBridge is underrated — building event driven architectures is so clean now",
    "AWS documentation is confusing and outdated in many places",
    "Multi region deployment on AWS is surprisingly straightforward",
    "Getting throttled by DynamoDB again — capacity planning is hard",
    "AWS free tier is perfect for learning and building side projects",
    "Route 53 failover saved us during a regional outage last night"
]

def analyze_sentiment_batch(mentions, topic):
    print(f"🤖 Analyzing sentiment for {len(mentions)} mentions about '{topic}'...")

    prompt = f"""
You are a sentiment analysis expert. Analyze the sentiment of each mention about "{topic}".

MENTIONS TO ANALYZE:
{json.dumps(mentions, indent=2)}

For each mention provide:
1. Sentiment: POSITIVE, NEGATIVE, or NEUTRAL
2. Score: -1.0 (very negative) to 1.0 (very positive)
3. Key theme: one word or short phrase
4. Intensity: LOW, MEDIUM, HIGH

Return ONLY a JSON array with this exact format for each mention:
[
  {{
    "mention_index": 0,
    "sentiment": "POSITIVE",
    "score": 0.8,
    "theme": "ease of use",
    "intensity": "HIGH"
  }}
]

Return only the JSON array, nothing else.
    """

    import time
    for attempt in range(3):
        try:
            message = client.messages.create(
                model="claude-opus-4-5",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            response_text = message.content[0].text.strip()
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
            return json.loads(response_text)
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                time.sleep(5)

    return []

def calculate_dashboard(mentions, sentiments):
    positive = [s for s in sentiments if s['sentiment'] == 'POSITIVE']
    negative = [s for s in sentiments if s['sentiment'] == 'NEGATIVE']
    neutral = [s for s in sentiments if s['sentiment'] == 'NEUTRAL']

    avg_score = sum(s['score'] for s in sentiments) / len(sentiments) if sentiments else 0

    themes = {}
    for s in sentiments:
        theme = s.get('theme', 'general')
        themes[theme] = themes.get(theme, 0) + 1

    top_themes = sorted(themes.items(), key=lambda x: x[1], reverse=True)[:5]

    overall_sentiment = 'POSITIVE' if avg_score > 0.2 else 'NEGATIVE' if avg_score < -0.2 else 'NEUTRAL'

    return {
        'total_mentions': len(mentions),
        'positive_count': len(positive),
        'negative_count': len(negative),
        'neutral_count': len(neutral),
        'positive_percentage': round(len(positive) / len(mentions) * 100, 1),
        'negative_percentage': round(len(negative) / len(mentions) * 100, 1),
        'neutral_percentage': round(len(neutral) / len(mentions) * 100, 1),
        'average_score': round(avg_score, 2),
        'overall_sentiment': overall_sentiment,
        'top_themes': top_themes
    }

def print_dashboard(topic, dashboard, sentiments, mentions):
    print("\n" + "="*50)
    print(f"📊 SENTIMENT DASHBOARD — {topic.upper()}")
    print("="*50)
    print(f"\nOverall Sentiment: {dashboard['overall_sentiment']}")
    print(f"Average Score: {dashboard['average_score']} (-1 to +1)")
    print(f"\nTotal Mentions Analyzed: {dashboard['total_mentions']}")
    print(f"✅ Positive: {dashboard['positive_count']} ({dashboard['positive_percentage']}%)")
    print(f"❌ Negative: {dashboard['negative_count']} ({dashboard['negative_percentage']}%)")
    print(f"➖ Neutral:  {dashboard['neutral_count']} ({dashboard['neutral_percentage']}%)")
    print(f"\nTop Themes:")
    for theme, count in dashboard['top_themes']:
        print(f"  • {theme}: {count} mentions")
    print("\nSample Analysis:")
    for i, (mention, sentiment) in enumerate(zip(mentions[:3], sentiments[:3])):
        emoji = '✅' if sentiment['sentiment'] == 'POSITIVE' else '❌' if sentiment['sentiment'] == 'NEGATIVE' else '➖'
        print(f"\n{emoji} {sentiment['sentiment']} ({sentiment['score']})")
        print(f"   \"{mention[:80]}...\"" if len(mention) > 80 else f"   \"{mention}\"")
        print(f"   Theme: {sentiment.get('theme', 'N/A')} | Intensity: {sentiment.get('intensity', 'N/A')}")

def send_dashboard_email(topic, dashboard):
    message = f"""
SENTIMENT DASHBOARD REPORT
===========================
Topic: {topic}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OVERALL SENTIMENT: {dashboard['overall_sentiment']}
Average Score: {dashboard['average_score']} (-1.0 to +1.0)

BREAKDOWN:
✅ Positive: {dashboard['positive_count']} mentions ({dashboard['positive_percentage']}%)
❌ Negative: {dashboard['negative_count']} mentions ({dashboard['negative_percentage']}%)
➖ Neutral:  {dashboard['neutral_count']} mentions ({dashboard['neutral_percentage']}%)

TOP THEMES:
{chr(10).join([f"• {theme}: {count} mentions" for theme, count in dashboard['top_themes']])}

Sentiment Dashboard 📊
    """

    ses.send_email(
        Source=os.getenv('YOUR_EMAIL'),
        Destination={'ToAddresses': [os.getenv('YOUR_EMAIL')]},
        Message={
            'Subject': {'Data': f"📊 Sentiment Report — {topic} — {dashboard['overall_sentiment']}"},
            'Body': {'Text': {'Data': message}}
        }
    )
    print(f"\n📧 Dashboard sent to {os.getenv('YOUR_EMAIL')}")

def run():
    print("📊 Real-Time Sentiment Dashboard")
    print("=================================\n")

    topic = os.getenv('TOPIC', 'AWS Cloud Computing')

    # Step 1 — Get mentions
    print(f"Step 1: Loading mentions about '{topic}'...")
    mentions = SAMPLE_MENTIONS
    print(f"Loaded {len(mentions)} mentions\n")

    # Step 2 — Analyze sentiment
    print("Step 2: Analyzing sentiment with Claude AI...")
    sentiments = analyze_sentiment_batch(mentions, topic)

    if not sentiments:
        print("❌ Sentiment analysis failed")
        return

    # Step 3 — Calculate dashboard
    print("\nStep 3: Calculating dashboard metrics...")
    dashboard = calculate_dashboard(mentions, sentiments)

    # Step 4 — Print dashboard
    print_dashboard(topic, dashboard, sentiments, mentions)

    # Step 5 — Send email
    print("\nStep 5: Sending dashboard report...")
    send_dashboard_email(topic, dashboard)

    # Save report
    report = {
        'timestamp': datetime.now().isoformat(),
        'topic': topic,
        'dashboard': dashboard,
        'sentiments': sentiments
    }

    with open('sentiment_report.json', 'w') as f:
        json.dump(report, f, indent=2)

    print("📄 Report saved to sentiment_report.json")
    print("\n✅ Sentiment Dashboard complete!")

if __name__ == "__main__":
    run()