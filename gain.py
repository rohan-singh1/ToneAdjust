def gain(s, m):
    if (s < 0.1):
        return 0
    db = 3.0 * (s - m)
    return pow(10.0, db / 20.0)

