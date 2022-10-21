import asyncio
from hashlib import new
import aiohttp
import jinja2 
import os
import json
import yaml
import sys

### Templates
fl = jinja2.FileSystemLoader('templates')
env = jinja2.Environment(loader=fl)
template = env.get_template('payload.j2')

### 
with open(sys.argv[1]) as monf:
    fyaml = yaml.safe_load(monf)
    monitors = fyaml['monitors']
    namespace = fyaml['namespace']
    tenant = fyaml['tenant']

### Vars
token = os.getenv('F5XC_TOKEN')
env = "console.ves.volterra.io"

### API destination
url = "https://{}.{}/api/synthetic_monitor/namespaces/{}/http_monitors" # tenant, env, namespace
headers = {'Authorization':'APIToken {}'.format(token)}
results = {"create":[], "update": [], "fail":[]}


async def req(payload):
  async with aiohttp.ClientSession() as session:
      r = await session.post(url.format(tenant, env, namespace),data=payload, headers=headers, ssl=True)
  # print(r.status)
  return r.status

async def cm():
  tasks = []
  for mon in monitors:
    payload = template.render(monitor=mon)
    print(payload)
    tasks.append(asyncio.create_task(req(payload)))

  responses = await asyncio.gather(*tasks)

  for mon,resp in zip(monitors, responses):
    if resp == 200:
      results["create"].append(mon['name'])
    elif resp == 409:
      results["update"].append(mon['name'])
    else:
      results["fail"].append(mon['name'])
  
  return results

    


  


completed = asyncio.run(cm())

####OUTPUT
print("\n")
print("CREATED")
for i in completed['create']:
  print(i)
print("\n")
print("UPDATED")
for i in completed['update']:
  print(i)
print("\n")
print("FAILED")
for i in completed['fail']:
  print(i)
print("\n")