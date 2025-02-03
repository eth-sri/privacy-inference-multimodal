Taken from [https://github.com/haotian-liu/LLaVA/blob/main/README.md#install](https://github.com/haotian-liu/LLaVA/blob/main/README.md#install)

## Install

If you are not using Linux, do _NOT_ proceed, see instructions for [macOS](https://github.com/haotian-liu/LLaVA/blob/main/docs/macOS.md) and [Windows](https://github.com/haotian-liu/LLaVA/blob/main/docs/Windows.md).

1. Clone this repository and navigate to LLaVA folder

```bash
git clone https://github.com/haotian-liu/LLaVA.git
cd LLaVA
```

2. Install Package

```Shell
conda create -n llava python=3.10 -y
conda activate llava
pip install --upgrade pip  # enable PEP 660 support
pip install -e .
```
