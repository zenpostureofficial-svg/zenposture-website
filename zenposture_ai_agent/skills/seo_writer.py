"""
SEO / GEO Writer Skill
Generates SEO metadata, GEO-targeted content, blog posts, product descriptions.
"""

SEO_SYSTEM = """You are an expert SEO and GEO (Generative Engine Optimization) copywriter for ZenPosture.

BRAND: ZenPosture | zenposture.in | ₹499 products
PRODUCTS: Posture Corrector, Postpartum Belt, Compression Gym Belt
TARGET MARKET: India — metro cities (Mumbai, Delhi, Bengaluru, Chennai, Hyderabad)
TARGET AUDIENCE: Office workers 25-40, new moms, gym-goers

SEO PRINCIPLES YOU FOLLOW:
- Use long-tail, buyer-intent keywords
- Include local Indian context (cities, price in INR, Indian lifestyle)
- Write for both Google and AI answer engines (GEO: clear, factual, quotable)
- Meta titles: under 60 chars | Meta descriptions: 150-160 chars
- Use H1/H2/H3 structure in blog content
- Include schema-friendly FAQ sections
- Natural keyword density (1.5-2.5%), never stuffed
"""


def generate_product_seo(product_name, product_description, target_keywords,
                         ollama_chat_fn, model):
    """Generate complete SEO package for a product."""
    messages = [
        {"role": "system", "content": SEO_SYSTEM},
        {"role": "user", "content": f"""
Generate a complete SEO package for this product:

PRODUCT: {product_name}
DESCRIPTION: {product_description}
TARGET KEYWORDS: {', '.join(target_keywords)}

Return in this exact format:
META TITLE: ...
META DESCRIPTION: ...
H1: ...
H2s: (list 3-5)
FOCUS KEYWORD: ...
SECONDARY KEYWORDS: (list 5)
SCHEMA FAQ:
Q1: ...
A1: ...
Q2: ...
A2: ...
Q3: ...
A3: ...
PRODUCT DESCRIPTION (150 words, SEO-optimized):
...
"""}
    ]
    return ollama_chat_fn(messages, model, temperature=0.5)


def generate_blog_post(topic, keywords, word_count=600, ollama_chat_fn=None, model=None):
    """Write a full SEO blog post."""
    messages = [
        {"role": "system", "content": SEO_SYSTEM},
        {"role": "user", "content": f"""
Write a {word_count}-word SEO blog post for zenposture.in:

TOPIC: {topic}
TARGET KEYWORDS: {', '.join(keywords)}

Structure:
- H1 title (keyword-rich, compelling)
- Introduction (hook + problem statement)
- 3-4 H2 sections with practical content
- FAQ section (3 questions)
- Conclusion with CTA to zenposture.in

Tone: Helpful, conversational, Indian context. Not overly medical.
"""}
    ]
    return ollama_chat_fn(messages, model, temperature=0.6)


def generate_ad_copy(product, platform, tone, brief, ollama_chat_fn, model):
    """Write ad copy for Meta/Google."""
    messages = [
        {"role": "system", "content": SEO_SYSTEM},
        {"role": "user", "content": f"""
Write {platform} ad copy for ZenPosture {product}.
Tone: {tone}
Brief: {brief}

Return:
PRIMARY HEADLINE (30 chars max):
SECONDARY HEADLINE (30 chars max):
DESCRIPTION (90 chars max):
BODY COPY (125 words):
CTA:
"""}
    ]
    return ollama_chat_fn(messages, model, temperature=0.7)


def generate_captions(product, count, platform, tone, ollama_chat_fn, model):
    """Generate social media captions."""
    messages = [
        {"role": "system", "content": SEO_SYSTEM},
        {"role": "user", "content": f"""
Write {count} {platform} captions for ZenPosture {product}.
Tone: {tone}
Include: relevant hashtags, emojis, call to action (link in bio → zenposture.in)
Price mention: ₹499

Make each caption unique with a different hook angle.
"""}
    ]
    return ollama_chat_fn(messages, model, temperature=0.8)
