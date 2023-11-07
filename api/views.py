import json
from typing import Any

from django.http import HttpRequest
from ninja import NinjaAPI
from ninja.renderers import JSONRenderer

from .qqwry import QQWry, is_valid_ip


class MyRenderer(JSONRenderer):
    def render(self, request: HttpRequest, data: Any, *, response_status: int) -> Any:
        if type(data) == str:
            self.media_type = "text/plain"
            return data
        return json.dumps(data, cls=self.encoder_class, **self.json_dumps_params)


api = NinjaAPI(renderer=MyRenderer())


@api.get("/v1/ip")
def query(request: HttpRequest):
    ip = request.META.get("HTTP_CF_CONNECTING_IP", "") or request.META.get("HTTP_X_FORWARDED_FOR",
                                                                           "") or request.META.get('REMOTE_ADDR', "")
    if is_valid_ip(ip):
        if ":" in ip:
            return ip
        q = QQWry()
        q.load_file('./api/qqwry.dat')
        return f'{ip} {q.lookup(ip)[0]} {q.lookup(ip)[1]}'
    else:
        return '无效的ip地址'


@api.get("/v1/ip/{ip}")
def query_ip(request: HttpRequest, ip: str):
    if is_valid_ip(ip):
        if ":" in ip:
            return '暂不支持ipv6查询'
        q = QQWry()
        q.load_file('./api/qqwry.dat')
        return f'{q.lookup(ip)[0]} {q.lookup(ip)[1]}'
    else:
        return '无效的ip地址'
