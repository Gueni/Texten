#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
#?  Expressions : evaluator for the MATLAB/Octave expressions and init scripts of PLECS parameters (used by signal_names)
#?
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
import  json
import  os
import  re

from    .plecs_file     import  read_text


#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
#? Expressions : small evaluator for the MATLAB/Octave expressions written in block parameters
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
# Enough to evaluate configuration selectors, vector widths and selector indices :
#       numbers, 'strings', struct fields (a.b.c), indexing a(i), [1 2; 3 4], ranges 1:n, + - * / ^, comparisons, and the
#       functions min max zeros ones length numel sum abs floor ceil round mod.
# Vectors are python lists, structs are dicts.

class EvalError(Exception):
    pass

_EXPR_TOKEN = re.compile(r"\s+|\d+\.?\d*(?:[eE][+-]?\d+)?|\.\d+(?:[eE][+-]?\d+)?|[A-Za-z_]\w*|'(?:[^']|'')*'|\.\*|\./|\.\^|==|~=|<=|>=|&&|\|\||\.'|[-+*/^()\[\],;:.<>~&|]")

def _expr_tokens(text):
    toks, pos, depth = [], 0, 0
    for m in _EXPR_TOKEN.finditer(text):
        if m.start() != pos :   raise EvalError("can not read %r" % text)
        pos, tok = m.end(), m.group(0)
        if tok.isspace():
            if depth and toks and _ends_operand(toks[-1]) and m.end() < len(text):
                nxt = _EXPR_TOKEN.match(text, m.end())
                if nxt and (_starts_operand(nxt.group(0)) or (nxt.group(0) in "+-" and not text[nxt.end():nxt.end() + 1].isspace())):
                    toks.append(",")                                                                    # [1 2 -3] : blank = separator
            continue
        if tok == "["   :   depth += 1
        if tok == "]"   :   depth -= 1
        toks.append(tok)
    if pos != len(text) :   raise EvalError("can not read %r" % text)
    return toks

def _ends_operand(tok)  :   return tok[0].isdigit() or tok[0] == "." and len(tok) > 1 or tok[0].isalpha() or tok[0] in "_')]"
def _starts_operand(tok):   return tok[0].isdigit() or tok[0] == "." and len(tok) > 1 or tok[0].isalpha() or tok[0] in "_'(["

def _num(x):
    if isinstance(x, bool)          :   return float(x)
    if isinstance(x, (int, float))  :   return float(x)
    raise EvalError("not a number : %r" % (x,))

def _elementwise(a, b, op):
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b) :   raise EvalError("size mismatch")
        return [op(_num(x), _num(y)) for x, y in zip(a, b)]
    if isinstance(a, list)  :   return [op(_num(x), _num(b)) for x in a]
    if isinstance(b, list)  :   return [op(_num(a), _num(y)) for y in b]
    return op(_num(a), _num(b))

def _flat(x):
    if isinstance(x, list)  :   return [v for e in x for v in _flat(e)]
    return [x]

