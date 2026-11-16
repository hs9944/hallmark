import json, sys, os, urllib.request, urllib.error
UA="curl/8.5.0"
def req(url,method,headers=None,data=None):
    r=urllib.request.Request(url,data=data,method=method,headers={"User-Agent":UA,**(headers or {})})
    try:
        with urllib.request.urlopen(r,timeout=120) as resp: return resp.status, resp.read().decode(errors='replace')
    except urllib.error.HTTPError as e: return e.code, e.read().decode(errors='replace')
st,body=req("https://developers.hostinger.com/api/hosting/v1/files/upload-urls","POST",{"Content-Type":"application/json","Accept":"application/json"},json.dumps({"username":"u888169918","domain":"shopcharmie.in"}).encode())
if st!=200: sys.exit(f"upload-urls HTTP {st}: {body[:400]}")
u=json.loads(body); base=u['url'].rstrip('/'); H={"X-Auth":u['auth_key'],"X-Auth-Rest":u['rest_auth_key'],"Tus-Resumable":"1.0.0"}
root=sys.argv[1]; files=sys.argv[2:]
ok=0
for rel in files:
    data=open(os.path.join(root,rel),'rb').read()
    url=f"{base}/{rel}?override=true"
    st,b=req(url,"POST",{**H,"Upload-Length":str(len(data)),"Upload-Offset":"0"})
    if st not in (200,201): print(f"FAIL create {rel}: HTTP {st} {b[:200]}"); continue
    st,b=req(url,"PATCH",{**H,"Upload-Offset":"0","Content-Type":"application/offset+octet-stream"},data)
    if st not in (200,204): print(f"FAIL patch {rel}: HTTP {st} {b[:200]}"); continue
    ok+=1; print(f"ok {rel} ({len(data)} B)")
print(f"{ok}/{len(files)} uploaded")
