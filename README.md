<img width="100" alt="portfolio_view" align="right" src="http://safeai.ethz.ch/img/sri-logo.svg">

# Private Attribute Inference from Images with Vision-Language Models

This is the accompanying code repository to the paper "Private Attribute Inference from Images with Vision-Language Models" published at NeurIPS 2024. For any questions, please feel free to contact the authors.

# Folder Structure

At the top level we have:

```
.
├── backend
├── Experimentation
├── frontend
└── README.md
```

## Labelling

In order to run the labelling platform, follow the README in [./backend](./backend/) and in [./frontend](./frontend/). We use a fastapi backend and a nextjs frontend. Both of them should be running and the labeller should visit: [http://localhost:4000](http://localhost:4000) to start labelling.

1. First go to [./backend](./backend/) and follow the [README](./backend/README.md) to install the environment and start the server.
2. Go to [./frontend](./frontend/) and follow the [README](./frontend/README.md) to install the environment and start the frontend server.
3. Then go to [http://localhost:4000](http://localhost:4000) and compile a dataset through labelling.

Once you have the dataset, follow instruction in [Experimetation/dataset/README](./Experimetation/dataset/README.md) to get make the dataset ready for experiments.

## Experiments

1. You can simply put the images and the dataset into the [./Experimentation/dataset](./Experimentation/dataset) folder.
2. Then you can set up your environements. There are different environments for different models.
3. Once you have the environments, you can start running the models.
4. Running models will store intermediate data which will be used to run [comparison](./Experimentation/src/utils/compare.py) scripts.
5. Then to get the performance, you can run the [performance](./Experimentation/performance.py) scripts.

More details are to be found in the corresponding [README.md](./Experimentation/README.md)

------
**Authors**:<br>
Batuhan Tömekçe, tbatuhan@student.ethz.ch<br>
Mark Vero, mark.vero@inf.ethz.ch<br>
Robin Staab, robin.staab@inf.ethz.ch<br>
Martin Vechev, martin.vechev@inf.ethz.ch

**License**:<br>
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. Note that this applies only to our code in this repository and not to any dependencies nor the data for which their respective licenses apply.


**Citation**:<br>
```bibtex
@inproceedings{tomekce2024private,
  title={Private Attribute Inference from Images with Vision-Language Models},
  author={Tömekçe, Batuhan and Vero, Mark and Staab, Robin and Vechev, Martin},
  booktitle={Advances in Neural Information Processing Systems},
  year={2024}
}
```
