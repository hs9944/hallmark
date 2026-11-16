import json, sys, time, urllib.request, urllib.error, re
B="https://developers.hostinger.com/api/ecommerce/v1/stores/store_01M4XH3NVCQKCKQ2T7T5RGYESF"
RAW="https://raw.githubusercontent.com/hs9944/hallmark/charmie-product-image/charmie-designs/"
def call(m,p,body=None):
    data=json.dumps(body).encode() if body is not None else None
    req=urllib.request.Request(B+p,data=data,method=m,headers={"Content-Type":"application/json","Accept":"application/json","User-Agent":"curl/8.5.0"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req,timeout=60) as r:
                t=r.read().decode(); return json.loads(t) if t.strip() else {}
        except urllib.error.HTTPError as e:
            txt=e.read().decode()
            if e.code==429: time.sleep(int(e.headers.get('Retry-After','10'))+1); continue
            raise SystemExit(f"HTTP {e.code} {m} {p}: {txt[:600]}")
    raise SystemExit("rate limited too long")
# index: file|Name: charms
rows=[l.strip().split('|',1) for l in open(sys.argv[1]) if '|' in l]
targets=sys.argv[2:]   # file prefixes like 05
existing={p['title']:p['id'] for p in call("GET","/products?per_page=50")['data'] if p['status']=='published'}
for fn,desc in rows:
    num=fn[:2]
    if targets and num not in targets: continue
    name,charms=desc.split(':',1); name=name.strip(); charms=charms.strip()
    sku=f"D{int(num)+21}"
    description=(f"{name} charm piece from Charmiè. Five hand-picked charms on our signature gold-tone ribbed curb chain: {charms}. "
                 "Lobster clasp with extender. Choose it as a bracelet, anklet or necklace.")
    img=RAW+fn
    if name in existing:
        pid=existing[name]; print(f"{num} {name}: exists {pid}, refreshing image + description")
        call("PATCH",f"/products/{pid}",{"description":description})
    else:
        r=call("POST","/products/physical",{"name":name,"price":59900,"seo_settings":{"slug":re.sub(r'[^a-z0-9-]','',name.lower().replace(' ','-'))}})
        pid=r['product']['id']; print(f"{num} {name}: created {pid}")
        before={v['id'] for v in call("GET",f"/products/{pid}/variants")['data']}
        for piece,code,amt in (("Bracelet","BR",59900),("Anklet","AN",69900),("Necklace","NE",79900)):
            call("POST",f"/products/{pid}/variants",{"sku":f"{sku}-{code}","options":[{"name":"Piece","value":piece}],"prices":[{"amount":amt}],"inventory_quantity":1,"manage_inventory":True})
        vs=call("GET",f"/products/{pid}/variants")['data']
        for v in vs:
            if v['id'] in before and v.get('title')=='Default':
                call("DELETE",f"/products/{pid}/variants/{v['id']}"); print("   removed default variant")
        call("PATCH",f"/products/{pid}",{"description":description,"status":"published"})
    im=call("POST",f"/products/{pid}/images",{"image_url":img,"is_thumbnail":True})
    print("   image:",im.get('url','?')[:90])
    vs=call("GET",f"/products/{pid}/variants")['data']
    print("   variants:",[(v['sku'],v['prices'][0]['amount']) for v in vs])
    time.sleep(1)