def _call(name, args):
    def n(i)    :   return int(round(_num(args[i])))
    if name == "zeros"  :   return [0.0] * (n(0) * n(1) if len(args) > 1 else n(0) * n(0))
    if name == "ones"   :   return [1.0] * (n(0) * n(1) if len(args) > 1 else n(0) * n(0))
    if name in ("length", "numel")  :   return float(len(args[0])) if isinstance(args[0], list) else 1.0
    if name == "min" and len(args) == 2 :   return _elementwise(args[0], args[1], min)
    if name == "max" and len(args) == 2 :   return _elementwise(args[0], args[1], max)
    if name in ("min", "max", "sum"):
        vals = [_num(v) for v in _flat(args[0])]
        return {"min": min, "max": max, "sum": sum}[name](vals)
    if name in ("abs", "floor", "ceil", "round"):
        import math
        f = {"abs": abs, "floor": math.floor, "ceil": math.ceil, "round": round}[name]
        return [float(f(_num(v))) for v in args[0]] if isinstance(args[0], list) else float(f(_num(args[0])))
    if name == "mod"    :   return _elementwise(args[0], args[1], lambda a, b: a % b)
    if name in ("isfinite", "isnan", "isinf"):
        import math
        f = {"isfinite": math.isfinite, "isnan": math.isnan, "isinf": math.isinf}[name]
        return [float(f(_num(v))) for v in args[0]] if isinstance(args[0], list) else float(f(_num(args[0])))
    if name == "isempty"    :   return float(args[0] == [] or args[0] == "")
    if name == "isstruct"   :   return float(isinstance(args[0], dict))
    if name == "ischar"     :   return float(isinstance(args[0], str))
    if name == "isnumeric"  :   return float(isinstance(args[0], (float, list)) and not isinstance(args[0], str))
    if name == "isfield"    :   return float(isinstance(args[0], dict) and args[1] in args[0])
    if name == "struct"     :   return {args[i]: args[i + 1] for i in range(0, len(args) - 1, 2)}
    if name in ("sqrt", "exp", "log", "log10"):
        import math
        f = getattr(math, name)
        return [f(_num(v)) for v in args[0]] if isinstance(args[0], list) else f(_num(args[0]))
    if name == "any"        :   return float(any(_num(v) for v in _flat(args[0])))
    if name == "all"        :   return float(all(_num(v) for v in _flat(args[0])))
    if name == "logical"    :   return _elementwise(args[0], 0.0, lambda a, b: float(a != 0))
    if name == "double"     :   return args[0]
    raise EvalError("unknown function %s" % name)

_FUNCTIONS = {"zeros", "ones", "length", "numel", "min", "max", "sum", "abs", "floor", "ceil", "round", "mod", "isfinite", "isnan",
              "isinf", "isempty", "isstruct", "ischar", "isnumeric", "isfield", "struct", "sqrt", "exp", "log", "log10", "any", "all",
              "logical", "double"}
_CONSTANTS = {"pi": 3.141592653589793, "inf": float("inf"), "Inf": float("inf"), "nan": float("nan"), "NaN": float("nan"),
              "true": 1.0, "false": 0.0, "eps": 2.220446049250313e-16}

def truth(value):
    """ MATLAB truth of a value : not empty and every element non zero. """
    vals = _flat(value) if isinstance(value, list) else [value]
    try                         :   return bool(vals) and all(_num(v) != 0 for v in vals)
    except EvalError            :   return bool(value)

