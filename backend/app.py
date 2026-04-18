import praw
import time, threading, hashlib, re
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime

try:
    import snscrape.modules.twitter as sntwitter
    SNSCRAPE_AVAILABLE = True
except ImportError:
    SNSCRAPE_AVAILABLE = False

app = Flask(__name__)
CORS(app)

REDDIT_CLIENT_ID     = "YOUR_CLIENT_ID"
REDDIT_CLIENT_SECRET = "YOUR_CLIENT_SECRET"
REDDIT_USER_AGENT    = "Swipely/1.0"

CACHE_TTL    = 300
MAX_ARTICLES = 80
MIN_SCORE    = 50

SUBREDDITS = {
    "worldnews":"World","news":"World",
    "technology":"Tech","gadgets":"Tech","artificial":"Tech",
    "science":"Science","space":"Science",
    "business":"Business","economics":"Business","stocks":"Business",
    "sports":"Sports","soccer":"Sports","nba":"Sports",
    "movies":"Culture","television":"Culture",
    "health":"Health","medicine":"Health",
}

TWITTER_ACCOUNTS = {
    "Reuters":"World","AP":"World","BBCBreaking":"World","CNN":"World",
    "TechCrunch":"Tech","verge":"Tech","WIRED":"Tech",
    "WSJ":"Business","Forbes":"Business",
    "NASAHubble":"Science",
    "espn":"Sports","BBCSport":"Sports",
    "RollingStone":"Culture",
    "WHO":"Health",
}

ACCENT = {
    "World":"#10b981","Tech":"#6366f1","Science":"#3b82f6",
    "Business":"#f59e0b","Sports":"#ef4444","Culture":"#ec4899","Health":"#8b5cf6",
}

FALLBACKS = {
    "World":   "https://images.unsplash.com/photo-1524055988636-436cfa46e59e?w=600&q=80",
    "Tech":    "https://images.unsplash.com/photo-1518770660439-4636190af475?w=600&q=80",
    "Science": "https://images.unsplash.com/photo-1446776877081-d282a0f896e2?w=600&q=80",
    "Business":"https://images.unsplash.com/photo-1611532736597-de2d4265fba3?w=600&q=80",
    "Sports":  "https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=600&q=80",
    "Culture": "https://images.unsplash.com/photo-1574267432553-4b4628081c31?w=600&q=80",
    "Health":  "https://images.unsplash.com/photo-1576671081837-49000212a370?w=600&q=80",
}

cache = {
    "articles":[],"breaking":[],
    "last_updated":0,"stats":{"reddit":0,"twitter":0},"errors":[],
}

def uid(s): return int(hashlib.md5(s.encode()).hexdigest()[:8], 16)
def time_ago(ts):
    d=int(time.time()-ts)
    if d<60: return f"{d}s ago"
    if d<3600: return f"{d//60}m ago"
    if d<86400: return f"{d//3600}h ago"
    return f"{d//86400}d ago"

def reddit_img(post, cat):
    try:
        if hasattr(post,"preview") and "images" in post.preview:
            rs=post.preview["images"][0]["resolutions"]
            if rs:
                b=min(rs,key=lambda r:abs(r["width"]-600))
                return b["url"].replace("&amp;","&")
    except: pass
    if post.url and any(post.url.lower().endswith(e) for e in [".jpg",".jpeg",".png",".webp"]):
        return post.url
    if post.thumbnail and post.thumbnail.startswith("http") and "reddit" not in post.thumbnail:
        return post.thumbnail
    return FALLBACKS.get(cat, FALLBACKS["World"])

def tweet_img(tweet, cat):
    try:
        if tweet.media:
            for m in tweet.media:
                url=getattr(m,"fullUrl",None) or getattr(m,"previewUrl",None)
                if url: return url
    except: pass
    return FALLBACKS.get(cat, FALLBACKS["World"])

def clean_tweet(text):
    text=re.sub(r"http\S+","",text)
    text=re.sub(r"@\w+","",text)
    text=re.sub(r"#\w+","",text)
    return text.strip()

def fetch_reddit():
    print("  Fetching Reddit...")
    articles,seen=[],set()
    try:
        reddit=praw.Reddit(client_id=REDDIT_CLIENT_ID,client_secret=REDDIT_CLIENT_SECRET,user_agent=REDDIT_USER_AGENT)
        for sub,cat in SUBREDDITS.items():
            try:
                for post in reddit.subreddit(sub).hot(limit=8):
                    if post.stickied or post.id in seen or post.score<MIN_SCORE: continue
                    seen.add(post.id)
                    desc=post.selftext.strip()
                    if desc in ["","[removed]","[deleted]"]:
                        desc=f"{post.score:,} upvotes · {post.num_comments:,} comments on r/{sub}"
                    articles.append({
                        "id":uid(post.id),"source_id":post.id,
                        "source":f"r/{sub}","source_type":"reddit",
                        "category":cat,"headline":post.title,
                        "desc":desc[:300]+("…" if len(desc)>300 else ""),
                        "img":reddit_img(post,cat),
                        "time":time_ago(post.created_utc),"time_ts":post.created_utc,
                        "color":ACCENT.get(cat,"#6366f1"),
                        "score":post.score,"comments":post.num_comments,
                        "url":f"https://reddit.com{post.permalink}",
                    })
            except Exception as e:
                cache["errors"].append(f"r/{sub}: {e}")
        cache["stats"]["reddit"]=len(articles)
        print(f"    Reddit: {len(articles)} posts")
    except Exception as e:
        cache["errors"].append(f"Reddit init: {e}")
    return articles

