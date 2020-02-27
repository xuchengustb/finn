import os
import subprocess

from pyverilator import PyVerilator


class IPGenBuilder:
    """Builds the bash script to generate IP blocks using Vivado HLS."""
    def __init__(self):
        self.tcl_script = ""
        self.ipgen_path = ""
        self.code_gen_dir = ""
        self.ipgen_script = ""

    def append_tcl(self, tcl_script):
        """Sets member variable "tcl_script" to given tcl script."""
        self.tcl_script = tcl_script

    def set_ipgen_path(self, path):
        """Sets member variable ipgen_path to given path."""
        self.ipgen_path = path

    def build(self, code_gen_dir):
        """Builds the bash script with given parameters and saves it in given folder.
        To guarantee the generation in the correct folder the bash script contains a 
        cd command."""
        self.code_gen_dir = code_gen_dir
        self.ipgen_script = str(self.code_gen_dir) + "/ipgen.sh"
        working_dir = os.environ["PWD"]
        f = open(self.ipgen_script, "w")
        f.write("#!/bin/bash \n")
        f.write("cd {}\n".format(code_gen_dir))
        f.write("vivado_hls {}\n".format(self.tcl_script))
        f.write("cd {}\n".format(working_dir))
        f.close()
        bash_command = ["bash", self.ipgen_script]
        process_compile = subprocess.Popen(bash_command, stdout=subprocess.PIPE)
        process_compile.communicate()


def pyverilate_stitched_ip(model):
    "Given a model with stitched IP, return a PyVerilator sim object."
    vivado_stitch_proj_dir = model.get_metadata_prop("vivado_stitch_proj")
    with open(vivado_stitch_proj_dir + "/all_verilog_srcs.txt", "r") as f:
        all_verilog_srcs = f.read().split()

    def file_to_dir(x):
        return os.path.dirname(os.path.realpath(x))

    all_verilog_dirs = list(map(file_to_dir, all_verilog_srcs))
    top_verilog = model.get_metadata_prop("wrapper_filename")
    sim = PyVerilator.build(top_verilog, verilog_path=all_verilog_dirs)
    return sim


def pyverilate_get_liveness_threshold_cycles():
    """Return the number of no-output cycles rtlsim will wait before assuming
    the simulation is not finishing and throwing an exception."""

    return int(os.getenv("LIVENESS_THRESHOLD", 10000))