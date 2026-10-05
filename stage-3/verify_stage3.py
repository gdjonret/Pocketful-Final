#!/usr/bin/env python3
"""Independent Stage 3 smoke/regression checks against a disposable container."""
import concurrent.futures, json, subprocess, time, urllib.error, urllib.parse, urllib.request

PORT=18083; BASE=f"http://127.0.0.1:{PORT}"
def call(method,path,body=None,token=None,key=None):
    data=None if body is None else json.dumps(body).encode(); h={}
    if body is not None:h["Content-Type"]="application/json"
    if token:h["Authorization"]="Bearer "+token
    if key:h["Idempotency-Key"]=key
    try:
        with urllib.request.urlopen(urllib.request.Request(BASE+path,data=data,headers=h,method=method),timeout=5) as r:return r.status, json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:return e.code,json.loads(e.read())
def must(x,msg="assertion"): assert x,msg
subprocess.run(["docker","build","-t","pocketful-stage3-check","."],check=True,stdout=subprocess.DEVNULL)
cid=subprocess.check_output(["docker","run","-d","--rm","-e",f"PORT={PORT}","-p",f"{PORT}:{PORT}","pocketful-stage3-check"],text=True).strip()
try:
  for _ in range(60):
    try:
      if call("GET","/health")[0]==200:break
    except Exception:time.sleep(.1)
  past="2025-01-01T00:00:00+00:00"
  fixture={"currency":"EUR","minor_units":2,"users":[{"id":"a","email":"a@x","password":"password1","display_name":"A","handle":"a","balance":900},{"id":"b","email":"b@x","password":"password1","display_name":"B","handle":"b","balance":100}],"payments":[{"id":"seed","from_user_id":"a","to_user_id":"b","amount":100,"note":"seed","visibility":"public","created_at":past}],"requests":[]}
  must(call("POST","/_test/reset",fixture)[0]==204)
  ta=call("POST","/auth/login",{"email":"a@x","password":"password1"})[1]["token"]
  tb=call("POST","/auth/login",{"email":"b@x","password":"password1"})[1]["token"]
  must(call("GET","/me?as_of=2024-01-01T00:00:00%2B00:00",token=ta)[1]["balance"]==1000,"opening")
  st=call("GET","/statement?limit=1",token=ta)[1]; must(st["opening_balance"]==1000 and st["closing_balance"]==900 and st["entries"][0]["balance_after"]==900,"statement")
  snap=st["snapshot"]
  eff=time.strftime("%Y-%m-%dT%H:%M:%S+00:00",time.gmtime(time.time()-10))
  body={"expected_revision":1,"amount":50,"effective_at":eff,"reason":"correct"}
  rs=[]
  with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex: rs=list(ex.map(lambda k:call("POST","/payments/seed/corrections",body,ta,k),["c1","c2"]))
  must(sorted(x[0] for x in rs)==[201,409],"concurrent stale revision")
  must(call("GET","/me",token=ta)[1]["balance"]==950 and call("GET","/me",token=tb)[1]["balance"]==50,"correction balances")
  must(call("GET","/statement?snapshot="+snap+"&limit=1",token=ta)[1]["closing_balance"]==900,"snapshot stability")
  must(len(call("GET","/payments/seed/revisions",token=tb)[1]["revisions"])==2,"revision permission")
  exp=call("GET","/_test/export")[1]; must(call("POST","/_test/import",exp)[0]==204,"round trip")
  # Emulate a Stage 2 export: closed authorization and capture links exist, but
  # Stage 3 ledger metadata does not. Import must reconstruct its historical hold.
  fixture["payments"]=[]; fixture["users"][0]["balance"]=100; fixture["users"][1]["balance"]=0
  must(call("POST","/_test/reset",fixture)[0]==204)
  ta=call("POST","/auth/login",{"email":"a@x","password":"password1"})[1]["token"]
  tb=call("POST","/auth/login",{"email":"b@x","password":"password1"})[1]["token"]
  auth=call("POST","/authorizations",{"to_handle":"b","amount":60},ta,"auth-migrate")[1]
  time.sleep(.01)
  must(call("POST",f"/authorizations/{auth['authorization_id']}/capture",{},tb,"capture-migrate")[0]==201)
  old=call("GET","/_test/export")[1]
  for field in ("opening_balances","revisions","hold_events","reset_at"): old["state"].pop(field,None)
  for value in old["state"]["authorizations"].values(): value.pop("closed_at",None)
  must(call("POST","/_test/import",old)[0]==204,"stage2 migration")
  at=urllib.parse.quote(auth["created_at"],safe="")
  historical=call("GET",f"/me?as_of={at}",token=ta)[1]
  must((historical["total"],historical["held"],historical["available"])==(100,60,40),"imported hold history")
  print("PASS: stage3 timestamps/opening/statements/snapshots/corrections/concurrency/import")
finally: subprocess.run(["docker","stop",cid],stdout=subprocess.DEVNULL)
