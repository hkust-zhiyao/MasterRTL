# MasterRTL: A Pre-Synthesis PPA Estimation Framework for Any RTL Design

Code repository for the sumbitted paper in ICCAD'23: MasterRTL: A Pre-Synthesis PPA Estimation Framework for Any RTL Design

## Abstract

In modern VLSI design flow, the register-transfer level (RTL) stage is a critical point, where designers define precise design behavior with hardware description languages (HDLs) like Verilog. Since the RTL design is in the format of HDL code, the standard way to evaluate its quality requires time-consuming subsequent synthesis steps with EDA tools. This time-consuming process significantly impedes design optimization at the early RTL stage. Despite the emergence of some recent ML-based solutions, they fail to maintain high accuracy for any given RTL design. In this work, we propose an innovative pre-synthesis PPA estimation framework named MasterRTL. It first converts the HDL code to a new bit-level design representation named the simple operator graph (SOG). By only adopting single-bit simple operators, this SOG proves to be a general representation that unifies different design types and styles. The SOG is also more similar to the target gate-level netlist, reducing the gap between RTL representation and netlist. In addition to the new SOG representation, MasterRTL proposes new ML methods for the RTL-stage modeling of timing, power, and area separately. Compared with state-of-the-art solutions, the experiment on a comprehensive dataset with 90 different designs shows accuracy improvement by 0.33, 0.22, and 0.15 in correlation for total negative slack (TNS), worst negative slack (WNS), and power, respectively.

## Repo Structure

1. Circuit processing

   * Preprocess the circuit data, including
     * Converte the RTL code into graph representation
     * Process the graph into directed acyclic graph (DAG)
     * Prepare for the toggle rate propagation for power prediction and delay propagation for timing estimation
2. Feature extraction

   * Perform different feature extraction techniques for timing, power, area, respectively
     * Timing: analytical node delay feature, propagated path delay feature, and graph-level feature, etc.
     * Power: propagated toggle rate feature, module-level power feature, and graph-level feature, etc.
     * Area: analytical area feature, graph-level feature, etc.
3. ML models

   * Customize different machine learning models for timing, power, area, respectively
     * Timing: path-level model training and inference, and design-level calibration model
     * Power: module-level power model and design-level calibration model
     * Area: design-level area prediction model
