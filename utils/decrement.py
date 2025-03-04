import re

def decrement(match):
    num = int(match.group(1))
    #print(f"numb: {num}")
    if num == 0:
        return match.group(0)

    return f"_p{num}_"