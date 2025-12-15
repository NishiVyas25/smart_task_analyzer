from datetime import date
from collections import defaultdict, deque

DEFAULT_WEIGHTS = {
    "urgency": 0.4,   # 40%
    "importance": 0.3,# 30%
    "effort": 0.2,    # 20%
    "dependency": 0.1 # 10%
}

STRATEGY_WEIGHTS = {
    "fastest": {
        "urgency": 0.2,
        "importance": 0.1,
        "effort": 0.6,
        "dependency": 0.1
    },
    "impact": {
        "urgency": 0.2,
        "importance": 0.6,
        "effort": 0.1,
        "dependency": 0.1
    },
    "deadline": {
        "urgency": 0.6,
        "importance": 0.2,
        "effort": 0.1,
        "dependency": 0.1
    },
    "smart": DEFAULT_WEIGHTS
}

def normalize(x, xmin, xmax):
    if xmax == xmin:
        return 0.5
    return max(0, min(1, (x - xmin) / (xmax - xmin)))

def days_until(due_date):
    if not due_date:
        return None
    today = date.today()
    return (due_date - today).days

def detect_cycles(tasks):
    # tasks: list of dicts (each has an 'id' and dependencies list)
    graph = defaultdict(list)
    indeg = defaultdict(int)
    ids = set()
    for t in tasks:
        tid = t.get("id")
        ids.add(tid)
    for t in tasks:
        tid = t.get("id")
        for dep in t.get("dependencies", []):
            if dep in ids:
                graph[dep].append(tid)
                indeg[tid] += 1
    # Kahn's algorithm for topo sort
    q = deque([n for n in ids if indeg[n] == 0])
    visited = 0
    while q:
        n = q.popleft(); visited += 1
        for nbr in graph[n]:
            indeg[nbr] -= 1
            if indeg[nbr] == 0:
                q.append(nbr)
    return visited != len(ids)  # True if cycle exists

def score_tasks(tasks, strategy="smart"):
    weights = STRATEGY_WEIGHTS.get(strategy, DEFAULT_WEIGHTS)
    # validate and set defaults
    for t in tasks:
        t.setdefault("importance", 5)
        t.setdefault("estimated_hours", 4)
        t.setdefault("dependencies", [])
        t.setdefault("due_date", None)

    # convert due_date strings to date objects if needed (caller should parse)
    # compute raw metrics
    urgencies = []
    importances = []
    efforts = []
    dep_counts = []
    today = date.today()
    id_map = {t["id"]: t for t in tasks}

    for t in tasks:
        dd = t.get("due_date")
        if dd:
            days = (dd - today).days
        else:
            days = None
        # urgency: inverse days (so smaller days => higher urgency)
        if days is None:
            urg = 0.2
        elif days < 0:
            urg = 1.0  # past due => max urgency
        else:
            # map days to 0..1 where 0 is distant (>30 days) and 1 is due today
            urg = max(0, 1 - (days / 30.0))
        urgencies.append(urg)
        importances.append(max(0, min(10, t["importance"])) / 10.0)
        # effort: lower hours -> higher score (quick wins)
        eff = 1 / (1 + t["estimated_hours"])
        efforts.append(eff)
        # dependency: how many tasks depend on this task
        dep_counts.append(0)  # we'll compute after

    # compute dependency counts (how many tasks list this id in dependencies)
    dep_map = {t["id"]:0 for t in tasks}
    for t in tasks:
        for d in t.get("dependencies", []):
            if d in dep_map:
                dep_map[d] += 1
    for i,t in enumerate(tasks):
        dep_counts[i] = dep_map.get(t["id"], 0)

    # normalize lists to 0..1
    def normalize_list(lst):
        if not lst: return [0]*len(lst)
        lo, hi = min(lst), max(lst)
        if hi == lo:
            return [0.5]*len(lst)
        return [(x-lo)/(hi-lo) for x in lst]

    U = normalize_list(urgencies)
    I = normalize_list(importances)
    E = normalize_list(efforts)
    D = normalize_list(dep_counts)

    results = []
    for i,t in enumerate(tasks):
        s = (weights["urgency"] * U[i] +
             weights["importance"] * I[i] +
             weights["effort"] * E[i] +
             weights["dependency"] * D[i])
        results.append({
            **t,
            "score": round(s, 4),
            "explanation": {
                "urgency": round(U[i],3),
                "importance": round(I[i],3),
                "effort": round(E[i],3),
                "dependency": round(D[i],3),
            }
        })
    # sort descending by score
    results.sort(key=lambda x: x["score"], reverse=True)
    return results
