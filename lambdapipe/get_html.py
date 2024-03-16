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
    df_html['green_count'] = (df_html.select_dtypes(include='float') <= 0.3).sum(axis=1)
    df_html['Score Pharmit'] = df_html_old['Score Pharmit']
    df_html['RMSD Pharmit'] = df_html_old['RMSD Pharmit']
    df_html = df_html.sort_values(by='green_count', ascending=False)
    df_html = df_html.drop(columns=['green_count'])
    return df_html


def results_to_html(output_folder_path: str, folder_name: str):
    """Converts the results to a html file"""
    df = pd.read_csv(f"{output_folder_path}/results/admet_filtered.csv")
    df_html = get_df_html(df)
    styled_html_df = df_html.style.map(color_format, subset=df_html.columns[1:12])
    html = styled_html_df.to_html()
    with open(f"{output_folder_path}/results/{folder_name}_results.html", "w") as f:
        f.write(html)


if __name__ == '__main__':
    results_to_html("/home/kdunorat/lambdapipe_results/testefinal", "testefinal")

