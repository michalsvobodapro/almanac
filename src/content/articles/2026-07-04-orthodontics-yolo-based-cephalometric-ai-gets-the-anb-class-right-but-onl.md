---
author: Jacek Kotuła et al.
category: orthodontics
clinicalTakeaway: AI cephalometric classification is reliable only with large, well-annotated
  training sets — treat vendor claims about small-dataset models with scepticism.
date: '2026-07-02T00:00:00Z'
digestDate: '2026-07-04'
evidenceGrade: moderate
evidenceNote: AI validation study, n=131 cephalograms, YOLO-based landmark detection
evidenceType: cohort
excerpt: 'Background/Objectives: Automated cephalometric landmark detection using
  deep learning has the potential to streamline routine orthodontic diagnosis. However,
  the clinical relevance of artificial intelligence (AI) localisation accuracy depends
  on how detection errors propagate into derived angular measurements and skeletal
  classifications. We retrospectively evaluated 14 YOLO-based model configurations
  and quantified the agreement between AI-derived and expert-derived ANB-based skeletal
  classifications. Methods: Twelve working YOLO-based models (YOLOv5xu, YOLOv11 nano/small/medium/large
  variants) were trained on a single-centre dataset of 120 lateral cephalograms and
  evaluated on an independent test set of 11 cephalograms (stratified across skeletal
  Classes I, II, III). The four ANB-defining landmarks (Sella, Nasion, A-point, B-point)
  were the focus of the analysis. Each test cephalogram had been annotated by four
  orthodontists (44 measurements per image), yielding the expert reference. We assessed
  the effects of architecture, bounding-box size (40/100/150 px), training dataset
  scale (235–4255 images) and training epochs on localisation accuracy (mean radial
  error, MRE; Successful Detection Rate, SDR) and on the downstream ANB-based skeletal
  classification. Diagnostic concordance was quantified by classification agreement,
  Cohen’s κ with bootstrap 95% confidence intervals (10,000 iterations), an exact
  one-sided binomial test for discordance, and Wilson exact CIs per class. Res'
guidelineFlag: false
originalTitle: 'Automated YOLO-Based Cephalometric Landmark Detection for ANB-Based
  Skeletal Classification: A Retrospective Single-Centre Study'
rank: 6
relatedSlugs:
- 2026-07-04-conservative-yolov8-outperforms-general-dentists-at-caries-detection-on-b
sampleSize: 131
sourceId: openalex-dentistry
sourceName: OpenAlex · Dentistry
sourceUrl: https://doi.org/10.3390/jcm15135149
summary: Fourteen YOLO configurations trained on up to 4,255 lateral cephalograms
  are benchmarked against four-orthodontist consensus on ANB-based skeletal classification.
  Best models achieve substantial agreement (κ up to ~0.7), but performance collapses
  with small training sets and tiny bounding boxes.
summaryDeep: 'This single-centre retrospective study trained YOLOv5xu and YOLOv11
  variants on datasets ranging from 235 to 4,255 augmented cephalograms, testing on
  11 stratified cephalograms with four-orthodontist reference annotations (44 measurements
  per image). The focus was whether localisation errors in four ANB-defining landmarks
  (Sella, Nasion, A-point, B-point) propagate into misclassification of skeletal class.
  The answer is: yes, but only when training data are sparse or bounding boxes are
  too small. Larger architectures (YOLOv5xu, YOLOv11-large) with 150 px bounding boxes
  and full training sets achieved classification agreement comparable to inter-examiner
  variability. The test set of 11 images is a significant limitation — confidence
  intervals are wide. Still, the study is practically useful: it quantifies the minimum
  training data threshold and the architecture choices that matter, which is actionable
  for anyone building or evaluating a cephalometric AI tool.'
summaryLang: en
tags:
- ai
- cephalometrics
- orthodontic-diagnosis
- deep-learning
title: YOLO-Based Cephalometric AI Gets the ANB Class Right — But Only With Enough
  Training Data
topicThread: ai-yolo-cephalometric-landmark-detection-skeletal-classification
---
