import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch
import matplotlib.pyplot as plt
import matplotlib.colors as mc
import colorsys
from scipy.stats import mstats
import seaborn as sns
from matplotlib.ticker import MultipleLocator
from matplotlib.ticker import FuncFormatter
import matplotlib.colors as mc
import warnings 
warnings.filterwarnings("ignore")


def bootstrap_CI(data, n_bootstraps=10000, ci=95, mean=True): 
    """
    Bootstrap confidence interval for mean or median.
    """
    bootstrap_samples = np.zeros(n_bootstraps)
    for i in range(n_bootstraps):
        sample = np.random.choice(data, size=len(data), replace=True)
        if mean == True:
            bootstrap_samples[i] = np.mean(sample)
        else:
            bootstrap_samples[i] = np.median(sample)
    lower = (100 - ci) / 2
    upper = 100 - lower
    ci_low, ci_high = mstats.mquantiles(bootstrap_samples, prob=[lower/100, upper/100])
    ci_low = round(ci_low, 3)
    ci_high = round(ci_high, 3)
    return ci_low, ci_high

def lighten_color(color, amount=0.5, desaturation=0.2):
    """
    Eric's function.
    Lightens and desaturates the given color by multiplying (1-luminosity) by the given amount
    and decreasing the saturation by the specified desaturation amount.
    Input can be matplotlib color string, hex string, or RGB tuple.
    Examples:
    >> lighten_color('g', 0.3, 0.2)
    >> lighten_color('#F034A3', 0.6, 0.4)
    >> lighten_color((.3,.55,.1), 0.5, 0.1)
    """
    try:
        c = mc.cnames[color]
    except:
        c = color
    c = colorsys.rgb_to_hls(*mc.to_rgb(c))
    new_luminosity = 1 - amount * (1 - c[1])
    new_saturation = max(0, c[2] - desaturation)
    return colorsys.hls_to_rgb(c[0], new_luminosity, new_saturation)

def get_fancy_bbox(bb, boxstyle, color, background=False, mutation_aspect=3):
    """
    Creates a fancy bounding box for the bar plots. Adapted from Eric's function.
    """
    if background:
        height = bb.height - 2
    else:
        height = bb.height
    if background:
        base = bb.ymin # - 0.2
    else:
        base = bb.ymin
    return FancyBboxPatch(
        (bb.xmin, base),
        abs(bb.width), height,
        boxstyle=boxstyle,
        ec="none", fc=color,
        mutation_aspect=mutation_aspect, # change depending on ylim
        zorder=2
    )

def change_saturation(rgb, change=0.6):
    """
    Changes the saturation for the plotted bars, rgb is from sns.colorblind (used change=0.6 in paper)
    """
    hsv = colorsys.rgb_to_hsv(rgb[0], rgb[1], rgb[2])
    saturation = max(0, min(hsv[1] * change, 1))
    return colorsys.hsv_to_rgb(hsv[0], saturation, hsv[2])

def compute_stats(df_raw, pp_level=False):
    """
    Creates a DataFrame with the average accuracy and bootsrapped CI.
    """
    group_cols = ['direction', 'condition', 'init_belief', 'variable', 
                  'true_false', 'model_name', 'method', 'temperature']
    
    # Compute mean and bootstrap_CI, then merge the two dataframes
    df_mean = df_raw.groupby(group_cols).mean().reset_index()
    df_ci = df_raw.groupby(group_cols).agg(bootstrap_CI).reset_index()

    
    
    df = pd.merge(df_mean, df_ci, on=group_cols, suffixes=('_mean', '_ci'))
    
    # Create new columns and rename existing ones
    df['Question'] = (df['direction'].astype(str) + ' ' + df['variable'].astype(str)).str.title()
    df['Type'] = df['true_false']
    df['Method'] = df['method']
    df = df.rename(columns={'correct_mean': 'Average Accuracy', 'correct_ci': 'Error'})
    
    # Drop the original group columns
    df = df.drop(group_cols, axis=1)

    return df

