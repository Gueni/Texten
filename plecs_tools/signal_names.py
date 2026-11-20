#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
#?  Signal names
#?
#?  SignalNames(model, library, variables).names()
#?
#?  Clean name + source component of every signal that reaches a sink (To File by default, or Scope, Display, ...), traced
#?  back through any depth of subsystems / configurable subsystems / library blocks and any number of Goto / From / Mux /
#?  Demux / Selector blocks, down to the component the Probe (and the MaskProbe signals of masked blocks) really measures.
#?  Works on linked models (library read in place, nothing is broken) and on standalone copies (no library needed).
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
import  json
import  os
import  re

from    .plecs_file     import  (Document, Field, Block, path_name, path_join, path_split, path_leaf, display_name, containers,
                                 configurations, load_libraries, split_source)
from    .expressions    import  EvalError, evaluate, load_variables, run_script, _num


#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
#? Signal names
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
# A signal entering a sink (To File, Scope, ...) is a vector. Each element is traced back to the component signal it comes from :
#       Goto -> From (local, scoped, global), Mux, Demux, Selector, subsystem input / output ports at any depth, configurable
#       subsystems (active configuration from the parameter values), library blocks (read in the library, links do not have to be
#       broken), Probe blocks and the probe signals of masked blocks (MaskProbe) down to the component that really measures it.

# blocks that keep the signal (element i of the output is element i of the first input)
PASS_THROUGH = {"Gain", "Abs", "TransferFunction", "DiscreteTransferFunction", "ZeroOrderHold", "Saturation", "Offset", "Memory",
                "PeriodicAverage", "PeriodicImpulseAverage", "Integrator", "RateLimiter", "DataTypeConversion", "Delay", "Rounding",
                "TriggeredSubsystem", "SignalInport", "MovingAverage", "Filter", "StateSpace", "DiscreteStateSpace"}
SUBSYSTEMS   = {"Subsystem", "ConfigurableSubsystem"}
REDUCING     = {"Sum", "Product", "MinMax", "LogicalOperator"}  # one vector input -> one value
INPUT_PORTS  = {"Input", "Enable", "Trigger"}
SINKS        = {"ToFile", "Scope", "Display", "XYPlot", "FourierScope", "SignalOutport", "Output"}

class Element:
    """ One element of a signal vector. """
    __slots__ = ("component", "signal", "chain", "route", "probe", "group", "note")

    def __init__(self, component, signal, chain=(), note="", route=(), probe=None, group=None):
        self.component  = component                 # model path of the block the value comes from
        self.signal     = signal                    # signal of that block (probe signal name, or 'out <n>')
        self.chain      = tuple(chain)              # [(probed component path, probe signal name)] from the Probe block down
        self.route      = tuple(route)              # [('via', block path) | ('tag', Goto tag)] from the source to the sink
        self.probe      = probe                     # path of the Probe block the value is read by
        self.group      = group                     # elements of one probe signal share a group
        self.note       = note                      # why the value is not a clean signal (placeholder, unresolved, ...)

    def _copy(self, **kw):
        e = Element(self.component, self.signal, self.chain, self.note, self.route, self.probe, self.group)
        for k, v in kw.items()  :   setattr(e, k, v)
        return e

    def through(self, block)    :   return self._copy(route=self.route + (("via", block),))
    def tagged(self, tag)       :   return self._copy(route=self.route + (("tag", tag),))

    @property
    def via(self)               :   return [x for k, x in self.route if k in ("via", "op")]
    @property
    def tags(self)              :   return [x for k, x in self.route if k == "tag"]

    @property
    def processed_as(self):
        """ Goto tag naming the value after the last processing block (Abs, Gain, ...) it went through, if any. """
        last = max((i for i, (k, _) in enumerate(self.route) if k == "via"), default=None)
        if last is None :   return None
        return next((x for k, x in self.route[last + 1:] if k == "tag"), display_name(path_leaf(self.route[last][1])))

    def as_dict(self):
        return {"component": self.component, "signal": self.signal, "chain": [list(c) for c in self.chain], "probe": self.probe,
                "via": self.via, "tags": self.tags, "category": self.tags[-1] if self.tags else None, "note": self.note}

    def __repr__(self)  :   return "Element(%r, %r)" % (self.component, self.signal)

