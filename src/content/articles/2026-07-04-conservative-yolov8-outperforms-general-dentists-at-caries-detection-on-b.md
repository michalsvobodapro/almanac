---
author: Komtui P et al.
category: conservative
clinicalTakeaway: YOLOv8 catches nearly twice as many carious lesions as general dentists,
  but always verify its depth grading — it systematically underestimates severity.
coverAlt: 'Deep learning versus general dentists: a clinical evaluation of caries
  diagnostic accuracy on bitewing radiographs'
coverImage: /og-cache/2026-07-04-conservative-yolov8-outperforms-general-dentists-at-caries-detection-on-b.png
coverSourceUrl: https://media.springernature.com/full/springer-static/cover-hires/journal/12903
date: '2026-07-02T00:00:00Z'
digestDate: '2026-07-04'
evidenceGrade: moderate
evidenceNote: Deep learning validation study, n=1427 bitewings, YOLOv8 vs dentists
evidenceType: cohort
excerpt: Background The diagnostic accuracy of caries detection on bitewing radiographs
  varies among dentists and is strongly influenced by lesion severity. Improving the
  detection of initial and extensive carious lesions remains clinically important
  for appropriate treatment planning. This study evaluated the diagnostic performance
  of a deep learning-based detection model and compared its performance with that
  of general dentists in detecting caries on bitewing radiographs of primary teeth,
  applying lesion severity criteria relevant to clinical caries management. Methods
  A total of 1,427 bitewing radiographs was included, with 1,180 allocated for training
  and validation, and 247 for testing. As the reference dataset, two experienced dentists
  annotated carious lesions according to six depth categories based on the International
  Caries Classification and Management System (ICCMS™). The diagnostic performance
  of YOLOv8 and the general dentists were compared using recall, precision, F1-score,
  average precision (AP), and mean average precision (mAP) at an intersection over
  union (IoU) threshold of 50%. Results YOLOv8 outperformed the general dentists in
  recall (0.51 vs. 0.29), precision (0.41 vs. 0.31), F1-score (0.44 vs. 0.29), and
  mAP (0.41 vs. 0.22). Both YOLOv8 and the general dentists demonstrated greater diagnostic
  accuracy for extensive carious lesions than for initial lesions. Based on the pattern
  of mispredictions, YOLOv8 tended to underestimate lesion severity, predicting shallo
guidelineFlag: false
originalTitle: 'Deep learning versus general dentists: a clinical evaluation of caries
  diagnostic accuracy on bitewing radiographs'
rank: 1
relatedSlugs:
- 2026-07-04-conservative-niri-via-itero-5d-detects-dentinal-caries-in-primary-teeth-w
- 2026-07-04-orthodontics-yolo-based-cephalometric-ai-gets-the-anb-class-right-but-onl
sampleSize: 1427
sourceId: epmc-conservative
sourceName: EuropePMC · Conservative & Restorative
sourceUrl: https://doi.org/10.1186/s12903-026-09088-7
summary: 'A 1,427-bitewing validation study pits YOLOv8 against general dentists using
  ICCMS depth categories as the reference standard. The model doubles the mAP (0.41
  vs 0.22) and nearly doubles recall (0.51 vs 0.29). The catch: both the AI and the
  dentists struggle most with initial lesions, and YOLOv8 systematically underestimates
  depth.'
summaryDeep: Researchers trained YOLOv8 on 1,180 bitewing radiographs of primary teeth,
  annotated by two experienced dentists across six ICCMS depth categories, then tested
  it on a held-out set of 247 images alongside general dentists. The AI outperformed
  clinicians on every metric — recall 0.51 vs 0.29, precision 0.41 vs 0.31, F1 0.44
  vs 0.29, mAP 0.41 vs 0.22. Crucially, the performance gap was largest for extensive
  lesions, where both groups did better, but the AI's advantage was consistent across
  depths. The model's systematic failure mode is underestimating severity — it calls
  deep lesions shallow — which has direct treatment-planning consequences if used
  without calibration. The study uses a realistic, heterogeneous clinical dataset
  rather than a curated research set, making the numbers more trustworthy than most
  AI dental papers. For a student rotating through a practice with AI-assisted radiograph
  reading, this is the evidence base that justifies the workflow — with the caveat
  that depth grading still needs a human eye.
summaryLang: en
tags:
- ai
- caries-detection
- bitewing-radiography
- deep-learning
title: YOLOv8 Outperforms General Dentists at Caries Detection on Bitewing Radiographs
topicThread: ai-deep-learning-caries-detection-bitewing-radiographs
---
