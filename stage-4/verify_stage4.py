#!/usr/bin/env python3
import concurrent.futures,json,subprocess,time,urllib.error,urllib.request
PORT=18084;BASE=f"http://127.0.0.1:{PORT}"
def c(method,path,body=None,tok=None,key=None):
 d=None if body is None else json.dumps(body).encode();h={}
 if body is not None:h["Content-Type"]="application/json"
 if tok:h["Authorization"]="Bearer "+tok
 if key:h["Idempotency-Key"]=key
 try:
  with urllib.request.urlopen(urllib.request.Request(BASE+path,data=d,headers=h,method=method),timeout=5) as r:return r.status,json.loads(r.read() or b"null")
 except urllib.error.HTTPError as e:return e.code,json.loads(e.read())
def must(v,m):assert v,m
subprocess.run(["docker","build","-t","pocketful-stage4-check","."],check=True,stdout=subprocess.DEVNULL)
cid=subprocess.check_output(["docker","run","-d","--rm","-e",f"PORT={PORT}","-p",f"{PORT}:{PORT}","pocketful-stage4-check"],text=True).strip()
try:
 for _ in range(50):
  try:
   if c("GET","/health")[0]==200:break
  except Exception:time.sleep(.1)
 f={"currency":"EUR","minor_units":2,"settlement_operator_ids":["a"],"users":[{"id":"a","email":"a@x","password":"password1","display_name":"A","handle":"a","balance":1000},{"id":"b","email":"b@x","password":"password1","display_name":"B","handle":"b","balance":1000},{"id":"c","email":"c@x","password":"password1","display_name":"C","handle":"c","balance":1000}],"payments":[],"requests":[]}
 must(c("POST","/_test/reset",f)[0]==204,"reset")
 ta=c("POST","/auth/login",{"email":"a@x","password":"password1"})[1]["token"];tb=c("POST","/auth/login",{"email":"b@x","password":"password1"})[1]["token"]
 p=c("POST","/payments",{"to_handle":"b","amount":400,"note":"x","visibility":"private"},ta,"p")[1];must(p["refund_of"] is None,"null link")
 key="r";r=c("POST",f"/payments/{p['payment_id']}/refunds",{"amount":150},tb,key);must(r[0]==201 and r[1]["refund_of"]==p["payment_id"],"refund");must(c("POST",f"/payments/{p['payment_id']}/refunds",{"amount":150},tb,key)[0]==200,"refund replay")
 must(c("POST",f"/payments/{r[1]['payment_id']}/refunds",{"amount":1},ta,"bad")[1]["error"]["code"]=="invalid_refund_target","refund target")
 eff=p["created_at"];body={"expected_revision":1,"amount":100,"effective_at":eff,"reason":"too low"};must(c("POST",f"/payments/{p['payment_id']}/corrections",body,ta,"floor")[1]["error"]["code"]=="refund_exceeds_payment","floor")
 body={"corrections":[{"payment_id":p["payment_id"],"expected_revision":1,"amount":250,"effective_at":eff,"reason":"adjust"}]};first=c("POST","/correction-batches",body,ta,"batch");must(first[0]==201 and first[1]["revisions"][0]["correction_batch_id"]==first[1]["correction_batch_id"],"batch");must(c("POST","/correction-batches",body,ta,"batch")[0]==200,"batch replay")
 exp=c("GET","/_test/export")[1];must(c("POST","/_test/import",exp)[0]==204,"import");must(c("POST","/correction-batches",body,ta,"batch")[0]==200,"post import replay")
 print("PASS: stage4 refunds/floors/links/batches/replay/import")
finally:subprocess.run(["docker","stop",cid],stdout=subprocess.DEVNULL)
