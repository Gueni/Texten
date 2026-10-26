# PyPLECS – Code Generation & RT Box

PyPLECS can do more than run offline PLECS simulations. With two switches in `Input_vars.json`, the same run can:

- **Generate real-time code** from a PLECS model with PLECS Coder (the `.elf` plus generated sources), with no GUI and no clicking *Build* in Coder Options.
- **Upload and run that code on a Plexim RT Box**, then stop it cleanly when finished.

When PLECS Coder also writes an `.a2l` file, PyPLECS merges it into an **INCA-compatible `.a2l`** in the background, so calibration can start right away.

All generated files are collected in the run's results folder under `RT_BOX_CODEGEN`, next to the usual run log.

---

## When to use what

| You want to… | `RT` | `codegen_only` | Hardware needed |
|---|---|---|---|
| Run a normal offline simulation (unchanged behaviour) | `false` | – | No |
| Only generate the code / `.elf` (and INCA `.a2l`) | `true` | `true` | No |
| Generate the code **and** upload and run it on the RT Box | `true` | `false` | Yes, an RT Box reachable over the network |

> **Note:** With `RT: false`, nothing changes compared with before. All RT Box code paths are switched off and the run is a normal PLECS simulation.

---

## The three settings

Add these keys at the top level of `Script/assets/Configuration/Input_vars.json`:

```json
"RT"             : true,
"codegen_only"   : true,
"codegen_target" : "Plant + Controller"
```

| Key | Type | Meaning |
|---|---|---|
| `RT` | bool | Turns the codegen/RT Box workflow on. |
| `codegen_only` | bool | `true` stops after code generation (no upload, no hardware). `false` also uploads to and runs on the RT Box. |
| `codegen_target` | string | Name of the **subsystem** that has *Enable code generation* ticked. Give only the subsystem name. PyPLECS adds the model name in front automatically (`<model>/<codegen_target>`). |

---

## Prerequisites (both cases)

- PLECS with **PLECS Coder** licensed and the **RPC interface enabled** (PLECS Preferences, default port `1080`; PyPLECS reads `url`/`port` from `assets/Dependencies.py`).
- The model is prepared for code generation (see the example pages):
  - *Enable code generation* is ticked on the subsystem named in `codegen_target`.
  - All Target I/O blocks sit at the **top level of that subsystem**.
  - In **Coder Options**, the **Base name** is set to the model file name (without `.plecs`). PyPLECS expects `<modelname>.elf` next to the model file.
- Python 3.10.8 with the usual PyPLECS environment.

---

## Pages in this section

1. **[How it works](./How-it-works)**: the full flow, the codegen part and the RT Box part, with diagrams.
2. **[Example – Codegen only](./Example-Codegen-only)**: generate the `.elf` and INCA `.a2l` without hardware.
3. **[Example – Codegen + RT Box](./Example-Codegen-and-RT-Box)**: generate, upload and run on the RT Box.

---

## Known limitations / to confirm

> **Warning:** PyPLECS currently uses **one RPC connection** (`url:port` from `Dependencies.py`) for both the PLECS calls (`plecs.codegen`) and the RT Box calls (`rtbox.load`, `rtbox.start`, …), with no `/RPC2` suffix. The RT Box scripting reference documents a separate RPC server on the RT Box itself, at `http://<rtbox-ip>:<port>/RPC2`. **This still needs to be confirmed on real hardware.** Codegen-only runs do not depend on it.

- `parallel` should be `false` (and a single iteration used) for codegen/RT runs. Code is generated once from one parameter set.
- With `RT: true`, PyPLECS does not save simulation data, plot scopes or build an HTML report, because no offline simulation runs.
