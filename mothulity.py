#! /usr/bin/env python


import jinja2 as jj2
import argparse
import requests as rq
from tqdm import tqdm
import os
import sys
import glob


__author__ = "Dariusz Izak IBB PAS"
__version = "0.9.7"


def get_dir_path(file_name=""):
    """
    Find out what is the script system path and return its location. Optionally
    put desired file name at the end of the path. Facilitates access to files
    stored in the same directory as executed script. Requires the executed
    script being added to the system path
    Parameters
    --------
    file_name: str, default <"">
        File name to put at the end of the path. Use empty string if want just
        the directory.
    Returns
    --------
    str
        System path of the executable.
    Examples
    -------
    >>> get_dir_path()
    '/home/user/program/bin/'
    >>> get_dir_path("foo")
    '/home/user/program/bin/foo'
    """
    prog_path = sys.argv[0].replace(sys.argv[0].split("/")[-1],
                                    file_name)
    return prog_path


def load_template_str(template_str):
    template = jj2.Environment().from_string(template_str)
    return template


def load_template_file(template_file):
    template_Loader = jj2.FileSystemLoader(searchpath="/")
    template_Env = jj2.Environment(loader=template_Loader)
    template = template_Env.get_template(template_file)
    return template


def render_template(template_loaded,
                    files_directory=".",
                    output_dir=".",
                    job_name="mothur.job",
                    run=None,
                    partition="long",
                    nodes=1,
                    ntasks_per_node=6,
                    mem_per_cpu=24,
                    node_list=None,
                    processors=24,
                    max_ambig=0,
                    max_homop=8,
                    min_length=None,
                    max_length=None,
                    min_overlap=25,
                    screen_criteria=95,
                    chop_length=250,
                    precluster_diffs=2,
                    chimera_dereplicate="T",
                    classify_seqs_cutoff=80,
                    classify_ITS=False,
                    align_database=None,
                    taxonomy_database=None,
                    cluster_cutoff=0.15,
                    full_ram_load=False,
                    label=0.03,
                    junk_grps=None,
                    notify_email=None,
                    sampl_num=None):
    mem_per_cpu = "{0}G".format(mem_per_cpu)
    template_vars = {"files_directory": files_directory,
                     "output_dir": output_dir,
                     "job_name": job_name,
                     "run": run,
                     "partition": partition,
                     "nodes": nodes,
                     "ntasks_per_node": ntasks_per_node,
                     "mem_per_cpu": mem_per_cpu,
                     "node_list": node_list,
                     "processors": processors,
                     "max_ambig": max_ambig,
                     "max_homop": max_homop,
                     "min_length": min_length,
                     "max_length": max_length,
                     "min_overlap": min_overlap,
                     "screen_criteria": screen_criteria,
                     "chop_length": chop_length,
                     "precluster_diffs": precluster_diffs,
                     "chimera_dereplicate": chimera_dereplicate,
                     "classify_seqs_cutoff": classify_seqs_cutoff,
                     "classify_ITS": classify_ITS,
                     "align_database": align_database,
                     "taxonomy_database": taxonomy_database,
                     "cluster_cutoff": cluster_cutoff,
                     "full_ram_load": full_ram_load,
                     "label": label,
                     "junk_grps": junk_grps,
                     "notify_email": notify_email,
                     "sampl_num": sampl_num}
    template_rendered = template_loaded.render(template_vars)
    return template_rendered


def save_template(out_file_name,
                  template_rendered):
    with open(out_file_name, "w") as fout:
        fout.write(template_rendered)


def save_template(out_file_name,
                  template_rendered):
    with open(out_file_name, "w") as fout:
        fout.write(template_rendered)


def read_label_from_file(file_glob):
    for i in glob.glob(file_glob):
        for ii in i.split("."):
            try:
                temp_label = float("0.{0}".format(ii))
                if len(str(temp_label)) > 3:
                    return temp_label
                else:
                    pass
            except:
                pass


def read_sampl_num(files_file):
    with open(files_file) as fin:
        lines_num = len(fin.readlines())
    return lines_num


def read_count_from_log(log_file,
                        keyword="contains",
                        strip_char=".\n",
                        threshold=100):
    log_file = str(glob.glob(log_file)[0])
    with open(log_file) as fin:
        log = fin.readlines()
    log_list = [i.strip(strip_char) for i in log if keyword in i]
    log_split_list = [i.split(" {0} ".format(keyword)) for i in log_list]
    log_dict = {i[0]: i[1] for i in log_split_list}
    groups2remove = "".join([k for k, v in log_dict.items() if int(v) < 100])
    return groups2remove


