
# RFC references

The metadata exposed by the RFC Editor doesn't include references. This repo captures *only* those references that are internal to the RFC Series, in `refs.json`.

Note that prior to ~RFC8650, the canonical format for RFCs was a text file, and therefore we need to parse it to recover those references. Due to *ahem* considerable variances in style across the Series -- especially in the early years -- this is difficult, and imprecise. As such, the code to extract references from text is... ugly.

All of this is a long way of saying:

1. Use at your own risk, and
2. Pulls that improve parsing greatly appreciated.

## Using the references

Just download `refs.json` [from the repo](https://raw.githubusercontent.com/mnot/rfc-refs/main/refs.json). There's no sense in running this locally (and soon I'll have GitHub Actions updating it automatically).