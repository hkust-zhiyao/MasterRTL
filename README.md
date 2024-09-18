# MasterRTL: A Pre-Synthesis PPA Estimation Framework for Any RTL Design

Wenji Fang, Yao Lu, Shang Liu, Qijun Zhang, Ceyu Xu, Lisa Wu Wills, Hongce Zhang, Zhiyao Xie. In Proceedings of IEEE/ACM International Conference on Computer Aided Design (ICCAD), 2023. [[paper]](https://ieeexplore.ieee.org/abstract/document/10323951)

## Update!
Thanks for your interest in our RTL-stage PPA modeling work. We have improved this work to achieve more fine-grained register slack evaluation and more accurate WNS and TNS prediction at the RTL stage, with much easier pre-processing for RTL designs. For more details, please refer to [RTL-Timer (DAC'24)](https://github.com/hkust-zhiyao/RTL-Timer).

## Abstract

In modern VLSI design flow, the register-transfer level (RTL) stage is a critical point, where designers define precise design behavior with hardware description languages (HDLs) like Verilog. Since the RTL design is in the format of HDL code, the standard way to evaluate its quality requires time-consuming subsequent synthesis steps with EDA tools. This time-consuming process significantly impedes design optimization at the early RTL stage. Despite the emergence of some recent ML-based solutions, they fail to maintain high accuracy for any given RTL design. In this work, we propose an innovative pre-synthesis PPA estimation framework named MasterRTL. It first converts the HDL code to a new bit-level design representation named the simple operator graph (SOG). By only adopting single-bit simple operators, this SOG proves to be a general representation that unifies different design types and styles. The SOG is also more similar to the target gate-level netlist, reducing the gap between RTL representation and netlist. In addition to the new SOG representation, MasterRTL proposes new ML methods for the RTL-stage modeling of timing, power, and area separately. Compared with state-of-the-art solutions, the experiment on a comprehensive dataset with 90 different designs shows accuracy improvement by 0.33, 0.22, and 0.15 in correlation for total negative slack (TNS), worst negative slack (WNS), and power, respectively.

## Collected Benchmarks
All the RTL designs used in our work are collected from open-source projects, their links are attached below:

1. IWLS05 (ISCAS89+ITC99)
   ```
   https://iwls.org/iwls2005/benchmarks.html
   ```
2. OpenCores
   ```
   https://opencores.org/
   ```
2. VexRiscv (generated with different configs)
   ```
   https://github.com/SpinalHDL/VexRiscv
   ```
3. NVDLA
   ```
   https://github.com/nvdla/hw
   ```
4. Chipyard (generated with different configs)
   ```
   https://github.com/ucb-bar/chipyard
   ```
5. RISC-V cores
   ```
   https://github.com/YosysHQ/picorv32
   https://github.com/onchipuis/mriscvcore
   ```

## Code Structure

### 1. Process RTL files (foler: "ys_script")

```
   $ cd ys_script
   $ yosys run_TinyRocket_sog.ys
   $ python3 clean_vlg.py
   
   ## Input: example/verilog/TinyRocket (original Verilog files)
   ## Output: example/verilog/TinyRocket_sog.v (SOG Verilog)
```

* Convert the original RTL files into standard Verilog format
  * Exmploy [Yosys](https://github.com/YosysHQ/yosys) for flattening (i.e., word-level AST) or bit-blasting (i.e., bit-level SOG).
  * Clean the generated Verilog file ("clean_vlg.py").

### 2. Verilog to Graph (folder: "vlg2ir")

```
   $ cd vlg2ir
   $ python3 auto_run.py
   
   ## Input: example/verilog/TinyRocket_sog.v
   ## Output: example/sog/*.pkl
```

* Parse the Verilog code and convert it to graph representation
  * Build upon the open-source Verilog parser [Pyverilog](https://github.com/PyHDI/Pyverilog), converting the Verilog code into the abstract syntax tree (AST).
  * Construct graph representation by traversing the AST from the Verilog parser (Details in "DG.py", "logicGraph.py", and "AST_analyzer.py").
  * Analyze the graph for feature extraction ("graph_stat.py").

### 3. Circuit Preprocessing (folder: "preproc")

```
   ## Timing
   $ cd preproc/timing
   $ python3 delay_propagation.py
   
   ## Power
   $ cd preproc/power
   $ python3 tr_propagate.py
```

* Preprocess the circuit graph data, including:
  * Process the graph into a directed acyclic graph (DAG) by removing the loop of the registers ("timing/delay_propagation.py").
  * Conduct delay propagation for timing estimation ("timing/delay_propagate.py").
  * Perform toggle rate propagation for power prediction ("power/tr_propagate.py"). Note that the toggle rate propagation is performed at the module level and the original Verilog is partitioned using Yosys. The initial toggle rate is obtained from Design Compiler at the beginning of the synthesis process, the variable names from Yosys and DC are slightly different and need alignment.

### 4. Feature Extraction (folder: "feature_extract")

```
   ## Timing
   $ cd feature_extract/timing
   $ python3 feature_extra_graph_STA.py
	  ## Please note that this feature extraction step needs the trained path-level model ('rfr' in the code) to infer the path delay. You may train the path model first referring to the method in the paper. 
   $ python3 pred_slack_calibration.py
   
   ## Power
   $ cd feature_extract/power
   $ python3 feature_extra_module_pwr.py
    ## Please note that this feature extraction step needs the toggle rate information obtained from the EDA tool (e.g., Design Compiler) at the beginning of the logic synthesis process. 
   $ python3 feature_extra_graph_pwr.py
   
   ## Area:
   $ cd feature_extract/area
   $ python3 feature_extra_graph_stat.py
```

* Perform feature extractions for timing, power, and area, the example of extracted features are saved in "./example/feature"
  * Timing: analytical node delay feature, propagated path delay feature, graph-level feature, etc.
  * Power: propagated toggle rate feature, module-level power feature, graph-level feature, etc.
  * Area: analytical area feature, graph-level feature, etc.

### 5. ML model Training (folder: "ML_model")

```
   ## Timing
   $ cd ML_model/timing/model
   $ python3 xgbooster_regression_kf_tns.py
   $ python3 xgbooster_regression_kf_wns.py
   
   ## Power
   $ cd ML_model/power/model
   $ python3 mix_regression_kf.py
   
   ## Area:
   $ cd ML_model/area/model
   $ python3 mix_regression_kf.py
```

### 6. ML model inference (folder: "ML_model/infer")

```
   ## Timing (WNS)
   $ cd ML_model/infer
   $ python3 infer_wns.py

   ## Timing (TNS)
   $ cd ML_model/infer
   $ python3 infer_tns.py

   ## Area
   $ cd ML_model/infer
   $ python3 infer_area.py

```

## Citation
If MasterRTL could help your project, please cite our work:

```
@inproceedings{fang2023masterrtl,
  title={MasterRTL: A Pre-Synthesis PPA Estimation Framework for Any RTL Design},
  author={Fang, Wenji and Lu, Yao and Liu, Shang and Zhang, Qijun and Xu, Ceyu and Wills, Lisa Wu and Zhang, Hongce and Xie, Zhiyao},
  booktitle={Proceedings of 2023 IEEE/ACM International Conference on Computer-Aided Design (ICCAD)},
  pages={1--9},
  year={2023},
  organization={IEEE}
}
```

* Customize different machine learning models for timing, power, and area, respectively
  * Timing: path-level model training and inference, and design-level calibration model
  * Power: module-level power model and design-level calibration model
  * Area: design-level area prediction model
