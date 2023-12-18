from __future__ import absolute_import
from __future__ import print_function
import sys
import os, time
from optparse import OptionParser

# the next line can be removed after installation
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pyverilog
from pyverilog.vparser.parser import parse
from AST_analyzer import *


def main(design_name=None, cmd=None, out_path=None):
    start_time = time.perf_counter()
    INFO = "Verilog code parser"
    VERSION = pyverilog.__version__
    USAGE = "Usage: python example_parser.py file ..."

    def showVersion():
        print(INFO)
        print(VERSION)
        print(USAGE)
        sys.exit()

    optparser = OptionParser()
    optparser.add_option("-v", "--version", action="store_true", dest="showversion",
                         default=False, help="Show the version")
    optparser.add_option("-I", "--include", dest="include", action="append",
                         default=[], help="Include path")
    optparser.add_option("-D", dest="define", action="append",
                         default=[], help="Macro Definition")
    optparser.add_option("-N", dest="Name", action="append",
                         default=[], help="Design Name")
    optparser.add_option("-C", dest="cmd", action="append",
                         default=[], help="Design command")
    optparser.add_option("-O", dest="out_path", action="append",
                         default=[], help="Output path")
    (options, args) = optparser.parse_args()

    if options.Name:
        design_name = options.Name[0]
    if options.cmd:
        cmd = options.cmd[0]
    if options.out_path:
        out_path = options.out_path[0]

    filelist = args
    if options.showversion:
        showVersion()

    for f in filelist:
        if not os.path.exists(f):
            raise IOError("file not found: " + f)

    if len(filelist) == 0:
        showVersion()


    ast, directives = parse(filelist,
                            preprocess_include=options.include,
                            preprocess_define=options.define)
    
    print('Verilog2AST Finish!')
    ast_analysis = AST_analyzer(ast)
    
    ast_analysis.AST2Graph(ast)

    g = ast_analysis.graph

    # g.show_graph()

    g.graph2pkl(design_name, cmd, out_path)


if __name__ == '__main__':
    main()