import os, time, json
from multiprocessing import Pool


def convert_one_design(design, cmd, output_dir):
    bench_path = f"../example/verilog/"
    design_dir = bench_path + design + '_' + cmd + '.v'
    print('Current Design: ', design)
    print('Current CMD: ', cmd)
    os.system(f'python3 analyze.py {design_dir} -N {design} -C {cmd} -O {output_dir}')

    

if __name__ == '__main__':

    design_name = "TinyRocket"
    
    cmd = 'ast' ## for word-level
    cmd = 'sog' ## for bit-level

    output_dir = f'../example/{cmd}/'

    convert_one_design(design_name, cmd, output_dir)


