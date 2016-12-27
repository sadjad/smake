#!/usr/bin/env python2

from __future__ import print_function

import sys

Y4M_DOWNLOAD = "curl https://s3-us-west-2.amazonaws.com/excamera-us-west-2/sintel-4k-y4m_06/{0:08d}.y4m > {0:08d}.y4m"
VPXENC = 'vpxenc --ivf --codec=vp8 --good --cpu-used=0 --end-usage=cq --min-q=0 --max-q=63 --cq-level={quality} --buf-initial-sz=10000 --buf-optimal-sz=20000 --buf-sz=40000 --undershoot-pct=100 --passes=2 --auto-alt-ref=1 --threads=1 --token-parts=0 --tune=ssim --target-bitrate=4294967295 -o "{i:08d}-0.ivf" "{i:08d}.y4m"'
XC_DUMP_0 = 'xc-dump {i:08d}-0.ivf {i:08d}-0.state'
XC_DUMP_1 = 'xc-dump -S {j:08d}-0.state {i:08d}-1.ivf {i:08d}-1.state'
XC_ENC_FIRST_FRAME = 'echo "" | xc-enc -w 0.75 -i y4m -o {i:08d}-1.ivf -r -I {j:08d}-0.state -p {i:08d}-0.ivf {i:08d}.y4m 2>&1'
XC_ENC_REBASE = 'echo "" | xc-enc -w 0.75 -i y4m -o {i:08d}-2.ivf -r -I {j:08d}-2.state -p {i:08d}-1.ivf -S {j:08d}-0.state {i:08d}.y4m 2>&1'
XC_DUMP_2 = 'xc-dump -S {j:08d}-2.state {i:08d}-2.ivf {i:08d}-2.state'
REMOVE_Y4M = "rm -f {i:08d}.y4m"
TERMINATE_CHUNK = "xc-terminate-chunk {i:08d}-0.ivf {i:08d}-A.ivf && mv {i:08d}-A.ivf {i:08d}-0.ivf"

def generate(start, end, quality=16):
    with open("Makefile", "w") as fout:
        fout.write("all: output.tar.gz")
        fout.write("\n\n")

        fout.write("# stage 1: vpxenc\n")
        for i in range(start, end + 1):
            fout.write("{i:08d}-0.ivf: dummy-file\n\t".format(i=i))
            fout.write(Y4M_DOWNLOAD.format(i))
            fout.write("\n\t")
            fout.write(VPXENC.format(quality=quality, i=i))
            fout.write("\n\t")
            fout.write(TERMINATE_CHUNK.format(i=i))
            fout.write("\n\n")

        fout.write("# stage 2: xc-dump-0\n")
        for i in range(start, end + 1):
            fout.write("{i:08d}-0.state: {i:08d}-0.ivf\n\t".format(i=i))
            fout.write(XC_DUMP_0.format(i=i))
            fout.write("\n\n")

        fout.write("# stage 3: xc-enc-first-frame\n")
        for i in range(start + 1, end + 1):
            fout.write("{i:08d}-1.ivf: {j:08d}-0.state {i:08d}-0.ivf\n\t".format(i=i, j=i-1))
            fout.write(Y4M_DOWNLOAD.format(i))
            fout.write("\n\t")
            fout.write(XC_ENC_FIRST_FRAME.format(i=i, j=i-1))
            fout.write("\n\n")

        fout.write("# stage 4: xc-dump-1\n")
        for i in range(start + 1, end + 1):
            fout.write("{i:08d}-1.state: {j:08d}-0.state {i:08d}-1.ivf\n\t".format(i=i, j=i-1))
            fout.write(XC_DUMP_1.format(i=i, j=i-1))
            fout.write("\n\n")

        fout.write("# stage 5: xc-rebase\n")
        fout.write("output.tar.gz: ")
        for i in range(start, end + 1):
            if i == start:
                fout.write("{i:08d}-0.ivf ".format(i=i))
            else:
                fout.write("{i:08d}-1.ivf {i:08d}-1.state {i:08d}-0.state ".format(i=i))

        fout.write("\n\t")
        fout.write("mv {i:08d}-0.ivf {i:08d}-2.ivf\n\t".format(i=start))
        fout.write("mv {i:08d}-1.ivf {i:08d}-2.ivf\n\t".format(i=start+1))
        fout.write("cp {i:08d}-1.state {i:08d}-2.state\n\t".format(i=start+1))
        for i in range(start + 2, end + 1):
            fout.write(Y4M_DOWNLOAD.format(i))
            fout.write("\n\t")
            fout.write(XC_ENC_REBASE.format(i=i, j=i-1))
            fout.write("\n\t")
            fout.write(REMOVE_Y4M.format(i=i))
            fout.write("\n\t")
            fout.write(XC_DUMP_2.format(i=i, j=i-1))
            fout.write("\n\t")
            fout.write("rm -f {j:08d}-2.state {i:08d}-1.state {i:08d}-1.ivf {j:08d}-0.state\n\t".format(i=i, j=i-1))

        fout.write("tar acvf output.tar.gz *-2.ivf\n")

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: gen_makefile.py <start> <end> <cq-level>", file=sys.stderr)
        sys.exit(1)

    start = int(sys.argv[1])
    end = int(sys.argv[2])
    quality = int(sys.argv[3])
    generate(start, end, quality)
