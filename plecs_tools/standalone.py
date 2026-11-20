#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
#?  Standalone copy of a model
#?
#?  Standalone(model, library).save(output)
#?
#?  Copies the model as a file that does not need the libraries any more (BreakLinks on the copy, the source is never
#?  modified). The copy gets its own name inside the file.
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
import  os

from    .break_links    import  BreakLinks


class Standalone:
    """
    Standalone copy of a model.

    Args:
        model     (str)             : model file.
        libraries                   : library file, folder of libraries, or a list of them.
        rename    (bool)            : write the name of the copy in the file ('Name' field).

    Use:
        Standalone(model, library).save(output)         # output = None : '<model>_standalone.plecs' next to the model
    """

    def __init__(self, model, libraries, rename=True):
        self.model, self.libraries, self.rename = str(model), libraries, rename
        self.links  = None                                                  # BreakLinks of the last save (report : .links.report)

    def save(self, output=None):
        """ Write the copy. Returns its path. """
        if output is None:
            stem, ext   = os.path.splitext(self.model)
            output      = stem + "_standalone" + ext
        if os.path.abspath(output) == os.path.abspath(self.model):
            raise ValueError("the standalone copy can not overwrite the source model : %s" % output)
        name        = os.path.splitext(os.path.basename(output))[0] if self.rename else None
        self.links  = BreakLinks(self.model, self.libraries, name=name)
        return self.links.save(output)

    @property
    def report(self)    :   return self.links.report if self.links else None
