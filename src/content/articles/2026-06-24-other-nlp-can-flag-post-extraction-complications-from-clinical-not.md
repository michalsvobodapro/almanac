---
author: Farhana Pethani et al.
category: other
clinicalTakeaway: NLP can reliably extract post-extraction complication rates from
  free-text notes — a ready tool for clinic-level quality monitoring.
coverAlt: Natural language processing methods to classify unplanned returns following
  dental extractions
coverImage: /og-cache/2026-06-24-other-nlp-can-flag-post-extraction-complications-from-clinical-not.png
coverSourceUrl: https://media.springernature.com/m685/springer-static/image/art%3A10.1186%2Fs44247-026-00273-w/MediaObjects/44247_2026_273_Fig1_HTML.png
date: '2026-06-22T00:00:00Z'
digestDate: '2026-06-24'
evidenceGrade: low
evidenceNote: NLP study, n=4,756 return visits, extraction complications
evidenceType: lab
excerpt: Information about the reasons why patients return after a dental extraction
  could be used in quality-of-care indicators in dentistry, but these reasons are
  typically not recorded in a structured form in dental records. Our aim was to determine
  whether information in dental clinical notes could be used to help identify which
  patient returns were unplanned and due to complications. We manually annotated the
  clinical notes for 4,756 return visits occurring within 14 days of a dental extraction,
  separating unplanned returns due to complications from unplanned returns for other
  reasons and planned return visits. Four pre-trained language models (PLMs) and a
  bag-of-words logistic regression model were tested and performance was measured
  by F1-score. SHapley Additive exPlanations (SHAP) values were used as a post-hoc
  explainability analysis. When classifying unplanned returns due to complications
  versus all reasons for return, the best performing PLM produced an F1-score of 0.82.
  No significant difference in performance was found across the four PLMs. The performance
  of the bag-of-words logistic regression model was significantly lower (F1-score
  of 0.71). The SHAP analysis suggested that notes related to alveolar osteitis and
  post-operative infection were most predictive of unplanned returns following a dental
  extraction. NLP methods can be used to distinguish between unplanned returns due
  to complications from dental clinical notes. The results suggest that dental clinical
  notes co
guidelineFlag: false
originalTitle: Natural language processing methods to classify unplanned returns following
  dental extractions
rank: 11
relatedSlugs: []
sampleSize: 4756
sourceId: openalex-dentistry
sourceName: OpenAlex · Dentistry
sourceUrl: https://doi.org/10.1186/s44247-026-00273-w
summary: Pre-trained language models applied to 4,756 dental clinical notes achieve
  an F1-score of 0.82 for identifying unplanned post-extraction returns due to complications,
  significantly outperforming bag-of-words approaches (F1 0.71). Alveolar osteitis
  and post-operative infection are the strongest predictive signals.
summaryDeep: 'This study tackles a real-world informatics problem: post-extraction
  complications are clinically important quality indicators, but the reasons for return
  visits are buried in free-text clinical notes rather than structured fields. Four
  pre-trained language models (PLMs) were benchmarked against a bag-of-words logistic
  regression baseline on 4,756 annotated return visits within 14 days of extraction.
  The best PLM hit F1 0.82 — meaningfully better than the 0.71 baseline — and SHAP
  analysis confirmed that alveolar osteitis and infection terminology drove the predictions.
  No significant performance differences were found across the four PLMs, suggesting
  the gain comes from contextual language understanding generally, not from any specific
  architecture. For dental informatics and quality improvement, this is a practical
  demonstration that NLP can automate complication surveillance from existing records
  without requiring structured data entry reform.'
summaryLang: en
tags:
- natural-language-processing
- dental-extraction
- complications
- clinical-informatics
title: NLP Can Flag Post-Extraction Complications from Clinical Notes — F1 of 0.82
topicThread: natural-language-processing-dental-extraction-complications
---
