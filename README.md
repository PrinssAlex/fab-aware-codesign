
# Manufacturing-Aware Hardware–Control Co-Design for Adaptive Robotic Manipulation
 

## Overview
This project presents a manufacturing-aware, differentiable co-design workflow that integrates **morphology**, **physics/control objectives**, and **feasibility constraints** into a single gradient-based optimization pipeline. A common failure mode in robotic manipulation development is the sequential workflow (optimize in simulation → fabricate → discover manufacturability violations), which often leads to repeated iteration due to overhang collapse, insufficient wall thickness, or excessive support requirements. The work addresses this bottleneck by incorporating feasibility into the optimization objective rather than validating it post hoc. 

The central technical approach replaces discontinuous, hard feasibility checks with **smooth differentiable surrogates** so that infeasible designs still produce meaningful gradients that guide optimization toward feasible regions. The reported experiments validate the principle in (i) a minimal differentiable constraint setting and (ii) a contact-aware identification setting used as a proxy for feasibility/physics consistency. 

## Problem statement
Automated robot hardware optimization under manufacturing constraints is challenging because many fabrication constraints are **discrete and geometrically discontinuous** (overhang feasibility can change abruptly with small geometry changes). Such discontinuities violate the smoothness assumptions required by gradient-based methods and implicit differentiation frameworks. 

The addressed problem is:
- Enable gradient-based optimization of morphology (and, by extension, hardware–control co-optimization) under additive manufacturing feasibility constraints (overhang limits, minimum wall thickness, build-plate/build-volume boundaries) while retaining the efficiency advantages of differentiable simulation. 

## Hypothesis
Discrete manufacturing constraints can be approximated using smooth, differentiable surrogates (softplus/log-sum-exp barrier functions). These surrogates are differentiable everywhere, yield informative gradients in violated regions, and can be integrated into differentiable simulation frameworks to make feasibility restoration accessible to first-order optimization. 

## Method
The workflow is organized around a single design principle:

> **Feasibility restoration must be gradient-accessible.**  
> If the penalty term is gradient-silent where the constraint is violated, optimization can stall outside the feasible set. 

### Differentiable constraint validation (hard vs smooth)
A minimal differentiable pipeline is used to establish:
- Baseline gradient correctness by comparing automatic differentiation to finite differences for a task loss. 
- Failure of a hard-indicator feasibility penalty due to lack of an informative gradient signal in the violated region. 
- Success of a smooth surrogate (softplus-based) that provides nonzero gradients when constraints are violated and converges to feasibility. 

#### Smooth surrogate form 
Let $z(E) = \theta(E) - \theta_{\max}$. A smooth approximation of the violation is:  
- $\tilde{v}(E) = \frac{1}{\beta}\log\left(1+\exp(\beta z(E))\right)$

A smooth constrained objective is:  
- $L_{\text{smooth}}(E) = L_{\text{task}}(E) + \lambda\,\tilde{v}(E)^2$

### Contact-aware identification as a feasibility/physics proxy
A simplified beam identification setup is used to demonstrate the same principle under a **contact-active regime**, where feasibility is interpreted as **physical consistency** (preventing interpenetration using a smooth penalty-style contact response rather than a hard feasibility switch). 

#### Parameters
- `s`: discrete support index (support-location hypothesis)
- `E`: Young’s modulus
- `h`: support height parameter
- `kc`: contact stiffness parameter 

#### Optimization task (high level)
Given a synthetic target deformation profile, candidate discrete supports `s` are scanned and continuous parameters `(E, h, kc)` are identified by minimizing data misfit under each support hypothesis. 

## Results 

### Identification (main synthetic target)
**Truth used to generate the target**
- `s_true = 4`
- `E_true = 60.0`
- `h_true = 0.03`
- `kc_true = 30000.0` 

**Identified best-fit**
- `s_hat = 4`
- `E_hat = 55.0`
- `h_hat = 0.032083`
- `kc_hat = 48000.0`
- `mse = 3e-6` 