def get_contingency(df, contingency="true_and_false"):
    """
    Calculates the contingency
        true_and_false: P(T and F) -
        not_true_and_false: P(not T and F)
        false_and_true: P(F and T)
        not_false_and_true: P(not F and T)
        marginal P(T) and P(F)
    """
    # Ensuring the data types are correct for our operations
    df['true_false'] = df['true_false'].astype(bool)
    df['correct'] = df['correct'].astype(int)

    # Splitting the DataFrame based on 'true_false' column values
    df_true, df_false = df[df['true_false']], df[~df['true_false']]
    # Checking if both the parts have equal rows
    assert len(df_true) == len(df_false), "DataFrames don't have the same length"

    # Defining the operations for different conditions
    conditions = {
        'true_and_false': np.logical_and(df_true['correct'].values, df_false['correct'].values),
        'not_true_and_false': np.logical_and(~df_true['correct'].values, df_false['correct'].values),
        'false_and_true': np.logical_and(df_false['correct'].values, df_true['correct'].values),
        'not_false_and_true': np.logical_and(~df_false['correct'].values, df_true['correct'].values),
        'marginal': df_false['correct']
    }
    # Assigning the result based on the selected condition
    if contingency == "true_and_false" or contingency == "not_true_and_false":
        df_false['correct'] = conditions[contingency].astype(int)
        return pd.concat([df_true, df_false]).reset_index(drop=True)
    elif contingency == "false_and_true" or contingency == "not_false_and_true":
        df_true['correct'] = conditions[contingency].astype(int)
        return pd.concat([df_true, df_false]).reset_index(drop=True)
    elif contingency == "marginal":
        return pd.concat([df_true, df_false]).reset_index(drop=True)
    
def get_plot_df(results, 
                model_name, 
                init_belief=1, 
                condition="belief", 
                method="0shot", 
                contingency="false_and_true"):
    """
    Creates a DataFrame for plotting the results.
    """
    df = results[(results['init_belief'] == init_belief) & \
        (results['condition'] == condition) & \
        (results['method'] == method) & (results['model_name'] == model_name)]

    df = get_contingency(df, contingency=contingency)
    df = compute_stats(df)
    df["model_name"] = model_name
    return df


def plot_model(grouped_df, 
               palette, 
               plot_dir,
               init_belief=0, 
               condition="belief_backward", 
               method="0shot", 
               contingency="false_and_true"):
    """
    Plots the results for a given model. Adapted from Eric's function.
    """
    plt.rcParams["font.family"] = "Avenir"
    plt.rcParams["font.size"] = 24
    
 
    fig, ax = plt.subplots(figsize=(10, 5))
    print(grouped_df['Average Accuracy'])
    grouped_df['Average Accuracy'].plot(kind='bar', ax=ax, width=2, color=[palette[i] for i in grouped_df['Average Accuracy'].columns], zorder=10,  alpha=1)
    new_patches = []
    # modify patchess
    for i, patch in enumerate(ax.patches):
        x = patch.get_x()
        if i in [0, 1]:
            patch.set_x(x + -0.2)
        if i in [2, 3]:
            patch.set_x(x + -0.1)
        if i in [4, 5]:
            patch.set_x(x)
        if i in [6, 7]:
            patch.set_x(x + 0.1)
        if i in [8, 9]:
            patch.set_x(x + 0.2)

        # y = patch.get_height()
        # set patch y to y + 0.1
        # patch.set_height(y + 0.1)
        
        bb = patch.get_bbox()
        color=patch.get_facecolor()
        p_bbox = get_fancy_bbox(bb, "round,pad=-0.005,rounding_size=0.02", color, mutation_aspect=0.6)
        patch.remove()
        new_patches.append(p_bbox)
    for patch in new_patches:
        ax.add_patch(patch)
    # Adding error bars
    
    for i, bar in enumerate(ax.patches):

        yerr = grouped_df['Error'].values.T.flatten()[i]
        bar_color = bar.get_facecolor()
        bar_color = "black"
        lower_error = bar.get_height() - yerr[0]
        upper_error = yerr[1] - bar.get_height()
        yerr = np.array([[lower_error], [upper_error]])
        lighter_bar_color = lighten_color(bar_color, 0.8)  # Create a lighter shade of the bar color
        # ax.errorbar(bar.get_x() + bar.get_width() / 2, bar.get_height(), yerr=yerr,  color=lighter_bar_color, capsize=1, ls='none', elinewidth=2, zorder=40)

        # Add symbol text above bars
            # Symbol text above bars
        if i in [0]:
            ax.text(bar.get_x() + bar.get_width(), -0.13, "llama-65", ha='center', fontsize=24)
        if i in [2]:
            ax.text(bar.get_x() + bar.get_width(), -0.13, "dav-003", ha='center', fontsize=24)
        if i in [4]:
            ax.text(bar.get_x() + bar.get_width(), -0.13, "gpt-3.5", ha='center', fontsize=24)
        if i in [6]:
            ax.text(bar.get_x() + bar.get_width(), -0.13, "claude", ha='center', fontsize=24)
        if i in [8]:
            ax.text(bar.get_x() + bar.get_width(), -0.13, "gpt-4", ha='center', fontsize=24)


    # Removing box
    sns.despine(left=True, bottom=False)
    plt.xlabel('')
    # set rotation
  
    # hiding the xiticks


    plt.legend(title='')
    fmt = FuncFormatter(lambda y, _: '{:.0%}'.format(y))  # Define a percentage format function
    ax.yaxis.set_major_formatter(fmt)  # Set the y-axis formatter

    ax.yaxis.set_major_locator(MultipleLocator(0.2))
    ax.yaxis.set_major_formatter(fmt)
    ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1])
    ax.set_yticklabels(['0', '20%', '40%', '60%', '80%', '100%'])

    plt.tick_params(axis='x', pad=25) 

   
    # Get the legend
    legend = plt.legend(title='', ncol=4, frameon=False)
    # plt.legend(frameon=False)  # Set frameon to False to remove the legend frame
    ax.set_xticklabels([""])

    legend._set_loc(2)
    for text in legend.get_texts():
        label = text.get_text()
        new_label = label.replace("shot", "").replace("(", "").replace(")", "").replace(",", "-").replace("'", "").replace(" ", "").replace("F", "f").replace("T", "t")
        text.set_text(new_label)

    handles, labels = ax.get_legend_handles_labels()

    true_handle = handles[labels.index("(openai_text-davinci-003_0, True)")]
    false_handle = handles[labels.index("(openai_text-davinci-003_0, False)")]
    legend = ax.legend([true_handle, false_handle], ['', ''], title='', ncol=1, frameon=False, loc='upper center', fontsize=20)

    ax.xaxis.set_tick_params(labelbottom=False)
    ax.set_xticks([])
    # Set grid, labels and limits
    ax.yaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.5, zorder=-100)
    ax.set_ylabel('Accuracy')
    ax.yaxis.set_label_coords(-0.1, 0.4)
    plt.tick_params(axis='y', length=0)
    plt.ylim(0.005, 1.4)
    ax.get_legend().remove()
   
    plt.savefig(f"{plot_dir}/{init_belief}_{condition}_{method}_{contingency}.pdf", bbox_inches='tight')
    plt.show()



