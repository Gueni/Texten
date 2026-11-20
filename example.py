#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
#?  Example on the project model and library
#?
#?  Run this file : standalone copy + signal names of archive/DCDC/psfbConverterFBR.plecs, written to archive/output.
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
import  os

from    plecs_tools     import  Standalone, SignalNames


HERE        = os.path.dirname(os.path.abspath(__file__))
MODEL       = os.path.join(HERE, "archive", "DCDC", "psfbConverterFBR.plecs")
LIBRARY     = os.path.join(HERE, "archive", "MyLibraries", "CustomLibraries.plecs")
VARIABLES   = os.path.join(HERE, "archive", "Script", "assets", "Configuration", "InitializationCommands.m")
OUTPUT      = os.path.join(HERE, "archive", "output")

if __name__ == "__main__":

    # Standalone copy (links broken)
    copy    = Standalone(MODEL, LIBRARY).save(os.path.join(OUTPUT, "psfbConverterFBR_standalone.plecs"))
    print("standalone copy : %s" % copy)

    # Signal names of the To File columns
    names   = SignalNames(MODEL, LIBRARY, VARIABLES).names()
    for i, name in enumerate(names, 1) :   print("%4d  %s" % (i, name))
