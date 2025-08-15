import asyncio, httpx, argparse, csv, time, urllib.parse
from selectolax.parser import HTMLParser

SEM=10
DELAY=0.2

async def fetch(client, url):
    try:
        r=await client.get(url, timeout=20)
        r.raise_for_status()
        return r.text
    except Exception:
        return None

async def allowed(client, url):
    # Minimal robots.txt disallow check
    p = urllib.parse.urlparse(url)
    robots = f"{p.scheme}://{p.netloc}/robots.txt"
    try:
        r = await client.get(robots, timeout=10)
        if r.status_code != 200:
            return True
        disallow = []
        for line in r.text.splitlines():
            line=line.strip()
            if line.lower().startswith("disallow:"):
                disallow.append(line.split(":",1)[1].strip())
        for d in disallow:
            if url.startswith(f"{p.scheme}://{p.netloc}{d}"):
                return False
        return True
    except Exception:
        return True

async def scrape(urls, selector, out):
    sem=asyncio.Semaphore(SEM)
    async with httpx.AsyncClient(headers={'User-Agent':'DemoScraper/1.0'}) as client:
        rows=[]
        async def worker(url):
            async with sem:
                if not await allowed(client, url):
                    rows.append((url, 'BLOCKED_BY_ROBOTS'))
                    return
                html=await fetch(client,url); await asyncio.sleep(DELAY)
                if not html: rows.append((url,'')); return
                tree=HTMLParser(html)
                node=tree.css_first(selector)
                rows.append((url, node.text().strip() if node else ''))
        await asyncio.gather(*[worker(u) for u in urls])
    with open(out,'w',newline='',encoding='utf-8') as f:
        w=csv.writer(f); w.writerow(['url','text']); w.writerows(rows)
    print('Saved', out)

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--urls', required=True)
    ap.add_argument('--selector', required=True)
    ap.add_argument('--out', default='results.csv')
    args = ap.parse_args()
    urls=[u.strip() for u in open(args.urls, encoding='utf-8') if u.strip()]
    asyncio.run(scrape(urls, args.selector, args.out))
