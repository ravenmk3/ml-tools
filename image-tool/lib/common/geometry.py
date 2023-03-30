def max_size_with_aspect_ratio(w: int, h: int, w_scale: int, h_scale: int) -> tuple[int, int]:
    if w == h and w_scale == h_scale:
        return (w, h)
    if w_scale > w or h_scale > h:
        raise RuntimeError('source too small')

    src_ratio = w / h
    dst_ratio = w_scale / h_scale
    if src_ratio > dst_ratio:
        n = int(h / h_scale)
    else:
        n = int(w / w_scale)
    return (w_scale * n, h_scale * n)


def max_rect_with_aspect_ratio(w: int, h: int, w_scale: int, h_scale: int,
                               horizontal: str = 'center', vertical: str = 'center') -> tuple[int, int, int, int]:
    dst_w, dst_h = max_size_with_aspect_ratio(w, h, w_scale, h_scale)
    left = 0
    top = 0
    right = dst_w
    bottom = dst_h
    print(dst_w, dst_h)

    if horizontal == 'left':
        pass
    elif horizontal == 'right':
        left = w - dst_w
        right = w
    elif horizontal == 'center':
        if w != dst_w:
            left = int((w - dst_w) / 2)
            right = left + dst_w
    else:
        raise RuntimeError('horizontal alignment not support: ' + horizontal)

    if vertical == 'top':
        pass
    elif vertical == 'bottom':
        top = h - dst_h
        bottom = h
    elif vertical == 'center':
        if h != dst_h:
            top = int((h - dst_h) / 2)
            bottom = top + dst_h
    else:
        raise RuntimeError('vertical alignment not support: ' + vertical)

    return (left, top, right, bottom)
