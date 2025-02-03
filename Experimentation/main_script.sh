#!/bin/bash

set -e

echo "GPT4V"
conda activate vlm
python run_models.py --config src/configs/run_openai.yaml
python -m src.utils.compare --config src/configs/run_openai.yaml
python performance.py --config src/configs/run_openai.yaml

echo "Gemini-Pro"
python run_models.py --config src/configs/run_gemini_pro.yaml
python -m src.utils.compare --config src/configs/run_gemini_pro.yaml
python performance.py --config src/configs/run_gemini_pro.yaml

echo "Cogagent"
conda activate vlm_os
python run_models.py --config src/configs/run_cogagent.yaml
python structure_correction.py --config src/configs/run_cogagent.yaml
python -m src.utils.compare --config src/configs/run_cogagent.yaml
python performance.py --config src/configs/run_cogagent.yaml

echo "LLaVa 1.5"
python run_models.py --config src/configs/run_llava1.5.yaml
python structure_correction.py --config src/configs/run_llava1.5.yaml
python -m src.utils.compare --config src/configs/run_llava1.5.yaml
python performance.py --config src/configs/run_llava1.5.yaml

echo "Idefics"
python run_models.py --config src/configs/run_idefics.yaml
python structure_correction.py --config src/configs/run_idefics.yaml
python -m src.utils.compare --config src/configs/run_idefics.yaml
python performance.py --config src/configs/run_idefics.yaml

echo "LLaVa-NeXT"
conda activate llava
python run_models.py --config src/configs/run_llava1.6.yaml
python structure_correction.py --config src/configs/run_llava1.6.yaml
python -m src.utils.compare --config src/configs/run_llava1.6.yaml
python performance.py --config src/configs/run_llava1.6.yaml

echo "InternVL"
conda activate internvl
python run_models.py --config src/configs/run_internvl.yaml
python structure_correction.py --config src/configs/run_internvl.yaml
python -m src.utils.compare --config src/configs/run_internvl.yaml
python performance.py --config src/configs/run_internvl.yaml

echo "plotting and tables"
python plots.py