def fetch_twitter():
    if not SNSCRAPE_AVAILABLE: return []
    print("  Fetching Twitter...")
    articles,seen=[],set()
    for handle,cat in TWITTER_ACCOUNTS.items():
        try:
            count=0
            for tweet in sntwitter.TwitterUserScraper(handle).get_items():
                if count>=5: break
                if tweet.content.startswith("RT @"): continue
                text=clean_tweet(tweet.content or "")
                if len(text)<40 or text in seen: continue
                seen.add(text)
                headline=text[:120]+("…" if len(text)>120 else "")
                articles.append({
                    "id":uid(str(tweet.id)),"source_id":str(tweet.id),
                    "source":f"@{handle}","source_type":"twitter",
                    "category":cat,"headline":headline,"desc":text[:300],
                    "img":tweet_img(tweet,cat),
                    "time":time_ago(tweet.date.timestamp()),"time_ts":tweet.date.timestamp(),
                    "color":ACCENT.get(cat,"#1da1f2"),
                    "score":(tweet.likeCount or 0)+(tweet.retweetCount or 0)*3,
                    "comments":tweet.replyCount or 0,
                    "url":f"https://twitter.com/{handle}/status/{tweet.id}",
                })
                count+=1
        except Exception as e:
            cache["errors"].append(f"@{handle}: {e}")
    cache["stats"]["twitter"]=len(articles)
    print(f"    Twitter: {len(articles)} tweets")
    return articles

def fetch_breaking():
    items=[]
    try:
        reddit=praw.Reddit(client_id=REDDIT_CLIENT_ID,client_secret=REDDIT_CLIENT_SECRET,user_agent=REDDIT_USER_AGENT)
        for sub in ["worldnews","news","technology","science"]:
            for p in reddit.subreddit(sub).new(limit=4):
                if p.score>20: items.append(f"🔴 {p.title}")
    except: pass
    if SNSCRAPE_AVAILABLE:
        for handle in ["Reuters","AP","BBCBreaking","TechCrunch"]:
            try:
                for tweet in sntwitter.TwitterUserScraper(handle).get_items():
                    t=clean_tweet(tweet.content or "")
                    if len(t)>50 and not tweet.content.startswith("RT @"):
                        items.append(f"⚡ {t[:150]}")
                        break
            except: pass
    return items[:20] or ["🔴 Live feed loading…"]

def refresh_loop():
    while True:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Refreshing cache...")
        cache["errors"]=[]
        all_a=fetch_reddit()+fetch_twitter()
        seen,deduped=set(),[]
        for a in all_a:
            if a["source_id"] not in seen:
                seen.add(a["source_id"]); deduped.append(a)
        deduped.sort(key=lambda x:(-x["time_ts"],-x["score"]))
        cache["articles"]=deduped[:MAX_ARTICLES]
        cache["breaking"]=fetch_breaking()
        cache["last_updated"]=time.time()
        print(f"Done: {len(deduped)} articles")
        time.sleep(CACHE_TTL)

threading.Thread(target=refresh_loop,daemon=True).start()

@app.route("/api/news")
def get_news():
    cat=request.args.get("category","All")
    src=request.args.get("source","all")
    limit=min(int(request.args.get("limit",30)),MAX_ARTICLES)
    offset=int(request.args.get("offset",0))
    w=0
    while not cache["articles"] and w<15: time.sleep(1);w+=1
    arts=cache["articles"]
    if cat!="All": arts=[a for a in arts if a["category"]==cat]
    if src!="all": arts=[a for a in arts if a["source_type"]==src]
    page=arts[offset:offset+limit]
    return jsonify({"ok":True,"total":len(arts),"count":len(page),"offset":offset,"articles":page,"last_updated":cache["last_updated"],"sources":cache["stats"]})

@app.route("/api/breaking")
def get_breaking():
    w=0
    while not cache["breaking"] and w<10: time.sleep(1);w+=1
    return jsonify({"ok":True,"items":cache["breaking"] or ["🔴 Loading…"]})

@app.route("/api/categories")
def get_categories():
    arts=cache["articles"]
    cats={"All":len(arts)}
    for a in arts: cats[a["category"]]=cats.get(a["category"],0)+1
    order=["All","World","Tech","Business","Science","Sports","Culture","Health"]
    return jsonify({"ok":True,"categories":[{"name":k,"count":cats.get(k,0)} for k in order if k in cats]})

@app.route("/api/status")
def get_status():
    age=int(time.time()-cache["last_updated"]) if cache["last_updated"] else None
    return jsonify({"ok":True,"cached":len(cache["articles"]),"last_updated":cache["last_updated"],"age_sec":age,"sources":cache["stats"],"errors":cache["errors"][-5:],"snscrape":SNSCRAPE_AVAILABLE})

@app.route("/")
def index():
    return "<h2>Swipely API</h2><ul><li><a href='/api/news'>/api/news</a></li><li><a href='/api/status'>/api/status</a></li></ul>"

if __name__ == "__main__":
    print("Swipely backend starting on port 5000...")
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
