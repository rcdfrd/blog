import logging
import socket
import struct
from typing import Tuple, Union

logger = logging.getLogger(__name__)


def int3(data: bytes, offset: int) -> int:
    return data[offset] + (data[offset + 1] << 8) + \
        (data[offset + 2] << 16)


def int4(data: bytes, offset: int) -> int:
    return data[offset] + (data[offset + 1] << 8) + \
        (data[offset + 2] << 16) + (data[offset + 3] << 24)


class QQWry(object):
    def __init__(self) -> None:
        self.data: bytes = b''
        self.index_begin = -1
        self.index_end = -1
        self.index_count = -1

    def load_file(self, filename: Union[str, bytes]) -> bool:
        """加载qqwry.dat文件。成功返回True，失败返回False。
        参数filename可以是qqwry.dat的文件名（str类型），也可以是bytes类型的文件内容。"""

        if type(filename) == bytes:
            self.data = filename
            filename = 'memory data'
        elif type(filename) == str:
            try:
                with open(filename, 'br') as f:
                    self.data = f.read()
            except Exception as e:
                logger.error(f'{filename} open failed：{str(e)}')
                return False

            if self.data is None:
                return False
        else:
            return False

        if len(self.data) < 8:
            logger.error(f'{filename} load failed, file only {len(self.data)} bytes')
            return False

        # index range
        index_begin = int4(self.data, 0)
        index_end = int4(self.data, 4)
        if index_begin > index_end or \
                (index_end - index_begin) % 7 != 0 or \
                index_end + 7 > len(self.data):
            return False
        self.index_begin = index_begin
        self.index_end = index_end
        self.index_count = (index_end - index_begin) // 7 + 1

        return True

    def __get_addr(self, offset: int) -> Tuple[str, str]:
        # mode 0x01, full jump
        mode = self.data[offset]
        if mode == 1:
            offset = int3(self.data, offset + 1)
            mode = self.data[offset]

        # country
        if mode == 2:
            off1 = int3(self.data, offset + 1)
            c = self.data[off1:self.data.index(b'\x00', off1)]
            offset += 4
        else:
            c = self.data[offset:self.data.index(b'\x00', offset)]
            offset += len(c) + 1

        # province
        if self.data[offset] == 2:
            offset = int3(self.data, offset + 1)
        p = self.data[offset:self.data.index(b'\x00', offset)]

        return c.decode('gb18030', errors='replace'), \
            p.decode('gb18030', errors='replace')

    def lookup(self, ip_str: str) -> Union[Tuple[str, str], None]:
        """查找IP地址的归属地。
           找到则返回一个含有两个字符串的元组，如：('国家', '省份')
           没有找到结果，则返回一个None。"""
        ip = struct.unpack(">I", socket.inet_aton(ip_str.strip()))[0]

        try:
            return self.__raw_search(ip)
        except Exception as e:
            if not self.is_loaded():
                logger.error('Error: qqwry.dat not loaded yet.')
            else:
                logger.error(f'Error: {str(e)}')

    def __raw_search(self, ip: int) -> Union[Tuple[str, str], None]:
        l: int = 0
        r: int = self.index_count

        while r - l > 1:
            m = (l + r) >> 1
            offset = self.index_begin + m * 7
            new_ip = int4(self.data, offset)

            if ip < new_ip:
                r = m
            else:
                l = m

        offset = self.index_begin + 7 * l
        ip_begin = int4(self.data, offset)

        offset = int3(self.data, offset + 4)
        ip_end = int4(self.data, offset)

        return self.__get_addr(offset + 4) if ip_begin <= ip <= ip_end else None

    def is_loaded(self) -> bool:
        return self.__raw_search is not None

    def get_last_one(self) -> Union[Tuple[str, str], None]:
        """返回最后一条数据，最后一条通常为数据的版本号。"""
        try:
            offset = int3(self.data, self.index_end + 4)
            return self.__get_addr(offset + 4)
        except Exception as e:
            logger.error(f'Error: {str(e)}')
            return None


def is_valid_ip(ip: str) -> bool:
    """Returns true if the given string is a well-formed IP address.
    Supports IPv4 and IPv6.
    """
    if not ip or '\x00' in ip:
        return False
    try:
        res = socket.getaddrinfo(ip, 0, socket.AF_UNSPEC,
                                 socket.SOCK_STREAM,
                                 0, socket.AI_NUMERICHOST)
        return bool(res)
    except socket.gaierror as e:
        if e.args[0] == socket.EAI_NONAME:
            return False
        raise


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        fn = 'qqwry.dat'
        q = QQWry()
        q.load_file(fn)

        for _ip in sys.argv[1:]:
            if not is_valid_ip(_ip):
                print(f'无效的ip地址：{_ip}')
                continue
            s = q.lookup(_ip)
            print('%s\n%s' % (_ip, s))
    else:
        print('请以查询ip作为参数运行')
