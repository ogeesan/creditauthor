# %%
from pathlib import Path
import pandas as pd
import matplotlib as mpl
from seaborn import heatmap
from matplotlib.transforms import blended_transform_factory


def read_data(filepath, sheet_name='Sheet1', verbose=False):
    """Create dataframe from file that is ready to heatmap

    Parameters
    ----------
    filepath : pathlib.Path
        Path to .xlsx file or .csv file
    sheet_name : str, optional
        Which sheet to read if fed an Excel file, by default 'Sheet1'

    Returns
    -------
    pandas.DataFame
        Table from file with index as CRediT roles and each column as author, with blank columns removed.
    """
    filepath = Path(filepath)
    if filepath.suffix == '.xlsx':
        df = pd.read_excel(filepath, sheet_name=sheet_name)
    else:
        df = pd.read_csv(filepath)
        
    authors = []
    for col, key in enumerate(df):
        if col == 0:
            continue
        if (col > 0) & ('Unnamed: ' in key):
            # users can leave a space to build a Sum column
            break
        authors.append(key)
        
    df.set_index(pd.Index(df.iloc[:, 0]), inplace=True)
    df.index.name = 'Role'
    data = df.loc[:, authors]
    if verbose:
        print(f"Identified roles ({len(data.index)}): {', '.join(data.index.to_list())}")
        print(f"Identified authors ({len(authors)}): {', '.join(authors)}")
    
    return data


def plot_heatmap(ax, data, cmap):
    heatmap(data, ax=ax,
            linewidth=.5,
            square=True,
            cmap=cmap,
            cbar=False,
            )


def style_axis(ax, authors, rotation=45, greylevel=None):
    """Make axis have a nice placement and style"""
    # Remove unnecessary items
    ax.set_ylabel(None)
    ax.set_xticks([])
    
    if greylevel is not None:
        grey = [greylevel for _ in range(3)]
        ax.set_facecolor(grey)
    
    # Put authors on the top as text objects
    trans = blended_transform_factory(ax.transData, ax.transAxes) # x positions are in data units, y positions in axes fraction
    for x, author in enumerate(authors):
        ax.text(x, # author column
                1, # top of axes
                ' ' + author, # add a space to lift author name off from the heatmap
                transform=trans, rotation=rotation)

# %%

if __name__ == '__main__':
    
    import argparse

    parser = argparse.ArgumentParser(
        prog='creditauthor',
        description='Generate image of credit authors from a table'
    )
    
    parser.add_argument('filepath')
    parser.add_argument('-o', '--output',
                        type=str,
                        default=None,
                        help="Where to output the file. Defaults to input filename but with .png.")
    parser.add_argument('-cmap', '--colormap',
                        type=str,
                        default='Purples',
                        help='Colormap to use in figure, default Purples. For options see: https://matplotlib.org/stable/users/explain/colors/colormaps.html'
                        )
    parser.add_argument('--grey',
                        type=float,
                        default=0.90,
                        help="RGB value of grey boxes when values are not entered, default 0.90")
    parser.add_argument('--rotation',
                        type=float,
                        default=45.0,
                        help='Rotation angle of author list, default 45 degrees')
    parser.add_argument('--sheet',
                        type=str,
                        default='Sheet1',
                        help="SSheet to use if the source file is an Excel file, default 'Sheet1'.")

    args = parser.parse_args()
    
    # filepath = 'pk-paternalcytokine.xlsx'
    filepath = Path(args.filepath)
    if args.output is None:
        outputpath = filepath.with_suffix('.png')

    df = read_data(filepath, verbose=True)
    
    fig = mpl.figure.Figure()
    ax = fig.subplots()
    plot_heatmap(ax, df, args.colormap)
    style_axis(ax, df.keys(), rotation=args.rotation, greylevel=args.grey)
    fig.savefig(outputpath, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f"Saved file to {outputpath}")