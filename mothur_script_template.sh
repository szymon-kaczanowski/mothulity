#!/bin/bash
#SBATCH --job-name="{{job_name}}"
#SBATCH --partition={{partition}}
#SBATCH --nodes={{nodes}}
#SBATCH --ntasks-per-node={{ntasks_per_node}}
#SBATCH --mem-per-cpu={{mem_per_cpu}}
{%if node_list != None%}
#SBATCH --nodelist={{node_list}}
{%endif%}

mothur '#set.current(processors={{processors}}); make.contigs(file={{job_name}}.files); summary.seqs(fasta=current); screen.seqs(fasta=current, contigsreport={{job_name}}.contigs.report, group=current, maxambig={{max_ambig}}, maxhomop={{max_homop}}, minlength={{min_length}}, maxlength={{max_length}}, minoverlap={{min_overlap}}); summary.seqs(fasta=current); unique.seqs(fasta=current); count.seqs(name=current, group=current); summary.seqs(fasta=current, count=current); align.seqs(fasta=current, reference=/home/dizak/db/Silva.nr_v119/silva.nr_v119.align); summary.seqs(fasta=current, count=current); screen.seqs(fasta=current, count=current, summary=current,  optimize=start-end, criteria={{screen_criteria}}); summary.seqs(fasta=current, count=current); filter.seqs(fasta=current, vertical=T, trump=.); unique.seqs(fasta=current, count=current); summary.seqs(fasta=current, count=current); pre.cluster(fasta=current, count=current, diffs={{precluster_diffs}}); chimera.uchime(fasta=current, count=current, dereplicate={{chimera_dereplicate}}); remove.seqs(fasta=current, accnos=current); summary.seqs(fasta=current, count=current); classify.seqs(fasta=current, count=current, reference=/home/dizak/db/Silva.nr_v119/silva.nr_v119.align, taxonomy=/home/dizak/db/Silva.nr_v119/silva.nr_v119.tax, cutoff={{classify_seqs_cutoff}}); get.groups(fasta={{job_name}}.trim.contigs.good.unique.good.filter.unique.precluster.pick.pick.fasta, count={{job_name}}.trim.contigs.good.unique.good.filter.unique.precluster.denovo.uchime.pick.pick.count_table, groups=Mock); seq.error(fasta={{job_name}}.trim.contigs.good.unique.good.filter.unique.precluster.pick.pick.pick.fasta, count={{job_name}}.trim.contigs.good.unique.good.filter.unique.precluster.denovo.uchime.pick.pick.pick.count_table, reference=HMP_MOCK.v35.fasta, aligned=F); dist.seqs(fasta={{job_name}}.trim.contigs.good.unique.good.filter.unique.precluster.pick.pick.pick.fasta, cutoff=0.20); cluster(column={{job_name}}.trim.contigs.good.unique.good.filter.unique.precluster.pick.pick.pick.dist, count={{job_name}}.trim.contigs.good.unique.good.filter.unique.precluster.denovo.uchime.pick.pick.pick.count_table); make.shared(list={{job_name}}.trim.contigs.good.unique.good.filter.unique.precluster.pick.pick.pick.an.unique_list.list, count={{job_name}}.trim.contigs.good.unique.good.filter.unique.precluster.denovo.uchime.pick.pick.pick.count_table, label=0.03); rarefaction.single(shared={{job_name}}.trim.contigs.good.unique.good.filter.unique.precluster.pick.pick.pick.an.unique_list.shared); remove.lineage(fasta=current, count=current, taxonomy=current, taxon=Chloroplast-Mitochondria-Eukaryota-unknown-Unknown); remove.groups(fasta=current, count=current, taxonomy=current, groups=Mock); cluster.split(fasta=current, count=current, taxonomy=current, splitmethod=classify, taxlevel=4, cutoff={{cluster_cutoff}}); make.shared(list=current, count=current, label=0.03); classify.otu(list=current, count=current, taxonomy=current, label=0.03); count.groups(shared=current)'