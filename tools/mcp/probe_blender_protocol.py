import asyncio,json
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
async def probe():
 server=StdioServerParameters(command='mcp-for-blender',env={'DISABLE_TELEMETRY':'true','BLENDER_HOST':'127.0.0.1','BLENDER_PORT':'9876'})
 async with stdio_client(server) as (read,write):
  async with ClientSession(read,write) as session:
   init=await session.initialize();tools=await session.list_tools()
   result={'package':'mcp-for-blender','version_pin':'2.2.4','initialize':'PASS','server':init.serverInfo.model_dump(),'tools':[{'name':t.name,'description':t.description[:180] if t.description else ''} for t in tools.tools],'blender_addon_connected':False,'paid_generation_submitted':False,'global_codex_registered':False,'note':'Isolated stdio protocol test only. No Blender scene, GUI or animation edit was attempted.'}
   Path(__file__).resolve().parents[2].joinpath('docs/mcp-research/blender-protocol-test.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
asyncio.run(asyncio.wait_for(probe(),timeout=30))
