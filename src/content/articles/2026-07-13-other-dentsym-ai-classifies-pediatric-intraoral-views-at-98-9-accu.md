---
author: Elham Tahsin Yasin et al.
category: other
clinicalTakeaway: AI view classification for pediatric intraoral photos is technically
  mature, but patient-level external validation is still needed before clinical deployment.
coverAlt: 'Automated classification of maxillary and mandibular dental views on intraoral
  photographs: a comparative benchmark study and mobile proof-of-concept'
coverImage: /og-cache/2026-07-13-other-dentsym-ai-classifies-pediatric-intraoral-views-at-98-9-accu.png
coverSourceUrl: https://media.springernature.com/full/springer-static/cover-hires/journal/12903
date: '2026-07-11T00:00:00Z'
digestDate: '2026-07-13'
evidenceGrade: moderate
evidenceNote: Benchmark study, n=9,562 pediatric intraoral images
evidenceType: cohort
excerpt: Artificial intelligence is increasingly explored in dentistry to improve
  workflow efficiency and support image-based analysis. This study benchmarks deep
  learning (DL) and machine learning (ML) approaches for classifying pediatric dental
  views using a publicly available dataset of 9,562 intraoral images from children
  aged 1–14 years, covering eight maxillary and mandibular view classes. Under 10-fold
  cross-validation, MobileNetV2 achieved the highest performance among DL models (accuracy
  95.18%, F1-score 0.95, AUC 0.997), followed by InceptionV3 (93.76%) and Xception
  (93.07%). Among ML methods, Logistic Regression achieved 93.33% accuracy with an
  AUC of 0.996. A symmetry-aware architecture, DentSym, was further proposed, achieving
  an average accuracy of 98.92% with balanced precision, recall, and F1-score. Model
  interpretability was examined using Grad-CAM, indicating that predictions were based
  on relevant dental regions. The highest-performing model was integrated into a prototype
  iOS application for real-time classification as a proof of concept. However, as
  cross-validation was performed at the image level due to the absence of patient
  identifiers, the reported performance should be interpreted as an upper-bound estimate
  under the current experimental setting. The study provides baseline reference results
  for this dataset and highlights the potential of explainable, mobile-based AI systems
  for future dental applications.
guidelineFlag: false
originalTitle: 'Automated classification of maxillary and mandibular dental views
  on intraoral photographs: a comparative benchmark study and mobile proof-of-concept'
rank: 5
relatedSlugs:
- 2026-07-13-other-self-supervised-foundation-model-detects-maxillary-sinus-pat
- 2026-07-13-conservative-chatgpt-5-and-claude-4-5-lead-five-llms-on-pediatric-caries
sampleSize: 9562
sourceId: openalex-dentistry
sourceName: OpenAlex · Dentistry
sourceUrl: https://doi.org/10.1186/s12903-026-09089-6
summary: A benchmark study on 9,562 pediatric intraoral images compared deep learning
  and classical ML models for dental view classification. A novel symmetry-aware architecture
  (DentSym) hit 98.9% accuracy; the best off-the-shelf model (MobileNetV2) reached
  95.2%. The top model was integrated into a prototype iOS app for real-time use.
summaryDeep: 'Automated image triage — knowing which arch and region a photo shows
  before analysis begins — is a foundational step for any AI dental workflow. This
  benchmark used a publicly available dataset of 9,562 intraoral images from children
  aged 1–14, covering eight view classes. DentSym, a purpose-built symmetry-aware
  architecture, outperformed MobileNetV2 (95.2%), InceptionV3 (93.8%), and even Logistic
  Regression (93.3%) by a meaningful margin. Grad-CAM visualizations confirmed predictions
  were anchored to clinically relevant dental regions rather than image artifacts.
  The iOS proof-of-concept demonstrates real-world deployment feasibility. Critical
  caveat: cross-validation was image-level, not patient-level, so reported accuracy
  is an upper bound — patient-level validation on an independent dataset is the next
  required step before clinical adoption. For a student, this illustrates how explainability
  tools (Grad-CAM) are becoming a non-negotiable part of AI validation.'
summaryLang: en
tags:
- ai
- deep-learning
- intraoral-photography
- pediatric-dentistry
title: DentSym AI Classifies Pediatric Intraoral Views at 98.9% Accuracy — and Runs
  on an iPhone
topicThread: deep-learning-dental-view-classification-ai-mobile-app
---
