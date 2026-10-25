# LabSmith uProcess scripts

- `PBS_Ethanol_SPS01.usq`: original PBS/Ethanol dual-syringe sequencing example from our discussion. Verify physical syringe limits, connections and valve orientation before use; the 90 µL command is from the original script and is **not** a validated 80 µL syringe setting.
- `Pressure_Stability_Detector_PROTOTYPE.usq`: proposed pressure mean/CV stability detector with beep. **Not tested on hardware**; target pressures are illustrative, sampling interval and parser syntax require validation. It does not yet run concurrently with pump control.

Keep a dated, validated copy of each working program before changing it.
