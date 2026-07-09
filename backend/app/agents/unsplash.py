"""Unsplash 图片搜索 Agent — LLM翻译景点名 → 英文检索"""

import json, httpx
from langchain_openai import ChatOpenAI
from app.agents.state import TravelState
from app.core.config import settings


async def unsplash_agent(state: TravelState) -> dict:
    attractions = state.get("attractions") or []
    if not attractions or not settings.unsplash_access_key:
        return {"unsplash_images": [], "messages": []}

    city = state.get("destination", "")
    names = [a.get("name", "") for a in attractions[:8] if a.get("name")]

    # 一次LLM调用，批量翻译所有景点名
    llm = ChatOpenAI(model=settings.llm_model, api_key=settings.llm_api_key,
                     base_url=settings.llm_base_url, temperature=0, max_tokens=500)
    prompt = f"""Translate these Chinese tourist attractions into English search keywords for Unsplash.
Return ONLY a JSON array of strings, one per attraction. Each string should be 3-5 English words suitable for photo search.

City: {city}
Attractions: {json.dumps(names, ensure_ascii=False)}

Example output format: ["Beijing Forbidden City palace", "Chengdu ancient street traditional"]

Return JSON array only, no other text:"""
    resp = await llm.ainvoke(prompt)
    try:
        # 提取JSON
        text = resp.content.strip()
        if text.startswith("```"): text = text.split("\n", 1)[1].rsplit("\n", 1)[0]
        queries = json.loads(text)
    except:
        queries = [f"{city} {n} China travel" for n in names]  # fallback

    # 搜索 Unsplash
    images = []
    used_urls = set()

    async with httpx.AsyncClient(timeout=10) as client:
        for name, query in zip(names, queries):
            added = False
            # 精确查询 → 城市fallback
            for q in [query, f"{city} travel"]:
                if added: break
                try:
                    resp = await client.get(
                        "https://api.unsplash.com/search/photos",
                        params={"query": q, "per_page": 3, "orientation": "landscape"},
                        headers={"Authorization": f"Client-ID {settings.unsplash_access_key}"},
                    )
                    results = resp.json().get("results", [])
                    for img in results:
                        url = img["urls"]["small"]
                        if url not in used_urls:
                            used_urls.add(url)
                            images.append({
                                "name": name, "image_url": url,
                                "image_regular": img["urls"]["regular"],
                                "photographer": img["user"]["name"],
                                "unsplash_link": img["links"]["html"],
                            })
                            added = True
                            break
                except Exception:
                    continue

    return {"unsplash_images": images, "messages": []}