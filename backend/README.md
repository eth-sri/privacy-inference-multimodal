This is a fastapi backend.

# Dataset

If you aim to use the RedCaps dataset, you need to install the [RedCaps dataset](https://redcaps.xyz/download) and extract it into [../../Datasets/RedCaps/redcaps_v1.0_annotations/annotations](../../Datasets/RedCaps/redcaps_v1.0_annotations/annotations)

To run the backend server, you first need to set up an environment:

```bash
conda create -n labellingenv python=3.10.12
conda activate labellingenv
pip install -r requirements.txt
```

To run the backend server:

```bash
python -m uvicorn main:app --reload
```

All the files including the obtained dataset can be found in [./data](./data) folder once labelling finishes.
The saved dataset can be found in [./data/labels/dataset.jsonl](./data/labels/dataset.jsonl)
