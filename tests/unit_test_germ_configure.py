# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 13:18:34 2016

@author: okada

"""

import os
import sys
import shutil
import unittest
import subprocess
import snakemake

def func_path (root, name):
    wdir = root + "/" + name
    ss_path = root + "/" + name + ".csv"
    return (wdir, ss_path)

BAM_IMP = "bam-import"
BAM_2FQ = "bam-tofastq"
ALN = "bwa-alignment-parabricks"
HT_CALL = "gatk-haplotypecaller-parabricks"
SUMMARY1 = "gatk-collect-wgs-metrics"
SUMMARY2 = "gatk-collect-multiple-metrics"

class ConfigureTest(unittest.TestCase):
    
    DATA_DIR = "/tmp/temp-test/gcat_test_germ_configure"
    SAMPLE_DIR = DATA_DIR + "/samples"
    REMOVE = False
    SS_NAME = "/test.csv"
    GC_NAME = "/gcat.cfg"
    GC_NAME_P = "/gcat_parabricks.cfg"

    # init class
    @classmethod
    def setUpClass(self):
        if os.path.exists(self.DATA_DIR):
            shutil.rmtree(self.DATA_DIR)
        os.makedirs(self.SAMPLE_DIR, exist_ok = True)
        os.makedirs(self.DATA_DIR + "/reference", exist_ok = True)
        os.makedirs(self.DATA_DIR + "/image", exist_ok = True)
        os.makedirs(self.DATA_DIR + "/parabricks", exist_ok = True)
        touch_files = [
            "/samples/A1.fastq",
            "/samples/A2.fastq",
            "/samples/B1.fq",
            "/samples/B2.fq",
            "/samples/C1_1.fq",
            "/samples/C1_2.fq",
            "/samples/C2_1.fq",
            "/samples/C2_2.fq",
            "/samples/A.markdup.cram",
            "/samples/A.markdup.cram.crai",
            "/samples/B.markdup.cram",
            "/samples/B.markdup.crai",
            "/reference/XXX.fa",
            "/image/YYY.simg",
            "/parabricks/pbrun"
        ]
        for p in touch_files:
            open(self.DATA_DIR + p, "w").close()
        
        data_sample = """[fastq]
A_tumor,{sample_dir}/A1.fastq,{sample_dir}/A2.fastq
pool1,{sample_dir}/B1.fq,{sample_dir}/B2.fq
pool2,{sample_dir}/C1_1.fq;{sample_dir}/C1_2.fq,{sample_dir}/C2_1.fq;{sample_dir}/C2_2.fq

[{bam2fq}]
A_control,{sample_dir}/A.markdup.cram

[{bamimp}]
pool3,{sample_dir}/B.markdup.cram

[{ht_call}]
A_tumor
A_control
pool1
pool2
pool3

[manta]
A_tumor

[melt]
A_tumor

[gridss]
A_tumor
""".format(sample_dir = self.SAMPLE_DIR, bam2fq = BAM_2FQ, bamimp = BAM_IMP, ht_call = HT_CALL)
        
        f = open(self.DATA_DIR + self.SS_NAME, "w")
        f.write(data_sample)
        f.close()

        conf_template = """[{bam2fq}]
qsub_option = -l s_vmem=2G,mem_req=2G -l os7
image = {sample_dir}/image/YYY.simg
singularity_option = 
params = collate=1 exclude=QCFAIL,SECONDARY,SUPPLEMENTARY tryoq=0

[{aln}-compatible]
qsub_option = -l s_vmem=10.6G,mem_req=10.6G -l os7
image = {sample_dir}/image/YYY.simg
singularity_option = 
bwa_option = -t 8 -K 10000000 -T 0
read_group_pl = na
read_group_lb = ILLUMINA 
read_group_pu = na
gatk_jar = /tools/gatk-4.0.4.0/gatk-package-4.0.4.0-local.jar
gatk_sort_option = --MAX_RECORDS_IN_RAM=5000000
gatk_sort_java_option = -XX:-UseContainerSupport -Xmx32g 
gatk_markdup_option =
gatk_markdup_java_option = -XX:-UseContainerSupport -Xmx32g 
samtools_view_option = -@ 8
samtools_index_option = -@ 8
reference = {sample_dir}/reference/XXX.fa

