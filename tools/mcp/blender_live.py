import asyncio,json,sys,base64
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
async def run():
 params=StdioServerParameters(command='mcp-for-blender',env={'DISABLE_TELEMETRY':'true','BLENDER_HOST':'127.0.0.1','BLENDER_PORT':'9876'})
 async with stdio_client(params) as (read,write):
  async with ClientSession(read,write) as s:
   await s.initialize()
   if sys.argv[1]=='schemas':
    ts=await s.list_tools();out={t.name:t.inputSchema for t in ts.tools if t.name in ['look','execute_blender_code','get_scene_info']};print(json.dumps(out));Path(str(Path(__file__).resolve().parents[2]/'dist/mcp-proof/tool-schemas.json')).write_text(json.dumps(out));return
   tool=sys.argv[1]
   args=json.loads(sys.argv[2]) if len(sys.argv)>2 and tool!='execute-file' else {}
   if tool=='execute-file':tool='execute_blender_code';args={'code':Path(sys.argv[2]).read_text(),'user_prompt':'Build and inspect the Bilge reference-animation study'}
   result=await s.call_tool(tool,args)
   failed=bool(result.isError)
   for i,c in enumerate(result.content):
    if c.type=='text':
     print(c.text)
     failed|=c.text.startswith('Error executing code:')
    elif c.type=='image':
     p=Path(__file__).resolve().parents[2]/f'dist/mcp-proof/live-{i}.png';p.write_bytes(base64.b64decode(c.data));print('SAVED_IMAGE',p)
   if failed:raise RuntimeError('Blender MCP tool reported an error')
asyncio.run(asyncio.wait_for(run(),timeout=80))
