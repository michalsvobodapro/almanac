---
author: Moharrami M et al.
category: conservative
clinicalTakeaway: General-purpose AI can screen occlusal caries from photos without
  dental training, but tooth-level localisation is still too unreliable for clinical
  use.
date: '2026-07-22T00:00:00Z'
digestDate: '2026-07-24'
evidenceGrade: moderate
evidenceNote: diagnostic accuracy, n=1255 images, AI caries detection
evidenceType: cohort
excerpt: Objectives To determine whether a general-purpose large multimodal model
  (LMM) can detect dental caries from intraoral photographs without task-specific
  training, evaluating image-level classification and tooth-level localisation under
  zero-shot (no reference examples) and five-shot (five annotated examples) conditions.
  Methods This diagnostic accuracy study used the benchmark test split of 1255 publicly
  available intraoral photographs. Gemini 3.1 reasoning and instant were queried via
  Vertex AI API using stateless calls and structured prompts for sequential, tooth-by-tooth
  scanning. Each model under different configurations was evaluated across 10 independent
  inference runs. Predictions (bounding boxes) were evaluated against expert annotations
  using greedy Intersection-over-Union (IoU ≥ 0.5). True positives required spatial
  overlap at the tooth level, or at least one correctly localised lesion at the image
  level. Performance was summarised using sensitivity, precision, F1-score, and mAP@50.
  Results Performance was strongly dependent on image view and model type, with reliable
  results observed mainly for the reasoning models on occlusal images. At the image
  level, zero-shot prompting showed high sensitivity but lower precision, yielding
  values of 0.95, 0.80, and 0.87 for sensitivity, precision, and F1-score, respectively.
  Five-shot prompting produced a more balanced profile, with corresponding values
  of 0.88, 0.87, and 0.87. At the tooth level, zero-shot reasoning showed a s
guidelineFlag: false
originalTitle: Detecting Dental Caries Using General-Purpose Large Multimodal Models
  From Oral Photographs
rank: 2
relatedSlugs: []
sampleSize: 1255
sourceId: epmc-conservative
sourceName: EuropePMC · Conservative & Restorative
sourceUrl: https://doi.org/10.1016/j.identj.2026.109735
summary: Google's Gemini 3.1 reasoning model detected dental caries from 1,255 intraoral
  photographs under zero-shot and five-shot conditions — no custom training on dental
  data. Image-level sensitivity hit 0.95 zero-shot, with F1 of 0.87 in both conditions.
  Performance was strongest on occlusal views and dropped on other angulations, flagging
  a real clinical limitation.
summaryDeep: 'The premise here is provocative: can a general-purpose large multimodal
  model (LMM) — one never fine-tuned on dental images — reliably find caries? Using
  a benchmark set of 1,255 publicly available intraoral photographs, this diagnostic
  accuracy study queried Gemini 3.1 via structured prompts for tooth-by-tooth scanning.
  Zero-shot reasoning achieved 0.95 sensitivity and 0.80 precision at image level;
  five-shot prompting balanced that to 0.88/0.87. The catch is tooth-level localisation:
  spatial accuracy was considerably lower, and reliable performance was largely confined
  to occlusal images. Proximal and buccal views remain a weak spot. For a dental student,
  the takeaway is double-edged — these models are already surprisingly capable out
  of the box, but they are not yet a substitute for trained diagnostic AI or clinical
  examination. The study also highlights that off-the-shelf LMMs could serve as low-barrier
  screening tools in resource-limited settings before purpose-built systems arrive.'
summaryLang: en
tags:
- ai-caries-detection
- large-multimodal-model
- diagnostic-accuracy
- intraoral-photography
title: General-Purpose AI Detects Caries From Intraoral Photos — No Task-Specific
  Training Required
topicThread: ai-caries-detection-multimodal-models
---