def main():
    parser = argparse.ArgumentParser(prog="mothulity",
                                     usage="mothulity [OPTION]",
                                     description="creates headnode-suitable\
                                     mothur script",
                                     version="0.9.4")
    headnode = parser.add_argument_group("headnode options")
    mothur = parser.add_argument_group("mothur options")
    parser.add_argument(action="store",
                        dest="files_directory",
                        metavar="path/to/files",
                        default=".",
                        help="input directory path. It is used as working\
                        directory for the job. Default CWD.")
    parser.add_argument("-n",
                        "--job-name",
                        action="store",
                        dest="job_name",
                        metavar="",
                        default="mothur.job",
                        help="job name. Used for naming scripts, queued job\
                        and html output. Default <mothur.job>.")
    parser.add_argument("-d",
                        "--output-dir",
                        action="store",
                        dest="output_dir",
                        metavar=".",
                        default=".",
                        help="output directory path for script. It is NOT\
                        output directory for actual job.")
    parser.add_argument("-r",
                        "--run",
                        action="store",
                        dest="run",
                        metavar="",
                        default=None,
                        help="shell call. Use if you want to run the mothur\
                        script immediately, in current directory. eg -r sh for\
                         regular bash or -r sbatch for slurm.")
    parser.add_argument("-a",
                        "--analysis-only",
                        action="store_true",
                        dest="analysis_only",
                        default=False,
                        help="outputs just the part involved in statistical\
                        analysis and drawing.")
    parser.add_argument("-t",
                        "--template",
                        action="store",
                        dest="template_file_name",
                        metavar="",
                        default=None,
                        help="path/to/template. Use if you want to use other\
                        template than default.")
    parser.add_argument("--render-html",
                        action="store_true",
                        dest="render_html",
                        default=False,
                        help="path/to/html-template-file. Use to pass args into\
                        fancy html.")
    parser.add_argument("--notify-email",
                        action="store",
                        dest="notify_email",
                        metavar="",
                        default=None,
                        help="email address you want to notify when job is\
                        done.")
    headnode.add_argument("--partition",
                          action="store",
                          dest="partition",
                          metavar="",
                          default="long",
                          help="headnode's partition. Values: test, short, big,\
                          long, accel. Accel necessary for phi/gpu nodes\
                          Default <long>.")
    headnode.add_argument("--nodes",
                          action="store",
                          dest="nodes",
                          metavar="",
                          default=1,
                          help="number of nodes. Default: <1>.")
    headnode.add_argument("--ntasks-per-node",
                          action="store",
                          dest="ntasks_per_node",
                          metavar="",
                          default=6,
                          help="number of tasks to invoke on each node.\
                          Default <6>")
    headnode.add_argument("--mem-per-cpu",
                          action="store",
                          dest="mem_per_cpu",
                          metavar="",
                          default=24,
                          help="maximum amount of real memory per node in\
                          gigabytes. Default <24>.")
    headnode.add_argument("--node-list",
                          action="store",
                          dest="node_list",
                          metavar="",
                          default=None,
                          help="request a specific list of nodes")
    headnode.add_argument("--processors",
                          action="store",
                          dest="processors",
                          metavar="",
                          default=24,
                          help="number of logical processors. Default: <24>")
    headnode.add_argument("--resources",
                          action="store",
                          dest="resources",
                          metavar="",
                          default=None,
                          help="shortcut for headnode's resources reservation.\
                          Accepted values are: <S>mall, <M>edium, <L>arge,\
                          <XL>arge for regular nodes with mpi. <PHI> for\
                          single phi node, <JUMBO> for two phi nodes.\
                          Overrides all the other headnode arguments. Use if\
                          you are lazy.")
    mothur.add_argument("--max-ambig",
                        action="store",
                        dest="max_ambig",
                        metavar="",
                        default=0,
                        help="maximum number of ambiguous bases allowed.\
                        screen.seqs param. Default <0>.")
    mothur.add_argument("--max-homop",
                        action="store",
                        dest="max_homop",
                        metavar="",
                        default=8,
                        help="maximum number of homopolymers allowed.\
                        screen.seqs param. Default <8>.")
    mothur.add_argument("--min-length",
                        action="store",
                        dest="min_length",
                        metavar="",
                        default=None,
                        help="minimum length of read allowed.\
                        screen.seqs param. Default <400>.")
    mothur.add_argument("--max-length",
                        action="store",
                        dest="max_length",
                        metavar="",
                        default=None,
                        help="minimum length of read allowed.\
                        screen.seqs param. Default <500>.")
    mothur.add_argument("--min-overlap",
                        action="store",
                        dest="min_overlap",
                        metavar="",
                        default=25,
                        help="minimum number of bases overlap in contig.\
                        screen.seqs param. Default <25>.")
    mothur.add_argument("--screen-criteria",
                        action="store",
                        dest="screen_criteria",
                        metavar="",
                        default=95,
                        help="trim start and end of read to fit this\
                        percentage of all reads.\
                        screen.seqs param. Default <95>.")
    mothur.add_argument("--chop-length",
                        action="store",
                        dest="chop_length",
                        metavar="",
                        default=250,
                        help="cut all the reads to this length. Keeps front\
                        of the sequences. chop.seqs argument.\
                        Default <250>")
    mothur.add_argument("--precluster-diffs",
                        action="store",
                        dest="precluster_diffs",
                        metavar="",
                        default=2,
                        help="number of differences between reads treated as\
                        insignificant. screen.seqs param. Default <2>.")
    mothur.add_argument("--chimera-dereplicate",
                        action="store",
                        dest="chimera_dereplicate",
                        metavar="",
                        default="T",
                        help="checking for chimeras by group. chimera.uchime\
                        param. Default <T>.")
    mothur.add_argument("--classify-seqs-cutoff",
                        action="store",
                        dest="classify_seqs_cutoff",
                        metavar="",
                        default=80,
                        help="bootstrap value for taxonomic assignment.\
                        classify.seqs param. Default <80>.")
    mothur.add_argument("--classify-ITS",
                        action="store_true",
                        dest="classify_ITS",
                        default=False,
                        help="removes align.seqs step and modifies\
                        classify.seqs with <method=knn>,\
                                           <search=blast>,\
                                           <match=2>,\
                                           <mismatch=-2>,\
                                           <gapopen=-2>,\
                                           <gapextend=-1>,\
                                           <numwanted=1>).\
                        Default <False>")
    mothur.add_argument("--align-database",
                        action="store",
                        dest="align_database",
                        metavar="",
                        default="~/db/Silva.nr_v119/silva.nr_v119.align",
                        help="path/to/align-database. Used by align.seqs\
                        command as <reference> argument. Default\
                        <~/db/Silva.nr_v119/silva.nr_v119.align>.")
    mothur.add_argument("--taxonomy-database",
                        action="store",
                        dest="taxonomy_database",
                        metavar="",
                        default="~/db/Silva.nr_v119/silva.nr_v119.tax",
                        help="path/to/taxonomy-database. Used by\
                        classify.seqs as <taxonomy> argument.\
                        Default <~/db/Silva.nr_v119/silva.nr_v119.tax>")
    mothur.add_argument("--cluster-cutoff",
                        action="store",
                        dest="cluster_cutoff",
                        metavar="",
                        default=0.15,
                        help="cutoff value. Smaller == faster cluster param.\
                        Default <0.15>.")
    mothur.add_argument("--full-ram-load",
                        action="store_true",
                        dest="full_ram_load",
                        default=False,
                        help="Use if you want to use cluster command instead\
                        of cluster.split.")
    mothur.add_argument("--label",
                        action="store",
                        dest="label",
                        metavar="",
                        default=0.03,
                        help="label argument for number of commands for OTU\
                        analysis approach. Default 0.03.")
    mothur.add_argument("--remove-below",
                        action="store",
                        dest="remove_below",
                        metavar="",
                        default=None,
                        help="remove groups below this threshold. Omit this\
                        argument if you want to keep them all.")
    args = parser.parse_args()

    files_directory_abs = "{0}/".format(os.path.abspath(args.files_directory))
    output_dir_abs = "{0}/".format(os.path.abspath(args.output_dir))
    if args.render_html is True:
        html_template_path = get_dir_path("output_template.html")
        html_output_name = "{0}.html".format(args.job_name)
        loaded_template = load_template_file(html_template_path)
        rendered_template = render_template(loaded_template,
                                            files_directory=files_directory_abs,
                                            job_name=args.job_name,
                                            partition=args.partition,
                                            nodes=args.nodes,
                                            ntasks_per_node=args.ntasks_per_node,
                                            mem_per_cpu=args.mem_per_cpu,
                                            node_list=args.node_list,
                                            processors=args.processors,
                                            max_ambig=args.max_ambig,
                                            max_homop=args.max_homop,
                                            min_length=args.min_length,
                                            max_length=args.max_length,
                                            min_overlap=args.min_overlap,
                                            screen_criteria=args.screen_criteria,
                                            chop_length=args.chop_length,
                                            precluster_diffs=args.precluster_diffs,
                                            chimera_dereplicate=args.chimera_dereplicate,
                                            classify_seqs_cutoff=args.classify_seqs_cutoff,
                                            classify_ITS=args.classify_ITS,
                                            align_database=args.align_database,
                                            taxonomy_database=args.taxonomy_database,
                                            cluster_cutoff=args.cluster_cutoff,
                                            label=args.label)
        save_template(html_output_name,
                      rendered_template)
        quit()
    else:
        pass
    if args.template_file_name is not None:
        loaded_template = load_template_file(args.template_file_name)
    else:
        pass
    if args.analysis_only is True:
        label = read_label_from_file("{0}*cons.taxonomy".format(files_directory_abs))
        sampl_num = read_sampl_num("{0}*files".format(files_directory_abs))
        if args.remove_below is not None:
            junk_grps = read_count_from_log("{0}*logfile".format(files_directory_abs),
                                            threshold=args.remove_below)
        else:
            junk_grps = None
        loaded_template = load_template_file(get_dir_path("analysis_template.sh.j2"))
    else:
        label = args.label
        junk_grps = None
        loaded_template = load_template_file(get_dir_path("preproc_template.sh.j2"))
    if args.resources is not None:
        node_list = None
        resources = args.resources.upper()
        if resources == "S":
            partition = "long"
            nodes = 2
            ntasks_per_node = 6
            mem_per_cpu = 24
            processors = 48
        elif resources == "M":
            partition = "long"
            nodes = 10
            ntasks_per_node = 6
            mem_per_cpu = 24
            processors = 240
        elif resources == "L":
            partition = "long"
            nodes = 20
            ntasks_per_node = 6
            mem_per_cpu = 24
            processors = 480
        elif resources == "XL":
            partition = "long"
            nodes = 40
            ntasks_per_node = 6
            mem_per_cpu = 24
            processors = 960
        elif resources == "PHI":
            partition = "accel"
            nodes = 1
            ntasks_per_node = 16
            mem_per_cpu = 128
            processors = 32
        elif resources == "JUMBO":
            partition = "accel"
            nodes = 4
            ntasks_per_node = 16
            mem_per_cpu = 128
            processors = 128
        else:
            pass
    else:
        nodes = args.nodes
        node_list = args.node_list
        ntasks_per_node = args.ntasks_per_node
        mem_per_cpu = args.mem_per_cpu
        processors = args.processors
        partition = args.partition
    rendered_template = render_template(loaded_template,
                                        files_directory=files_directory_abs,
                                        output_dir=output_dir_abs,
                                        job_name=args.job_name,
                                        run=args.run,
                                        partition=partition,
                                        nodes=nodes,
                                        ntasks_per_node=ntasks_per_node,
                                        mem_per_cpu=mem_per_cpu,
                                        node_list=node_list,
                                        processors=processors,
                                        max_ambig=args.max_ambig,
                                        max_homop=args.max_homop,
                                        min_length=args.min_length,
                                        max_length=args.max_length,
                                        min_overlap=args.min_overlap,
                                        screen_criteria=args.screen_criteria,
                                        chop_length=args.chop_length,
                                        precluster_diffs=args.precluster_diffs,
                                        chimera_dereplicate=args.chimera_dereplicate,
                                        classify_seqs_cutoff=args.classify_seqs_cutoff,
                                        classify_ITS=args.classify_ITS,
                                        align_database=args.align_database,
                                        taxonomy_database=args.taxonomy_database,
                                        cluster_cutoff=args.cluster_cutoff,
                                        full_ram_load=args.full_ram_load,
                                        label=label,
                                        junk_grps=junk_grps,
                                        notify_email=args.notify_email,
                                        sampl_num=sampl_num)
    save_template("{0}{1}.sh".format(output_dir_abs,
                                     args.job_name),
                  rendered_template)
    if args.run is not None:
        os.system("{0} {1}".format(args.run, "{0}{1}.sh".format(output_dir_abs,
                                                                args.job_name)))
    else:
        pass


if __name__ == "__main__":
    main()
