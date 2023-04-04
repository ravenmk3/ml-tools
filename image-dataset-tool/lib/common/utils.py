import hashlib


def md5_hex(val: any) -> str:
    if not isinstance(val, bytes):
        if not isinstance(val, str):
            val = str(val)
        val = val.encode('utf-8')
    h = hashlib.md5()
    h.update(val)
    return h.hexdigest().lower()


def write_lines(filename: str, lines: list[str], encoding: str = 'ascii'):
    data = '\n'.join(lines).encode(encoding)
    with open(filename, 'wb+') as fp:
        fp.write(data)
