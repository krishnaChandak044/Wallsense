# Data rights, evidence, and claim language

## Permission state

The user reports that the hackathon mentor approved use of **both** Wallhack1.8k and CSI-Bench for this event. Separately, Wallhack1.8k author Julian Strohmayer emailed permission to use that dataset in the hackathon on October 26. Treat those as approval for hackathon use. Store the original correspondence privately. Permission to use data in a project does **not by itself** establish permission to redistribute raw files publicly or license trained weights commercially; check source terms before publication. Public code should link to the official dataset sources and cite creators.

Sources: [Wallhack1.8k on Zenodo](https://zenodo.org/records/13950918), [CSI-Bench official repository](https://github.com/guozhen-jenn-zhu/CSI-Bench-Real-WiFi-Sensing-Benchmark), [CSI-Bench data listing](https://www.kaggle.com/datasets/guozhenjennzhu/csi-bench). Pin versions/checksums in the implementation manifest. Source pages and terms may change, so inspect them at download time.

## Task and claim matrix

| Source | What to evaluate | Allowed result wording after held-out verification | Unavailable from that recording |
| --- | --- | --- | --- |
| Wallhack1.8k | No-presence vs walking vs walking plus arm movement; LOS/NLOS by capture setup | “Motion/activity classification on held-out Wallhack recordings, including documented NLOS cases.” Include counts, error, and abstention. | Fall, heart rate, numerical respiration, identity, exact location, still-person absence. |
| CSI-Bench FallDetection | Fall-related labels under its documented capture schema | “Fall classification on held-out CSI-Bench recordings.” Add NLOS only if the fall test actually contains documented NLOS captures. | Wallhack-style through-wall motion claims unless separately evaluated. |
| CSI-Bench BreathingDetection, if validated | Its actual label classes | “Breathing-related classification” with exact class meaning and held-out result. | Breaths/minute or heart rate unless paired numeric reference exists. |

## Critical separation rule

Dataset A showing through-wall motion and Dataset B showing a fall must **never** be narrated as the product detecting a fall through a wall in one scene. Every event/report states source, model, task, capture condition, and evaluation scope. Unsupported capabilities show `not_measured`, not zero, normal, or negative.

## Reporting template

For every on-screen metric include dataset/version, source URL, split unit, train/validation/test group and sample counts, task labels, capture condition, model hash, threshold-selection method, numerator/denominator, and run command. Failure cases and abstention coverage are part of the result. If cross-domain transfer is weak, state it plainly.

## Privacy and product boundaries

Raw CSI remains local by default. The Meta agent receives bounded derived event evidence only on an explicit investigation request. Avoid medical advice or emergency-response language; this is a research demonstration. The console says “recorded CSI replay” throughout. No hardware was used to create live capture in this build.
