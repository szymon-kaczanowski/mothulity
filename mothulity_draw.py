#! /usr/bin/env python


from utilities import get_dir_path
import os
import ConfigParser
import argparse
from Bio import Phylo as ph
import matplotlib
matplotlib.use('Agg')
import pylab
import matplotlib.pyplot as plt
import matplotlib.style as style
import mpld3
from pandas import read_csv
from seaborn import heatmap
from seaborn import pairplot
from seaborn import lmplot
from lxml import etree as et


__author__ = "Dariusz Izak IBB PAS"


def load_template_file(template_file):
    template_Loader = jj2.FileSystemLoader(searchpath="/")
    template_Env = jj2.Environment(loader=template_Loader)
    template = template_Env.get_template(template_file)
    return template


def render_template(template_loaded,
                    venn_diagrams,
                    javascript):
    template_vars = {"venn_diagrams": venn_diagrams}
    template_rendered = template_loaded.render(template_vars)
    return template_rendered


def save_template(output_file_name,
                  template_rendered):
    with open(output_file_name, "w") as fout:
        fout.write(template_rendered)


def draw_rarefaction(input_file_name,
                     output_file_name):
    df = read_csv(input_file_name,
                  sep="\t",
                  index_col="numsampled")
    cols = [i for i in df.columns if "lci" not in i]
    cols = [i for i in cols if "hci" not in i]
    df = df[cols]
    fig, ax = plt.subplots()
    df[cols].plot(ax=ax,
                  figsize=(15, 8))
    labels = list(df.columns.values)
    for i in range(len(labels)):
        tooltip = mpld3.plugins.LineLabelTooltip(ax.get_lines()[i],
                                                 labels[i])
        mpld3.plugins.connect(plt.gcf(), tooltip)
    plt.grid(True)
    plt.title("Rarefaction curve")
    plt.ylabel("OTU count")
    plt.xlabel("number of sequences")
    with open(output_file_name, "w") as fout:
        fout.write(mpld3.fig_to_html(fig))


def draw_heatmap(input_file_name,
                 output_file_name):
    df = read_csv(input_file_name,
                  sep="\t",
                  skiprows=1,
                  header=None,
                  index_col=0)
    df.columns = df.index
    fig = heatmap(df, square=True, cmap="plasma").get_figure()
    fig.savefig(output_file_name)


def draw_tree(input_file_name,
              output_file_name):
    pylab.ion()
    tree = ph.read(input_file_name, "newick")
    ph.draw(tree)
    pylab.savefig(output_file_name)


def draw_scatter(input_file_name,
                 output_file_name):
    df = read_csv(input_file_name,
                  sep="\t")
    fig = lmplot(x="axis1",
                 y="axis2",
                 data=df,
                 hue="group",
                 fit_reg=False)
    fig.savefig(output_file_name)


def summary2html(input_file_name,
                 output_file_name,
                 css_link,
                 js_input_file_name):
    with open(js_input_file_name) as fin:
        js_str = fin.read()
    df = read_csv(input_file_name, sep="\t")
    html_df = df.to_html(classes=["compact",
                                  "hover",
                                  "order-column"],
                         index=False)
    html_str = "{0}{1}{2}".format(css_link,
                                  html_df,
                                  js_str)
    with open(output_file_name, "w") as fout:
        fout.write(html_str)


def get_daughter_df(df,
                    mother_taxon,
                    mother_rank,
                    tax_level):
    """
    Get pandas.DataFrame containing daughter taxa of passed mother taxon info.
    Based upon mothur's tax.summary file.

    Parameters:
    --------
    df: pandas.DataFrame
        pandas.DataFrame read from mothur's tax.summary file.
    mother_taxon: str
        Taxon of which daughter taxa will be in returned pandas.DataFrame.
    mother_rank: str
        Taxon rankID value of which daughter taxa will be in returned pandas.DataFrame.
    tax_level: int
        Taxon taxonomical level value of which daughter taxa will be in returned pandas.DataFrame.
    Returns
    -------
    pandas.DataFrame
        pandas.DataFrame containing daughter taxa.
    """
    sel_df = df[(df.taxon == mother_taxon) &
                (df.rankID == mother_rank) &
                (df.taxlevel == tax_level)]
    daughter_levels = int(sel_df.daughterlevels)
    if daughter_levels > 0:
        mother_rank = sel_df.rankID.to_string(index=False)
        daughter_df = df[df.rankID.str.contains(mother_rank)][df.rankID.str.len() == len(mother_rank) + 2]
        return daughter_df


