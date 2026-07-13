---
author: S Y Chen et al.
category: other
clinicalTakeaway: Foundation models can detect sinus pathology reliably with minimal
  labelled training data — watch for integration into CBCT reporting software within
  the next product cycle.
date: '2026-07-11T00:00:00Z'
digestDate: '2026-07-13'
evidenceGrade: moderate
evidenceNote: Multicentre validation study, n=30,794 unlabeled images
evidenceType: cohort
excerpt: 'OBJECTIVES: Maxillary sinus abnormalities reduce quality of life and can
  be life-threatening. However, traditional supervised deep learning models for their
  detection are constrained by class-specific training, reliance on large-scale labelled
  datasets, and unpredictable generalisability. This study aims to achieve intelligent
  detection of complex and variable maxillary sinus abnormalities via self-supervised
  learning. METHOD: A maxillary sinus foundation model (MSFound) was developed using
  self-supervised learning on 30 794 unlabeled maxillary sinus images. Clinical validation
  of reconstructed images was conducted to verify the pre-training effect. MSFound
  was then fine-tuned using labelled images at different proportions for downstream
  tasks, including mucosal thickening, polypoid lesions, and the palatonasal recess.
  Model performance was evaluated on multicentre datasets using AUROC, AUPR, and accuracy,
  and was compared with different training strategies. Clinical applicability was
  also prospectively evaluated in multicentre settings. RESULTS: MSFound successfully
  reconstructed the main anatomical structures of the maxillary sinus, and clinical
  validation confirmed the effectiveness of pre-training. During the fine-tuning process,
  MSFound achieved the highest performance with the least amount of labelled data
  compared to control groups across all tasks. The model consistently achieved the
  highest AUROC, AUPR, accuracy, and F1-score on multicentre test sets. Visualisation
  a'
guidelineFlag: false
originalTitle: 'A Foundation Model for Generalisable Detection of Maxillary Sinus
  Abnormalities: A Multicentre and Clinical Applicability Study'
rank: 6
relatedSlugs:
- 2026-07-13-other-dentsym-ai-classifies-pediatric-intraoral-views-at-98-9-accu
sampleSize: 30794
sourceId: openalex-dentistry
sourceName: OpenAlex · Dentistry
sourceUrl: https://doi.org/10.1111/joor.70250
summary: MSFound, a foundation model pre-trained on 30,794 unlabelled maxillary sinus
  images via self-supervised learning, outperformed supervised baselines on mucosal
  thickening, polypoid lesions, and palatonasal recess detection — using a fraction
  of the labelled data. Multicentre prospective validation confirmed real-world applicability.
summaryDeep: The bottleneck for medical AI is labelled data, and maxillary sinus pathology
  is no exception. MSFound sidesteps this by pre-training on 30,794 unlabelled images,
  learning anatomical representations without annotation, then fine-tuning on small
  labelled subsets for three downstream tasks. It consistently achieved the highest
  AUROC, AUPR, accuracy, and F1-score across multicentre test sets, and Grad-CAM visualizations
  confirmed anatomically coherent attention. The prospective multicentre clinical
  validation is the study's strongest feature — most dental AI papers stop at retrospective
  benchmarks. Sinus abnormalities are directly relevant to implant planning and CBCT
  interpretation, making this a clinically grounded application. The foundation model
  paradigm — pre-train once, fine-tune cheaply — is likely the architecture that will
  dominate dental AI in the next five years.
summaryLang: en
tags:
- ai
- foundation-model
- maxillary-sinus
- cbct
title: Self-Supervised Foundation Model Detects Maxillary Sinus Pathology with Minimal
  Labelled Data
topicThread: foundation-model-maxillary-sinus-abnormalities-ai-detection
---
