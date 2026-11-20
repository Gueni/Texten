#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
#?  PLECS file format : lossless parser, paths, documents (shared by break_links / standalone / signal_names)
#?
#?  A .plecs file is parsed into Field / Block nodes that remember their character span, so a file is changed by replacing
#?  spans : what is not changed stays byte-identical.
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
import  base64
import  os
import  re


#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
#? File format : lossless parser
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
# A .plecs file is a tree of   Key value   fields and   Key { ... }   blocks. Values are bare words, [matrices], "strings"
# (long strings continue on the next lines as further "..." pieces), base64 "..." strings (non ASCII text) or { "a", "b" } lists.
# Every node remembers its character span in the source text, so a file is modified by replacing spans : untouched parts stay
# byte-identical.

_TOKEN  = re.compile(r'"(?:[^"\\]|\\.)*"|\[[^\]]*\]|[{},]|[^\s{}\[\],"]+', re.S)
_STRING = re.compile(r'"((?:[^"\\]|\\.)*)"', re.S)
_ESCAPE = re.compile(r'\\(.)', re.S)
EMPTY_BLOCKS = {"Schematic", "Configurations", "Probe", "MaskProbe", "Parameter", "Terminal", "Component", "Connection", "Branch"}
_LIST_ITEM = re.compile(r'"(?:[^"\\]|\\.)*"|base64|[{},]', re.S)

class Field:
    """ One   Key value   line. raw is the value exactly as written in the file. """
    __slots__ = ("key", "raw", "start", "vstart", "end")

    def __init__(self, key, raw, start, vstart, end):
        self.key, self.raw, self.start, self.vstart, self.end = key, raw, start, vstart, end

    @property
    def text(self)  :   return decode(self.raw)

    @property
    def items(self):
        """ Elements of a { "a", "b" } list (an element can be written as several "..." pieces over several lines). """
        out, cur = [], None
        for m in _LIST_ITEM.finditer(self.raw):
            if m.group(0) == ",":
                if cur is not None  :   out.append(decode(cur))
                cur = None
            elif m.group(0) not in "{}":
                cur = m.group(0) if cur is None else cur + " " + m.group(0)
        if cur is not None  :   out.append(decode(cur))
        return out

class Block:
    """ One   Key { ... }   block. """
    __slots__ = ("key", "children", "start", "end", "parent")

    def __init__(self, key, start, parent=None):
        self.key, self.children, self.start, self.end, self.parent = key, [], start, None, parent

    def field(self, key):
        for c in self.children:
            if c.key == key and isinstance(c, Field)    :   return c
        return None

    def raw(self, key, default=None):
        f = self.field(key)
        return f.raw if f is not None else default

    def get(self, key, default=None):
        f = self.field(key)
        return f.text if f is not None else default

    def blocks(self, key=None):
        return [c for c in self.children if isinstance(c, Block) and (key is None or c.key == key)]

    def param(self, variable, default=None):
        """ Value of the   Parameter { Variable "<variable>" ... }   block. """
        for p in self.children:
            if isinstance(p, Block) and p.key == "Parameter" and p.get("Variable") == variable  :   return p.get("Value", default)
        return default

def _unescape(s):
    return _ESCAPE.sub(lambda m: {"n": "\n", "t": "\t"}.get(m.group(1), m.group(1)), s)

def decode(raw):
    """ Value as written in the file -> python string. """
    if raw is None  :   return None
    pieces = _STRING.findall(raw)
    if not pieces   :   return raw.strip()
    joined = "".join(pieces)
    if raw.startswith("base64") :   return base64.b64decode(joined).decode("utf-8")
    return _unescape(joined)

