# tiny-chess-01: fresh rebuild of the trial-6 design (see REBUILD.md).
# 0x88 board, PVS + TT + NMP(R=4) + LMR + killer ordering, PeSTO
# middlegame eval, fixed 60000-node budget. Packed by the kit's compress.
import json
import os
import sys
import urllib.error
import urllib.request

L = 60000
M = [0, 82, 337, 365, 477, 1025, 0]
S = [[(ord(c) - 107) * 5 for c in s] for s in (
    "kkkkkkkkuuuuuuuummoqqommllmppmllkkkookkkljikkijllmmggmmlkkkkkkkk",
    "aceeeecacgkkkkgcekmnnmkeelnoonleeknoonkeelmnnmlecgkllkgcaceeeeca",
    "giiiiiigikkkkkkiiklmmlkiillmmlliikmmmmkiimmmmmmiilkkkkligiiiiiig",
    "kkkkkkkklmmmmmmljkkkkkkjjkkkkkkjjkkkkkkjjkkkkkkjjkkkkkkjkkkllkkk",
    "giijjiigikkkkkkiikllllkijkllllkjkkllllkjilllllkiiklkkkkigiijjiig",
    "eccaacceeccaacceeccaacceeccaaccegeecceegiggggggiookkkkoooqmkkmqo",
)]
KN = [33, 31, 18, 14, -33, -31, -18, -14]
KI = [16, 15, 17, 1, -16, -15, -17, -1]
BD = [15, 17, -15, -17]
RD = [16, 1, -16, -1]
CM = [15] * 128
CM[0] = 13
CM[7] = 14
CM[112] = 7
CM[119] = 11
CM[4] = 12
CM[116] = 3

x = 1


def rnd():
    global x
    x = (x * 1103515245 + 12345) & ((1 << 64) - 1)
    return x


Z = [[rnd() for _ in range(128)] for _ in range(13)]
ZS = rnd()
ZC = [rnd() for _ in range(16)]
ZE = [rnd() for _ in range(8)]

b = [0] * 128
T = 1
C = 15
E = -1
k = [4, 116]
H = 0
y = [0]
st = []
ns = []
N = 0
D = [None] * 262144
Y = [[0] * 128 for _ in range(13)]
K = [0] * 128


class Ab(Exception):
    pass


def atk(q, by):
    for t in (q - 15 * by, q - 17 * by):
        if not (t & 0x88) and b[t] == by:
            return True
    for o in KN:
        t = q + o
        if not (t & 0x88) and b[t] == 2 * by:
            return True
    for o in KI:
        t = q + o
        if not (t & 0x88) and b[t] == 6 * by:
            return True
    for o in BD:
        t = q + o
        while not (t & 0x88):
            if b[t]:
                if b[t] == 3 * by or b[t] == 5 * by:
                    return True
                break
            t += o
    for o in RD:
        t = q + o
        while not (t & 0x88):
            if b[t]:
                if b[t] == 4 * by or b[t] == 5 * by:
                    return True
                break
            t += o
    return False