def plot_human_exp_1(df, palette, plot_dir):
    plt.rcParams["font.family"] = "Avenir"
    plt.rcParams["font.size"] = 24

    grouped_df = df.groupby(['Question', 'Survey Type']).sum().unstack()
    grouped_df = grouped_df.reindex(['BigTom (Ours)', 'socialIQa', 'Expert'], level='Survey Type', axis=1)

    fig, ax = plt.subplots(figsize=(15, 5))
    grouped_df['Median Rating'].plot(kind='bar', ax=ax, width=0.8, color=[palette[i] for i in grouped_df['Median Rating'].columns], zorder=10)

    for patch in ax.patches:
        bb = patch.get_bbox()
        color = patch.get_facecolor()
        p_bbox = get_fancy_bbox(bb, "round,pad=-0.005,rounding_size=0.02", color, mutation_aspect=4)
        patch.remove()
        ax.add_patch(p_bbox)

    for i, bar in enumerate(ax.patches):
        yerr = grouped_df['Error'].values.T.flatten()[i]
        lower_error = bar.get_height() - yerr[0]
        upper_error = yerr[1] - bar.get_height()
        yerr = np.array([[lower_error], [upper_error]])
        bar_color = "black"
        lighter_bar_color = lighten_color(bar_color, 0.8)
        
        ax.errorbar(bar.get_x() + bar.get_width() / 2, bar.get_height(), yerr=yerr, color=lighter_bar_color, capsize=1, ls='none', elinewidth=2, zorder=40)

    plt.xticks(rotation=0)
    sns.despine(left=True, bottom=False)
    plt.xlabel('')
    plt.legend(title='', frameon=False, ncol=4)
    fmt = FuncFormatter(lambda y, _: '{:.0%}'.format(y / 5))
    ax.yaxis.set_major_formatter(fmt)
    ax.yaxis.set_major_locator(MultipleLocator(1))
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(['1', '2', '3', '4', '5'])
    ax.yaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.5, zorder=-100)
    plt.tick_params(axis='y', length=0)
    ax.set_ylabel('Average Rating')
    ax.yaxis.set_label_coords(-0.03, 0.4)
    plt.ylim(0.02, 7)
    plt.savefig(f"{plot_dir}/exp_1_average_ratings.pdf", format='pdf', bbox_inches='tight')

