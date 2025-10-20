def suavization(p1:list[float], p2:list[float], alpha = 0.05) -> None:
    p1[0], p1[1] = p2[0]*alpha + p1[0]*(1-alpha), p2[1]*alpha + p1[1]*(1-alpha)
