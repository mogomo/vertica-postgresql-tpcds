"""Helpers for adjusting dsqgen-generated TPC-DS queries to a product's SQL dialect.

Each product composes its scripts/<product>/rewrite.py from these functions; all of
them are semantics-preserving (see README "Query changes").
  days_to_integer:            "<date> + 30 days"  ->  "<date> + 30"      (date + integer adds days)
  add_derived_table_aliases:  "from (select ...)"  ->  "from (select ...) dt1"
  correlated_count_to_exists: "(select count(*) as item_cnt ... correlated ...) > 0"  ->  "exists (select * ...)"  (query 41)
  inline_order_by_alias:      "order by ... case when lochierarchy = 0 ..."  ->  "... case when (grouping(a)+grouping(b)) = 0 ..."
  decimal_division:           "inv_after / inv_before"  ->  "cast(inv_after as numeric) / inv_before"
"""
import re

WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
# tokens that may directly follow a derived table when it has no alias
NO_ALIAS_FOLLOWERS = {"where", "group", "order", "union", "intersect", "except",
                      "limit", "having", "join", "inner", "left", "right", "full",
                      "cross", "on", "window"}


def code_mask(sql):
    """True for every character that is SQL code (not in a literal, quoted name or comment)."""
    mask, i, n = [True] * len(sql), 0, len(sql)
    while i < n:
        if sql[i] in "'\"":
            q, j = sql[i], i + 1
            while j < n and not (sql[j] == q and (j + 1 >= n or sql[j + 1] != q)):
                j += 2 if sql[j] == q else 1
            for k in range(i, min(j + 1, n)):
                mask[k] = False
            i = j + 1
        elif sql.startswith("--", i):
            j = sql.find("\n", i)
            j = n if j < 0 else j
            for k in range(i, j):
                mask[k] = False
            i = j
        else:
            i += 1
    return mask


def matching_paren(sql, mask, start):
    depth = 0
    for i in range(start, len(sql)):
        if not mask[i]:
            continue
        if sql[i] == "(":
            depth += 1
        elif sql[i] == ")":
            depth -= 1
            if depth == 0:
                return i
    raise ValueError("unbalanced parentheses")


CLAUSES = {"select", "from", "where", "group", "having", "order", "on", "limit"}


def clause_of(sql, mask, pos):
    """The clause keyword (from, where, ...) that position pos belongs to."""
    depth, i = 0, pos - 1
    while i >= 0:
        c = sql[i]
        if mask[i]:
            if c == ")":
                depth += 1
            elif c == "(":
                if depth == 0:
                    return ""
                depth -= 1
            elif depth == 0 and (c.isalpha() or c == "_"):
                j = i
                while j > 0 and (sql[j - 1].isalnum() or sql[j - 1] == "_"):
                    j -= 1
                if sql[j:i + 1].lower() in CLAUSES:
                    return sql[j:i + 1].lower()
                i = j
        i -= 1
    return ""


def next_token(sql, pos):
    m = re.match(r"\s*(\S)", sql[pos:])
    if not m:
        return ""
    w = WORD.match(sql, pos + m.start(1))
    return w.group(0).lower() if w else m.group(1)


def add_derived_table_aliases(sql):
    n = 0
    while True:
        mask = code_mask(sql)
        for m in re.finditer(r"\(\s*select\b", sql, re.I):
            p = m.start()
            if not mask[p] or clause_of(sql, mask, p) != "from":
                continue
            end = matching_paren(sql, mask, p)
            nxt = next_token(sql, end + 1)
            if nxt in ("", ")", ",", ";") or nxt in NO_ALIAS_FOLLOWERS:
                n += 1
                sql = sql[:end + 1] + f" dt{n}" + sql[end + 1:]
                break  # positions changed, rescan
        else:
            return sql


def correlated_count_to_exists(sql):
    while True:
        mask = code_mask(sql)
        m = re.search(r"\(\s*select\s+count\(\*\)\s+as\s+item_cnt\b", sql, re.I)
        if not m or not mask[m.start()]:
            return sql
        end = matching_paren(sql, mask, m.start())
        tail = re.match(r"\s*>\s*0", sql[end + 1:])
        if not tail:
            return sql
        body = sql[m.end():end]
        sql = sql[:m.start()] + "exists (select *" + body + ")" + sql[end + 1 + tail.end():]


def days_to_integer(sql):
    mask = code_mask(sql)
    return re.sub(r"([+-])\s*(\d+)\s+days\b",
                  lambda m: f"{m.group(1)} {m.group(2)}" if mask[m.start()] else m.group(0), sql)


def quote_reserved_identifiers(sql, words):
    """Double-quote the given words where they are used as identifiers in SQL code
    (TPC-DS uses e.g. "returns" and "at" as aliases, reserved words in some products).
    Quoted identifiers keep their meaning, so the query is unchanged otherwise."""
    mask = code_mask(sql)
    pattern = re.compile(r"\b(" + "|".join(re.escape(w) for w in words) + r")\b", re.I)
    return pattern.sub(lambda m: f'"{m.group(1)}"' if mask[m.start()] else m.group(0), sql)


def inline_order_by_alias(sql, alias):
    """Replace an output column alias inside a CASE expression of the final ORDER BY by
    the select-list expression it names (TPC-DS queries 36, 70 and 86). Products that
    resolve output aliases in ORDER BY only as a whole sort key reject the alias there;
    the expression is the same value, so the order is unchanged."""
    m = re.search(r",\s*([^,]*?)\s+as\s+" + re.escape(alias) + r"\b", sql, re.I)
    if not m:
        return sql
    expr = m.group(1).strip()
    i = sql.lower().rfind("order by")
    if i < m.end():
        return sql
    tail = re.sub(r"(case\s+when\s+)" + re.escape(alias) + r"\b",
                  lambda x: f"{x.group(1)}({expr})", sql[i:], flags=re.I)
    return sql[:i] + tail


def decimal_division(sql, numerators):
    """Divide as decimals where the query divides two integers (TPC-DS queries 21, 34,
    73, 78 and 83: ratios such as hd_dep_count / hd_vehicle_count > 1.2). Vertica
    returns a decimal for integer / integer; products that truncate integer division
    would compute other answers, so the numerator is cast to numeric there."""
    mask = code_mask(sql)
    pattern = re.compile(r"(?<![\w.])(" + "|".join(re.escape(n) for n in numerators) + r")(\s*/)", re.I)
    return pattern.sub(lambda m: f"cast({m.group(1)} as numeric){m.group(2)}" if mask[m.start()] else m.group(0), sql)
