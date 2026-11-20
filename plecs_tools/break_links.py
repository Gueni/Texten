#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
#?  Break library links
#?
#?  BreakLinks(model, library).save(output)
#?
#?  Every linked block of the model is replaced by the library block itself, at any depth (links inside library blocks too),
#?  with the name / place / parameter values of the link and the Probe paths moved to the model. Links to the PLECS
#?  built-in library ('Components/...') are kept : every PLECS installation resolves them.
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
import  os
import  shutil

from    .plecs_file     import  Document, encode, parse, write_text, path_join, load_libraries, indent_of, apply_edits, split_source


#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
#? Library links
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
# A linked block is stored as
#       Component { Type Reference  SrcComponent "<Library>/<path>"  Name ... Position ...  Parameter {..}  Terminal {..} }
# Breaking the link = writing the library block itself in its place, with
#       - the name / position / orientation of the instance,
#       - the parameter values of the instance,
#       - the links of the blocks inside it broken the same way (any depth),
#       - the paths of the Probe blocks inside it moved from the library to the place of the instance in the model.

INSTANCE_FIELDS = ("Name", "Show", "Position", "Direction", "Flipped", "LabelPosition", "Frame")

class LinkReport:
    """ What break_links() did. """

    def __init__(self):
        self.broken     = {}                # {library block path : number of links broken}
        self.external   = {}                # {library block path : number of links kept, library not given (PLECS built-in 'Components/...')}
        self.missing    = {}                # {library block path : number of links kept, block not found in the given library}
        self.probes     = 0                 # number of probe paths moved to the model

    @property
    def count(self) :   return sum(self.broken.values())

    def summary(self):
        lines = ["links broken                  : %d  (%d different library blocks)" % (self.count, len(self.broken)),
                 "probe paths moved             : %d" % self.probes,
                 "links kept (library not given): %d  %s" % (sum(self.external.values()), sorted(self.external) if self.external else ""),
                 "links kept (block not found)  : %d  %s" % (sum(self.missing.values()), sorted(self.missing) if self.missing else "")]
        return "\n".join(lines)

def _reindent(text, delta):
    """ Shift every line but the first by delta columns. Continuation lines of long strings start at column 0 with a quote : untouched. """
    if delta == 0   :   return text
    lines = text.split("\n")
    for i in range(1, len(lines)):
        line = lines[i]
        if not line.startswith(" ") :   continue
        if delta > 0                :   lines[i] = " " * delta + line
        else                        :   lines[i] = line[min(-delta, len(line) - len(line.lstrip(" "))):]
    return "\n".join(lines)

def _instance_edits(comp, ref):
    """ Edits that give the library block comp the name / place / parameter values of the Reference ref. """
    values  = {p.get("Variable"): p for p in ref.blocks("Parameter")}
    edits   = []
    for key in INSTANCE_FIELDS:
        mine, theirs = comp.field(key), ref.field(key)
        if mine is not None and theirs is not None  :   edits.append((mine.vstart, mine.end, theirs.raw))
    for p in comp.blocks("Parameter"):
        inst = values.get(p.get("Variable"))
        if inst is None :   continue
        for key in ("Value", "Show"):
            mine, theirs = p.field(key), inst.field(key)
            if mine is not None and theirs is not None  :   edits.append((mine.vstart, mine.end, theirs.raw))
    return edits

def _expand(ref, doc, inst_path, libs, report, stack):
    """
    Text of the library block a Reference points to, written as it has to stand in place of that Reference.

    Args:
        ref       (Block)       : the Reference component.
        doc       (Document)    : file the Reference is written in (model or library).
        inst_path (str)         : path the block has in the final model.
        libs      (dict)        : {library name : Document}.
        report    (LinkReport)  : counters.
        stack     (tuple)       : library blocks being expanded (cycle guard).

    Returns:
        str or None : None if the link has to stay.
    """
    src             = ref.get("SrcComponent", "")
    libname, lpath  = split_source(src)
    lib             = libs.get(libname)
    if lib is None:
        report.external[src] = report.external.get(src, 0) + 1
        return None
    target = lib.index().get(lpath)
    if target is None or (libname, lpath) in stack:
        report.missing[src] = report.missing.get(src, 0) + 1
        return None
    stack = stack + ((libname, lpath),)

    if target.raw("Type") == "Reference":                                                               # library block that is itself a link
        alias   = True
        body    = _expand(target, lib, inst_path, libs, report, stack)
        if body is None:
            report.missing[src] = report.missing.get(src, 0) + 1
            return None
    else:
        alias   = False
        edits   = []
        for sub, subpath, _ in lib.walk_component(target, lpath):
            kind = sub.raw("Type")
            if kind == "Reference":                                                                     # link inside the library block
                new = _expand(sub, lib, path_join(inst_path, subpath[len(lpath) + 1:]), libs, report, stack)
                if new is not None  :   edits.append((sub.start, sub.end, new))
            elif kind == "PlecsProbe":                                                                  # probe paths are absolute : library path -> model path
                for probe in sub.blocks("Probe"):
                    f = probe.field("Path")
                    if f is None    :   continue
                    path = f.text
                    if path == lpath or path.startswith(lpath + "/"):
                        new_path = path_join(inst_path, path[len(lpath) + 1:])
                        edits.append((f.vstart, f.end, encode(new_path, indent_of(lib.text, f.vstart)).replace("\n", lib.newline)))
                        report.probes += 1
        edits += _instance_edits(target, ref)
        body   = apply_edits(lib.text[target.start:target.end], edits, target.start)
    body = _reindent(body, -indent_of(lib.text, target.start))                                         # block now starts at column 0
    if alias:
        body = apply_edits(body, _instance_edits(parse(body).blocks("Component")[0], ref))
    if lib.newline != doc.newline   :   body = body.replace("\r\n", "\n").replace("\n", doc.newline)
    report.broken[src] = report.broken.get(src, 0) + 1
    return _reindent(body, indent_of(doc.text, ref.start))

class BreakLinks:
    """
    Break the links of a model to its libraries.

    Args:
        model     (str | Document)  : model file.
        libraries                   : library file, folder of libraries, Document, or a list of them.
        name      (str, optional)   : model name to write in the file ('Name' field). Default : unchanged.

    Use:
        BreakLinks(model, library).save(output)         # output = None : the model itself (a .bak copy is written first)
    """

    def __init__(self, model, libraries, name=None):
        self.model      = model
        self.doc        = model if isinstance(model, Document) else Document.load(model)
        self.libs       = load_libraries(libraries)
        self.report     = LinkReport()
        edits           = []
        for comp, path, _ in self.doc.walk():
            if comp.raw("Type") != "Reference"  :   continue
            new = _expand(comp, self.doc, path, self.libs, self.report, ())
            if new is not None  :   edits.append((comp.start, comp.end, new))
        field = self.doc.plecs.field("Name")
        if name is not None and field is not None:
            edits.append((field.vstart, field.end, encode(name, indent_of(self.doc.text, field.vstart)).replace("\n", self.doc.newline)))
        self.text       = apply_edits(self.doc.text, edits)                 # model text without links

    def save(self, output=None):
        """ Write the model without links. output = None : the model file itself, after a .bak copy. Returns the path. """
        if output is None:
            if isinstance(self.model, Document) and not self.model.path :   raise ValueError("no file to write : give output")
            output = self.model.path if isinstance(self.model, Document) else self.model
            shutil.copy2(output, str(output) + ".bak")
        write_text(output, self.text)
        return output

    def __repr__(self)  :   return "BreakLinks(%s)\n%s" % (getattr(self.doc, "path", ""), self.report.summary())
