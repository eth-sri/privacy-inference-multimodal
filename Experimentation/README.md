# VLP Privacy Experiments

## Dataset

Prepare the dataset following [dataset/README.md](./dataset/README.md).

## Models

### Closed source models

To run the experiments with closed source models, you need to have an openai api key and a google ai studio api key.
Fill in the keys in [src/keys.py](./src/keys.py) file:

```python
OPENAI_API_KEY = ""
OPENAI_ORG_ID = ""
GOOGLE_API_KEY = ""
```

### Open source models

To run the experiments with open source models (Idefics, CogAgent, and LLaVa 1.5) you need to set the environment. Create conda environment or a python virtual environment then run:

```bash
conda create -n vlm_os python=3.10.12
conda activate vlm
pip install -r requirements_os.py
```

#### LLaVa-NeXT

Running LLaVa-NeXT requires a little bit more effort in setting up the environment. Please follow [LLaVa](https://github.com/haotian-liu/LLaVA/tree/main?tab=readme-ov-file#install) instructions. Once you are complete also change the `eval` function in the LLaVa repository inside [`run_llava.py`](https://github.com/haotian-liu/LLaVA/blob/5d8f1760c08b7dfba3ae97b71cbd4c6f17d12dbd/llava/eval/run_llava.py#L50) to accept new arguments.

Change

```python
def eval_model(args):
```

to

```python
def eval_model(args, model_name, tokenizer, model, image_processor, context_len):
```

delete

```python
model_name = get_model_name_from_path(args.model_path)
tokenizer, model, image_processor, context_len = load_pretrained_model(
    args.model_path, args.model_base, model_name
)
```

and add a return statement

```python
print(outputs)
return outputs
```

For ease of implementation you can replace the `run_llava.py` function in the [`run_llava.py`](https://github.com/haotian-liu/LLaVA/blob/5d8f1760c08b7dfba3ae97b71cbd4c6f17d12dbd/llava/eval/run_llava.py) with the one we have in `LLaVa-NeXT/run_llava.py`

For ease of installation we also put the instructions in [README_llavanext.md](./README_llavanext.md)

#### InternVL

Please follow the instructions in the [InternVL](https://github.com/OpenGVLab/InternVL/blob/main/INSTALLATION.md) git repository. For ease of installation we also put the instructions in [README_internvl.md](./README_internvl.md)

## Running the models

To run any model first activate the environment it will run and then call `run_models.py` script with the corresponding config of the requested model e.g.:

```bash
python run_models.py --config src/configs/run_openai.yaml
```

### Closed source models

To run closed source models, make a new environment:

```bash
conda create -n vlm python=3.10.12
conda activate vlm
pip install -r requirements.txt
```

Now you will have a folder in [model_responses/](./model_responses/) inside which you can find one model response in a `.json` file per `image_id` and `attribute`.

### Open Source models

Now you will have a `.json` file starting with the word `results`. Since the open source models can have difficulty int outputting a structured output consistently we postprocess their outputs to be structured via GPT-4.
To get the results in the same format as closed source models also run e.g.

```bash
python structure_correction.py --config src/configs/run_cogagent.yaml
```

Now you will have a folder in [model_responses/](./model_responses/) inside which you can find one model response in a `.json` file per `image_id` and `attribute`.

### Measuring Performance

To get the performance of the models we need to now parse and compare the outputs of the models and the ground truth labels.

Run e.g.

```bash
python -m src.utils.compare --config src/configs/run_cogagent.yaml
```

This will output a `.json` performance file per image_id and attribute in the [performances/](./performances/) folder.

Since we use GPT-4 evaluation for free text attributes: `location, placeOfImage, occupation`, we need to manually check whether the evaluations of GPT-4 were correct. To do the check and update the performance file for the desired attributes and category, run e.g.:

```bash
python human_labeling.py --config src/configs/run_cogagent.yaml --true_pred 2 --attribute location
```

Here `--true_pred 2` means we only look for the ground truth and prediction pairs that are labelled `less precise` by the GPT-4 evaluation.

To check `precise` use `--true_pred 1` and to check `wrong predictions` use `true_pred 0`

This will update the `.json` performance file in place.

To get the performance summary of the any model run e.g.:

```bash
python performance.py --config src/configs/run_cogagent.yaml
```

You can adjust the [performance.py](./performance.py) file to check `precise` or `less precise` accuracy.

Once you have all the performance files, you can adjust the [plots.py](./plots.py) file to get the comparison plots and tables.

To run the zoom experiments, you can run e.g.

```bash
python zoom.py --attribute location
```

## Results

Once you ran all the models and have all the data in place, you can run:

```bash
python plots.py
```

to get a comparison plot.
