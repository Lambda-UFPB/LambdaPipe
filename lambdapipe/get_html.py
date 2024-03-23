import pandas as pd


def color_format(val):
    """Color formatting for the DataFrame."""
    color = '#2e7d32' if 0 <= val <= 0.3 else ('#ffeb3b' if 0.3 < val <= 0.7 else '#b71c1c')
    return f'background-color: {color}; font-weight: bold'


def get_df_html(df_html_old: pd.DataFrame):
    first_column = df_html_old.iloc[:, 0]
    lipinski = df_html_old.loc[:, 'Lipinski']
    toxicity = df_html_old.iloc[:, 2:13]
    df_html = pd.concat([first_column, toxicity, lipinski], axis=1)
    df_html['mean_toxicity'] = df_html.select_dtypes(include='float').mean(axis=1)
    df_html['std_toxicity'] = df_html.select_dtypes(include='float').std(axis=1)
    df_html['score'] = df_html['mean_toxicity'] + df_html['std_toxicity']
    df_html['Score Pharmit'] = df_html_old['Score Pharmit']
    df_html['RMSD Pharmit'] = df_html_old['RMSD Pharmit']
    df_html['smiles'] = df_html_old['smiles']
    df_html = df_html.sort_values(by='score', ascending=True)
    df_html = df_html.reset_index(drop=True)
    df_html = df_html.drop(columns=['mean_toxicity', 'std_toxicity', 'score'])
    if len(df_html) > 500:
        df_html = df_html.head(500)
    return df_html


def results_to_html(output_folder_path: str, folder_name: str):
    """Converts the results to a html file"""
    df = pd.read_csv(f"{output_folder_path}/results/admet_filtered.csv")
    df_html = get_df_html(df)
    styled_html_df = df_html.style.map(color_format, subset=df_html.columns[1:12])
    html = styled_html_df.to_html(index=False)
    if len(df_html) > 500:
        subtitle = "<h4>Only the top 500 molecules are shown</h4>"
        html = subtitle + html
    with open(f"{output_folder_path}/results/{folder_name}_results.html", "w") as f:
        f.write(html)


if __name__ == '__main__':
    results_to_html("/home/kdunorat/lambdapipe_results/testefinal", "agoravai")

