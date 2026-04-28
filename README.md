# Real-Time Sentiment Dashboard 📊

Analyzes mentions about any topic using Claude AI and generates sentiment trend dashboards.

## The Problem
Companies have no idea what people are saying about their products online in real time. By the time someone reads through mentions manually the moment has passed.

## What It Does
- Ingests text mentions about any topic
- Sends all mentions to Claude AI for sentiment scoring
- Scores each mention from -1.0 (very negative) to +1.0 (very positive)
- Identifies themes and intensity levels
- Calculates overall sentiment dashboard
- Sends detailed report via email

## Sample Results
Topic: AWS Cloud Computing
Overall Sentiment: POSITIVE
Average Score: 0.24

Breakdown:
Positive: 8 mentions (53.3%)
Negative: 5 mentions (33.3%)
Neutral: 2 mentions (13.3%)

Top Themes:
- pricing transparency
- certification
- ease of use
- reliability
- documentation

## Tech Stack
- Python 3
- Claude API (Anthropic)
- AWS SES
- boto3

## Key Concepts Demonstrated
- Real-time sentiment analysis
- AI powered text classification
- Dashboard metrics calculation
- AWS Kinesis streaming pattern (production version)

## How To Run
- Clone the repo
- pip install boto3 anthropic python-dotenv
- Add your keys to .env
- Set TOPIC in .env to any topic you want
- Run py sentiment.py

## Part of my 30 cloud projects in 30 days series
Follow along: https://www.linkedin.com/in/aishatolatunji/