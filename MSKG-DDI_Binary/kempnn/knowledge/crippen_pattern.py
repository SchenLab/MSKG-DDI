#
# Copyright 2021 by Tatsuya Hasebe, Hitachi, Ltd.
# All rights reserved.
#
# This file is part of the KEMPNN package,
# and is released under the "BSD 3-Clause License". Please see the LICENSE
# file that should have been included as part of this package.
#
# The following "crippen_pattern" variable's definition is referred
# from RDKit's source code. The Copyright belongs to
# "Rational Discovery LLC, Greg Landrum, and Julie Penzotti and others".
# and is licensed under BSD 3-Clause License
# (https://github.com/rdkit/rdkit/blob/master/license.txt).
#

import io

import numpy as np
import pandas as pd
from rdkit import Chem

from kempnn.loader import MoleculeDataset, loadESOL, loadFreeSolv


def knowledgeDatasetFromFunc(
    dataset: MoleculeDataset, knowledge_func, factor=1
):
    for i in range(len(dataset)):
        smiles = dataset[i].smiles
        dataset.annotate_node(i, factor * knowledge_func(smiles))
    return dataset


def make_crippen_knowledge_attention(smiles: str) -> np.ndarray:
    crippen_io = io.StringIO(crippen_pattern)
    crippen_df = pd.read_csv(crippen_io, sep="\t")
    mol = Chem.MolFromSmiles(smiles)
    n_atoms = mol.GetNumAtoms()
    ret = [0 for i in range(n_atoms)]
    for i in range(crippen_df.shape[0]):
        sm = Chem.MolFromSmarts(crippen_df.iloc[i, 1])
        value = crippen_df.iloc[i, 2]
        match = mol.GetSubstructMatches(sm)
        for ids in match:
            for _id in ids:
                ret[_id] += value

    def clip(r):
        if r > 0.3:
            return 1
        elif r < -0.3:
            return -1
        else:
            return 0

    ret_i = np.array(list(map(clip, ret)), dtype=np.float)
    return ret_i


def load_esol_crippen_knowledge(factor=1):
    knowledge, _, _ = loadESOL(1, 0, 0, method="random")
    for i in range(len(knowledge)):
        smiles = knowledge[i].smiles
        knowledge.annotate_node(
            i, factor * make_crippen_knowledge_attention(smiles)
        )
    return knowledge


def load_freesolv_crippen_knowledge(factor=1):
    knowledge, _, _ = loadFreeSolv(1, 0, 0, method="random")
    for i in range(len(knowledge)):
        smiles = knowledge[i].smiles
        knowledge.annotate_node(
            i, factor * make_crippen_knowledge_attention(smiles)
        )
    return knowledge