class _Parser:
    def __init__(self, text, lookup):
        self.t, self.i, self.lookup = _expr_tokens(text), 0, lookup

    def peek(self)      :   return self.t[self.i] if self.i < len(self.t) else None
    def take(self, tok=None):
        cur = self.peek()
        if cur is None or (tok is not None and cur != tok)  :   raise EvalError("expected %r" % tok)
        self.i += 1
        return cur

    def parse(self):
        v = self.expr()
        if self.peek() is not None  :   raise EvalError("unexpected %r" % self.peek())
        return v

    def expr(self):
        v = self.compare()
        while self.peek() in ("&&", "||"):
            op, w = self.take(), self.compare()
            v = float(truth(v) and truth(w)) if op == "&&" else float(truth(v) or truth(w))
        return v

    def compare(self):
        v = self.range()
        while self.peek() in ("&", "|"):
            op, w = self.take(), self.range()
            v = _elementwise(v, w, (lambda a, b: float(bool(a) and bool(b))) if op == "&" else (lambda a, b: float(bool(a) or bool(b))))
        ops = {"==": lambda a, b: float(a == b), "~=": lambda a, b: float(a != b), "<": lambda a, b: float(a < b),
               ">": lambda a, b: float(a > b), "<=": lambda a, b: float(a <= b), ">=": lambda a, b: float(a >= b)}
        while self.peek() in ops:
            op = self.take()
            v  = _elementwise(v, self.range(), ops[op])
        return v

    def range(self):
        a = self.additive()
        if self.peek() != ":"   :   return a
        self.take(":")
        b = self.additive()
        step = 1.0
        if self.peek() == ":":
            self.take(":")
            step, b = _num(b), self.additive()
        a, b = _num(a), _num(b)
        if step == 0    :   raise EvalError("zero step")
        n = int((b - a) / step + 1e-9) + 1
        return [a + k * step for k in range(max(n, 0))]

    def additive(self):
        v = self.term()
        while self.peek() in ("+", "-"):
            op = self.take()
            v  = _elementwise(v, self.term(), (lambda a, b: a + b) if op == "+" else (lambda a, b: a - b))
        return v

    def term(self):
        v = self.unary()
        while self.peek() in ("*", "/", ".*", "./"):
            op = self.take()
            w  = self.unary()
            if op in ("*", ".*")    :   v = _elementwise(v, w, lambda a, b: a * b)
            else                    :   v = _elementwise(v, w, lambda a, b: a / b)
        return v

    def unary(self):
        if self.peek() == "-"   :   self.take(); return _elementwise(0.0, self.unary(), lambda a, b: a - b)
        if self.peek() == "+"   :   self.take(); return self.unary()
        if self.peek() == "~":
            self.take()
            v = self.unary()
            return [float(not _num(x)) for x in v] if isinstance(v, list) else float(not _num(v))
        return self.power()

    def power(self):
        v = self.postfix()
        if self.peek() in ("^", ".^"):
            self.take()
            v = _elementwise(v, self.unary(), lambda a, b: a ** b)
        return v

    def args(self):
        self.take("(")
        out = []
        if self.peek() != ")":
            out.append(self.expr())
            while self.peek() == ",":
                self.take(",")
                out.append(self.expr())
        self.take(")")
        return out

    def postfix(self):
        tok = self.peek()
        if tok is None  :   raise EvalError("unexpected end")
        if tok[0].isalpha() or tok[0] == "_":
            self.take()
            if tok in _FUNCTIONS and self.peek() == "(" and not self._defined(tok):
                v = _call(tok, self.args())
            elif tok in _CONSTANTS and not self._defined(tok):
                v = _CONSTANTS[tok]
            else:
                v = self.lookup(tok)
        else:
            v = self.primary()
        while self.peek() in (".", "(", ".'"):
            if self.peek() == ".'":
                self.take()
                continue
            if self.peek() == "(" and self.t[self.i + 1:self.i + 3] == [":", ")"]:
                self.i += 3
                continue
            if self.take() == ".":
                field = self.take()
                if not isinstance(v, dict) or field not in v    :   raise EvalError("no field %s" % field)
                v = v[field]
            else:
                self.i -= 1
                idx = self.args()
                if len(idx) != 1    :   raise EvalError("only 1-D indexing")
                vals = v if isinstance(v, list) else [v]
                try:
                    v = [vals[int(round(_num(k))) - 1] for k in idx[0]] if isinstance(idx[0], list) else vals[int(round(_num(idx[0]))) - 1]
                except IndexError:
                    raise EvalError("index out of range")
        return v

    def _defined(self, name):
        try:
            self.lookup(name)
            return True
        except Exception:
            return False

    def primary(self):
        tok = self.take()
        if tok[0].isdigit() or tok[0] == "."    :   return float(tok)
        if tok[0] == "'"                        :   return tok[1:-1].replace("''", "'")
        if tok == "(":
            v = self.expr()
            self.take(")")
            return v
        if tok == "[":
            rows, row = [], []
            while self.peek() != "]":
                if self.peek() in (",",)    :   self.take(); continue
                if self.peek() == ";"       :   self.take(); rows.append(row); row = []; continue
                row.extend(_flat(self.expr()))
            self.take("]")
            rows.append(row)
            return [v for r in rows for v in r]
        raise EvalError("unexpected %r" % tok)

def evaluate(text, scope=None):
    """
    Evaluate a parameter expression.

    Args:
        text  (str)                     : expression, e.g. 'zeros(1,Common.ToFile.Y1.Length)'.
        scope (dict | callable)         : variables, or a function name -> value raising EvalError for unknown names.
    """
    if callable(scope)  :   lookup = scope
    else:
        variables = scope or {}
        def lookup(name):
            if name in variables    :   return variables[name]
            raise EvalError("unknown variable %s" % name)
    return _Parser(str(text), lookup).parse()

