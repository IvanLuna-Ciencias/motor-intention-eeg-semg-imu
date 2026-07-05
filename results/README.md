# Results

This directory is reserved for evaluation outputs, reports, figures, and result summaries.

By default, generated results are ignored by Git because they may be:

- Large.
- Temporary.
- Derived from restricted participant data.
- Difficult to interpret without the complete experimental context.
- Not intended for public distribution before curation.

## Do not commit by default

Do not commit:

- Full experiment outputs.
- Raw evaluation logs.
- Large figures.
- Temporary plots.
- Complete per-participant result tables derived from private data.
- Intermediate files generated during training or evaluation.
- Files containing local paths.

## Allowed content

Allowed content may include:

- Curated summary tables.
- Synthetic demo outputs.
- Publicly approved figures.
- Reproducible example results based only on synthetic/sample data.
- Documentation explaining how results are generated.

## Future organization

A future curated result structure may look like:

```text
results/
├── demo/
│   └── README.md
├── figures/
│   └── README.md
└── summaries/
    └── README.md
```

Only curated and approved files should be committed publicly.
