import os
import json
import requests
from datetime import datetime

DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
DEEPSEEK_URL = 'https://api.deepseek.com/chat/completions'

# ─── Base DeepSeek call ───────────────────────────────────────────────────────

def call_deepseek(system_prompt, user_prompt, max_tokens=2000):
    response = requests.post(
        DEEPSEEK_URL,
        headers={
            'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
            'Content-Type': 'application/json'
        },
        json={
            'model': 'deepseek-chat',
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user',   'content': user_prompt}
            ],
            'max_tokens': max_tokens,
            'temperature': 0.7
        },
        timeout=90
    )
    data = response.json()
    return data['choices'][0]['message']['content'].strip()

def safe_json(text):
    try:
        clean = text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean)
    except Exception:
        return None

# ─── Agent 1: Trend Hunter ───────────────────────────────────────────────────

def trend_hunter():
    headlines = []
    feeds = [
        'https://feeds.feedburner.com/TechCrunch',
        'https://www.theverge.com/rss/index.xml',
        'https://feeds.arstechnica.com/arstechnica/technology-lab',
    ]
    try:
        import feedparser
        for url in feeds:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:4]:
                    headlines.append(entry.title)
            except Exception:
                pass
    except ImportError:
        pass

    headlines_text = '\n'.join(headlines[:12]) if headlines else 'No external headlines available today.'

    result = call_deepseek(
        """You are a Trend Hunter for Neo Vision Hub — a blog covering AI, Trading, and Gaming.
Your job: find the single best trending topic to write about today.
Return ONLY valid JSON, no extra text:
{"topic": "...", "niche": "AI or Trading or Gaming", "reason": "why trending in 1 sentence", "keywords": ["kw1","kw2","kw3"]}""",
        f"Today's tech headlines:\n{headlines_text}\n\nPick the best topic for Neo Vision Hub."
    )

    data = safe_json(result)
    if not data:
        data = {
            "topic": "How DeepSeek AI is Changing the Future of Work in 2025",
            "niche": "AI",
            "reason": "DeepSeek AI is the most discussed AI model globally right now",
            "keywords": ["DeepSeek AI", "AI future of work", "AI 2025"]
        }
    return data

# ─── Agent 2: CEO ─────────────────────────────────────────────────────────────

def ceo_agent(trend_data):
    result = call_deepseek(
        """You are the CEO of Neo Vision Hub. You assign tasks to your content team.
Given a trending topic, create a clear content brief.
Return ONLY valid JSON, no extra text:
{"title": "...", "angle": "unique angle", "target_audience": "...", "tone": "...", "word_count": 900}""",
        f"Trending topic data: {json.dumps(trend_data)}\nCreate a content brief."
    )
    data = safe_json(result)
    if not data:
        data = {
            "title": trend_data.get('topic', 'AI Trends 2025'),
            "angle": "Beginner-friendly deep dive",
            "target_audience": "Young professionals interested in tech and finance",
            "tone": "informative, engaging, and accessible",
            "word_count": 900
        }
    return data

# ─── Agent 3: Content Writer ──────────────────────────────────────────────────

def content_writer(ceo_brief, trend_data):
    result = call_deepseek(
        """You are a professional Content Writer for Neo Vision Hub.
Write a complete, high-quality blog post in English.
Structure: engaging intro → 3-4 H2 sections → practical tips → conclusion with CTA.
Format in clean HTML: use <h2>, <p>, <ul>, <li>, <strong>, <em> tags.
Make it informative, SEO-friendly, and genuinely useful.
Return ONLY the HTML content — no markdown fences, no extra text.""",
        f"Brief: {json.dumps(ceo_brief)}\nTopic data: {json.dumps(trend_data)}\nWrite the full blog post now.",
        max_tokens=3000
    )
    return result

# ─── Agent 4: SEO Expert ─────────────────────────────────────────────────────

def seo_expert(topic, title, content_preview):
    result = call_deepseek(
        """You are an SEO Expert for Neo Vision Hub.
Return ONLY valid JSON, no extra text:
{
  "meta_title": "max 60 chars",
  "meta_description": "max 160 chars",
  "focus_keyword": "main keyword",
  "secondary_keywords": ["kw1","kw2","kw3"],
  "labels": ["Label1","Label2","Label3"],
  "slug": "url-friendly-slug"
}""",
        f"Topic: {topic}\nTitle: {title}\nContent preview: {content_preview[:400]}"
    )
    data = safe_json(result)
    if not data:
        data = {
            "meta_title": title[:60],
            "meta_description": f"Discover everything about {topic}. Read the full guide on Neo Vision Hub.",
            "focus_keyword": topic,
            "secondary_keywords": [],
            "labels": ["AI", "Technology", "Neo Vision Hub"],
            "slug": title.lower().replace(' ', '-')[:50]
        }
    return data

# ─── Agent 5: Image Agent ─────────────────────────────────────────────────────

def image_agent(topic, title):
    prompt = f"{topic} futuristic digital technology concept professional blog header"
    encoded = requests.utils.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1200&height=630&nologo=true&seed=42"
    return {
        "url": url,
        "alt": title,
        "prompt": prompt
    }

# ─── Agent 6: Editor ─────────────────────────────────────────────────────────

def editor_agent(content, seo_data):
    kw = seo_data.get('focus_keyword', '')
    result = call_deepseek(
        f"""You are the Chief Editor of Neo Vision Hub.
Review and improve this blog post HTML:
- Ensure the focus keyword "{kw}" appears naturally 2-3 times
- Improve headline appeal
- Fix any HTML issues
- Make intro more hook-worthy
- Ensure the conclusion has a clear call-to-action
Return ONLY the improved HTML — no extra text.""",
        content,
        max_tokens=3000
    )
    return result

