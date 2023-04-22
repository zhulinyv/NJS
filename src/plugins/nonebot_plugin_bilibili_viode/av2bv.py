from httpx import AsyncClient


_api="https://api.bilibili.com/x/web-interface/view"
async def av2bv(av_id: str) -> str:
	async with AsyncClient() as client:
		resp = await client.get(_api, params={"aid": av_id})
		if resp.status_code == 200:
			data = resp.json()
			if data["code"] == 0:
				return data["data"]["bvid"]
	return None

async def bv2av(bv_id: str)->str:
	async with AsyncClient() as client:
		resp = await client.get(_api, params={"bvid": bv_id})
		if resp.status_code == 200:
			data = resp.json()
			if data["code"] == 0:
				return str(data["data"]["aid"])
	return None