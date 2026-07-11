---
author: Lisa Liu et al.
category: periodontology
clinicalTakeaway: AI-based gingival biotype classification from photos is promising
  but needs multi-centre validation before replacing probe transparency in clinical
  protocols.
date: '2026-07-09T00:00:00Z'
digestDate: '2026-07-11'
evidenceGrade: moderate
evidenceNote: AI model development and validation, n=1,600 participants
evidenceType: lab
excerpt: Objectives Gingival biotype is a key factor influencing dental treatment
  outcomes. This study aimed to construct and validate an artificial intelligence
  (AI) model for objective and reproducible gingival biotype assessment based on intraoral
  photographs, thereby supporting clinical decision-making and personalized treatment
  planning. Methods A total of 1,600 participants (aged 24 ± 2 years; 720 males and
  880 females) with healthy periodontal conditions were enrolled. Gingival biotype
  was clinically identified using the probe transparency method and categorized as
  thick, medium, or thin. The dataset (640 thick, 520 medium, 440 thin) was split
  into a training set ( n = 1,500) and testing set ( n = 100) with proportional distribution.
  Weighted cross-entropy was applied to account for class imbalance. The Vision Transformer
  (ViT) model was trained using AdamW with an initial learning rate of 0.001 and a
  batch size of 8 for 10 epochs, whereas Residual Network-18 (ResNet-18) was trained
  using Adam with a learning rate of 1 × 10 −4 and a batch size of 32 with early stopping.
  Offline data augmentation (rotation ±15°, horizontal/vertical flipping, contrast/gamma
  adjustment, and contrast-limited adaptive histogram equalization (CLAHE)) was applied
  in a 1:4 ratio with fixed random seeds (123) to expand the training set from 1,500
  to 7,500 images, while the test set underwent fixed preprocessing only. Model performance
  was evaluated using F1-score and area under the receiver operating ch
guidelineFlag: false
originalTitle: Automated assessment of gingival biotype using deep learning on intraoral
  photographs
rank: 4
relatedSlugs:
- 2026-07-11-periodontology-l-prf-adds-1-mm-of-probing-depth-reduction-and-attachment-ga
sampleSize: 1600
sourceId: openalex-dentistry
sourceName: OpenAlex · Dentistry
sourceUrl: https://doi.org/10.7717/peerj-cs.3518
summary: A Vision Transformer model trained on 1,600 participants classifies gingival
  biotype (thick/medium/thin) from standard intraoral photographs, removing the need
  for probe transparency assessment. The model was validated on a held-out test set
  and outperformed ResNet-18, suggesting deep learning can standardise a measurement
  that is notoriously examiner-dependent.
summaryDeep: Gingival biotype — thick, medium, or thin — influences treatment planning
  for implants, restorations, and orthodontics, yet its clinical assessment via probe
  transparency is subjective and poorly reproducible. This study trained a Vision
  Transformer (ViT) and a ResNet-18 on 1,600 intraoral photographs from young adults
  with healthy periodontium, using weighted cross-entropy to handle class imbalance
  and offline augmentation to expand the training set to 7,500 images. The ViT outperformed
  ResNet-18 on F1-score and AUC across all three biotype categories. The test set
  (n=100) was held out with proportional class distribution. Limitations include the
  narrow age range (24 ± 2 years), single-centre recruitment, and the fact that the
  ground truth itself (probe transparency) carries measurement error. Still, an AI
  tool that delivers consistent, photograph-based biotype classification could meaningfully
  reduce inter-examiner variability in treatment planning — particularly relevant
  for implant site assessment and anterior esthetic cases. For students, this is a
  preview of how AI will enter the periodontal examination workflow.
summaryLang: en
tags:
- ai-dentistry
- gingival-biotype
- deep-learning
- periodontal-diagnosis
title: AI Classifies Gingival Biotype from Intraoral Photos with Clinically Useful
  Accuracy
topicThread: ai-gingival-biotype-assessment-deep-learning
---
