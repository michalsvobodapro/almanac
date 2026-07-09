---
author: Asghari E et al.
category: conservative
clinicalTakeaway: AI segmentace kazů na panoramatických snímcích dosahuje vysoké přesnosti,
  ale pouze při správném předzpracování dat — architektura modelu je druhořadá.
coverAlt: 'Impact of data augmentation and backbone architecture selection on dental
  caries segmentation in panoramic radiographs: a comparative deep learning study
  using pre-trained U-Net models'
coverImage: /og-cache/2026-07-09-conservative-xception-based-u-net-achieves-0-95-dice-for-caries-segmentat.png
coverSourceUrl: https://media.springernature.com/m685/springer-static/image/art%3A10.1007%2Fs44445-026-00211-6/MediaObjects/44445_2026_211_Fig1_HTML.png
date: '2026-07-07T00:00:00Z'
digestDate: '2026-07-09'
evidenceGrade: low
evidenceNote: In vitro deep learning study, n=500 panoramic X-rays
evidenceType: lab
excerpt: 'This study evaluates the impact of data augmentation and preprocessing on
  U-Net model performance for dental caries segmentation in panoramic X-ray images,
  comparing different pre-trained backbone architectures. A combined dataset of 500
  panoramic dental X-ray images was analyzed: 400 from Tabriz University of Medical
  Sciences (1024 × 2048 pixels) and 100 publicly available images (1536 × 768 pixels),
  all with manually annotated, expert-validated segmentation masks. A preprocessing
  pipeline including resizing, bilateral filtering, CLAHE contrast enhancement, unsharp
  masking, and normalization was applied, and data augmentation (rotation, shifting,
  shearing, zooming, horizontal flipping) expanded the dataset to 1,000 images. Four
  U-Net architectures (standard, VGG16, ResNet50, and Xception) were evaluated across
  four scenarios (with/without augmentation and preprocessing), using Dice coefficient,
  IoU, accuracy, precision, recall, F1-score, and AUC-ROC through five-fold cross-validation.
  The Xception-based U-Net, with both augmentation and preprocessing, achieved the
  highest performance (Dice: 0.9517 ± 0.0029, IoU: 0.9079 ± 0.0053), while the standard
  U-Net achieved Dice: 0.7380 ± 0.2099 and IoU: 0.6203 ± 0.2193 under the same configuration.
  Models lacking augmentation or preprocessing performed substantially worse, with
  ResNet50 without augmentation showing severe degradation (Dice: 0.0068 ± 0.0002).
  The combined configuration also yielded the lowest validation loss (0.0154) a'
guidelineFlag: false
originalTitle: 'Impact of data augmentation and backbone architecture selection on
  dental caries segmentation in panoramic radiographs: a comparative deep learning
  study using pre-trained U-Net models'
rank: 5
relatedSlugs:
- 2026-07-09-endodontics-chatgpt-5-reads-endodontic-radiographs-poorly-sensitivity-fo
- 2026-07-09-other-llms-in-dentistry-need-continuous-red-teaming-not-a-one-time
sampleSize: 500
sourceId: epmc-conservative
sourceName: EuropePMC · Conservative & Restorative
sourceUrl: https://doi.org/10.1007/s44445-026-00211-6
summary: 'A deep learning comparison of four U-Net architectures on 500 panoramic
  radiographs finds the Xception-backbone model — with data augmentation and preprocessing
  — reaches a Dice coefficient of 0.9517 and IoU of 0.9079 for caries segmentation.
  Models without augmentation collapsed catastrophically (ResNet50 Dice: 0.007). The
  preprocessing pipeline, not just architecture choice, is the decisive variable.'
summaryDeep: Automated caries detection on panoramic radiographs is a high-value clinical
  AI target, and this study provides one of the most systematic architecture comparisons
  to date. Four U-Net variants (standard, VGG16, ResNet50, Xception) were tested across
  four experimental conditions — with and without data augmentation, with and without
  preprocessing — using five-fold cross-validation on 500 annotated panoramic images.
  The Xception-based model with full preprocessing achieved near-ceiling performance
  (Dice 0.9517), while the same model without augmentation degraded substantially,
  and ResNet50 without augmentation essentially failed (Dice 0.007). The practical
  lesson is that pipeline design — CLAHE contrast enhancement, bilateral filtering,
  augmentation — matters as much as backbone selection. The dataset is modest (500
  images) and single-center in part, so external validation is needed before clinical
  deployment. Still, this is a technically credible contribution to the AI-caries
  literature and directly relevant to students learning about AI tool evaluation.
summaryLang: en
tags:
- ai-diagnostics
- caries-detection
- deep-learning
- panoramic-radiograph
title: Xception-Based U-Net Achieves 0.95 Dice for Caries Segmentation on Panoramic
  Radiographs
topicThread: ai-caries-segmentation-panoramic-radiographs
---