def gen(q=0):
    ms = []
    for s in range(128):
        if s & 0x88:
            continue
        p = b[s]
        if p * T <= 0:
            continue
        a = abs(p)
        if a == 1:
            d = 16 * T
            t = s + d
            if not (t & 0x88) and b[t] == 0:
                if (s >> 4) == (6 if T > 0 else 1):
                    for pr in (5, 4, 3, 2):
                        ms.append(s | t << 7 | pr << 14)
                elif q == 0:
                    ms.append(s | t << 7)
                    if (s >> 4) == (1 if T > 0 else 6) and b[s + 2 * d] == 0:
                        ms.append(s | (s + 2 * d) << 7)
            for t in (s + d - 1, s + d + 1):
                if t & 0x88:
                    continue
                if b[t] * T < 0 or t == E:
                    if (s >> 4) == (6 if T > 0 else 1):
                        for pr in (5, 4, 3, 2):
                            ms.append(s | t << 7 | pr << 14)
                    else:
                        ms.append(s | t << 7)
        elif a == 2 or a == 6:
            for o in KN if a == 2 else KI:
                t = s + o
                if t & 0x88:
                    continue
                if b[t] == 0:
                    if q == 0:
                        ms.append(s | t << 7)
                elif b[t] * T < 0:
                    ms.append(s | t << 7)
            if a == 6 and q == 0:
                if T > 0:
                    if C & 1 and b[5] == 0 and b[6] == 0 and not atk(4, -1) and not atk(5, -1) and not atk(6, -1):
                        ms.append(4 | 6 << 7)
                    if C & 2 and b[3] == 0 and b[2] == 0 and b[1] == 0 and not atk(4, -1) and not atk(3, -1) and not atk(2, -1):
                        ms.append(4 | 2 << 7)
                else:
                    if C & 4 and b[117] == 0 and b[118] == 0 and not atk(116, 1) and not atk(117, 1) and not atk(118, 1):
                        ms.append(116 | 118 << 7)
                    if C & 8 and b[115] == 0 and b[114] == 0 and b[113] == 0 and not atk(116, 1) and not atk(115, 1) and not atk(114, 1):
                        ms.append(116 | 114 << 7)
        else:
            ds = BD if a == 3 else RD if a == 4 else BD + RD
            for o in ds:
                t = s + o
                while not (t & 0x88):
                    if b[t] == 0:
                        if q == 0:
                            ms.append(s | t << 7)
                    else:
                        if b[t] * T < 0:
                            ms.append(s | t << 7)
                        break
                    t += o
    return ms


def make(m):
    global C, E, H, T
    f = m & 127
    t = (m >> 7) & 127
    pr = m >> 14
    p = b[f]
    c = b[t]
    epc = -1
    if abs(p) == 1 and t == E:
        epc = t - 16 * T
        c = b[epc]
    st.append((m, p, c, C, E, H, k[0], k[1], epc))
    if E != -1:
        H ^= ZE[E & 7]
    H ^= ZC[C]
    H ^= Z[p + 6][f]
    if c:
        H ^= Z[c + 6][epc if epc != -1 else t]
    C = C & CM[f] & CM[t]
    H ^= ZC[C]
    b[f] = 0
    np = pr * T if pr else p
    b[t] = np
    H ^= Z[np + 6][t]
    if epc != -1:
        b[epc] = 0
    if abs(p) == 6 and abs(t - f) == 2:
        if t == 6:
            rf, rt = 7, 5
        elif t == 2:
            rf, rt = 0, 3
        elif t == 118:
            rf, rt = 119, 117
        else:
            rf, rt = 112, 115
        r = b[rf]
        b[rf] = 0
        b[rt] = r
        H ^= Z[r + 6][rf] ^ Z[r + 6][rt]
    if abs(p) == 6:
        if T > 0:
            k[0] = t
        else:
            k[1] = t
    if abs(p) == 1 and abs(t - f) == 32:
        E = (f + t) // 2
        H ^= ZE[E & 7]
    else:
        E = -1
    H ^= ZS
    T = -T
    y.append(H)
    return c


def unmake():
    global C, E, H, T
    m, p, c, C, E, H, k0, k1, epc = st.pop()
    f = m & 127
    t = (m >> 7) & 127
    if abs(p) == 6 and abs(t - f) == 2:
        if t == 6:
            rf, rt = 7, 5
        elif t == 2:
            rf, rt = 0, 3
        elif t == 118:
            rf, rt = 119, 117
        else:
            rf, rt = 112, 115
        b[rf] = b[rt]
        b[rt] = 0
    b[f] = p
    b[t] = 0
    if epc != -1:
        b[epc] = c
    elif c:
        b[t] = c
    k[0] = k0
    k[1] = k1
    T = -T
    y.pop()


def mnull():
    global E, H, T
    ns.append((E, H))
    if E != -1:
        H ^= ZE[E & 7]
    E = -1
    H ^= ZS
    T = -T
    y.append(H)


def unull():
    global E, H, T
    E, H = ns.pop()
    T = -T
    y.pop()