def encode(text, column=0):
    """
    Python string -> value as PLECS writes it : quoted and escaped, base64 if not ASCII, wrapped the way PLECS wraps.

    Args:
        text   (str)    : the string.
        column (int)    : column at which the value starts on its line (only used for wrapping).
    """
    width = 79
    if all(ord(ch) < 128 for ch in text):
        prefix  = ""
        units   = [{"\\": "\\\\", '"': '\\"', "\n": "\\n", "\t": "\\t"}.get(ch, ch) for ch in text]
    else:
        prefix  = "base64 "
        units   = list(base64.b64encode(text.encode("utf-8")).decode("ascii"))
    lines, cur, room = [], "", max(width - column - len(prefix) - 2, 20)
    for u in units:
        if len(cur) + len(u) > room:
            lines.append(cur)
            cur, room = "", width - 2
        cur += u
        if u == "\\n":                                                                                  # PLECS starts a new piece after every line break
            lines.append(cur)
            cur, room = "", width - 2
    if cur or not lines :   lines.append(cur)
    return prefix + "\n".join('"%s"' % l for l in lines)

def parse(text):
    """ Text of a .plecs file -> root Block (its only child is the 'Plecs' block). """
    toks    = [(m.group(0), m.start(), m.end()) for m in _TOKEN.finditer(text)]
    n       = len(toks)
    root    = Block("", 0)
    cur     = root
    i       = 0
    while i < n:
        tok, start, end = toks[i]
        if tok == "}":
            if cur.parent is None   :   raise ValueError("unbalanced '}' at offset %d" % start)
            cur.end = end
            cur     = cur.parent
            i      += 1
            continue
        if i + 1 >= n   :   raise ValueError("unexpected end of file after '%s'" % tok)
        nxt = toks[i + 1][0]
        if nxt == "{":
            after = toks[i + 2][0] if i + 2 < n else "}"
            if (after == "}" and tok not in EMPTY_BLOCKS) or after == "," or after.startswith('"'):    # { "a", "b" } list
                j = i + 2
                while toks[j][0] != "}" :   j += 1
                cur.children.append(Field(tok, text[toks[i + 1][1]:toks[j][2]], start, toks[i + 1][1], toks[j][2]))
                i = j + 1
            else:                                                                                       # nested block
                blk = Block(tok, start, cur)
                cur.children.append(blk)
                cur = blk
                i  += 2
            continue
        if "\n" in text[end:toks[i + 1][1]] or nxt == "}":                                              # key without value
            cur.children.append(Field(tok, "", start, end, end))
            i += 1
            continue
        j = i + 1                                                                                       # value : rest of the line + continued "..." pieces
        while j + 1 < n and toks[j + 1][0] not in ("{", "}") and (
                "\n" not in text[toks[j][2]:toks[j + 1][1]] or (toks[j][0][0] == '"' and toks[j + 1][0][0] == '"')):
            j += 1
        cur.children.append(Field(tok, text[toks[i + 1][1]:toks[j][2]], start, toks[i + 1][1], toks[j][2]))
        i = j + 1
    if cur is not root  :   raise ValueError("unbalanced '{' : block '%s' at offset %d is never closed" % (cur.key, cur.start))
    root.end = len(text)
    return root

def read_text(path):
    with open(path, "r", encoding="utf-8", newline="") as f :   return f.read()

def write_text(path, text):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f :   f.write(text)

#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
#? Paths
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
# PLECS writes a block path as its names joined by '/'. Inside a name a line break is written as the two characters \n and a
# slash as \/.

_PATH_SEP = re.compile(r'((?:[^/\\]|\\.)*)(?:/|$)', re.S)

def path_name(name):
    return name.replace("\\", "\\\\").replace("\n", "\\n").replace("/", "\\/")

def path_join(*parts):
    return "/".join(p for p in parts if p)

def path_split(path):
    """ Path -> its names (still written the path way). """
    parts = [m.group(1) for m in _PATH_SEP.finditer(path)]
    return parts[:-1] if len(parts) > 1 and parts[-1] == "" and not path.endswith("/") else parts

def path_leaf(path):
    """ Path -> plain name of its last block. """
    return re.sub(r'\\(.)', lambda m: "\n" if m.group(1) == "n" else m.group(1), path_split(path)[-1], flags=re.S)

def display_name(name):
    """ Block name on one line (line breaks -> spaces). """
    return " ".join(name.replace("\\n", "\n").split())

