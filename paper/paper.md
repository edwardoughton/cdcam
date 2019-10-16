---
title: 'cdcam: Cambridge Digital Communications Assessment Model'
tags:
  - python
  - mobile telecommunications
  - technoeconomic
  - simulation
  - 5G
authors:
  - name: Edward J. Oughton
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


# Submission notes

See [guidelines](https://joss.readthedocs.io/en/latest/submitting.html)

Your paper should include:
- [x] A list of the authors of the software and their affiliations, using the correct format
- [x] A summary describing the high-level functionality and purpose of the software for a
  diverse, non-specialist audience.
- [x] A clear Statement of Need that illustrates the research purpose of the software.
- [x] A list of key references, including to other software addressing related needs.
- [x] Mention (if applicable) of any past or ongoing research projects using the software and
  recent scholarly publications enabled by it.
- [x] Acknowledgement of any financial support.

# Summary

Increasingly everything needs to be connected to the internet, both humans and machines. Hence, digital connectivity is now considered an essential infrastructure service. Internet access via cellular is one of the main ways to connect now that wireless (e.g. 5G) can rival fixed broadband access speeds. However, user generated traffic has been growing exponentially and future growth forecasts vary considerably, from conservative to continuing expansion (@Oughton:2018a). Hence, the cellular network needs to keep pace with this potential demand growth.

Successive generations of mobile telecommunications technology (3G-5G) have increased rates of data transmission and reduced latency, by rolling-out new infrastructure upgrades. But we have generally lacked the types of planning simulation models for mobile, that other sectors such as electricity or transport have long had.

Consequently, the Cambridge Digital Communications Assessment Model (`cdcam`), is a decision-support model which quantifies the performance of digital infrastructure strategies for mobile digital communications. `cdcam` models the performance of 4G and 5G technologies as they roll-out over space and time, given a set of exogenous population and data growth scenarios, and deployment strategies.

The simulation approach can be used nationally, or for a specific sub-region. The same
decision-support modelling approach is taken as in the field of telecommunication regulation,
where the Long-Run Incremental Cost  is estimated for a representative 'hypothetical
mobile network operator'.

# Statement of Need

Every decade a new generation of cellular technology is standardised and released. Increasingly, given the importance of the Internet of Things, Industry 4.0 and Smart Health applications, both governments and other digital ecosystem actors want to understand the costs associated with digital connectivity. However, there are very few open-source tools to help simultaneously understand both the engineering and cost implications of new connectivity technologies such as 5G. Hence, there is a key research need for this software.

Governments have a strong interest in 5G currently, with many making it a cornerstone of their industrial strategy. But as there remains many coverage issues associated with mobile connectivity, particularly in rural areas, this is highly concerning. Market-led deployment approaches have many benefits, but as the delivery of connectivity in low population density areas becomes less viable, the market will at some point fail to deliver necessary services. Researchers have a key role in helping government develop effective strategies to address this issue, as require associated software tools to develop a policy evidence base.

Additionally, while many large mobile network operators have their own in-house technoeconomic network planning capabilities, smaller operators do not. As a result, engineering analysis and business case assessment often take place as separate steps, rather than as an integrated process. This is another key use case for `cdcam` as engineers and business analysts at smaller operators could use the software to assess the costs of delivering connectivity target areas.

# Uniqueness
The software is unique because unlike the industry-standard Long-Run Incremental Cost modelling approach, which is predominantly spreadsheet-based, the `cdcam` explicitly models the spatio-temporal roll-out of a new generation of cellular technology (e.g. 5G roll-out).

Such a framework allows users to explore how different infrastructure strategies based on different technologies perform in terms of the capacity provided, the level of population coverage, and the necessary investment costs.

# Spatial Units

The three types of spatial units are used in the model, including sites (points), lower layer statistical units, treated here are postcode sectors (polygons), and upper layer statistical units, treated here as local authority districts (polygons). The justification for using two layers of polygon statistical units is that it allows local areas to be upgraded using a high level of spatial granularity (n=~9000), but then provide a level of aggregation for reporting results in a more manageable way (n=~380).

# Technologies and Deployment Strategies

There are three main ways to enhance the capacity and coverage of a wireless network,
including:

- Improving the spectral efficiency
- Adding more spectrum
- Building more sites

For those new to radio engineering, an analogy with a highway can be a useful way to explain
these techniques. Improving the spectral efficiency enables you to fit more bits per Hertz on a
radio wave, which is analogous to more vehicles per lane on a highway. Next, adding more spectrum
provides you with more lanes on the highway, in which to fit more vehicles. Finally, building
more sites can enable greater spatial reuse of existing spectrum, which is analogous to increasing
the density of roads, reducing the level of vehicle congestion.

`cdcam` is capable of testing all three technology options by:

- Upgrading sites (i) to 4G, or (ii) from 4G to 5G, hence improving spectral efficiency
- Adding more spectrum bands, for either (i) 4G (0.8 and 2.6 GHz), or (ii) 5G (0.7, 3.5, 26 GHz)
- Building more sites (a Small Cell layer)

Each of these technology options is then grouped into a set of strategies, including:

- No Investment
- Spectrum Integration
- Small Cells
- Spectrum integration and Small Cells

# Cellular capacity estimation

A common way to estimate the system capacity of a cellular network is via stochastic geometry
methods. In this model we make use of another open-source Python library with stochastic
geometry capabilities – the
[Python Simulator for Integrated Modelling of 5G ](https://github.com/edwardoughton/pysim5g),
known as `pysim5G`. Using `pysim5G`, a capacity lookup table is generated using a set of
simulations for each frequency band, for Inter-Site Distances ranging from 400m to 30km.
This lookup table is provided with the `cdcam` release in the data folder.

#Application

`cdcam` has already been used to test the capacity, coverage and cost of 5G infrastructure in
Britain (@Oughton:2018a, @Oughton:2018b) and the Netherlands (@Oughton:2019).

The model is one of several infrastructure simulation models being used in ongoing research as
part of the [Mistral](https://www.itrc.org.uk/) project to analyse national infrastructure
systems-of-systems.

Increasingly, the modelling capability is being applied internationally, including to provide
the analytics for the World Bank's Flagship 5G report.

- Could expand on software addressing related needs here...
- connected by a loose model coupling library, `smif` (@smif)
- scenarios of population change can be generated by `simim` (@simim)

# Acknowledgements

We would like to acknowledge the funding which has enabled development of cdcam, from the EPSRC
via (i) the Infrastructure Transitions Research Consortium Mistral project (EP/N017064/1) and
(ii) the UK's Digital Catapult Researcher in Residence programme.

# References