crippen_pattern = """#ID	SMARTS	logP	MR	Notes/Questions
C1	[CH4]	0.1441	2.503
C1	[CH3]C	0.1441	2.503
C1	[CH2](C)C	0.1441	2.503
C2	[CH](C)(C)C	0	2.433
C2	[C](C)(C)(C)C	0	2.433
C3	[CH3][N,O,P,S,F,Cl,Br,I]	-0.2035	2.753
C3	[CH2X4]([N,O,P,S,F,Cl,Br,I])[A;!#1]	-0.2035	2.753
C4	[CH1X4]([N,O,P,S,F,Cl,Br,I])([A;!#1])[A;!#1]	-0.2051	2.731
C4	[CH0X4]([N,O,P,S,F,Cl,Br,I])([A;!#1])([A;!#1])[A;!#1]	-0.2051	2.731
C5	[C]=[!C;A;!#1]	-0.2783	5.007
C6	[CH2]=C	0.1551	3.513
C6	[CH1](=C)[A;!#1]	0.1551	3.513
C6	[CH0](=C)([A;!#1])[A;!#1]	0.1551	3.513
C6	[C](=C)=C	0.1551	3.513
C7	[CX2]#[A;!#1]	0.0017	3.888
C8	[CH3]c	0.08452	2.464
C9	[CH3]a	-0.1444	2.412
C10	[CH2X4]a	-0.0516	2.488
C11	[CHX4]a	0.1193	2.582
C12	[CH0X4]a	-0.0967	2.576
C13	[cH0]-[A;!C;!N;!O;!S;!F;!Cl;!Br;!I;!#1]	-0.5443	4.041
C14	[c][#9]	0	3.257
C15	[c][#17]	0.245	3.564
C16	[c][#35]	0.198	3.18
C17	[c][#53]	0	3.104
C18	[cH]	0.1581	3.35
C19	[c](:a)(:a):a	0.2955	4.346
C20	[c](:a)(:a)-a	0.2713	3.904
C21	[c](:a)(:a)-C	0.136	3.509
C22	[c](:a)(:a)-N	0.4619	4.067
C23	[c](:a)(:a)-O	0.5437	3.853
C24	[c](:a)(:a)-S	0.1893	2.673
C25	[c](:a)(:a)=[C,N,O]	-0.8186	3.135
C26	[C](=C)(a)[A;!#1]	0.264	4.305
C26	[C](=C)(c)a	0.264	4.305
C26	[CH1](=C)a	0.264	4.305
C26	[C]=c	0.264	4.305
C27	[CX4][A;!C;!N;!O;!P;!S;!F;!Cl;!Br;!I;!#1]	0.2148	2.693
CS	[#6]	0.08129	3.243
H1	[#1][#6,#1]	0.123	1.057
H2	[#1]O[CX4,c]	-0.2677	1.395
H2	[#1]O[!C;!N;!O;!S]	-0.2677	1.395
H2	[#1][!C;!N;!O]	-0.2677	1.395
H3	[#1][#7]	0.2142	0.9627
H3	[#1]O[#7]	0.2142	0.9627
H4	[#1]OC=[#6,#7,O,S]	0.298	1.805
H4	[#1]O[O,S]	0.298	1.805
HS	[#1]	0.1125	1.112
N1	[NH2+0][A;!#1]	-1.019	2.262
N2	[NH+0]([A;!#1])[A;!#1]	-0.7096	2.173
N3	[NH2+0]a	-1.027	2.827
N4	[NH1+0]([!#1;A,a])a	-0.5188	3
N5	[NH+0]=[!#1;A,a]	0.08387	1.757
N6	[N+0](=[!#1;A,a])[!#1;A,a]	0.1836	2.428
N7	[N+0]([A;!#1])([A;!#1])[A;!#1]	-0.3187	1.839
N8	[N+0](a)([!#1;A,a])[A;!#1]	-0.4458	2.819
N8	[N+0](a)(a)a	-0.4458	2.819
N9	[N+0]#[A;!#1]	0.01508	1.725
N10	[NH3,NH2,NH;+,+2,+3]	-1.95
N11	[n+0]	-0.3239	2.202
N12	[n;+,+2,+3]	-1.119
N13	[NH0;+,+2,+3]([A;!#1])([A;!#1])([A;!#1])[A;!#1]	-0.3396	0.2604
N13	[NH0;+,+2,+3](=[A;!#1])([A;!#1])[!#1;A,a]	-0.3396	0.2604
N13	[NH0;+,+2,+3](=[#6])=[#7]	-0.3396	0.2604
N14	[N;+,+2,+3]#[A;!#1]	0.2887	3.359
N14	[N;-,-2,-3]	0.2887	3.359
N14	[N;+,+2,+3](=[N;-,-2,-3])=N	0.2887	3.359
NS	[#7]	-0.4806	2.134
O1	[o]	0.1552	1.08
O2	[OH,OH2]	-0.2893	0.8238
O3	[O]([A;!#1])[A;!#1]	-0.0684	1.085
O4	[O](a)[!#1;A,a]	-0.4195	1.182
O5	[O]=[#7,#8]	0.0335	3.367
O5	[OX1;-,-2,-3][#7]	0.0335	3.367
O6	[OX1;-,-2,-2][#16]	-0.3339	0.7774
O6	[O;-0]=[#16;-0]	-0.3339	0.7774
O12	[O-]C(=O)	-1.326		\"order flip here intentional\"
O7	[OX1;-,-2,-3][!#1;!N;!S]	-1.189	0
O8	[O]=c	0.1788	3.135
O9	[O]=[CH]C	-0.1526	0
O9	[O]=C(C)([A;!#1])	-0.1526	0
O9	[O]=[CH][N,O]	-0.1526	0
O9	[O]=[CH2]	-0.1526	0
O9	[O]=[CX2]=O	-0.1526	0
O10	[O]=[CH]c	0.1129	0.2215
O10	[O]=C([C,c])[a;!#1]	0.1129	0.2215
O10	[O]=C(c)[A;!#1]	0.1129	0.2215
O11	[O]=C([!#1;!#6])[!#1;!#6]	0.4833	0.389
OS	[#8]	-0.1188	0.6865
F	[#9-0]	0.4202	1.108
Cl	[#17-0]	0.6895	5.853
Br	[#35-0]	0.8456	8.927
I	[#53-0]	0.8857	14.02
Hal	[#9,#17,#35,#53;-]	-2.996
Hal	[#53;+,+2,+3]	-2.996
Hal	[+;#3,#11,#19,#37,#55]	-2.996		\" \"
P	[#15]	0.8612	6.92
S2	[S;-,-2,-3,-4,+1,+2,+3,+5,+6]	-0.0024	7.365	\" \"
S2	[S-0]=[N,O,P,S]	-0.0024	7.365	\" \"
S1	[S;A]	0.6482	7.591	\"Order flip here is intentional\"
S3	[s;a]	0.6237	6.691
Me1	[#3,#11,#19,#37,#55]	-0.3808	5.754
Me1	[#4,#12,#20,#38,#56]	-0.3808	5.754
Me1	[#5,#13,#31,#49,#81]	-0.3808	5.754
Me1	[#14,#32,#50,#82]	-0.3808	5.754
Me1	[#33,#51,#83]	-0.3808	5.754
Me1	[#34,#52,#84]	-0.3808	5.754
Me2	[#21,#22,#23,#24,#25,#26,#27,#28,#29,#30]	-0.0025
Me2	[#39,#40,#41,#42,#43,#44,#45,#46,#47,#48]	-0.0025
Me2	[#72,#73,#74,#75,#76,#77,#78,#79,#80]	-0.0025
"""

if __name__ == "__main__":
    print(make_crippen_knowledge_attention("OOCCCCCCO"))
