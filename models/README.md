# Models

This directory is reserved for model documentation and approved lightweight model artifacts.

By default, trained model files are ignored by Git because they may be:

- Large.
- Derived from restricted participant data.
- Difficult to reproduce without the private dataset.
- Inappropriate for public distribution without approval.

## Do not commit by default

Do not commit:

- Full trained models derived from restricted data.
- Private `.joblib`, `.pkl`, `.pickle`, `.sav`, `.onnx`, `.pt`, or `.pth` files.
- Calibration objects derived from private datasets.
- Feature selectors fitted on restricted participant data.
- Normalization statistics fitted on restricted participant data.

## Allowed content

Allowed content may include:

- Documentation about model architecture.
- Small synthetic demo models.
- Model cards.
- Approved public artifacts.
- Instructions to reproduce models locally.

## Future organization

A future private or approved model structure may look like:

```text
models/
├── l1/
│   ├── README.md
│   └── model_card.md
├── l2/
│   ├── README.md
│   └── model_card.md
└── demo/
    └── synthetic_model.joblib
```

Only approved demo models should be committed publicly.