def plot_human_exp_2(df, palette, plot_dir, condition):
    grouped_df = df.groupby(['Question', 'Type']).agg({'Average Accuracy': 'mean', 'Error': 'first'}).unstack()
    grouped_df = grouped_df.reindex(['True', 'False'], level='Type', axis=1)
    plt.rcParams["font.size"] = 30
    fig, ax = plt.subplots(figsize=(4, 7))

    grouped_df['Average Accuracy'].plot(kind='bar', ax=ax, width=0.8, color=[palette[i] for i in grouped_df['Average Accuracy'].columns], zorder=10)
    
    new_patches = []
    extra_patches = []
    
    for i, patch in enumerate(ax.patches):

        x = patch.get_x()
        if i == 0:
            patch.set_x(x + -0.1)
        elif i == 1:
            patch.set_x(x + +0.1)
        
        bb = patch.get_bbox()
        color = patch.get_facecolor()
        p_bbox = get_fancy_bbox(bb, "round,pad=-0.005,rounding_size=0.02", color, mutation_aspect=1)
        patch.remove()
        new_patches.append(p_bbox)
        back_bbox = get_fancy_bbox(bb, "round,pad=-0.005,rounding_size=0.0", color, background=True, mutation_aspect=1)
        extra_patches.append(back_bbox)

    for patch in new_patches:
        ax.add_patch(patch)

    for i, bar in enumerate(ax.patches):
        yerr = grouped_df['Error'].values.T.flatten()[i]
        bar_color = "black"
        lower_error = bar.get_height() - yerr[0]
        upper_error = yerr[1] - bar.get_height()
        yerr = np.array([[lower_error], [upper_error]])
        lighter_bar_color = lighten_color(bar_color, 0.8)
        ax.errorbar(bar.get_x() + bar.get_width() / 2, bar.get_height(), yerr=yerr, color=lighter_bar_color, capsize=0, ls='none', elinewidth=2, zorder=40)


    sns.despine(left=True, bottom=False)
    plt.xlabel('')
    
    fmt = FuncFormatter(lambda y, _: '{:.0%}'.format(y))
    ax.yaxis.set_major_locator(MultipleLocator(0.2))
    ax.yaxis.set_major_formatter(fmt)

    ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1])
    ax.set_yticklabels(['0', '20%', '40%', '60%', '80%', '100%'], fontsize=28)
    ax.set_xticks([-.3, .3])
    ax.set_xticks([])
    # ax.set_xticklabels(['True\nBelief', '& False\nBelief'], fontsize=27)
    plt.xticks(rotation=0)
    
    ax.get_legend().remove()
    ax.yaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.5, zorder=-100)
    
    plt.tick_params(axis='y', length=0)
    ax.set_ylabel('Accuracy', fontsize=28)
    ax.yaxis.set_label_coords(-0.3, 0.4)
    plt.ylim(.005, 1.4)
    plt.savefig(f"{plot_dir}/exp_2_{condition}_accuracy.pdf", format='pdf', bbox_inches='tight')
    plt.show()





