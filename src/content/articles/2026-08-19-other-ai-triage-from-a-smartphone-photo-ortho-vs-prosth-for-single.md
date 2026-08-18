---
author: Ehsan Shirdel et al.
category: other
clinicalTakeaway: Promising triage tool for single-tooth gaps from smartphone photos,
  but awaits prospective validation before clinical deployment.
coverAlt: A novel AI system for preliminary triage support in single-tooth edentulous
  spaces using intraoral images
coverImage: /og-cache/2026-08-19-other-ai-triage-from-a-smartphone-photo-ortho-vs-prosth-for-single.png
coverSourceUrl: https://media.springernature.com/m685/springer-static/image/art%3A10.1038%2Fs41598-026-58704-7/MediaObjects/41598_2026_58704_Figc_HTML.png
date: '2026-08-17T00:00:00Z'
digestDate: '2026-08-19'
evidenceGrade: moderate
evidenceNote: deep learning model validation, n=2962 occlusal photographs
evidenceType: lab
excerpt: 'This study aimed to demonstrate the integration of deep learning (DL) and
  machine learning (ML) using only occlusal photographs to provide preliminary triage
  support between orthodontic and prosthodontic treatments in cases requiring alternatives
  to implant-based interventions. Occlusal photographs ( n = 2,962) were collected
  under routine conditions using smartphones and digital cameras. Two groups of dental
  specialists independently annotated the dataset. A YOLOv8m model was used for the
  localization of single-tooth edentulous spaces (S-TES), which were defined as localized
  areas within the dental arch where a single tooth is absent while adjacent teeth
  remain present, as well as their mesial and distal adjacent teeth. ResNet-50/ResNet-101
  and VGG-16/VGG-19 models were employed to classify the clinical conditions and anatomical
  categories of teeth adjacent to S-TES. A deterministic function converted the mesiodistal
  width of the S-TES from pixels to millimeters using mean central incisor widths.
  Logistic Regression (LR) and XGBoost (XGB) models were used to predict the preliminary
  triage outputs. Among the classifiers for the clinical tooth condition classification
  task, VGG-19 showed the highest macro F1 score (0.928) and ResNet-101 yielded the
  highest macro AUC (0.961) and weighted kappa (0.927), with the narrowest 95% confidence
  intervals (95% CI) for both metrics. For the anatomical categorization task, ResNet-101
  showed the highest F1 score, recall, and precision. For '
guidelineFlag: false
originalTitle: A novel AI system for preliminary triage support in single-tooth edentulous
  spaces using intraoral images
rank: 2
relatedSlugs:
- 2026-08-19-other-gemini-chatgpt-claude-all-score-97-on-operative-dentistry-mc
sampleSize: 2962
sourceId: openalex-dentistry
sourceName: OpenAlex · Dentistry
sourceUrl: https://doi.org/10.1038/s41598-026-58704-7
summary: A YOLOv8m + ResNet-101 pipeline trained on 2,962 occlusal smartphone photographs
  can localize single-tooth edentulous spaces, classify adjacent tooth conditions,
  and output a preliminary ortho-vs-prosth triage recommendation. ResNet-101 hit AUC
  0.961 for tooth-condition classification. The system requires no radiograph — just
  a photo taken under routine conditions.
summaryDeep: 'The study addresses a genuinely common clinical bottleneck: a patient
  presents with a missing tooth and the referring GP must decide whether to send them
  to orthodontics (space opening/closing) or prosthodontics (implant/bridge). The
  pipeline uses YOLOv8m for spatial localization of the gap and its neighbors, ResNet-101
  for clinical condition classification (AUC 0.961, weighted kappa 0.927), and a deterministic
  pixel-to-millimeter conversion using mean central incisor width to estimate mesiodistal
  space. Logistic regression and XGBoost then output the triage call. Critically,
  the image source is a smartphone or standard digital camera under routine clinic
  lighting — no CBCT, no dedicated imaging hardware. Limitations include the single-institution
  dataset and the absence of a prospective validation cohort; the triage output is
  explicitly preliminary. Still, for a dental student or GP seeing a gap case, this
  represents a credible near-future decision-support layer that could reduce inappropriate
  referrals in both directions.'
summaryLang: en
tags:
- ai
- triage
- edentulous-space
- deep-learning
title: 'AI Triage From a Smartphone Photo: Ortho vs. Prosth for Single-Tooth Gaps'
topicThread: ai-triage-single-tooth-edentulous-space
---
