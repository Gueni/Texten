# OBC Matrix-DAB: single-stage three-phase on-board charger

Reference model, ideal PLECS components only: [OBC_MatrixDAB.plecs](OBC_MatrixDAB.plecs).
It is generated from [build_obc.py](build_obc.py), with parameters from [obc_param.py](obc_param.py).
Use it as the template to rebuild the OBC from CustomLibraries blocks in PLECS 5.

```
grid 3~ ─ LC filter ─ 3x1 matrix converter ─ Lr ─ transformer Np:Ns ─ full bridge ─ Co ─ battery / load
                      └────────────────── dual active bridge (DAB) ──────────────────┘
```

## 1. Why this architecture (compared with PFC + LLC)

The old OBC has two stages:

```
grid ─ PFC (AC → 400 V DC link) ─ big DC-link capacitor ─ LLC (DC → isolated DC) ─ battery
```

- **PFC:** shapes the grid current and regulates the DC link.
- **DC-link capacitor:** the large electrolytic buffers the power pulsation at twice the grid frequency.
- **LLC:** isolates and adapts the voltage at fixed gain around resonance.

The matrix DAB does all of this in **one stage**:

| | PFC + LLC | Matrix DAB |
|---|---|---|
| Stages | 2 (AC/DC + DC/DC) | 1 (AC/AC/DC) |
| DC link | yes, large electrolytic | **none** |
| Grid-current shaping done by | PFC current loop | **duty split dm** of the matrix converter |
| Power / output current set by | LLC frequency | **phase shift φ** between the bridges |
| Primary switches | PFC + 2 × LLC bridge | 6 bidirectional switches = 12 MOSFETs |

It works with **three-phase** input and no DC link because a balanced three-phase system delivers **constant** instantaneous power, p = va·ia + vb·ib + vc·ic = const. Nothing has to be buffered, so the converter can transfer the power directly from the grid to the transformer. Single-phase power pulsates at 100 Hz, which is why the single-phase PFC + LLC needs its bulk capacitor.

The price is the bidirectional switches (two common-source MOSFETs each, see 2.2), commutation between grid phases, and more complex modulation.

## 2. Power stage

### 2.1 Grid and input filter
- **Grid:** three AC sources, 230 V rms phase, 50 Hz.
- **Input filter (Lf ‖ Rd, star Cf):** the matrix converter draws **pulsed** currents, alternately from two phases within every switching period.
  - **Cf** supplies those pulses, so the converter sees a voltage-stiff input. This is the counterpart of the DC-link capacitor, but only 10 µF, because it only buffers one switching period, not 100 Hz.
  - **Lf** keeps the 100 kHz ripple out of the grid.
  - **Rd** damps the Lf–Cf resonance (5 kHz).

### 2.2 Matrix converter (3×1): replaces the PFC and the LLC primary bridge
- **Function:** two output nodes **g** and **h** (the transformer primary), and each grid phase can be connected to either node.
- **Bidirectional switches:** every switch must block voltage of **both** polarities, since the line-to-line voltages are AC. It must also conduct current in both directions, since the transformer current is AC.
  - A single MOSFET can't do that, because its body diode conducts in reverse.
  - So each switch is **two MOSFETs in common source**, gated together (Sga with Sag, and so on). 6 switches × 2 = 12 MOSFETs.
- **Rule:** g and h must always be on two **different** phases; same phase would short the transformer, and two phases on one node would short the grid. At any instant, therefore, exactly one switch is on at g and one at h.

### 2.3 DAB tank and secondary
- **Lr:** the DAB energy-transfer inductance, the leakage of the transformer plus an external inductor.
- **Transformer Np:Ns = 13:10:** gives isolation and matches the voltages.
- **Full bridge (Spj/Sjn, Spk/Skn):** square-wave voltage ±Vo on the secondary, rectified into Co. It is bidirectional, so the same hardware could also do V2G.

## 3. How it works: one switching period

### 3.1 Sector: which phase is the "main" phase (zero crossings)
- **Main phase k:** the phase with the largest |v|.
  - In a balanced system it is always the phase whose **sign differs from the other two**.
  - With unity power factor it carries the sum of the other two currents.
- **Sign comparators:** the three comparators `Vabc > 0` give Sa, Sb, Sc.
  - Each one **rises / falls exactly at a zero crossing** of its phase voltage.
  - That happens every 60°, so there are 6 sectors:

| Sa Sb Sc | main phase k | sign s | other phases m, n |
|---|---|---|---|
| 1 0 0 | a | + | b, c |
| 1 1 0 | c | − | a, b |
| 0 1 0 | b | + | c, a |
| 0 1 1 | a | − | b, c |
| 0 0 1 | c | + | a, b |
| 1 0 1 | b | − | c, a |

### 3.2 Switching states and duty dm
- **Primary voltage:** v_gh is a square wave at fs.
  - **Positive half:** connect g to k (if s = +, otherwise h to k) and the other node to m, then to n.
  - **Negative half:** the same with g and h swapped.
- **Only two line-to-line voltages per half:**
  - first v_km for **dm·T/2**, then v_kn for **(1−dm)·T/2**
  - both have the same sign, so v_gh never reverses within a half period
- **Duty:** dm = |v_m| / |v_k|.
  - The transformer current flows through phase m for a fraction dm and through phase n for 1−dm. It always flows through k.
  - Averaged over a switching period, i_m : i_n : i_k = dm : (1−dm) : 1 = |v_m| : |v_n| : |v_k|.
  - So the grid currents are **proportional to the grid voltages**: sinusoidal, at unity power factor. This replaces the PFC current loop.
  - In the model, dm comes from the voltages, i.e. a unity-PF current reference. A current reference i* with a phase angle would give reactive power.