def plot_model_with_human(grouped_df, 
               palette, 
               plot_dir,
               init_belief=0, 
               condition="belief_backward", 
               method="0shot", 
               contingency="false_and_true"):
    """
    Plots the results for a given model. Adapted from Eric's function.
    """
    plt.rcParams["font.family"] = "Avenir"
    plt.rcParams["font.size"] = 24
    
 
    fig, ax = plt.subplots(figsize=(10, 5))
    print(grouped_df['Average Accuracy'])
    grouped_df['Average Accuracy'].plot(kind='bar', ax=ax, width=2, color=[palette[i] for i in grouped_df['Average Accuracy'].columns], zorder=10,  alpha=1)
    new_patches = []
    # modify patchess
    for i, patch in enumerate(ax.patches):
        x = patch.get_x()
        if i in [0, 1]:
            patch.set_x(x + -0.25)
        if i in [2, 3]:
            patch.set_x(x + -0.15)
        if i in [4, 5]:
            patch.set_x(x -0.04)
        if i in [6, 7]:
            patch.set_x(x + 0.05)
        if i in [8, 9]:
            patch.set_x(x + 0.15)
        if i in [10, 11]:
            patch.set_x(x + 0.25)

        # y = patch.get_height()
        # set patch y to y + 0.1
        # patch.set_height(y + 0.1)
        
        bb = patch.get_bbox()
        color=patch.get_facecolor()
        p_bbox = get_fancy_bbox(bb, "round,pad=-0.005,rounding_size=0.02", color, mutation_aspect=0.6)
        patch.remove()
        new_patches.append(p_bbox)
    for patch in new_patches:
        ax.add_patch(patch)
    # Adding error bars
    
    for i, bar in enumerate(ax.patches):

        yerr = grouped_df['Error'].values.T.flatten()[i]
        bar_color = bar.get_facecolor()
        bar_color = "black"
        lower_error = bar.get_height() - yerr[0]
        upper_error = yerr[1] - bar.get_height()
        yerr = np.array([[lower_error], [upper_error]])
        lighter_bar_color = lighten_color(bar_color, 0.8)  # Create a lighter shade of the bar color
        
        # Add symbol text above bars
            # Symbol text above bars
        if i in [0]:
            ax.text(bar.get_x() + bar.get_width(), -0.13, "llama-65", ha='center', fontsize=24)
        if i in [2]:
            ax.text(bar.get_x() + bar.get_width(), -0.13, "dav-003", ha='center', fontsize=24)
        if i in [4]:
            ax.text(bar.get_x() + bar.get_width(), -0.13, "gpt-3.5", ha='center', fontsize=24)
        if i in [6]:
            ax.text(bar.get_x() + bar.get_width(), -0.13, "claude", ha='center', fontsize=24)
        if i in [8]:
            ax.text(bar.get_x() + bar.get_width(), -0.13, "gpt-4", ha='center', fontsize=24)
        if i in [10]:
            ax.text(bar.get_x() + bar.get_width(), -0.13, "human", ha='center', fontsize=24)
        if i in [10, 11]:
            ax.errorbar(bar.get_x() + bar.get_width() / 2, bar.get_height(), yerr=yerr,  color=lighter_bar_color, capsize=1, ls='none', elinewidth=2, zorder=40)



    # Removing box
    sns.despine(left=True, bottom=False)
    plt.xlabel('')
    # set rotation
  
    # hiding the xiticks


    plt.legend(title='')
    fmt = FuncFormatter(lambda y, _: '{:.0%}'.format(y))  # Define a percentage format function
    ax.yaxis.set_major_formatter(fmt)  # Set the y-axis formatter

    ax.yaxis.set_major_locator(MultipleLocator(0.2))
    ax.yaxis.set_major_formatter(fmt)
    ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1])
    ax.set_yticklabels(['0', '20%', '40%', '60%', '80%', '100%'])

    plt.tick_params(axis='x', pad=25) 

   
    # Get the legend
    legend = plt.legend(title='', ncol=4, frameon=False)
    # plt.legend(frameon=False)  # Set frameon to False to remove the legend frame
    ax.set_xticklabels([""])

    legend._set_loc(2)
    for text in legend.get_texts():
        label = text.get_text()
        new_label = label.replace("shot", "").replace("(", "").replace(")", "").replace(",", "-").replace("'", "").replace(" ", "").replace("F", "f").replace("T", "t")
        text.set_text(new_label)

    handles, labels = ax.get_legend_handles_labels()

    true_handle = handles[labels.index("(openai_text-davinci-003_0, True)")]
    false_handle = handles[labels.index("(openai_text-davinci-003_0, False)")]
    legend = ax.legend([true_handle, false_handle], ['', ''], title='', ncol=1, frameon=False, loc='upper center', fontsize=20)

    ax.xaxis.set_tick_params(labelbottom=False)
    ax.set_xticks([])
    # Set grid, labels and limits
    ax.yaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.5, zorder=-100)
    ax.set_ylabel('Accuracy')
    ax.yaxis.set_label_coords(-0.1, 0.4)
    plt.tick_params(axis='y', length=0)
    plt.ylim(0.005, 1.4)
    ax.get_legend().remove()
   
    plt.savefig(f"{plot_dir}/{init_belief}_{condition}_{method}_{contingency}.pdf", bbox_inches='tight')
    plt.show()
