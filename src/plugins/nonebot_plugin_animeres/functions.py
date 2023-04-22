from lxml import etree
from typing import List
from .cartoon import BaseMethod, add_method, Cartoon, Cartoons

@add_method
class DMHY(BaseMethod):
    name: str = "动漫花园"
    base_url: str = "https://dmhy.anoneko.com"

    async def __call__(self, keyword: str) -> Cartoons:
        async with self.session.get("/topics/list", params={"keyword": keyword}) as res:
            data: List[etree._Element] = etree.HTML(await res.text(), etree.HTMLParser()).xpath("//table[@class='tablesorter']//tbody//tr")
            return Cartoons(Cartoon(
                title=value.xpath("string(./td[@class='title'])").replace("\n", ""),
                tag=value.xpath("string(./td/a//font)"),
                magnet=value.xpath("string(./td/a[@class='download-arrow arrow-magnet']/@href)").split("&")[0],
                size=value.xpath("./td")[4].text,
            ) for value in data)

                