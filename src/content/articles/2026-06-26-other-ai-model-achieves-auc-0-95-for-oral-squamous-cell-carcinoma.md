---
author: Li CX et al.
category: other
clinicalTakeaway: AI-assisted OSCC histopathology is advancing rapidly but external
  validation AUC of 0.745 means human pathologist oversight remains essential.
date: '2026-06-24T00:00:00Z'
digestDate: '2026-06-26'
evidenceGrade: low
evidenceNote: AI model (MILGDF) for OSCC diagnosis using whole-slide imaging
evidenceType: lab
excerpt: 'Aims This research was designed to establish an innovative diagnostic strategy
  employing whole-slide imaging (WSI) technology to address the diagnostic difficulties
  arising from the intricate histological architecture and morphological diversity
  observed in oral squamous cell carcinoma (OSCC). The developed methodology enables
  precise early identification and histomorphology-driven prognostic stratification
  of malignant lesions, thereby improving clinical management and patient prognosis.
  Methods We propose a multi-task learning framework that combines local-global attention
  mechanisms with adaptive decision fusion (MILGDF). This model utilises instance-level
  category-specific attention to enhance feature extraction efficacy while overcoming
  the limitations inherent in traditional bag-level attention methods. An adaptive
  weighting system was incorporated to dynamically adjust the contribution of local
  and global features, ensuring optimal performance in dual tasks of OSCC diagnosis
  and prognostic stratification. Results Rigorous validation on the HIDOC and TCGA-OSCC
  datasets revealed the predictive performance of our model. The MILGDF framework
  attained an area under the curve of 0.952 (accuracy: 0.909) on HIDOC and 0.745 (accuracy:
  0.725) on TCGA-OSCC. Statistical comparison using DeLong''s test and paired t-tests
  demonstrated significantly superior performance (p Conclusions Our findings demonstrate
  that the MILGDF model represents an improvement in whole-slide image-based O'
guidelineFlag: false
originalTitle: 'MILGDF: a multi-task, instance-level supervised model for oral squamous
  cell carcinoma integrating local-global attention and dynamic decision fusion'
rank: 9
relatedSlugs:
- 2026-06-26-endodontics-deep-learning-detects-periapical-lesions-on-panoramic-radiog
sourceId: epmc-oral-med-surg
sourceName: EuropePMC · Oral medicine, surgery & prostho
sourceUrl: https://doi.org/10.1136/jcp-2026-210630
summary: The MILGDF framework — a multi-task deep learning model combining local-global
  attention with adaptive decision fusion — reaches AUC 0.952 on the HIDOC dataset
  for OSCC diagnosis and prognostic stratification from whole-slide images. Performance
  on the independent TCGA-OSCC dataset drops to AUC 0.745, flagging the generalization
  gap that still separates lab performance from clinical deployment.
summaryDeep: 'Oral squamous cell carcinoma carries a poor prognosis largely because
  of late histopathological diagnosis and inconsistent prognostic stratification.
  MILGDF addresses both tasks simultaneously: it classifies WSI patches as malignant
  or benign and assigns a prognostic tier, using instance-level attention to focus
  on diagnostically relevant regions rather than averaging across the whole slide.
  The HIDOC AUC of 0.952 is impressive; the TCGA-OSCC AUC of 0.745 is the more honest
  number — it reflects what happens when a model trained on one institution''s slides
  meets a different staining protocol and scanner. The 20-point AUC gap is a canonical
  illustration of the domain-shift problem in computational pathology. For dental
  students interested in AI, this paper is a masterclass in reading AI performance
  claims critically: always look for the external validation result. For oral medicine
  clinicians, the technology is directionally promising but not yet ready to replace
  pathologist review.'
summaryLang: en
tags:
- artificial-intelligence
- oral-cancer
- whole-slide-imaging
- deep-learning
title: AI Model Achieves AUC 0.95 for Oral Squamous Cell Carcinoma Diagnosis on Whole-Slide
  Images
topicThread: ai-oral-cancer-diagnosis
---
