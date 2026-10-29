"""Read-only Supabase adapter. One deadline per request, no partial lists."""
import re
import time
from datetime import date, datetime
from urllib.parse import urlsplit
from uuid import UUID
import httpx
from supabase import create_client, ClientOptions
from postgrest.exceptions import APIError
from app.public.service import ResourceResult

PROFILE_COLUMNS="id,full_name,degree,summary,public_contacts,published_at"
SKILL_COLUMNS="id,profile_id,name,description,display_order,published_at"
ACADEMIC_COLUMNS="id,profile_id,activity,institution,start_date,end_date,ongoing,description,display_order,published_at"
PENDING=re.compile(r"\[[^\]]+\]|^(pendiente|por definir|tbd|todo|información pendiente)$",re.I)

def text(value, limit=None, optional=False):
    if value is None and optional: return None
    if not isinstance(value,str): raise ValueError
    value=value.strip()
    if not value or (limit and len(value)>limit) or PENDING.search(value) or any(ord(c)<32 and c not in "\n\t" for c in value): raise ValueError
    return value

def identifier(value):
    return str(UUID(value))

def contact(value):
    if not isinstance(value,dict) or set(value)!={"kind","label","value"}: raise ValueError
    kind=value["kind"]
    label=text(value["label"],200)
    raw=text(value["value"],2048)
    if any(c.isspace() for c in raw) and kind!="phone": raise ValueError
    if any(c in raw for c in "<>\r\n"): raise ValueError
    if kind=="email" and re.fullmatch(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+",raw): href="mailto:"+raw
    elif kind=="phone" and re.fullmatch(r"\+?[0-9 ()-]{7,30}",raw): href="tel:"+re.sub(r"[ ()-]","",raw)
    elif kind=="https":
        parsed=urlsplit(raw)
        if parsed.scheme!="https" or not parsed.hostname or parsed.username or parsed.password or "\\" in raw: raise ValueError
        href=raw
    else: raise ValueError
    return dict(kind=kind,label=label,value=raw,href=href)

def published(row):
    if not isinstance(row,dict): raise ValueError
    timestamp=datetime.fromisoformat(row["published_at"].replace("Z","+00:00"))
    if timestamp.tzinfo is None: raise ValueError
    return identifier(row["id"])

def profile(row):
    uid=published(row)
    contacts=row.get("public_contacts",[])
    if not isinstance(contacts,list) or len(contacts)>10: raise ValueError
    return dict(id=uid,full_name=text(row["full_name"],200),degree=text(row["degree"],200),summary=text(row.get("summary"),2000,True),public_contacts=[contact(item) for item in contacts])

def collection_item(row,academic,profile_id):
    uid=published(row)
    if identifier(row["profile_id"])!=profile_id or type(row["display_order"]) is not int: raise ValueError
    result=dict(id=uid,display_order=row["display_order"],description=text(row.get("description"),4000,True))
    if not academic:
        result["name"]=text(row["name"])
        return result
    start=date.fromisoformat(row["start_date"]) if row.get("start_date") else None
    end=date.fromisoformat(row["end_date"]) if row.get("end_date") else None
    ongoing=row["ongoing"]
    if type(ongoing) is not bool or (ongoing and end) or (start and end and end<start): raise ValueError
    result.update(activity=text(row["activity"],200),institution=text(row.get("institution"),200,True),start_date=start.isoformat() if start else None,end_date=end.isoformat() if end else None,ongoing=ongoing)
    return result

class PublicRepository:
    def __init__(self,config,*,clock=time.monotonic,client_factory=None):
        self.config=config
        self.clock=clock
        self.deadline=clock()+config.timeout
        self.client_factory=client_factory
        self.transports=[]

    def _client(self):
        remaining=self.deadline-self.clock()
        if remaining<=0: raise TimeoutError
        if self.client_factory: return self.client_factory(remaining)
        # A total wall-clock transport budget also bounds slow streaming responses.
        transport=DeadlineTransport(self.deadline,self.clock)
        http=httpx.Client(transport=transport,timeout=remaining,follow_redirects=False)
        self.transports.append(http)
        return create_client(self.config.url,self.config.key,options=ClientOptions(auto_refresh_token=False,persist_session=False,postgrest_client_timeout=remaining,httpx_client=http))

    def close(self):
        for transport in self.transports: transport.close()

    def _read(self,table,columns,validator,profile_id=None):
        if not self.config.valid: return ResourceResult("unavailable",error="configuration")
        try:
            rows=[]
            offset=0
            while True:
                client=self._client()
                query=client.table(table).select(columns).not_.is_("published_at","null")
                if profile_id is not None:
                    query=query.eq("profile_id",profile_id).order("display_order").order("id").range(offset,offset+99)
                else: query=query.limit(2)
                batch=query.retry(False).execute().data
                if not isinstance(batch,list) or (profile_id is not None and len(batch)>100): raise ValueError
                rows.extend(validator(row) for row in batch)
                if profile_id is None or len(batch)<100: break
                offset+=100
            if profile_id is None:
                if len(rows)>1: raise ValueError
                return ResourceResult("ready",rows[0]) if rows else ResourceResult("empty")
            if len({row["id"] for row in rows})!=len(rows): raise ValueError
            rows.sort(key=lambda row:(row["display_order"],row["id"]))
            return ResourceResult("ready",rows) if rows else ResourceResult("empty")
        except (TimeoutError,httpx.TimeoutException): return ResourceResult("unavailable",error="timeout")
        except APIError: return ResourceResult("unavailable",error="http")
        except (ValueError,KeyError,TypeError,AttributeError): return ResourceResult("unavailable",error="invalid")
        except Exception: return ResourceResult("unavailable",error="unavailable")

    def get_profile(self): return self._read("public_profiles",PROFILE_COLUMNS,profile)
    def list_skills(self,profile_id): return self._read("public_skills",SKILL_COLUMNS,lambda row:collection_item(row,False,profile_id),profile_id)
    def list_academic_experiences(self,profile_id): return self._read("public_academic_experiences",ACADEMIC_COLUMNS,lambda row:collection_item(row,True,profile_id),profile_id)

class DeadlineTransport(httpx.BaseTransport):
    def __init__(self,deadline,clock):
        self.deadline=deadline
        self.clock=clock
        self.transport=httpx.HTTPTransport(retries=0)

    def handle_request(self,request):
        remaining=self.deadline-self.clock()
        if remaining<=0: raise httpx.ReadTimeout("Public read deadline")
        request.extensions["timeout"]={key:remaining for key in ("connect","read","write","pool")}
        response=self.transport.handle_request(request)
        try:
            content=[]
            for chunk in response.iter_bytes():
                if self.clock()>=self.deadline: raise httpx.ReadTimeout("Public read deadline")
                content.append(chunk)
            if self.clock()>=self.deadline: raise httpx.ReadTimeout("Public read deadline")
            return httpx.Response(response.status_code,headers=response.headers,content=b"".join(content),request=request)
        finally: response.close()

    def close(self): self.transport.close()
