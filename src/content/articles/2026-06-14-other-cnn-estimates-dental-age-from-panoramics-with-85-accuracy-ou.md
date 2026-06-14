---
author: Essraa Gamal Mohamed et al.
category: other
clinicalTakeaway: Promising forensic and clinical tool, but single-population training
  data means external validation is essential before any real-world deployment.
date: '2026-06-12T00:00:00Z'
digestDate: '2026-06-14'
evidenceGrade: moderate
evidenceType: lab
excerpt: 'Background/Objectives: Determining chronological age is important in several
  domains, including forensic identification, clinical decision-making, legal matters,
  and immigration procedures. Dental tissues are widely recognized as reliable indicators
  of age because they undergo gradual and measurable structural changes throughout
  life. Nevertheless, most conventional dental methods show limited reliability when
  applied to adults and elderly individuals. The objective of this study was to investigate
  an automated deep learning-based approach for age-group classification in adults
  and seniors using panoramic dental radiographs. Methods: Panoramic dental radiographs
  were analyzed using a custom-designed Convolutional Neural Network (CNN) along with
  several established pre-trained deep learning architectures. The dataset consisted
  of 1469 radiographic images obtained from Egyptian individuals aged between 25 and
  70 years. Images were classified into five predefined age categories using a classification-based
  framework, and the models were trained to learn age-related dental patterns from
  radiographic images. Results: The proposed Custom CNN achieved the highest accuracy
  of 85.2%, outperforming YOLOv8 (79.1%) and all other evaluated models, with the
  lowest prediction error (MAE = 1.92 years; RMSE = 5.46 years). Overall, the deep
  learning models demonstrated strong performance in classifying dental age groups,
  particularly within adult and senior populations, where conventional meth'
guidelineFlag: false
originalTitle: Dental Age-Group Classification from Panoramic Radiographs Using Convolutional
  Neural Networks
rank: 10
relatedSlugs:
- 2026-06-14-orthodontics-ai-matches-but-doesn-t-yet-beat-expert-clinicians-in-orthodo
sampleSize: 1469
sourceId: openalex-dentistry
sourceName: OpenAlex · Dentistry
sourceUrl: https://doi.org/10.3390/diagnostics16121816
summary: A custom convolutional neural network classified adults and seniors into
  five age groups from panoramic radiographs with 85.2% accuracy and a mean absolute
  error of 1.92 years, outperforming YOLOv8 and other pretrained architectures. The
  dataset of 1,469 Egyptian patients aged 25–70 is a limitation, but the approach
  addresses a genuine gap in adult dental age estimation.
summaryDeep: Conventional dental age estimation methods lose reliability in adults,
  where root and pulp changes are subtler. This study trained a custom CNN and several
  established architectures (YOLOv8, ResNet, VGG variants) on 1,469 panoramic radiographs
  from Egyptian individuals aged 25–70, classified into five predefined age groups.
  The custom CNN achieved 85.2% accuracy with MAE of 1.92 years and RMSE of 5.46 years
  — the best performance across all tested models. The single-ethnicity, single-institution
  dataset is a significant generalizability constraint, and the five-group classification
  framework is coarser than continuous age estimation. Still, the performance gap
  over established architectures suggests that task-specific CNN design outperforms
  off-the-shelf transfer learning for this application. Forensic dentistry and clinical
  age assessment in undocumented patients are the most immediate use cases.
summaryLang: en
tags:
- artificial-intelligence
- dental-age-estimation
- panoramic-radiograph
- deep-learning
title: CNN Estimates Dental Age from Panoramics with 85% Accuracy — Outperforming
  YOLOv8
topicThread: ai-age-classification-panoramic-radiographs-cnn
---