def get_node_count(df,
                   node_taxon):
    groups = df.columns[5:]
    count_df = df[df.taxon == node_taxon][groups]
    count_vals = [int(count[i]) for i in count]
    return count_vals


def populate_node(node,
                  tax_level,
                  taxon_col="taxon",
                  rankID_col="rankID",
                  taxlevel_col="taxlevel"):
    """
    Populate input node with daughter taxa nodes.

    Parameters
    -------
    node: lxml.etree._Element
        Input node which will be populated with data selected with
        mothulity_draw.get_daughter_df.
    tax_level: int
        Taxon taxonomical level value of which daughter taxa will populate the input node.
    taxon_col: str
        Taxon column name in node's daughter pandas.DataFrame.
    rankID_col: str
        rank ID column name in node's daughter pandas.DataFrame.
    taxlevel_col: str
        Taxonomical level column name in node's daughter pandas.DataFrame.
    """
    node_tax_name = node.attrib["name"]
    node_rank = node.attrib["rankID"]
    children = get_daughter_df_2(tax_df,
                                 node_tax_name,
                                 node_rank,
                                 tax_level)
    if children is not None:
        for child in children.itertuples():
            et.SubElement(node,
                          "node",
                          name=getattr(child, taxon_col),
                          rankID=getattr(child, rankID_col),
                          taxlevel=getattr(child, taxlevel_col))


def main():
    parser = argparse.ArgumentParser(prog="mothulity_draw",
                                     usage="mothulity_draw [OPTION]",
                                     description="draws plots from\
                                     mothur-generated files.",
                                     version="0.9.4")
    parser.add_argument(action="store",
                        dest="input_file_name",
                        metavar="path/to/input_file",
                        default=".",
                        help="input file name. Default CWD.")
    parser.add_argument("--output",
                        dest="output_file_name",
                        default=None,
                        help="output file name")
    parser.add_argument("--rarefaction",
                        action="store_true",
                        dest="rarefaction",
                        default=False,
                        help="path/to/rarefaction-file. Use to draw rarefaction\
                        curves plot.")
    parser.add_argument("--phylip",
                        action="store_true",
                        dest="phylip",
                        default=False,
                        help="path/to/phylip-file. Use to draw heatmap and\
                        tree.")
    parser.add_argument("--tree",
                        action="store_true",
                        dest="tree",
                        default=False,
                        help="path/to/tree-file. Use to draw dendrogram.")
    parser.add_argument("--axes",
                        action="store_true",
                        dest="axes",
                        default=False,
                        help="path/to/axes-file. Use to draw scatter plots.")
    parser.add_argument("--summary-table",
                        action="store_true",
                        dest="summary_table",
                        help="/path/to/summary-table. Use to convert summary\
                        table into fancy DataTable.")
    parser.add_argument("--render-html",
                        action="store_true",
                        dest="render_html",
                        default=False,
                        help="path/to/html-template-file. Use to pass args into\
                        fancy html.")
    args = parser.parse_args()

    config_path_abs = get_dir_path("mothulity.config")
    config = ConfigParser.SafeConfigParser()
    config.read(config_path_abs)
    datatables_css = config.get("css", "datatables")
    datatables_js = get_dir_path(config.get("js", "datatables"))

    if args.rarefaction is True:
        draw_rarefaction(args.input_file_name, args.output_file_name)
    if args.phylip is True:
        draw_heatmap(args.input_file_name, args.output_file_name)
    if args.tree is True:
        draw_tree(args.input_file_name, args.output_file_name)
    if args.axes is True:
        draw_scatter(args.input_file_name, args.output_file_name)
    if args.summary_table is True:
        summary2html(args.input_file_name,
                     args.output_file_name,
                     datatables_css,
                     datatables_js)


if __name__ == '__main__':
    main()