_KEYWORD = re.compile(r"^(if|elseif|else|end|endif|for|while|switch|case|otherwise|function|try|catch)\b\s*(.*)$", re.S)

def _statements(text):
    """ Script text -> statements (split at line ends and at ; or , outside brackets / strings). """
    out = []
    for line in re.sub(r"%[^\n]*|#[^\n]*", "", text.replace("...\n", " ")).split("\n"):
        depth, cur, quote = 0, "", False
        for i, ch in enumerate(line):
            if ch == "'" and not quote and (not cur.strip() or not re.match(r"[\w)\]'.]", cur.rstrip()[-1:] or " ")):
                quote = True
            elif ch == "'" and quote    :   quote = False
            elif not quote and ch in "([{" :   depth += 1
            elif not quote and ch in ")]}" :   depth -= 1
            if not quote and depth == 0 and ch in ";,":
                out.append(cur.strip())
                cur = ""
                continue
            cur += ch
        out.append(cur.strip())
    return [x for x in out if x]

def run_script(text, variables, lookup=None):
    """
    Run the assignments of an initialization script in variables (dict, changed in place).

    Args:
        text      (str)             : script.
        variables (dict)            : variables written by the script (and read first).
        lookup    (callable)        : name -> value for names not in variables (outer scope).

    Statements that can not be evaluated are skipped. if / elseif / else blocks follow their condition (all skipped when it can
    not be evaluated), for / while / switch / try blocks are skipped.
    """
    def get(name):
        if name in variables    :   return variables[name]
        if lookup is not None   :   return lookup(name)
        raise EvalError("unknown variable %s" % name)

    stack = []                  # [(kind, running, done)] : running = this branch runs, done = a branch already ran
    for stmt in _statements(text or ""):
        running = all(r for _, r, _ in stack)
        m = _KEYWORD.match(stmt)
        if m:
            kw, rest = m.group(1), m.group(2).strip().rstrip(",")
            if kw == "if":
                ok = False
                if running:
                    try                 :   ok = truth(evaluate(rest, get))
                    except Exception    :   ok = None
                stack.append(("if", bool(ok) and running, ok is not False if ok is None else ok))
                if ok is None   :   stack[-1] = ("if", False, True)                                   # unknown : no branch runs
            elif kw == "elseif" and stack:
                kind, _, done = stack.pop()
                ok = False
                if not done and all(r for _, r, _ in stack):
                    try                 :   ok = truth(evaluate(rest, get))
                    except Exception    :   ok, done = False, True
                stack.append((kind, ok, done or ok))
            elif kw == "else" and stack:
                kind, _, done = stack.pop()
                stack.append((kind, not done, True))
            elif kw in ("end", "endif") and stack:
                stack.pop()
            elif kw in ("for", "while", "switch", "try", "function"):
                stack.append((kw, False, True))
            continue
        if not running  :   continue
        a = re.match(r"([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\s*=(?!=)(.*)$", stmt, re.S)
        if not a        :   continue
        names = a.group(1).split(".")
        try:
            value = evaluate(a.group(2).strip(), get)
        except Exception:
            if len(names) == 1  :   variables.pop(names[0], None)
            continue
        if len(names) > 1 and names[0] not in variables:
            try:
                base = get(names[0])
                variables[names[0]] = json.loads(json.dumps(base)) if isinstance(base, dict) else {}
            except EvalError:
                variables[names[0]] = {}
        node = variables
        for name in names[:-1]:
            if not isinstance(node.get(name), dict) :   node[name] = {}
            node = node[name]
        node[names[-1]] = value
    return variables

def load_variables(source, variables=None):
    """
    Variables of an initialization script (InitializationCommands text or a .m file).

    Args:
        source    (str)             : path of a .m file, or the script text itself.
        variables (dict, optional)  : variables to extend.

    Returns:
        dict                        : {name : value}, structs as nested dicts.
    """
    variables = {} if variables is None else variables
    if source and len(source) < 1000 and os.path.isfile(source)    :   source = read_text(source)
    return run_script(source or "", variables)