[{aln}]
gpu_support = {gpu_support}
pbrun = {sample_dir}/parabricks/pbrun
qsub_option = -l s_vmem=10.6G,mem_req=10.6G -l os7
bwa_option = -t 8 -K 10000000 -T 0
read_group_pl = na
read_group_lb = ILLUMINA 
read_group_pu = na
reference = {sample_dir}/reference/XXX.fa

[post-{aln}]
qsub_option = -l s_vmem=10.6G,mem_req=10.6G -l os7
image = {sample_dir}/image/YYY.simg
singularity_option = 
gatk_jar = /tools/gatk-4.0.4.0/gatk-package-4.0.4.0-local.jar
gatk_markdup_option =
gatk_markdup_java_option = -XX:-UseContainerSupport -Xmx32g 
samtools_view_option = -@ 8
samtools_index_option = -@ 8
reference = {sample_dir}/reference/XXX.fa

[{ht_call}-compatible]
qsub_option = -l s_vmem=5.3G,mem_req=5.3G -l os7
image = {sample_dir}/image/YYY.simg
singularity_option = 
gatk_jar = /tools/gatk-4.0.4.0/gatk-package-4.0.4.0-local.jar
haplotype_option = --native-pair-hmm-threads=8
haplotype_java_option = -XX:-UseContainerSupport -Xmx32g
reference = {sample_dir}/reference/XXX.fa

[{ht_call}]
gpu_support = {gpu_support}
pbrun = {sample_dir}/parabricks/pbrun
qsub_option = -l s_vmem=5.3G,mem_req=5.3G -l os7
haplotype_option = --native-pair-hmm-threads=8
reference = {sample_dir}/reference/XXX.fa

[{summary1}]
qsub_option = -l s_vmem=32G,mem_req=32G
image = {sample_dir}/image/YYY.simg
singularity_option = 
gatk_jar = /gatk/gatk.jar
wgs_metrics_option =
wgs_metrics_java_option = -XX:-UseContainerSupport -Xmx24g
reference = {sample_dir}/reference/XXX.fa

[{summary2}]
qsub_option = -l s_vmem=32G,mem_req=32G
image = {sample_dir}/image/YYY.simg
singularity_option = 
gatk_jar = /gatk/gatk.jar
multiple_metrics_option =
multiple_metrics_java_option = -XX:-UseContainerSupport -Xmx24g
reference = {sample_dir}/reference/XXX.fa

[gridss]
qsub_option = -l s_vmem=4G,mem_req=4G -pe def_slot 8
image = {sample_dir}/image/YYY.simg
singularity_option =
reference = {sample_dir}/reference/XXX.fa
gridss_option = --picardoptions VALIDATION_STRINGENCY=LENIENT -t 8
gridss_jar = gridss-2.8.0-gridss-jar-with-dependencies.jar
samtools_option = -@ 8

[manta]
qsub_option = -l s_vmem=2G,mem_req=2G -pe def_slot 8
image = {sample_dir}/image/YYY.simg
singularity_option =
reference = {sample_dir}/reference/XXX.fa
manta_config_option = 
manta_workflow_option = -m local -j 8

[melt]
qsub_option = -l s_vmem=32G,mem_req=32G
image = {sample_dir}/image/YYY.simg
singularity_option =