def ev():
    s = 0
    wb = 0
    bb = 0
    for sq in range(128):
        if sq & 0x88:
            continue
        p = b[sq]
        if p == 0:
            continue
        a = abs(p)
        r = sq >> 4
        f = sq & 7
        if p > 0:
            s += M[a] + S[a - 1][((7 - r) << 3) | f]
            if a == 3:
                wb += 1
        else:
            s -= M[a] + S[a - 1][(r << 3) | f]
            if a == 3:
                bb += 1
    if wb > 1:
        s += 30
    if bb > 1:
        s -= 30
    return s * T


def order(ms, tm, ply):
    def sc(m):
        if m == tm:
            return 1 << 20
        f = m & 127
        t = (m >> 7) & 127
        p = b[f]
        if b[t]:
            v = abs(b[t])
        elif abs(p) == 1 and t == E:
            v = 1
        else:
            v = 0
        if v:
            return 100000 + 10 * M[v] - M[abs(p)] // 16
        if m == K[ply]:
            return 90000
        return Y[p + 6][t]
    return sorted(ms, key=sc, reverse=True)


def qs(a, B, ply):
    global N
    N += 1
    if N >= L:
        raise Ab
    if y.count(H) > 1:
        return 0
    if ply >= 64:
        return ev()
    ck = atk(k[0] if T > 0 else k[1], -T)
    if ck:
        bm = 0
        bv = -1000000
        for m in order(gen(), 0, ply):
            make(m)
            if atk(k[0] if T < 0 else k[1], T):
                unmake()
                continue
            v = -qs(-B, -a, ply + 1)
            unmake()
            if v > bv:
                bv = v
                bm = m
            if v > a:
                a = v
            if a >= B:
                break
        if bm == 0:
            return -100000 + ply
        return bv
    v = ev()
    if v >= B:
        return v
    if v > a:
        a = v
    for m in order(gen(1), 0, ply):
        make(m)
        if atk(k[0] if T < 0 else k[1], T):
            unmake()
            continue
        v = -qs(-B, -a, ply + 1)
        unmake()
        if v > a:
            a = v
        if a >= B:
            break
    return a


def search(d, a, B, ply):
    global N
    N += 1
    if N >= L:
        raise Ab
    if y.count(H) > 1:
        return 0
    if d <= 0:
        return qs(a, B, ply)
    ck = atk(k[0] if T > 0 else k[1], -T)
    e = D[H & 262143]
    tm = 0
    ao = a
    if e and e[4] == H:
        tm = e[3]
        if e[0] >= d:
            if e[1] == 0:
                return e[2]
            if e[1] == 1:
                if e[2] >= B:
                    return e[2]
                if e[2] > a:
                    a = e[2]
            else:
                if e[2] <= a:
                    return e[2]
                if e[2] < B:
                    B = e[2]
            if a >= B:
                return e[2]
    if not ck and d >= 3 and ev() >= B:
        mnull()
        v = -search(d - 4, -B, 1 - B, ply + 1)
        unull()
        if v >= B:
            return B
    ms = order(gen(), tm, ply)
    bm = 0
    bv = -1000000
    for i, m in enumerate(ms):
        c = make(m)
        if atk(k[0] if T < 0 else k[1], T):
            unmake()
            continue
        if i >= 3 and d >= 3 and not ck and c == 0 and m >> 14 == 0:
            v = -search(d - 2, -B, -a, ply + 1)
            if v > a:
                v = -search(d, -B, -a, ply + 1)
        elif i == 0:
            v = -search(d - 1, -B, -a, ply + 1)
        else:
            v = -search(d - 1, -a - 1, -a, ply + 1)
            if a < v < B:
                v = -search(d - 1, -B, -a, ply + 1)
        unmake()
        if v > bv:
            bv = v
            bm = m
        if v > a:
            a = v
        if a >= B:
            if c == 0 and m >> 14 == 0:
                Y[b[m & 127] + 6][(m >> 7) & 127] += d * d
                K[ply] = m
            break
    if bm == 0:
        return -100000 + ply if ck else 0
    if bv <= ao:
        fl = 2
    elif bv >= B:
        fl = 1
    else:
        fl = 0
    D[H & 262143] = (d, fl, bv, bm, H)
    return bv


