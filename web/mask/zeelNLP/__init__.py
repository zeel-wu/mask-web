# -*- coding: utf-8 -*-
#                      _   _ _     ____
#   ___ ___   ___ ___ | \ | | |   |  _ \
#  / __/ _ \ / __/ _ \|  \| | |   | |_) |
# | (_| (_) | (_| (_) | |\  | |___|  __/
#  \___\___/ \___\___/|_| \_|_____|_|


# -*- coding: utf-8 -*-

"""
zeelNLP module
:copyright: (c) 2019 by Yang Yang.
:license: MIT, see LICENSE for more details.
@inproceedings{he-choi-2021-stem,
    title = "The Stem Cell Hypothesis: Dilemma behind Multi-Task Learning with Transformer Encoders",
    author = "He, Han and Choi, Jinho D.",
    booktitle = "Proceedings of the 2021 Conference on Empirical Methods in Natural Language Processing",
    month = nov,
    year = "2021",
    address = "Online and Punta Cana, Dominican Republic",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2021.emnlp-main.451",
    pages = "5555--5577",
    abstract = "Multi-task learning with transformer encoders (MTL) has emerged as a powerful technique to improve performance on closely-related tasks for both accuracy and efficiency while a question still remains whether or not it would perform as well on tasks that are distinct in nature. We first present MTL results on five NLP tasks, POS, NER, DEP, CON, and SRL, and depict its deficiency over single-task learning. We then conduct an extensive pruning analysis to show that a certain set of attention heads get claimed by most tasks during MTL, who interfere with one another to fine-tune those heads for their own objectives. Based on this finding, we propose the Stem Cell Hypothesis to reveal the existence of attention heads naturally talented for many tasks that cannot be jointly trained to create adequate embeddings for all of those tasks. Finally, we design novel parameter-free probes to justify our hypothesis and demonstrate how attention heads are transformed across the five tasks during MTL through label analysis.",
}
"""