- **Resulting levels:** v_gh takes values between 1.5·V̂ and 1.73·V̂ (488–563 V here). In the simulation, Vp spans ±563 V.

### 3.3 Power transfer: DAB phase shift φ
- **Phase shift:** the secondary square wave (±Vo) lags the primary by φ (a fraction of the period, 0 … 0.5).
- **Power:** Lr sees the difference of the two square waves. Power flows from the leading to the lagging bridge:

  P ≈ V_p · (Np/Ns · Vo) · d·(1 − d) / (2·fs·Lr),  with d = 2φ

  With V_p ≈ 525 V, Np/Ns·Vo ≈ 538 V, φ = 0.1, fs = 100 kHz and Lr = 19 µH, this gives P ≈ 11.9 kW. The simulation gives 11.8 kW.

### 3.4 Timing from comparators (rise / fall = exact switching edges)
- **Carriers:** two sawtooth carriers from wrapping integrators, `c` (0→1 at fs) and `c2` (0→1 at 2·fs), both start at t = 0.

| signal | comparator | meaning |
|---|---|---|
| Sa, Sb, Sc | `Vabc > 0` | sector (rise/fall at the grid zero crossings) |
| P | `c < 0.5` | positive half of the primary period |
| M | `c2 < dm` | first sub-interval (phase m) of each half period |
| A | `c ≥ φ` AND `c < φ + 0.5` | secondary positive half (Spj, Skn on); B = NOT A (Sjn, Spk on) |

- **Exact edges:** PLECS detects each comparator crossing as a zero-crossing event, so every rising and falling edge lands exactly at the crossing, independent of the step size.
- **Sector & Duty (C-Script):** runs once per switching period at the carrier reset. It turns Sa/Sb/Sc into k, s and dm, so the sector and duty only change between periods.
- **Gate Logic (C-Script):** a pure truth table that turns (k, s, P, M) into the 12 matrix gates. It makes no timing decisions.

## 4. Results (open loop, φ = 0.1, 2 grid periods)

| | |
|---|---|
| Output | 414 V mean, 28.6 A, **11.8 kW**; with ideal switches, P_in = P_out |
| Grid current | 17.2 A rms per phase, balanced |
| Displacement | +6° (leading: the Cf reactive current) |
| THD | 13 %: 5th 10.7 %, 7th 7.0 %, 11th/13th ≈ 1.9 % |
| Vo ripple | ±11.5 V at 300 Hz |

The 6-pulse harmonics and the 300 Hz ripple have the same cause:
- φ is **constant**, but the effective primary voltage changes 1.5 → 1.73·V̂ within every 60° sector.
- So the transferred power pulsates by ±1.9 kW at 6 × 50 Hz.

The fix, and the next step for the real model, is to adjust φ every switching period:
- **Feed-forward:** P ∝ V_p,eff · d(1−d), so reduce φ where V_p,eff is high.
- **Closed loop:** add a current / voltage loop around φ.

The Matrix_DAB reference is open loop too ("operating conditions not realistic").

## 5. Simplifications (ideal model) and what the real model needs

- **Commutation:**
  - Here the two devices of a bidirectional switch are gated together and commutate instantly (like "Modulation 1" in the Matrix_DAB reference).
  - Real hardware needs **4-step commutation** (current- or voltage-direction based). It also needs dead time on the secondary.
  - The reference's "Modulation 2: SR and dead-time support" is that step.
- **Components:** MOSFETs and diodes are ideal (Ron = 0); the transformer has only Lm and no losses or capacitances.
- **Load:** a resistor, where the real OBC charges a battery.
- **Control:** none yet. φ is fixed (open loop) and there is no PLL; dm uses the measured filter-capacitor voltages directly.

## 6. Rebuilding it in PLECS 5 with CustomLibraries

Keep the subsystem split and the signal names; replace the ideal parts block by block:

| ideal subsystem / block | CustomLibraries candidate |
|---|---|
| Grid | `Power/EVSE` (three-phase configuration; Vgrid = phase rms, Fgrid in Hz) |
| Input Filter Lf / Cf | `Magnetics/Chokes/*`, `Power/Capacitor Bank` |
| MOSFET (MosfetWithDiode) | `Transistors/Switch` (configuration 1, `Transistor.Config` 2 = ideal channel) |
| Lr | `Magnetics/Chokes/DC Choke` |
| Transformer | `Magnetics/Transformers/Transformer` (Lkp/Lks can hold Lr) |
| Co / Load | `Power/Capacitor Bank`, `Power/Load` or `Power/HV Storage` |
| Carriers / secondary PWM | `PWM/Sawthooth Generator`, `PWM/Single PWM with Phase-Shift` (adds dead time) |

Notes from trying the library version:
- `Transistors/Switch` has unused terminals: Temp input, heat port, and the g/g1 ports. Keep wires off them, or PLECS refuses to simulate ("unconnected terminals overlapped by other elements").
- `BodyDiode.Custom` must be an empty list `[]`, because the mask code only handles that.

## 7. Files

| file | |
|---|---|
| [OBC_MatrixDAB.plecs](OBC_MatrixDAB.plecs) | the model (opens in PLECS 4.9 and 5) |
| [obc_param.py](obc_param.py) | parameters; written into the model's Initialization Commands |
| [build_obc.py](build_obc.py) | generates the model: `py build_obc.py` |
| [plecs_gen.py](plecs_gen.py) | small .plecs writer used by build_obc.py |
| [tests/run_obc.py](tests/run_obc.py) | builds, simulates over XML-RPC (PLECS running, port 1080), prints the results: `py tests/run_obc.py [tSim] [phi]` |
| [tests/test_builtins.py](tests/test_builtins.py) | checks the comparator / logic operator codes the model uses |
