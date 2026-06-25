---
author: Gu X et al.
category: periodontology
clinicalTakeaway: AI-assisted periodontal defect classification is promising but not
  ready for clinical use — single-center, n=329 training set requires multicenter
  validation before it changes how you read films.
coverAlt: Deep learning-based identification, classification and segmentation of infraosseous
  periodontal defects using a YOLOv8 neural network
coverImage: /og-cache/2026-06-25-periodontology-yolov8-ai-classifies-infraosseous-periodontal-defects-on-per.png
coverSourceUrl: https://media.springernature.com/full/springer-static/cover-hires/journal/12903
date: '2026-06-23T00:00:00Z'
digestDate: '2026-06-25'
evidenceGrade: low
evidenceNote: Deep learning model development, 329 radiographs
evidenceType: lab
excerpt: 'Background The defect morphology determines single-tooth prognosis, surgical
  planning, and regenerative potential of intrabony defects. 2D radiographs are often
  compromised by superimposition of anatomical structures, leading to potential misinterpretation
  and diagnostic inaccuracies. The aim of this study was to develop YOLOv8 model to
  identify, classify and segment periodontal defects. Methods A dataset of 329 periapical
  radiographs from the Department of Periodontology, Semmelweis University, was utilized.
  All radiographs were preprocessed and manually annotated. The YOLOv8 neural network
  was trained and mainly assessed by area under the receiver operating characteristic
  curve (AUC-ROC), macro-average F1-score, Intersection over Union (IoU) and Dice
  similarity coefficient (DSC). Results The model achieved an AUC-ROC of 0.8078 (95%
  CI: 0.6633-0.9257). The macro-average F1-score was found to be 0.6559. IoU and DSC
  value averaged 0.6881 ± 0.2398 and 0.7789 ± 0.2664. High spatial overlap was observed
  for one -wall (DSC: 0.8688), three-wall (DSC: 0.8723) and four-wall (DSC: 0.8641)
  defects. Conclusions The utilized YOLOv8 model demonstrated the capability to identify,
  classify, and segment infraosseous periodontal defects, achieving good discriminative
  power and moderate classification/ segmentation performance. Future work will have
  to focus on constructing a larger and even more refined training dataset to further
  enhance model performance.'
guidelineFlag: false
originalTitle: Deep learning-based identification, classification and segmentation
  of infraosseous periodontal defects using a YOLOv8 neural network
rank: 10
relatedSlugs:
- 2026-06-25-endodontics-ai-for-accessory-canal-detection-in-endodontic-imaging-syste
sampleSize: 329
sourceId: epmc-perio
sourceName: EuropePMC · Periodontology
sourceUrl: https://doi.org/10.1186/s12903-026-08919-x
summary: A YOLOv8 deep learning model trained on 329 annotated periapical radiographs
  achieved AUC-ROC 0.81 for identifying and classifying infraosseous periodontal defects,
  with strong spatial overlap (DSC ~0.87) for one-, three-, and four-wall defects.
  Two-wall defects remained harder to classify. The model is a proof-of-concept; clinical
  deployment requires larger, multicenter datasets.
summaryDeep: 'Infraosseous defect morphology drives surgical planning and regenerative
  prognosis, but 2D periapical radiographs are notoriously prone to anatomical superimposition
  and reader variability. This study trained and evaluated a YOLOv8 instance segmentation
  model on 329 periapical radiographs from Semmelweis University, manually annotated
  by periodontists. The model achieved AUC-ROC 0.8078, macro-average F1-score 0.6559,
  and Dice similarity coefficients of 0.87–0.87 for one-, three-, and four-wall defects.
  Two-wall defects showed lower performance, likely reflecting their inherently ambiguous
  radiographic appearance. The dataset is single-center and relatively small, which
  limits generalizability. Still, the performance on well-defined defect morphologies
  is clinically interesting: if validated, automated defect classification could standardize
  treatment planning and reduce inter-examiner variability in periodontal surgery
  decisions. This sits alongside the AI-for-accessory-canal story as part of a broader
  wave of diagnostic AI entering dental specialties.'
summaryLang: en
tags:
- ai
- periodontal-defects
- yolov8
- radiographic-diagnosis
title: YOLOv8 AI Classifies Infraosseous Periodontal Defects on Periapical X-Rays
  with AUC 0.81
topicThread: ai-periodontal-defect-detection-yolo
---
