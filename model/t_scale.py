

def translate(x, y, p_x, p_y):
    return (x - float(p_x), float(p_y) - y)

def translate_scale(x, y, m_d):
    p_x, p_y, sc = m_d["pos_x"], m_d["pos_y"], m_d["scale"]

    p = (x, y)

    x, y = translate(x, y, p_x, p_y)

    return  (x / float(sc), y / float(sc))