# ─── Agent 7: Social Media ────────────────────────────────────────────────────

def social_media_agent(title, topic, meta_description):
    result = call_deepseek(
        """You are the Social Media Manager for Neo Vision Hub.
Create platform-specific captions for the new blog post.
Return ONLY valid JSON, no extra text:
{
  "twitter": "tweet with hashtags, max 270 chars",
  "instagram": "instagram caption with line breaks and hashtags",
  "linkedin": "professional linkedin post, 2-3 sentences"
}""",
        f"Blog title: {title}\nTopic: {topic}\nDescription: {meta_description}"
    )
    data = safe_json(result)
    if not data:
        data = {
            "twitter": f"Just published: {title} — Read now on Neo Vision Hub! #AI #Technology #NeoVisionHub",
            "instagram": f"New post just dropped! 🔥\n\n{title}\n\nLink in bio 👆\n\n#AI #Technology #NeoVisionHub",
            "linkedin": f"We just published a new in-depth post: '{title}'. Check it out on Neo Vision Hub for insights on {topic}."
        }
    return data

# ─── Agent 8: Marketing ──────────────────────────────────────────────────────

def marketing_agent(title, topic):
    result = call_deepseek(
        """You are the Marketing Agent for Neo Vision Hub.
Create a promotion strategy for the new blog post.
Return ONLY valid JSON, no extra text:
{
  "channels": ["channel1","channel2","channel3"],
  "best_times": {"twitter": "time", "instagram": "time", "linkedin": "time"},
  "hashtags": ["#tag1","#tag2","#tag3","#tag4","#tag5","#tag6"],
  "promotion_tips": ["tip1","tip2","tip3"]
}""",
        f"Post title: {title}\nTopic: {topic}"
    )
    data = safe_json(result)
    if not data:
        data = {
            "channels": ["Twitter/X", "Instagram", "LinkedIn"],
            "best_times": {"twitter": "9 AM & 6 PM", "instagram": "7 PM", "linkedin": "8 AM"},
            "hashtags": ["#AI", "#Technology", "#NeoVisionHub", "#Trading", "#Gaming", "#Tech2025"],
            "promotion_tips": ["Share in relevant Facebook groups", "Engage with comments in first hour", "Pin tweet for 24 hours"]
        }
    return data

# ─── Blogger Publisher ────────────────────────────────────────────────────────

def publish_to_blogger(title, content, seo_data, image_data):
    token   = os.environ.get('BLOGGER_ACCESS_TOKEN', '')
    blog_id = os.environ.get('BLOGGER_BLOG_ID', '')

    if not token or not blog_id:
        return {"status": "skipped", "reason": "Blogger credentials set nahi hain — manually publish karein"}

    img_html = f'<img src="{image_data["url"]}" alt="{image_data["alt"]}" style="width:100%;max-width:800px;height:auto;border-radius:8px;margin-bottom:24px;" />\n'
    full_html = img_html + content

    try:
        resp = requests.post(
            f'https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts/',
            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
            json={'title': title, 'content': full_html, 'labels': seo_data.get('labels', [])},
            timeout=30
        )
        data = resp.json()
        if 'url' in data:
            return {"status": "published", "url": data['url']}
        return {"status": "error", "reason": str(data)}
    except Exception as e:
        return {"status": "error", "reason": str(e)}

# ─── Main Pipeline ────────────────────────────────────────────────────────────

def run_pipeline(update_step, status):
    # 1. Trend Hunter
    update_step('trend', 'working')
    trend = trend_hunter()
    update_step('trend', 'done', {
        'topic': trend['topic'],
        'niche': trend['niche'],
        'reason': trend['reason']
    })

    # 2. CEO
    update_step('ceo', 'working')
    brief = ceo_agent(trend)
    update_step('ceo', 'done', {
        'title':    brief['title'],
        'angle':    brief['angle'],
        'audience': brief['target_audience']
    })

    # 3. Content Writer
    update_step('writer', 'working')
    content = content_writer(brief, trend)
    word_count = len(content.split())
    update_step('writer', 'done', {
        'preview':     content[:180] + '...',
        'word_count':  f"{word_count} words"
    })

    # 4. SEO Expert
    update_step('seo', 'working')
    seo = seo_expert(trend['topic'], brief['title'], content)
    update_step('seo', 'done', seo)

    # 5. Image Agent
    update_step('image', 'working')
    image = image_agent(trend['topic'], brief['title'])
    update_step('image', 'done', {'url': image['url']})

    # 6. Editor
    update_step('editor', 'working')
    final_content = editor_agent(content, seo)
    update_step('editor', 'done', {'status': 'Post reviewed and polished'})

    # 7. Social Media
    update_step('social', 'working')
    social = social_media_agent(brief['title'], trend['topic'], seo.get('meta_description', ''))
    update_step('social', 'done', social)

    # 8. Marketing
    update_step('marketing', 'working')
    marketing = marketing_agent(brief['title'], trend['topic'])
    update_step('marketing', 'done', marketing)

    # Publish
    publish = publish_to_blogger(brief['title'], final_content, seo, image)

    # Save result
    status['result'] = {
        'title':            brief['title'],
        'topic':            trend['topic'],
        'meta_title':       seo.get('meta_title', ''),
        'meta_description': seo.get('meta_description', ''),
        'focus_keyword':    seo.get('focus_keyword', ''),
        'labels':           seo.get('labels', []),
        'image_url':        image['url'],
        'social':           social,
        'marketing':        marketing,
        'publish':          publish,
        'content':          final_content
    }
    status['running'] = False
    status['finished_at'] = datetime.now().isoformat()