class Document:
    """ A parsed .plecs file (model or library). """

    def __init__(self, text, path=None):
        self.text       = text
        self.path       = path
        self.root       = parse(text)
        self.plecs      = self.root.blocks("Plecs")[0] if self.root.blocks("Plecs") else self.root.blocks()[0]
        self.name       = self.plecs.get("Name") or (os.path.splitext(os.path.basename(path))[0] if path else "")
        self.schematic  = self.plecs.blocks("Schematic")[0]
        self.newline    = "\r\n" if "\r\n" in text else "\n"
        self._index     = None

    @classmethod
    def load(cls, path) :   return cls(read_text(path), path)

    def children(self, container):
        """ Component blocks directly inside a Schematic / Configurations / Document. """
        return (self.schematic if container is None else container).blocks("Component")

    def walk(self, container=None, path=""):
        """ Yield (component, path, parent path) for every component, at any depth. """
        for comp in self.children(container):
            cpath = path_join(path, path_name(comp.get("Name", "")))
            yield comp, cpath, path
            for sub, subpath in containers(comp, cpath):
                yield from self.walk(sub, subpath)

    def walk_component(self, comp, path):
        """ Yield (component, path, parent path) for every component inside comp, at any depth (comp itself not included). """
        for sub, subpath in containers(comp, path):
            yield from self.walk(sub, subpath)

    def index(self):
        """ {path : component}. """
        if self._index is None  :   self._index = {p: c for c, p, _ in self.walk()}
        return self._index

def containers(comp, path):
    """ Yield (container block, path) of the schematics of a component : its Schematic, or one per configuration. """
    for sch in comp.blocks("Schematic"):
        yield sch, path
    for name, sch in configurations(comp):
        yield sch, path_join(path, path_name(name))

def configurations(comp):
    """ [(configuration name, Schematic block)] of a configurable subsystem, in order. """
    out = []
    for cfg in comp.blocks("Configurations"):
        name = ""
        for c in cfg.children:                                                                          # alternating  Name "..."  /  Schematic { ... }
            if isinstance(c, Field) and c.key == "Name" :   name = c.text
            elif isinstance(c, Block) and c.key == "Schematic":
                out.append((name, c))
    return out

#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
#? Libraries and edits (shared)
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------

def load_libraries(libraries):
    """
    Libraries given as Document, file path, folder path (every .plecs inside) or a list of those -> {library name : Document}.
    """
    out = {}
    if libraries is None            :   return out
    if isinstance(libraries, dict)  :   return dict(libraries)
    if isinstance(libraries, (str, os.PathLike, Document))  :   libraries = [libraries]
    for lib in libraries:
        if isinstance(lib, Document):
            out[lib.name] = lib
        elif os.path.isdir(lib):
            for name in sorted(os.listdir(lib)):
                if name.lower().endswith(".plecs"):
                    out[os.path.splitext(name)[0]] = Document.load(os.path.join(lib, name))
        else:
            out[os.path.splitext(os.path.basename(str(lib)))[0]] = Document.load(lib)                   # a library is addressed by its file name
    return out

def indent_of(text, offset):
    return offset - (text.rfind("\n", 0, offset) + 1)

def apply_edits(text, edits, base=0):
    """ Apply [(start, end, replacement)] (offsets relative to base, not overlapping) to text. """
    if not edits    :   return text
    out, pos = [], 0
    for start, end, new in sorted(edits, key=lambda e: e[0]):
        out.append(text[pos:start - base])
        out.append(new)
        pos = end - base
    out.append(text[pos:])
    return "".join(out)

def split_source(src):
    parts = path_split(src)
    return parts[0], "/".join(parts[1:])

def linked_blocks(model):
    """ {library block path : number of links} of a model (or library) file. """
    doc, out = model if isinstance(model, Document) else Document.load(model), {}
    for comp, _, _ in doc.walk():
        if comp.raw("Type") == "Reference":
            src         = comp.get("SrcComponent", "")
            out[src]    = out.get(src, 0) + 1
    return out
