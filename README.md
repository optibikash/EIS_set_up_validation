[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
# EIS_set_up_validation

This repository provides the experimental datasets supporting the paper submitted to **RSC Batteries** on a **galvanostatic EIS (electrochemical impedance spectroscopy) measurement setup** designed for **commercial lithium-ion cells in the mΩ regime**, including **validation against a commercial BioLogic EC301 potentiostat/galvanostat** and **temperature-dependent EIS measurements**.

---

## What is in this repository?

### 1) Validation datasets (`*_validate.xlsx`)
Files with `_validate` contain datasets used to **validate the proposed EIS setup** against the **BioLogic EC301** reference instrument.

- `Samsung_validate.xlsx` — Validation of the proposed EIS setup vs EC301 (Samsung cell)
- `LGM50_validate.xlsx` — Validation of the proposed EIS setup vs EC301 (LG M50 cell)

These files are intended for direct comparison of impedance spectra (e.g., Nyquist overlay, pointwise error, RMSE/MAE across frequency).

---

### 2) Temperature-sweep datasets (proposed setup)
The remaining files contain **EIS measured at different temperatures** using the proposed setup.

- `Samsung.xlsx` — Temperature-dependent EIS measurements for the Samsung cell
- `Panasonic.xlsx` — Temperature-dependent EIS measurements for the Panasonic cell

These datasets capture how impedance evolves with temperature (e.g., increase in ohmic intercept and polarization features at sub-zero temperatures), while demonstrating stable measurement capability across the defined sweep.

---

## Cells covered (as described in the paper)

The datasets correspond to commercial cylindrical lithium-ion cells:

- **Samsung (Cell A)**: NCA, *INR 18650-35E*, 18650 format, 3.63 V nominal, 3500 mAh  
- **LG (Cell B)**: NMC, *INR 21700 M50*, 21700 format, 3.63 V nominal, 5000 mAh  
- **Panasonic (Cell C)**: NCA, *NCR18650B*, 18650 format, 3.60 V nominal, 3400 mAh  

---

## Measurement overview (from the manuscript)

- **EIS method**: Galvanostatic EIS (current excitation, voltage response)
- **Frequency range**: 20 mHz to 10 kHz
- **Temperature range demonstrated**: −10 °C to 50 °C
- **Validation reference**: BioLogic EC301 potentiostat/galvanostat

---

## How to use the data

1. Download any `.xlsx` file.
2. Use the frequency column and the real/imaginary impedance columns to plot:
   - **Nyquist**: Re(Z) vs −Im(Z)
   - **Bode**: |Z| and phase vs frequency
3. For `*_validate.xlsx`, compare spectra from the proposed setup vs EC301.

> Note: The exact column names and sheet names may differ slightly between files. Please inspect the first row/header of each sheet for the data fields.

---

## Recommended citation

If you use these datasets, please cite the associated manuscript:

> [Authors], “A Sub-mΩ Galvanostatic Electrochemical Impedance Spectroscope for Wide Frequency Battery Characterisation,” submitted to *RSC Batteries*.  
> (Add DOI as well once available.)
> We will try to keep this file updated. 

---

## License

CC BY 4.0 for data sharing with attribution.

---

## Contact

For questions, issues, or requests (e.g., data schema clarification), please open an issue in this GitHub repository.