reference = {sample_dir}/reference/XXX.fa
melt_jar = /MELTv2.2.0/MELT.jar
melt_bed = /MELTv2.2.0/add_bed_files/Hg38/Hg38.genes.bed 
melt_refs = /MELTv2.2.0/me_refs/Hg38
melt_option =
melt_java_option = -XX:-UseContainerSupport -Xmx32g
"""
        # Not parabricks
        data_conf = conf_template.format(
            sample_dir = self.DATA_DIR, 
            bam2fq = BAM_2FQ, aln = ALN, ht_call = HT_CALL, summary1 = SUMMARY1, summary2 = SUMMARY2,
            gpu_support = "False"
        )
        
        f = open(self.DATA_DIR + self.GC_NAME, "w")
        f.write(data_conf)
        f.close()
        
        # parabricks
        data_conf2 = conf_template.format(
            sample_dir = self.DATA_DIR, 
            bam2fq = BAM_2FQ, aln = ALN, ht_call = HT_CALL, summary1 = SUMMARY1, summary2 = SUMMARY2,
            gpu_support = "True"
        )
        
        f = open(self.DATA_DIR + self.GC_NAME_P, "w")
        f.write(data_conf2)
        f.close()
        
    # terminated class
    @classmethod
    def tearDownClass(self):
        if self.REMOVE:
            shutil.rmtree(self.DATA_DIR)

    # init method
    def setUp(self):
        pass

    # terminated method
    def tearDown(self):
        pass
    
    def test1_01_version(self):
        subprocess.check_call(['python', 'gcat_workflow', '--version'])
    
    def test1_02_version(self):
        subprocess.check_call(['python', 'gcat_runner', '--version'])
    
    def test2_01_configure_drmaa_nogpu(self):
        (wdir, ss_path) = func_path (self.DATA_DIR, sys._getframe().f_code.co_name)
        options = [
            "germ",
            self.DATA_DIR + self.SS_NAME,
            wdir,
            self.DATA_DIR + self.GC_NAME,
        ]
        subprocess.check_call(['python', 'gcat_workflow'] + options)
        success = snakemake.snakemake(wdir + '/snakefile', workdir = wdir, dryrun = True)
        self.assertTrue(success)

    def test2_02_configure_nodramaa_nogpu(self):
        (wdir, ss_path) = func_path (self.DATA_DIR, sys._getframe().f_code.co_name)
        options = [
            "germ",
            self.DATA_DIR + self.SS_NAME,
            wdir,
            self.DATA_DIR + self.GC_NAME,
            "--disable_drmaa",
        ]
        subprocess.check_call(['python', 'gcat_workflow'] + options)
        success = snakemake.snakemake(wdir + '/snakefile', workdir = wdir, dryrun = True)
        self.assertTrue(success)
    
    def test2_03_configure_drmaa_gpu(self):
        (wdir, ss_path) = func_path (self.DATA_DIR, sys._getframe().f_code.co_name)
        options = [
            "germ",
            self.DATA_DIR + self.SS_NAME,
            wdir,
            self.DATA_DIR + self.GC_NAME_P,
        ]
        subprocess.check_call(['python', 'gcat_workflow'] + options)
        success = snakemake.snakemake(wdir + '/snakefile', workdir = wdir, dryrun = True)
        self.assertTrue(success)

    def test2_04_configure_nodrmaa_gpu(self):
        (wdir, ss_path) = func_path (self.DATA_DIR, sys._getframe().f_code.co_name)
        options = [
            "germ",
            self.DATA_DIR + self.SS_NAME,
            wdir,
            self.DATA_DIR + self.GC_NAME_P,
            "--disable_drmaa",
        ]
        subprocess.check_call(['python', 'gcat_workflow'] + options)
        success = snakemake.snakemake(wdir + '/snakefile', workdir = wdir, dryrun = True)
        self.assertTrue(success)


    def test3_01_bwa_limited(self):
        (wdir, ss_path) = func_path (self.DATA_DIR, sys._getframe().f_code.co_name)
        
        data_sample = """[fastq]
A_tumor,{sample_dir}/A1.fastq,{sample_dir}/A2.fastq
""".format(sample_dir = self.SAMPLE_DIR)
        
        f = open(ss_path, "w")
        f.write(data_sample)
        f.close()
        options = [
            "germ",
            ss_path,
            wdir,
            self.DATA_DIR + self.GC_NAME,
        ]
        subprocess.check_call(['python', 'gcat_workflow'] + options)
        success = snakemake.snakemake(wdir + '/snakefile', workdir = wdir, dryrun = True)
        self.assertTrue(success)

    def test3_02_1_bwa_limited(self):
        (wdir, ss_path) = func_path (self.DATA_DIR, sys._getframe().f_code.co_name)
        
        data_sample = """[{bam2fq}]
