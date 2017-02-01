#! /usr/bin/env python


import os
import argparse
import pandas as pd


__author__ = "Dariusz Izak IBB PAS"


def names_sanitizer(unwanted_sign,
                    files_directory):
    for i in os.listdir(files_directory):
        if unwanted_sign in i:
            os.rename("{0}/{1}".format(files_directory,
                                       i),
                      "{0}/{1}".format(files_directory,
                                       i.replace(unwanted_sign, "")))


def left_n_right_generator(files_directory,
                           split_sign,
                           files_extension,
                           left_reads_sign,
                           right_reads_sign):
    left_name_reads_list = []
    right_name_reads_list = []
    files_list = os.listdir(files_directory)
    files_list = [i for i in files_list if files_extension == i.split(".")[-1]]
    sample_names_list = [i.split(split_sign)[0] for i in files_list]
    sample_names_list = list(set(sample_names_list))
    for i in sample_names_list:
        for ii in files_list:
            if i == ii.split(split_sign)[0] and left_reads_sign in ii:
                left_name_reads_list.append({"name": i, "left_reads": ii})
            elif i == ii.split(split_sign)[0] and right_reads_sign in ii:
                right_name_reads_list.append({"name": i, "right_reads": ii})
            else:
                pass
    name_reads = {"left": left_name_reads_list,
                  "right": right_name_reads_list}
    return name_reads


def main():
    parser = argparse.ArgumentParser(prog="mothur_files_creator",
                                     usage="mothur_files_creator [directory] [OPTION]",
                                     description="creates mothur-suitable\
                                                    <.files> file just upon the\
                                                    input file names. Removes\
                                                    <-> from file names",
                                     version="1.0.1")
    parser.add_argument(action="store",
                        dest="files_directory",
                        metavar="path/to/files",
                        help="input directory path.")
    parser.add_argument("-o",
                        "--output",
                        action="store",
                        dest="output_file_name",
                        metavar="",
                        default="mothur.files",
                        help="output file name. Default <mothur.files>")
    parser.add_argument("-s",
                        "--split-sign",
                        action="store",
                        dest="split_sign",
                        metavar="",
                        default="_",
                        help="first group of characters before this sign is\
                                recognized as sample name. Default <_>")
    parser.add_argument("-e",
                        "--files-extension",
                        action="store",
                        dest="files_extension",
                        metavar="",
                        default="fastq",
                        help="reads files are recognized by this. Default\
                                <fastq>")
    parser.add_argument("-l",
                        "--left-reads-sign",
                        action="store",
                        dest="left_reads_sign",
                        metavar="",
                        default="R1",
                        help="left reads files are recognized by this.\
                                Default <R1>")
    parser.add_argument("-r",
                        "--right-reads-sign",
                        action="store",
                        dest="right_reads_sign",
                        metavar="",
                        default="R2",
                        help="right reads files are recognized by this.\
                                Default <R2>")
    parser.add_argument("--original-names",
                        action="store_true",
                        dest="original_names",
                        default=False,
                        help="use if you do not want to modify file names")
    args = parser.parse_args()

    if args.original_names is False:
        names_sanitizer("-",
                        args.files_directory)
    else:
        pass
    left_n_right = left_n_right_generator(args.files_directory,
                                          args.split_sign,
                                          args.files_extension,
                                          args.left_reads_sign,
                                          args.right_reads_sign)
    files_dataframe = pd.merge(left=pd.DataFrame(left_n_right["left"]),
                               right=pd.DataFrame(left_n_right["right"]),
                               on="name")
    files_dataframe[["name", "left_reads", "right_reads"]].to_csv(args.output_file_name,
                                                                  sep="\t",
                                                                  index=False,
                                                                  header=False)

if __name__ == "__main__":
    main()