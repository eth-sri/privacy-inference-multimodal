import pandas as pd
from performance import get_performance_summary, get_performance_summary_human
from src.configs.config import load_config

performances = [
    "image_performance_llava_1.5_13b_oss_f",
    "image_performance_cogagent_oss_f",
    "image_performance_idefics80b_oss_f",
    "image_performance_llava_1.6_34b_complex_f",
    "image_performance_internvl_complex_f",
    "image_performance_gpt4v_complex_",
    "image_performance_gemini_complex_",
]

configs = [
    "llava1.5",
    "cogagent",
    "idefics",
    "llava1.6",
    "internvl",
    "openai",
    "gemini_pro",
]

# performances = [
#     "gpt4v_complex_",
#     "gpt4v_mid_",
#     "gpt4v_simple_",
#     # "gpt4v_single",
#     # "gemini_single2",
# ]

# configs = [
#     "openai",
#     "openai",
#     "openai",
#     # "openai",
#     # "gemini_pro",
# ]

# performances = [
#     "image_performance_llava_1.5_13b_complex_",
#     "image_performance_cogagent_complex_",
#     "image_performance_idefics80b_complex_",
#     "image_performance_llava_1.5_13b_oss_",
#     "image_performance_cogagent_oss_",
#     "image_performance_idefics80b_oss_",
# ]

# configs = [
#     "llava1.5",
#     "cogagent",
#     "idefics",
#     "llava1.5",
#     "cogagent",
#     "idefics",
# ]


main_attributes = [
    "location",
    "placeOfImage",
    "sex",
    "age",
    "occupation",
    "income",
    "maritalStatus",
    "educationLevel",
]

main_attributes_order = [
    "sex",
    "placeOfImage",
    "age",
    "income",
    "location",
    "educationLevel",
    "occupation",
    "maritalStatus",
]

attribute_to_short = {
    "location": "LOC",
    "placeOfImage": "POI",
    "sex": "SEX",
    "age": "AGE",
    "occupation": "OCC",
    "income": "INC",
    "maritalStatus": "MAR",
    "educationLevel": "EDU",
}

model_to_text = {
    "human": "Human labelled",
    "gpt4v_single": "GPT4-V",
    "gpt4v": "GPT4-V",
    "gemini": "Gemini-Pro",
    "idefics80b_single": "Idefics 80B",
    "gemini_single2": "Gemini-Pro",
    "qwenvl": "Qwen-VL",
    "cogagent_single": "CogAgent-VQA",
    "llava13b_single": "LLaVa 1.5 13B",
    "fuyu": "Fuyu",
    "total_gt": "Human labelled",
    "openai": "GPT4-V",
    "gemini_pro": "Gemini Pro",
    "idefics": "Idefics 80B",
    "idefics80b": "Idefics 80B",
    "llava1.5": "LLaVa 1.5 13B",
    "llava_1.5_13b": "LLaVa 1.5 13B",
    "llava_1.6_34b": "LLaVa-NeXT 34B",
    "cogagent": "CogAgent-VQA",
    "internvl": "InternVL-Chat-V1.2-Plus",
}
model_to_prompt = {
    "gpt4v_simplest": "Naive Prompt",
    "gpt4v_single_mid": "Extended Prompt",
    "gpt4v_single": "Final Prompt",
    "gpt4v_single_zoom3": "Chain of Zoom",
}

model_to_prompt = {
    "gpt4v_simple_": "Naive Prompt",
    "gpt4v_mid_": "Extended Prompt",
    "gpt4v_complex_": "Final Prompt",
    "total_gt": "Human labelled",
}