class _Node:
    """ A component of the model seen with every library link resolved (lazily, nothing is copied). """
    __slots__ = ("comp", "defn", "doc", "path", "parent", "origin", "_containers", "_scope", "_params")

    def __init__(self, comp, path, parent, doc, origin, defn, defdoc):
        self.comp, self.path, self.parent, self.origin = comp, path, parent, origin
        self.defn, self.doc                             = defn, defdoc          # definition block (library block for a link) / its file
        self._containers, self._scope, self._params     = None, None, None

    @property
    def type(self)  :   return self.defn.raw("Type") if self.defn is not None else self.comp.raw("Type")
    @property
    def name(self)  :   return self.comp.get("Name", "")

class _Sheet:
    """ One schematic (a subsystem or one configuration of a configurable subsystem) with its connections. """
    __slots__ = ("block", "owner", "path", "doc", "origin", "nodes", "sources", "active")

    def __init__(self, block, owner, path, doc, origin, active=True):
        self.block, self.owner, self.path, self.doc, self.origin, self.active = block, owner, path, doc, origin, active
        self.nodes, self.sources = None, None

class SignalTracer:
    """
    Trace the signals of a model back to their components.

    Args:
        model       (str | Document)            : model file.
        libraries                               : library file / folder / list (links to them are followed).
        variables   (dict | str, optional)      : model variables (dict, or .m file / script text to read them from). The model's
                                                  own InitializationCommands are always read first.
        configurations (dict, optional)         : {configurable subsystem path : configuration name or number} forced choices.
    """

    def __init__(self, model, libraries=None, variables=None, configurations=None):
        self.doc        = model if isinstance(model, Document) else Document.load(model)
        self.libs       = load_libraries(libraries)
        self.variables  = load_variables(self.doc.plecs.get("InitializationCommands", ""))
        if isinstance(variables, dict)  :   self.variables.update(variables)
        elif variables                  :   load_variables(variables, self.variables)
        self.forced     = dict(configurations or {})
        self.warnings   = []
        self._memo      = {}
        self._previous  = {}
        self._loops     = 0
        self._gotos     = None
        self.root       = _Sheet(self.doc.schematic, None, "", self.doc, (self.doc, "", ""))

    #? tree ---------------------------------------------------------------------------------------------------------------------------------------------------

    def _warn(self, msg):
        if msg not in self.warnings :   self.warnings.append(msg)

    def nodes(self, sheet):
        """ {component name : _Node} of a schematic. """
        if sheet.nodes is None:
            sheet.nodes = {}
            for comp in sheet.block.blocks("Component"):
                name = comp.get("Name", "")
                path = path_join(sheet.path, path_name(name))
                defn, defdoc, origin = comp, sheet.doc, sheet.origin
                if comp.raw("Type") == "Reference":
                    defn, defdoc, origin = self._resolve(comp, path)
                sheet.nodes[name] = _Node(comp, path, sheet, defdoc, origin, defn, defdoc)
        return sheet.nodes

    def _resolve(self, ref, path, depth=0):
        """ Library block of a link -> (definition block or None, its file, origin). """
        src             = ref.get("SrcComponent", "")
        libname, lpath  = split_source(src)
        lib             = self.libs.get(libname)
        target          = lib.index().get(lpath) if lib is not None else None
        if target is None:
            if lib is not None  :   self._warn("library block not found : %s" % src)
            return None, None, None
        if target.raw("Type") == "Reference" and depth < 20 :   return self._resolve(target, path, depth + 1)
        return target, lib, (lib, lpath, path)

    def sources(self, sheet):
        """ {(destination block name, input terminal) : (source block name, output terminal)} of a schematic. """
        if sheet.sources is None:
            sheet.sources = {}
            for con in sheet.block.blocks("Connection"):
                if con.raw("Type") != "Signal"  :   continue
                src = (con.get("SrcComponent"), con.raw("SrcTerminal"))
                stack = [con]
                while stack:
                    b = stack.pop()
                    if b.field("DstComponent") is not None  :   sheet.sources[(b.get("DstComponent"), b.raw("DstTerminal"))] = src
                    stack.extend(b.blocks("Branch"))
        return sheet.sources

    def sheets(self, node):
        """ [(configuration name or None, _Sheet)] of a subsystem node, every configuration. """
        if node._containers is None:
            node._containers = []
            if node.defn is not None and node.type in SUBSYSTEMS:
                origin  = node.origin
                for sch in node.defn.blocks("Schematic"):
                    node._containers.append((None, _Sheet(sch, node, node.path, node.doc, origin)))
                cfgs    = configurations(node.defn)
                active  = self.active_configuration(node, [n for n, _ in cfgs]) if cfgs else None
                for i, (name, sch) in enumerate(cfgs):
                    node._containers.append((name, _Sheet(sch, node, path_join(node.path, path_name(name)), node.doc, origin, i == active)))
        return node._containers

    def active_sheet(self, node):
        for name, sheet in self.sheets(node):
            if name is None or sheet.active :   return sheet
        return None

    def active_configuration(self, node, names):
        """ Index of the active configuration of a configurable subsystem (forced choice, else its Configuration parameter). """
        choice = self.forced.get(node.path, self.forced.get(path_leaf(node.path)))
        if choice is None:
            expr = self.parameter(node, "Configuration")
            try:
                choice = int(round(_num(evaluate(expr, self.scope(node.parent.owner))))) if expr is not None else 1
            except (EvalError, TypeError, ValueError):
                self._warn("configuration of '%s' can not be evaluated (%s) : first configuration '%s' used, give it with "
                           "configurations={'%s': ...}" % (node.path, expr, names[0], node.path))
                choice = 1
        if isinstance(choice, str) and not choice.isdigit():
            if choice in names  :   return names.index(choice)
            raise ValueError("'%s' has no configuration '%s' (%s)" % (node.path, choice, names))
        index = int(choice) - 1
        if not 0 <= index < len(names):
            self._warn("configuration %s of '%s' out of range : first one used" % (choice, node.path))
            index = 0
        return index

    def parameter(self, node, variable):
        """ Expression of a block parameter (value given on the link if the block is a link). """
        value = node.comp.param(variable)
        if value is None and node.defn is not None and node.defn is not node.comp  :   value = node.defn.param(variable)
        return value

    def scope(self, node):
        """ Variable lookup inside a subsystem node : its mask parameters, then the enclosing ones, then the model variables. """
        if node is None:
            variables = self.variables
            def lookup(name):
                if name in variables    :   return variables[name]
                raise EvalError("unknown variable %s" % name)
            return lookup
        if node._scope is None:
            outer   = self.scope(node.parent.owner)
            local   = {}
            if node.defn is not None:
                for p in node.defn.blocks("Parameter"):
                    var = p.get("Variable")
                    if not var or var == "Configuration"    :   continue
                    expr = self.parameter(node, var)
                    if expr in (None, "")   :   local[var] = []                                         # empty field = []
                    else:
                        try                 :   local[var] = evaluate(expr, outer)
                        except Exception    :   pass
                init = node.defn.get("MaskInit")
                if init :   run_script(init, local, outer)
            def lookup(name, _local=local, _outer=outer):
                if name in _local   :   return _local[name]
                return _outer(name)
            node._scope = lookup
        return node._scope

    def evaluate(self, node, expr, default=None):
        """ Evaluate a parameter of a block in the scope it sits in. """
        try     :   return evaluate(expr, self.scope(node.parent.owner))
        except (EvalError, TypeError, ValueError, ZeroDivisionError):
            return default

    def find(self, path):
        """ Path in the model (configuration names included) -> (_Node or None, active). """
        sheet, node, active, parts = self.root, None, True, path_split(path) if path else []
        i = 0
        while i < len(parts):
            if sheet is None    :   return None, active
            node = self.nodes(sheet).get(path_leaf(parts[i]))
            if node is None     :   return None, active
            i += 1
            if i == len(parts)  :   break
            sheets = self.sheets(node)
            nxt    = None
            for name, sh in sheets:
                if name is not None and path_name(name) == parts[i]:
                    nxt, active = sh, active and sh.active
                    i += 1
                    break
            if nxt is None:
                nxt = next((sh for name, sh in sheets if name is None), None)
            sheet = nxt
        return node, active

    def model_path(self, origin, path):
        """ Absolute path written in a file -> path in the model. """
        doc, lpath, mpath = origin
        if doc is self.doc  :   return path
        if path == lpath or path.startswith(lpath + "/")    :   return path_join(mpath, path[len(lpath) + 1:])
        return None

    #? tracing ------------------------------------------------------------------------------------------------------------------------------------------------

    def input(self, sheet, name, terminal):
        """ Elements entering input terminal of block name in sheet. """
        src = self.sources(sheet).get((name, str(terminal)))
        if src is None:
            self._warn("input %s of '%s' is not connected" % (terminal, path_join(sheet.path, path_name(name))))
            return []
        return self.output(sheet, src[0], src[1])

    def trace_inputs(self, sheet, name, passes=3):
        """
        inputs() with feedback loops solved : a loop is cut where it is met and the signal there is taken from the previous pass,
        passes are repeated until the result does not change any more.
        """
        result = None
        for _ in range(passes):
            self._loops, warnings = 0, list(self.warnings)
            result  = self.inputs(sheet, name)
            if not self._loops  :   break
            shape   = {k: len(v) for k, v in self._memo.items() if v is not None}
            if self._previous and shape == {k: len(v) for k, v in self._previous.items() if v is not None}:
                break
            self._previous, self._memo, self.warnings = self._memo, {}, warnings
        return result

    def inputs(self, sheet, name):
        """ {input terminal : elements} of every connected input of a block. """
        terms = sorted((int(t) for (dst, t) in self.sources(sheet) if dst == name), key=int)
        return [(t, self.input(sheet, name, t)) for t in terms]

    def output(self, sheet, name, terminal):
        key = (id(sheet), name, str(terminal))
        if key in self._memo:
            if self._memo[key] is None:                                                                 # feedback loop : the value of
                self._loops += 1                                                                        # the previous pass is used
                return self._previous.get(key) or []
            return self._memo[key]
        self._memo[key] = None
        try     :   out = self._output(sheet, name, int(terminal))
        except RecursionError:
            out = [Element(path_join(sheet.path, path_name(name)), "out %s" % terminal, note="too deep")]
        self._memo[key] = out
        return out

    def _output(self, sheet, name, terminal):
        node = self.nodes(sheet).get(name)
        if node is None:
            self._warn("block '%s' not found in '%s'" % (name, sheet.path))
            return []
        kind = node.type if node.defn is not None else "Reference"

        if kind == "PlecsProbe":
            out = []
            for probe in node.comp.blocks("Probe"):
                path = self.model_path(sheet.origin, probe.get("Path", ""))
                comp = path_join(path, path_name(probe.get("Component", "")))
                for signal in (probe.field("Signals").items if probe.field("Signals") is not None else []):
                    group = (node.path, comp, signal, len(out))
                    out.extend(e._copy(group=group, probe=node.path) for e in self.probe(comp, signal))
            return out

        if kind == "SignalMux":
            out, width = [], self.evaluate(node, self.parameter(node, "Width"), 0)
            widths = [int(w) for w in width] if isinstance(width, list) else None
            count  = len(widths) if widths else int(width or 0)
            if not count:
                count = max((int(t) - 1 for (dst, t) in self.sources(sheet) if dst == name), default=0)
                self._warn("width of '%s' can not be evaluated (%s)" % (node.path, self.parameter(node, "Width")))
            for k in range(count):
                part = self.input(sheet, name, k + 2)
                if widths   :   part = self.fit(part, widths[k], node, "input %d" % (k + 1))
                out.extend(part)
            return out

        if kind == "SignalDemux":
            data   = self.input(sheet, name, 1)
            width  = self.evaluate(node, self.parameter(node, "Width"), 1)
            if isinstance(width, list):
                widths  = [int(w) for w in width]
                data    = self.fit(data, sum(widths), node, "input")
            else:
                n       = max(int(width), 1)
                widths  = [len(data) // n] * n
            start = sum(widths[:terminal - 2])
            return data[start:start + widths[terminal - 2]] if terminal - 2 < len(widths) else []

        if kind == "SignalSelector":
            data    = self.input(sheet, name, 1)
            width   = self.evaluate(node, self.parameter(node, "InputWidth"))
            if isinstance(width, float) and width > 0   :   data = self.fit(data, int(width), node, "input")
            indices = self.evaluate(node, self.parameter(node, "OutputIndices"))
            if indices is None:
                self._warn("indices of '%s' can not be evaluated" % node.path)
                return [Element(node.path, "out", note="unresolved selector")]
            out = []
            for k in (indices if isinstance(indices, list) else [indices]):
                k = int(round(_num(k)))
                out.append(data[k - 1] if 0 < k <= len(data) else Element(node.path, "element %d" % k, note="index out of range"))
            return out

        if kind == "From":
            goto = self.goto(sheet, node)
            if goto is None:
                self._warn("no Goto for From '%s' (tag %s)" % (node.path, self.parameter(node, "Tag")))
                return []
            tag = self.parameter(node, "Tag")
            return [e.tagged(tag) for e in self.input(goto[0], goto[1], 1)]

        if kind in INPUT_PORTS:
            owner = sheet.owner
            index = self.evaluate(node, self.parameter(node, "Index"))
            if owner is None or index is None:
                return [Element(node.path, "model input", note="model input port")]
            return self.fit(self.input(owner.parent, owner.name, int(index)), self.port_width(node), node, "port")

        if kind in SUBSYSTEMS:
            inner = self.active_sheet(node)
            if inner is None    :   return [Element(node.path, "out %d" % terminal, note="empty subsystem")]
            nodes   = self.nodes(inner).values()
            sampled = any(sub.type == "Trigger" for sub in nodes)                         # triggered subsystem = sample & hold
            for sub in nodes:
                if sub.type == "Output" and self.evaluate(sub, self.parameter(sub, "Index")) == terminal:
                    out = self.fit(self.input(inner, sub.name, 1), self.port_width(sub), sub, "port")
                    return [e.through(node.path) for e in out] if sampled else out
            return []

        if kind == "Constant":
            value = self.evaluate(node, self.parameter(node, "Value"))
            n     = len(value) if isinstance(value, list) else 1
            if value is None    :   self._warn("value of '%s' can not be evaluated : width 1 assumed" % node.path)
            return [Element(node.path, "Constant" if n == 1 else "Constant(%d)" % (k + 1)) for k in range(n)]

        ins = self.inputs(sheet, name)
        if kind in PASS_THROUGH and ins:
            return [e._copy(route=e.route + (("op", node.path),)) for e in ins[0][1]]

        if kind in REDUCING and len(ins) == 1   :   width = 1                                          # Sum / Product of one vector
        else                                    :   width = max((len(e) for _, e in ins), default=1)    # other blocks : new signal
        return [Element(node.path, "out %d" % terminal if width == 1 else "out %d(%d)" % (terminal, k + 1)) for k in range(width)]

    def port_width(self, node):
        """ Width a port declares (None : inherited). """
        width = self.evaluate(node, self.parameter(node, "Width"))
        return int(width) if isinstance(width, float) and width > 0 else None

    def fit(self, elements, width, node, where):
        """
        Make a traced signal the width the model declares at node : the model is right (PLECS checks these widths), so a block
        whose width could only be guessed never shifts the signals after it. Missing elements are marked, extra ones dropped.
        """
        if width is None or len(elements) == width or not elements :   return elements
        self._warn("'%s' %s : %d signals traced, the model declares %d (fixed)" % (node.path, where, len(elements), width))
        if len(elements) > width    :   return [e._copy(note=e.note or "width guessed upstream") for e in elements[:width]]
        return elements + [Element(node.path, "%s element %d" % (where, k + 1), note="width guessed upstream : unknown element")
                           for k in range(len(elements), width)]

    def goto(self, sheet, node):
        """ (sheet, Goto block name) a From block reads. """
        tag = self.parameter(node, "Tag")
        vis = self.parameter(node, "Visibility") or "2"
        for sub in self.nodes(sheet).values():                                                          # same schematic first
            if sub.type == "Goto" and self.parameter(sub, "Tag") == tag:
                return sheet, sub.name
        if vis == "2"   :   return None
        if vis == "3":                                                                                  # scoped : enclosing schematics
            sh = sheet.owner.parent if sheet.owner is not None else None
            while sh is not None:
                for sub in self.nodes(sh).values():
                    if sub.type == "Goto" and self.parameter(sub, "Tag") == tag and self.parameter(sub, "Visibility") == "3":
                        return sh, sub.name
                sh = sh.owner.parent if sh.owner is not None else None
            return None
        found = self.global_gotos().get(tag, [])
        if len(found) > 1:
            self._warn("global tag %s : %d active Goto blocks (%s), first one used" % (tag, len(found), [path_join(s.path, path_name(n)) for s, n in found]))
        return found[0] if found else None

    def global_gotos(self):
        """ {tag : [(sheet, Goto name)]} of the global Goto blocks in the active part of the model. """
        if self._gotos is None:
            self._gotos = {}
            stack = [self.root]
            while stack:
                sheet = stack.pop()
                for node in self.nodes(sheet).values():
                    kind = node.type if node.defn is not None else None
                    if kind == "Goto" and self.parameter(node, "Visibility") == "1":
                        self._gotos.setdefault(self.parameter(node, "Tag"), []).append((sheet, node.name))
                    elif kind in SUBSYSTEMS:
                        inner = self.active_sheet(node)
                        if inner is not None    :   stack.append(inner)
        return self._gotos

    def probe(self, path, signal, chain=()):
        """ Elements of probe signal 'signal' of the component at model path. """
        chain       = chain + ((path, signal),)
        node, alive = self.find(path)
        if not alive    :   return []                                                                   # inactive configuration
        if node is None:
            self._warn("probed component not found : %s" % path)
            return [Element(path, signal, chain, note="component not found")]
        if node.defn is not None:
            for mp in node.defn.blocks("MaskProbe"):
                if mp.get("Name") != signal :   continue
                out = []
                for probe in mp.blocks("Probe"):
                    sub = path_join(node.path, probe.get("Path", ""), path_name(probe.get("Component", "")))
                    for sig in (probe.field("Signals").items if probe.field("Signals") is not None else []):
                        out.extend(self.probe(sub, sig, chain))
                return out
        if node.defn is None:
            note = "" if node.comp.get("SrcComponent", "").startswith("Components/") else "library block not resolved"
            return [Element(node.path, signal, chain, note=note)]
        if node.type == "Constant" and signal == "Constant":
            value = self.evaluate(node, self.parameter(node, "Value"))
            note  = "constant placeholder (part disabled in this configuration)" if len(chain) > 1 else ""
            if isinstance(value, list) and len(value) != 1:
                return [Element(node.path, "%s(%d)" % (signal, k + 1), chain, note=note) for k in range(len(value))]
            return [Element(node.path, signal, chain, note=note)]
        if signal in ("Input", "Output") and node.type not in SUBSYSTEMS:                                # signal block : width of its signal
            sheet   = node.parent
            if node.type in INPUT_PORTS:                                                                # port : its own signal
                width = len(self.output(sheet, node.name, 1))
            elif node.type == "Output":
                width = len(self.input(sheet, node.name, 1))
            elif signal == "Input":
                terms   = sorted(int(t) for (dst, t) in self.sources(sheet) if dst == node.name)
                width   = len(self.input(sheet, node.name, terms[0])) if terms else 1
            else:
                terms   = sorted({int(st) for (sn, st) in self.sources(sheet).values() if sn == node.name})
                width   = len(self.output(sheet, node.name, terms[0])) if terms else 1
            if node.type in INPUT_PORTS or node.type == "Output":
                width = self.port_width(node) or width                                                  # declared width wins
            if width > 1:
                return [Element(node.path, "%s(%d)" % (signal, k + 1), chain) for k in range(width)]
        return [Element(node.path, signal, chain)]

    #? sinks --------------------------------------------------------------------------------------------------------------------------------------------------

    def sinks(self, types=("ToFile",)):
        """ [(model path, sheet, block name)] of the blocks of the given types in the active part of the model. """
        out, stack = [], [self.root]
        while stack:
            sheet = stack.pop(0)
            for node in self.nodes(sheet).values():
                if node.defn is None    :   continue
                if node.type in types   :   out.append((node.path, sheet, node.name))
                elif node.type in SUBSYSTEMS:
                    inner = self.active_sheet(node)
                    if inner is not None    :   stack.append(inner)
        return out

    def sink_signals(self, path):
        """ {input terminal : [Element]} of the sink block at model path. """
        node, _ = self.find(path)
        if node is None :   raise KeyError("block not found : %s" % path)
        return dict(self.inputs(node.parent, node.name))

def _words(text)    :   return display_name(text).split()
def _stem(word)     :   w = word.lower().rstrip(".,:"); return w[:-1] if w.endswith("s") and len(w) > 3 else w

def merge_labels(outer, inner):
    """
    'Choke RC Snubber Current' + 'Resistor Current' -> 'Choke RC Snubber Resistor Current' : the quantity word the outer label ends
    with is not repeated, words the inner label already starts with are not repeated.
    """
    a, b = _words(outer), _words(inner)
    if not b    :   return " ".join(a)
    if a and len(b) > 1 and _stem(a[0]) == _stem(b[0]) and _stem(a[-1]) == _stem(b[-1]):           # 'CT Trafo Current' / 'CT Transformer Current'
        return " ".join(a)
    if a and _stem(a[-1]) == _stem(b[-1])  :   a = a[:-1]                                              # same quantity (Current / Currents)
    k = min(len(a), len(b))
    while k and [_stem(w) for w in a[-k:]] != [_stem(w) for w in b[:k]]:
        k -= 1
    lower = {_stem(w) for w in a}
    if all(_stem(w) in lower for w in b)    :   return " ".join(a + b[-1:]) if a else " ".join(b)     # nothing new in inner
    return " ".join(a + b[k:])

def _differing_segment(paths):
    """ For each path, its first segment after the part all paths share (None if all paths are equal). """
    parts   = [path_split(p) for p in paths]
    k       = 0
    while all(len(x) > k for x in parts) and len(set(x[k] for x in parts)) == 1:
        k += 1
    return [display_name(path_leaf(x[k])) if len(x) > k else None for x in parts]

_GENERIC_PROBE  = re.compile(r"^(probe|plecs ?probe)\s*\d*$", re.I)
_GENERIC_TAG    = re.compile(r"^[A-Za-z]{0,2}\d*$")                    # P1, P2, X ... : routing tags, they say nothing

def _category(e)    :   return e.tags[-1] if e.tags else None

def _labels(e):
    """
    Names the model designer gave to the signal, outer first : the probe signal names (mask probes) down the chain. The last
    chain entry is the signal of the built-in block that really measures it ('Output', 'Constant', 'Measured voltage', ...),
    generic, so it is only used when the Probe block reads that built-in block directly.
    """
    if e.chain:
        labels = [display_name(sig) for _, sig in e.chain[:-1]]
        if not labels   :   labels = ["%s %s" % (display_name(path_leaf(e.component)), display_name(re.sub(r"\(\d+\)$", "", e.signal)))]
        return labels
    block   = display_name(path_leaf(e.component))
    tag     = next((t for t in e.tags if not _GENERIC_TAG.match(t) and t != _category(e)), None)
    if "placeholder" in block.lower() or e.note.startswith("constant placeholder"):
        return ["%s placeholder" % display_name((_category(e) or block).replace("_", " "))]
    return [tag or block]

def clean_names(elements, unique=False):
    """
    Short name for each element, built from the names the model designer gave (probe signal names of the mask probes) :
        - the outer probe signal name,
        - refined with the next probe levels only where they tell the elements of one probe signal apart,
        - then with the component that differs (e.g. 'Coc2' / 'Coc3', 'CPH_Vo' / 'CPH_Io'), then numbered.
    A value sampled on its way (triggered subsystem) gets the Goto tag it is sent with, e.g. 'HV Left-Leg HS Current (Ion_L)'.

    Args:
        elements (list)     : [Element].
        unique   (bool)     : make names unique in the whole list (same signal read twice, exported in two categories, ...) :
                              the probed component, the export category, the Probe block name are added where they differ,
                              a number otherwise.
    """
    def build(i, depth):
        lv   = labels[i]
        name = lv[0]
        for x in lv[1:depth]    :   name = merge_labels(name, x)
        tag = elements[i].processed_as
        return "%s (%s)" % (name, tag) if tag else name

    def collisions(idx):
        seen = {}
        for i in idx    :   seen.setdefault(names[i].lower(), []).append(i)
        return [same for same in seen.values() if len(same) > 1]

    def by_component(same):
        """ Suffix the colliding names with the component segment that differs, again on what still collides. """
        pending = [same]
        while pending:
            grp = pending.pop()
            seg = _differing_segment([elements[i].component for i in grp])
            if not any(seg) :   continue
            for i, s in zip(grp, seg):
                if s and s.lower() not in names[i].lower()  :   names[i] = "%s %s" % (names[i], s)
            pending.extend(c for c in collisions(grp))

    def number(same):
        for k, i in enumerate(same) :   names[i] = "%s %d" % (names[i], k + 1)

    labels  = [_labels(e) for e in elements]
    names   = [None] * len(elements)
    groups  = {}
    for i, e in enumerate(elements):
        groups.setdefault(e.group if e.group is not None else ("single", i), []).append(i)

    for idx in groups.values():
        depth = {i: 1 for i in idx}
        for i in idx    :   names[i] = build(i, 1)
        while True:                                                                                     # next label level, only where
            grow = []                                                                                   # it tells colliding names apart
            for same in collisions(idx):
                deeper = [i for i in same if depth[i] < len(labels[i])]
                if len({tuple(labels[i][depth[i]:depth[i] + 1]) for i in same}) > 1 :   grow.extend(deeper)
            if not grow :   break
            for i in grow:
                depth[i] += 1
                names[i] = build(i, depth[i])
        if len(idx) > 1 and any(depth[i] > 1 for i in idx):                                            # odd one out : no sub-label
            for i in idx:
                if depth[i] == 1 and len(labels[i]) == 1 and elements[i].chain and len(elements[i].chain) > 1:
                    names[i] = "%s %s" % (names[i], display_name(path_leaf(elements[i].component)))
        for same in collisions(idx):                                                                    # built-in signal that differs
            leaf = [display_name(re.sub(r"\(\d+\)$", "", elements[i].signal)) for i in same]
            if len(set(leaf)) > 1:
                for i, l in zip(same, leaf) :   names[i] = "%s %s" % (names[i], l)
        for same in collisions(idx) :   by_component(same)
        for same in collisions(idx) :   number(same)

    if unique:
        idx = list(range(len(elements)))
        for same in collisions(idx):                                                                    # probed component
            seg = _differing_segment([elements[i].chain[0][0] if elements[i].chain else elements[i].component for i in same])
            for i, s in zip(same, seg):
                if s and s.lower() not in names[i].lower()  :   names[i] = "%s [%s]" % (names[i], s)
        for same in collisions(idx):                                                                    # export category
            cats = [_category(elements[i]) for i in same]
            if len(set(cats)) > 1:
                for i, c in zip(same, cats):
                    if c and c != cats[0]   :   names[i] = "%s (%s)" % (names[i], c)
        for same in collisions(idx):                                                                    # Probe block
            probes = [display_name(path_leaf(elements[i].probe)) if elements[i].probe else None for i in same]
            if len(set(probes)) > 1:
                for i, p in zip(same, probes):
                    if p and not _GENERIC_PROBE.match(p)    :   names[i] = "%s [%s]" % (names[i], p)
        for same in collisions(idx) :   number(same)
    return names

def _is_placeholder(e):
    """ The element only carries a constant standing for a disabled part of the model. """
    if e.note.startswith("constant placeholder")    :   return True
    return not e.chain and "placeholder" in display_name(path_leaf(e.component)).lower()

class SignalNames:
    """
    Names of the signals reaching the sinks of a model.

    Args:
        model          (str | Document)     : model file.
        libraries                           : library file / folder / list (not needed for a standalone model).
        variables      (dict | str)         : model variables, or the .m file with them (configuration selectors, widths, ...).
        configurations (dict, optional)     : {configurable subsystem path : configuration name or number} forced choices.
        sinks          (tuple)              : sink block types ('ToFile', 'Scope', 'Display', ...).
        sink           (str, optional)      : path (or name) of one sink block. Default : every sink of the given types.
        unique         (bool)               : names unique over each sink input.

    Use:
        names   = SignalNames(model, library, variables).names()                        # every column, in order
        enabled = SignalNames(model, library, variables).names(placeholders=False)      # only the real (enabled) signals
        columns = SignalNames(model, library, variables).columns()                      # {column number : name} of the real signals
        SignalNames(model, library, variables).save(json_path)

    A placeholder is a column that only carries a constant : the part of the model it stands for is disabled in the active
    configuration (e.g. a 'Disable' / 'Pass' configuration), PLECS exports a constant there to keep the column count.
    """

    def __init__(self, model, libraries=None, variables=None, configurations=None, sinks=("ToFile",), sink=None, unique=True):
        tracer  = SignalTracer(model, libraries, variables, configurations)
        found   = tracer.sinks(tuple(sinks))
        if sink is not None:
            found = [s for s in found if s[0] == sink or path_leaf(s[0]) == sink or display_name(path_leaf(s[0])) == sink]
            if not found    :   raise KeyError("no active sink '%s' of type %s" % (sink, sinks))
        self.signals = {}                                                   # {sink path : {input terminal : [signal dict]}}
        for path, sheet, name in found:
            self.signals[path] = {}
            for term, elems in tracer.trace_inputs(sheet, name):
                names = clean_names(elems, unique)
                self.signals[path][term] = [dict(e.as_dict(), name=n, index=k + 1, placeholder=_is_placeholder(e))
                                            for k, (e, n) in enumerate(zip(elems, names))]
        self.warnings = tracer.warnings

    def names(self, sink=None, terminal=None, placeholders=True):
        """ Names of the signals of one sink input (default : first sink, first input), in column order. """
        return [s["name"] for s in self.table(sink, terminal, placeholders)]

    def columns(self, sink=None, terminal=None, placeholders=False):
        """
        {column number : name}. Column numbers are those of the exported file : 0 is the time, the signals start at 1, so
        a csv can be reduced to the real signals with  df.iloc[:, [0] + list(columns)].
        """
        return {s["index"]: s["name"] for s in self.table(sink, terminal, placeholders)}

    def table(self, sink=None, terminal=None, placeholders=True):
        """ Signal dicts (name, index, category, component, signal, placeholder, note, ...) of one sink input, in column order. """
        if not self.signals :   return []
        terms = self.signals[sink] if sink is not None else next(iter(self.signals.values()))
        if not terms        :   return []
        rows  = terms[terminal] if terminal is not None else next(iter(terms.values()))
        return rows if placeholders else [s for s in rows if not s["placeholder"]]

    def save(self, path):
        """ Write every signal and the warnings to a json file. Returns the path. """
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f    :   json.dump({"sinks": self.signals, "warnings": self.warnings}, f, indent=2, ensure_ascii=False)
        return path