def root():
    global N
    N = 0
    ms = []
    for m in gen():
        make(m)
        if atk(k[0] if T < 0 else k[1], T):
            unmake()
            continue
        unmake()
        ms.append(m)
    if not ms:
        return 0
    ms = order(ms, 0, 0)
    bm = ms[0]
    for d in range(1, 64):
        try:
            a = -1000000
            B = 1000000
            bv = -1000000
            bmv = ms[0]
            for i, m in enumerate(ms):
                make(m)
                if i == 0:
                    v = -search(d - 1, -B, -a, 1)
                else:
                    v = -search(d - 1, -a - 1, -a, 1)
                    if a < v < B:
                        v = -search(d - 1, -B, -a, 1)
                unmake()
                if v > bv:
                    bv = v
                    bmv = m
                if v > a:
                    a = v
            bm = bmv
            ms.remove(bmv)
            ms.insert(0, bmv)
        except Ab:
            break
    return bm


def setup(fen, moves):
    global b, T, C, E, k, H, y, st, ns
    if moves:
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    b = [0] * 128
    w = fen.split()
    for r, row in enumerate(w[0].split("/")):
        f = 0
        for ch in row:
            if ch.isdigit():
                f += int(ch)
            else:
                p = "PNBRQK".find(ch.upper()) + 1
                if ch.islower():
                    p = -p
                b[(7 - r) * 16 + f] = p
                f += 1
    T = 1 if w[1] == "w" else -1
    C = 0
    if "K" in w[2]:
        C |= 1
    if "Q" in w[2]:
        C |= 2
    if "k" in w[2]:
        C |= 4
    if "q" in w[2]:
        C |= 8
    E = -1
    if w[3] != "-":
        E = (int(w[3][1]) - 1) * 16 + ord(w[3][0]) - 97
    k = [0, 0]
    H = 0
    for s in range(128):
        if s & 0x88:
            continue
        p = b[s]
        if p:
            H ^= Z[p + 6][s]
            if abs(p) == 6:
                if p > 0:
                    k[0] = s
                else:
                    k[1] = s
    if T < 0:
        H ^= ZS
    H ^= ZC[C]
    if E != -1:
        H ^= ZE[E & 7]
    y = [H]
    st = []
    ns = []
    for u in moves:
        f = (int(u[1]) - 1) * 16 + ord(u[0]) - 97
        t = (int(u[3]) - 1) * 16 + ord(u[2]) - 97
        pr = 0
        if len(u) == 5:
            pr = "nbrq".find(u[4]) + 2
        make(f | t << 7 | pr << 14)


def uci(m):
    f = m & 127
    t = (m >> 7) & 127
    s = "abcdefgh"[f & 7] + str((f >> 4) + 1) + "abcdefgh"[t & 7] + str((t >> 4) + 1)
    if m >> 14:
        s += "nbrq"[(m >> 14) - 2]
    return s


U = os.environ.get("MAKEFUN_ENV_URL", "")


def post(p, o):
    if not U:
        sys.exit("MAKEFUN_ENV_URL is not set")
    r = urllib.request.Request(U + p, data=json.dumps(o).encode(), headers={"content-type": "application/json"})
    try:
        with urllib.request.urlopen(r) as s:
            return json.load(s)
    except urllib.error.HTTPError as e:
        sys.exit(p + ": HTTP " + str(e.code))


while True:
    g = post("/game", {})
    if g["status"] == "done":
        break
    while g["status"] == "your_move":
        setup(g["fen"], g["moves"])
        m = root()
        u = uci(m)
        if u not in g["legal_moves"]:
            u = g["legal_moves"][0]
        g = post("/move", {"game": g["game"], "move": u})
    print("game " + str(g["game"]) + ": " + str(g.get("outcome")) + " by " + str(g.get("reason")), file=sys.stderr)
print("done: " + str(g.get("wins")) + " won, " + str(g.get("draws")) + " drawn, " + str(g.get("losses")) + " lost", file=sys.stderr)