A_tumor,{sample_dir}/A.markdup.cram
""".format(sample_dir = self.SAMPLE_DIR, bam2fq = BAM_2FQ)
        
        f = open(ss_path, "w")
        f.write(data_sample)
        f.close()
        options = [
            "germ",
            ss_path,
            wdir,
            self.DATA_DIR + self.GC_NAME,
        ]
        subprocess.check_call(['python', 'gcat_workflow'] + options)
        success = snakemake.snakemake(wdir + '/snakefile', workdir = wdir, dryrun = True)
        self.assertTrue(success)

    def test3_03_bwa_limited(self):
        (wdir, ss_path) = func_path (self.DATA_DIR, sys._getframe().f_code.co_name)
        
        data_sample = """[{bamimp}]
A_tumor,{sample_dir}/A.markdup.cram
""".format(sample_dir = self.SAMPLE_DIR, bamimp = BAM_IMP)
        
        f = open(ss_path, "w")
        f.write(data_sample)
        f.close()
        options = [
            "germ",
            ss_path,
            wdir,
            self.DATA_DIR + self.GC_NAME,
        ]
        subprocess.check_call(['python', 'gcat_workflow'] + options)
        success = snakemake.snakemake(wdir + '/snakefile', workdir = wdir, dryrun = True)
        self.assertTrue(success)

    def test4_01_htc_limited(self):
        (wdir, ss_path) = func_path (self.DATA_DIR, sys._getframe().f_code.co_name)
        
        data_sample = """[fastq]
A_tumor,{sample_dir}/A1.fastq,{sample_dir}/A2.fastq
[{ht_call}]
A_tumor
""".format(sample_dir = self.SAMPLE_DIR, ht_call = HT_CALL)
        
        f = open(ss_path, "w")
        f.write(data_sample)
        f.close()
        options = [
            "germ",
            ss_path,
            wdir,
            self.DATA_DIR + self.GC_NAME,
        ]
        subprocess.check_call(['python', 'gcat_workflow'] + options)
        success = snakemake.snakemake(wdir + '/snakefile', workdir = wdir, dryrun = True)
        self.assertTrue(success)

    def test4_02_htc_limited(self):
        (wdir, ss_path) = func_path (self.DATA_DIR, sys._getframe().f_code.co_name)
        
        data_sample = """[{bam2fq}]
A_tumor,{sample_dir}/A.markdup.cram
[{ht_call}]
A_tumor
""".format(sample_dir = self.SAMPLE_DIR, bam2fq = BAM_2FQ, ht_call = HT_CALL)
        
        f = open(ss_path, "w")
        f.write(data_sample)
        f.close()
        options = [
            "germ",
            ss_path,
            wdir,
            self.DATA_DIR + self.GC_NAME,
        ]
        subprocess.check_call(['python', 'gcat_workflow'] + options)
        success = snakemake.snakemake(wdir + '/snakefile', workdir = wdir, dryrun = True)
        self.assertTrue(success)

    def test4_03_htc_limited(self):
        (wdir, ss_path) = func_path (self.DATA_DIR, sys._getframe().f_code.co_name)
        
        data_sample = """[{bamimp}]
A_tumor,{sample_dir}/A.markdup.cram
[{ht_call}]
A_tumor
""".format(sample_dir = self.SAMPLE_DIR, bamimp = BAM_IMP, ht_call = HT_CALL)
        
        f = open(ss_path, "w")
        f.write(data_sample)
        f.close()
        options = [
            "germ",
            ss_path,
            wdir,
            self.DATA_DIR + self.GC_NAME,
        ]
        subprocess.check_call(['python', 'gcat_workflow'] + options)
        success = snakemake.snakemake(wdir + '/snakefile', workdir = wdir, dryrun = True)
        self.assertTrue(success)


if __name__ == '__main__':
    unittest.main()