def prompt_comparison_plot(sorted_df: pd.DataFrame):
    # data from https://allisonhorst.github.io/palmerpenguins/

    import matplotlib.pyplot as plt
    import numpy as np

    x = np.arange(len(sorted_df.columns))  # the label locations
    width = 0.25  # the width of the bars
    multiplier = 0

    fig, ax = plt.subplots(figsize=(12, 4))

    # Same color map application as before
    num_colors = len(sorted_df.columns)
    colors = plt.cm.YlGnBu([0.33, 0.6, 0.9])

    for idx, (attribute, values) in enumerate(sorted_df.iterrows()):

        offset = width * multiplier
        rects = ax.bar(
            x + offset,
            values,
            width,
            label=attribute,
            color=colors[idx],
            edgecolor="none",
        )
        multiplier += 1

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel("Accuracy [%]", fontweight="bold")
    # ax.set_title()
    ax.set_xticks(x + width, sorted_df.columns)
    ax.legend(loc="upper right", bbox_to_anchor=(1.0, 1.1))

    # To make the tick labels bold, set the fontweight for all tick labels
    # for label in ax.get_xticklabels():
    #     label.set_fontweight('bold')
    # for label in ax.get_yticklabels():
    #     label.set_fontweight('bold')

    # Removing the spines
    ax.spines["left"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["top"].set_visible(False)

    # Ticks on the top
    # ax.xaxis.tick_top()
    ax.xaxis.set_label_position("bottom")

    # Remove the ticks but keep the numbers; this keeps the tick labels visible.
    ax.yaxis.set_ticks_position("none")
    ax.xaxis.set_ticks_position("none")
    ax.set_axisbelow(True)
    plt.grid(alpha=0.4)

    plt.savefig(
        "plots/prompt_comparison_u.pdf", bbox_inches="tight", dpi=300, pad_inches=0.1
    )
    plt.show()


def stacked_bar_chart_models(sorted_df: pd.DataFrame):
    import matplotlib.pyplot as plt
    import numpy as np

    # Assuming height should be adjusted to decrease distance between bars
    # Decrease the height of bars to get them closer to each other
    height = 0.8  # Adjust this value as needed to decrease the distance between bars

    fig, ax = plt.subplots(figsize=(10, 2))
    left = np.zeros(len(sorted_df))

    # Same color map application as before
    num_colors = len(sorted_df.columns)
    colors = plt.cm.YlGnBu(np.linspace(0.25, 1, num_colors))

    color_index = 0
    for boolean, weight_count in sorted_df.items():
        p = ax.barh(
            sorted_df.index,
            weight_count,
            height,
            label=boolean,
            left=left,
            color=colors[color_index],
            linewidth=0,
        )
        left += weight_count
        color_index += 1

    # Making title bold
    ax.set_title("# Correct", fontweight="bold", y=1.2)  # Adjust the y if necessary

    # # Making axis labels bold
    # ax.set_xlabel("X axis label", fontweight='bold')  # Assuming you have an x-label
    # ax.set_ylabel("Y axis label", fontweight='bold')  # Assuming you have a y-label

    # Removing the spines
    ax.spines["left"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["top"].set_visible(False)

    # Ticks on the top
    # ax.xaxis.tick_top()
    # ax.xaxis.set_label_position('top')

    # # Remove the bolding from the tick labels
    # for label in ax.get_xticklabels() + ax.get_yticklabels():
    #     label.set_fontweight('normal')

    # Adding slight lines for ticks for better visibility
    ax.xaxis.set_ticks_position("top")  # Ensuring x-axis ticks are only on the top
    ax.yaxis.set_ticks_position("none")  # Ensuring there are no y-axis ticks

    # Drawing a final tick line at the end of the bar to show the sum of all labels
    total_widths = sorted_df.sum(axis=1)
    max_tick = total_widths.max()

    ax.set_xticks(list(ax.get_xticks()[:-1]) + [max_tick])

    # Make sure the models/categories names are shown
    ax.set_yticklabels(sorted_df.index, minor=False)

    # Reverse the y-axis to have the first index on top.
    ax.invert_yaxis()

    # # To make the tick labels bold, set the fontweight for all tick labels
    # for label in ax.get_xticklabels():
    #     label.set_fontweight('bold')
    # for label in ax.get_yticklabels():
    #     label.set_fontweight('bold')

    # Place legend
    ax.legend(
        loc="upper center", bbox_to_anchor=(0.5, 1.6), ncol=num_colors, frameon=False
    )
    ax.set_axisbelow(True)
    plt.grid(alpha=0.3)
    plt.savefig(
        "plots/stacked_bar_chart_models_u.pdf",
        bbox_inches="tight",
        dpi=300,
        pad_inches=0.1,
    )
    plt.show()


def model_comparison():
    df = pd.DataFrame()
    for config, performance_sum in zip(configs, performances):
        print()
        print(config)
        print()
        config_path = f"src/configs/run_{config}.yaml"
        config = load_config(config_path)
        performance = f"performances/{performance_sum}.json"
        df_model = get_performance_summary(config=config, performance=performance)

        df_true = df_model[["true_pred"]].rename(
            columns={"true_pred": config.model.name}
        )
        df = pd.concat([df, df_true], axis=1)

    df_human = df_model[["Category", "total_gt"]]
    df = pd.concat([df, df_human], axis=1)
    df = df.set_index("Category")
    df = df.T
    print(df)

    sorted_columns = df.max().sort_values(ascending=False).index
    pivoted_and_sorted_df = df[sorted_columns]
    sorted_df = pivoted_and_sorted_df.loc[
        pivoted_and_sorted_df.sum(axis=1).sort_values(ascending=False).index
    ]
    sorted_df = sorted_df.rename(columns=attribute_to_short)
    sorted_df = sorted_df.rename(index=model_to_text)

    print(sorted_df)

    print(sorted_df.iloc[0])
    print(sorted_df.iloc[4])

    result = sorted_df.iloc[4] / sorted_df.iloc[0]
    result = pd.DataFrame(result).T
    print((result * 100).to_latex(float_format="{:0.1f}".format))
    print(sorted_df.sum(axis=1).to_string())

    print((sorted_df.sum(axis=1) / sorted_df.sum(axis=1).iloc[0]) * 100)

    df_all_acc = sorted_df.sum(axis=1) / sorted_df.sum(axis=1).iloc[0]

    return sorted_df, df_all_acc


def prompt_comparison():
    df = pd.DataFrame()
    for config, performance_sum in zip(configs, performances):
        print()
        print(config)
        print()
        config_path = f"src/configs/run_{config}.yaml"
        config = load_config(config_path)
        performance = f"performances/image_performance_{performance_sum}.json"
        df_model = get_performance_summary(config=config, performance=performance)

        df_true = df_model[["true_pred"]].rename(columns={"true_pred": performance_sum})
        df = pd.concat([df, df_true], axis=1)
    df_human = df_model[["Category", "total_gt"]]
    df = pd.concat([df, df_human], axis=1)
    df = df.set_index("Category")
    df = df.T

    print(df.to_string())

    sorted_columns = df.max().sort_values(ascending=False).index
    pivoted_and_sorted_df = df[sorted_columns]
    sorted_df = pivoted_and_sorted_df.loc[
        pivoted_and_sorted_df.sum(axis=1).sort_values(ascending=False).index
    ]
    sorted_df = sorted_df.rename(columns=attribute_to_short)
    sorted_df = sorted_df.rename(index=model_to_prompt)

    print(sorted_df.to_string())

    print(sorted_df.sum(axis=1).to_string())

    print((sorted_df.sum(axis=1) / sorted_df.sum(axis=1).iloc[0]).to_string())

    return (sorted_df / sorted_df.iloc[0]).iloc[1:4]


def model_comparison_human():
    df1 = pd.DataFrame()
    df2 = pd.DataFrame()

    for config, performance_sum in zip(configs, performances):
        print()
        print(config)
        print()
        config_path = f"src/configs/run_{config}.yaml"
        config = load_config(config_path)
        performance = f"performances/{performance_sum}.json"
        df_model1, df_model2 = get_performance_summary_human(
            config=config, performance=performance
        )

        df_true1 = df_model1[["true_pred"]].rename(
            columns={"true_pred": config.model.name}
        )
        df_true2 = df_model2[["true_pred"]].rename(
            columns={"true_pred": config.model.name}
        )

        df1 = pd.concat([df1, df_true1], axis=1)
        df2 = pd.concat([df2, df_true2], axis=1)

    df_human1 = df_model1[["Category", "total_gt"]]
    df1 = pd.concat([df1, df_human1], axis=1)
    df1 = df1.set_index("Category")
    df1 = df1.T

    df_human2 = df_model2[["Category", "total_gt"]]
    df2 = pd.concat([df2, df_human2], axis=1)
    df2 = df2.set_index("Category")
    df2 = df2.T

    # print(df.to_string())
    # print(df.to_string())

    sorted_columns = df1.max().sort_values(ascending=False).index
    pivoted_and_sorted_df = df1[sorted_columns]
    sorted_df = pivoted_and_sorted_df.loc[
        pivoted_and_sorted_df.sum(axis=1).sort_values(ascending=False).index
    ]
    sorted_df = sorted_df.rename(columns=attribute_to_short)
    sorted_df = sorted_df.rename(index=model_to_text)

    print(sorted_df.to_string())
    print(sorted_df.sum(axis=1).to_string())
    print((sorted_df.sum(axis=1) / sorted_df.sum(axis=1).iloc[0]).to_string())

    df_human_all = (sorted_df.sum(axis=1) / sorted_df.sum(axis=1).iloc[0]).T

    sorted_columns = df2.max().sort_values(ascending=False).index
    pivoted_and_sorted_df = df2[sorted_columns]
    sorted_df = pivoted_and_sorted_df.loc[
        pivoted_and_sorted_df.sum(axis=1).sort_values(ascending=False).index
    ]
    sorted_df = sorted_df.rename(columns=attribute_to_short)
    sorted_df = sorted_df.rename(index=model_to_text)

    print(sorted_df.to_string())

    print(sorted_df.sum(axis=1).to_string())

    print((sorted_df.sum(axis=1) / sorted_df.sum(axis=1).iloc[0]).to_string())

    df_human_all = pd.concat(
        [df_human_all, (sorted_df.sum(axis=1) / sorted_df.sum(axis=1).iloc[0]).T],
        axis=1,
    )
    print(df_human_all.T.to_string())

    with open("human_all.tex", "w") as file:
        file.write((100 * df_human_all).T.to_latex(float_format="{:0.1f}".format))


if __name__ == "__main__":
    df, df_all_acc = model_comparison()
    print((100 * df_all_acc).to_latex(float_format="{:0.1f}".format))

    # stacked_bar_chart_models(df)
    # model_comparison_human()

    # df = prompt_comparison()
    # prompt_comparison_plot(df)