### Ablation (contact-aware vs no-contact)
| Model | MSE | MAE | maxAE | MSE ratio vs contact | MAE ratio | maxAE ratio |
|---|---:|---:|---:|---:|---:|---:|
| Contact-aware (identified params) | 0.000089 | 0.007914 | 0.014877 | 1.000000 | 1.000000 | 1.000000 |
| No-contact (same s,E as identified) | 0.005816 | 0.067649 | 0.106182 | 65.147145 | 8.547752 | 7.137362 |
| No-contact (best E fit) | 0.000004 | 0.001551 | 0.005042 | 0.050290 | 0.195953 | 0.338926 | 

**Interpretation**
- Removing contact while holding `(s, E)` fixed produces a large error increase, indicating that contact handling is essential for consistency in contact-active regimes. 
- A no-contact model can still achieve low MSE by re-tuning `E`, demonstrating a cautionary failure mode: **low loss does not necessarily imply physical correctness**, because parameters can drift to compensate for missing mechanisms. 

### Sensitivity / identifiability (3 synthetic cases)
**Summary**
- `s` accuracy: `0.00 (0/3)`
- mean MSE: `3.492e-06`
- mean `|E_err|`: `24.2`
- mean `|h_err|`: `0.004`
- mean `|kc_err|`: `1.93e+04` 

**Interpretation**
Multiple combinations of `(s, E, h, kc)` can produce near-indistinguishable outputs under the available observation signal, implying weak identifiability of the discrete structural hypothesis `s` in this setup. 

### Figures 
- Target vs identified fit (contact-aware):  
  `fab-aware-codesign/outputs/runs/optB_20260208_184127/chapter4_target_vs_best.png`
- Identifiability scan (best coarse loss vs s):  
  `/content/fab-aware-codesign/outputs/runs/optB_20260208_184127/chapter4_identifiability_scan.png`  

### Saved CSVs (paths from the run)
- `fab-aware-codesign/outputs/runs/optB_20260208_184127/chapter4_table_identification.csv`
- `fab-aware-codesign/outputs/runs/optB_20260208_184127/chapter4_table_ablation.csv`
- `fab-aware-codesign/outputs/runs/optB_20260208_184127/chapter4_table_sensitivity.csv` 

## How to run 
The execution interface depends on the repository’s actual script names and configuration layout. A typical workflow is:

### Install
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run experiments
```bash
python scripts/run_experiments.py --config configs/default.yaml
```

### Export tables/figures
```bash
python scripts/export_results.py --run_dir outputs/runs/<run_id>
```

## Evaluation
Reported metrics:
- MSE (mean squared error)
- MAE (mean absolute error)
- maxAE (maximum absolute error)

Ablation ratios are reported relative to the contact-aware baseline. 

## Key takeaways
- Smooth, differentiable constraint surrogates enable feasibility restoration; hard indicator penalties can stall in violated regions due to gradient silence. 
- Contact-aware modeling is required for consistency in contact-active regimes; removing it can cause large mismatch or misleading fits via parameter drift. 
- Discrete hypotheses (support index `s`) may be weakly identifiable without stronger observation signals, priors, or additional constraints. 

## Limitations
- The demonstrated constraints/contact are simplified proxies; extending to full additive manufacturing constraints introduces additional discontinuities and uncertainties that require careful surrogate design.
- Identifiability issues were observed for discrete structure in sensitivity tests. 

## Future work
- Extend differentiable surrogates to richer additive manufacturing phenomena (supports, anisotropy, slicing constraints). 
- Multi-objective co-optimization: explicitly trade off task performance vs manufacturability. 
- Hardware validation on a real modular mechanism/gripper. 

## References
- Le Lidec et al., *Highly-Efficient Differentiable Simulation for Robotics*, arXiv:2409.07107 (2025). 
- Menager et al., *Differentiable Simulation of Soft Robots with Frictional Contacts*, arXiv:2501.18956 (2025). 
- Colle et al., *Co-Design Methodology for Modular Robotic Systems: The Robobrico Case Study* (2025). 
