"""After the end, without music: the disclaimer of the README."""
import textwrap

from kit import *

DISCLAIMER = [
    "The scripts, settings, results, documents and this video are provided \"as is\", without warranty "
    "of any kind (MIT license). The author accepts no responsibility or liability for any consequence of "
    "using them, or of any decision based on the results.",
    "One machine, one workload: Vertica ran as a single node. On a cluster, or on stronger hardware, it "
    "would probably show better results. Other workloads and other hardware can give different results.",
    "This is not an official TPC-DS benchmark result. The workload is derived from TPC-DS, the TPC run "
    "rules were not followed, and the numbers cannot be compared with published TPC-DS results. TPC-DS is "
    "a trademark of the Transaction Processing Performance Council.",
    "Vertica, Rocket Software, PostgreSQL and all other product and company names are trademarks or "
    "registered trademarks of their respective owners. They are used here only to identify the products.",
]


def build(f, seconds: float):
    head = body("Disclaimer", size=34, weight=BOLD)
    paras = VGroup(*[VGroup(*[body(ln, size=22, color=WHITE_SOFT) for ln in textwrap.wrap(p, 100)]
                            ).arrange(DOWN, buff=0.13, aligned_edge=LEFT) for p in DISCLAIMER])
    paras.arrange(DOWN, buff=0.42, aligned_edge=LEFT)
    VGroup(head, paras).arrange(DOWN, buff=0.5, aligned_edge=LEFT).move_to(ORIGIN)
    f.play(FadeIn(VGroup(head, paras)), run_time=0.4)
    f.wait(max(0.1, seconds - 0.4))
