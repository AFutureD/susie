def get_str_len_for_int(n: int) -> int:
    import math

    if n > 0:
        return int(math.log10(n)) + 1
    elif n == 0:
        return 1
    else:
        return int(math.log10(-n)) + 2
