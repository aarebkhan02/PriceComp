# from fastapi import FastAPI
# from pydantic import BaseModel
# from tavily import TavilyClient
# import os
# import re
# import html

# app = FastAPI()

# tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# class ProductRequest(BaseModel):
#     product: str


# def extract_price(text):
#     match = re.search(r"₹\s?[\d,]+", text)
#     if match:
#         return int(re.sub(r"[^\d]", "", match.group()))
#     return None


# def detect_platform(url):
#     if "amazon.in" in url:
#         return "Amazon"
#     if "flipkart.com" in url:
#         return "Flipkart"
#     if "meesho.com" in url:
#         return "Meesho"
#     return None


# @app.get("/")
# def home():
#     return {"message": "SmartPrice API running"}


# @app.post("/search")
# def search(data: ProductRequest):

#     response = tavily.search(
#         query=f"{data.product} price buy online India "
#               f"site:amazon.in OR site:flipkart.com OR site:meesho.com",
#         search_depth="basic",
#         max_results=8
#     )

#     results = response.get("results", [])

#     products = []
#     seen = set()

#     for r in results:

#         title = r.get("title", "")
#         content = r.get("content", "")
#         url = r.get("url", "")

#         if not url or url in seen:
#             continue

#         seen.add(url)

#         platform = detect_platform(url)
#         if not platform:
#             continue

#         price = extract_price(title + content)
#         if not price:
#             continue

#         products.append({
#             "title": html.escape(title),
#             "price": price,
#             "url": html.escape(url),
#             "platform": platform
#         })

#     products.sort(key=lambda x: x["price"])

#     return {"results": products}

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from tavily import TavilyClient
import os
import re
import html

# ---------------- APP ----------------

app = FastAPI(title="SmartPrice API")

# ---------------- CORS ----------------

origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- TAVILY ----------------

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# ---------------- REQUEST MODEL ----------------

class ProductRequest(BaseModel):
    product: str


# ---------------- HELPERS ----------------

def extract_price(text):
    match = re.search(r"₹\s?[\d,]+", text)
    if match:
        return int(re.sub(r"[^\d]", "", match.group()))
    return None


def detect_platform(url):
    if "amazon.in" in url:
        return "Amazon"
    if "flipkart.com" in url:
        return "Flipkart"
    if "meesho.com" in url:
        return "Meesho"
    return None


# ---------------- ROUTES ----------------

@app.get("/")
def home():
    return {"message": "SmartPrice API running 🚀"}


@app.post("/search")
def search(data: ProductRequest):

    response = tavily.search(
        query=f"{data.product} price buy online India "
              f"site:amazon.in OR site:flipkart.com OR site:meesho.com",
        search_depth="basic",
        max_results=8
    )

    results = response.get("results", [])

    products = []
    seen_urls = set()

    for r in results:

        title = r.get("title", "")
        content = r.get("content", "")
        url = r.get("url", "")

        if not url or url in seen_urls:
            continue

        seen_urls.add(url)

        platform = detect_platform(url)
        if not platform:
            continue

        price = extract_price(title + content)

        if not price:
            continue

        products.append({
            "title": html.escape(title),
            "price": price,
            "url": html.escape(url),
            "platform": platform
        })

    products.sort(key=lambda x: x["price"])

    return {
        "product": data.product,
        "results": products
    }