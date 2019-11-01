---
title: 'cdcam: Cambridge Digital Communications Assessment Model'
tags:
  - python
  - mobile telecommunications
  - technoeconomic
  - simulation
  - 5G
authors:
  - name: Edward J Oughton
    orcid: 0000-0002-2766-008X
    affiliation:  "1, 2"
  - name: Tom Russell
    orcid: 0000-0002-0081-400X
    affiliation: 1
affiliations:
  - name: Environmental Change Institute, University of Oxford
    index: 1
  - name: Computer Laboratory, University of Cambridge
    index: 2
date: 15 October 2019
bibliography: paper.bib
---

# Summary

Digital connectivity is an essential infrastructure service, as more and more people and machines are connected to the internet. Mobile internet access is one of the cheapest ways to connect wirelessly, and  new technologies (particularly 5G) can offer access speeds which can rival fixed broadband connections. Successive generations of mobile telecommunication technologies (3G-5G) have increased data transmission rates and reduced latency. However, user-generated data traffic has been growing exponentially over the past decade which is concerning for both mobile network operators and policy decision-makers, with future growth forecasts indicating this trend is likely to continue [@Oughton:2018a].

The Cambridge Digital Communications Assessment Model (``cdcam``), is a decision-support model which quantifies the performance of digital infrastructure strategies for mobile digital communications. ``cdcam`` models the performance of 4G and 5G technologies as they roll-out over space and time, given a set of exogenous population and data growth scenarios, and potential deployment strategies.

![Framework for capacity/demand/strategy assessment](cdcam-framework.png)

The simulation approach can be used nationally, or for a specific sub-regional area. The same decision-support modelling approach is taken as in the field of telecommunication regulation, where the Long-Run Incremental Cost is estimated for a representative hypothetical mobile network operator.


## Statement of Need

Every decade a new generation of cellular technology is standardised and released. Increasingly, given the importance of the Internet of Things, Industry 4.0 and Smart Health applications, both governments and other digital ecosystem actors want to understand the costs associated with digital connectivity. However, there are very few open-source tools to help simultaneously understand both the engineering and cost implications of new connectivity technologies such as 5G. Hence, there is a key research need for this software.

Governments currently have a strong interest in 5G, with many making it a cornerstone of their industrial strategy. But there remain many coverage issues associated with basic 2G-4G mobile connectivity, particularly in rural areas. Market-led deployment approaches have many benefits, but as the delivery of connectivity in low population density areas becomes less viable, the market will at some point fail to deliver the infrastructure to support these necessary services. Software tools can help to provide the evidence base for policy and government to develop effective strategies to address this issue.

Additionally, while many large mobile network operators have their own in-house technoeconomic network planning capabilities, smaller operators do not. As a result, engineering analysis and business case assessment often take place as separate steps, rather than as an integrated process. This is another key use case for ``cdcam`` as engineers and business analysts at smaller operators could use the software to assess the costs of delivering connectivity to target areas.


# References
