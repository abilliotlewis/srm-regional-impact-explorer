# Literature Review: Regional Climate Impacts of Solar Radiation Modification

## 1. Research context

Solar radiation modification (SRM), also referred to as solar geoengineering or solar climate intervention, describes proposed approaches for reducing some anthropogenic warming by altering Earth's radiative balance. The most extensively studied approach is stratospheric aerosol injection (SAI), although reduced solar irradiance, marine cloud brightening, and other concepts have also been investigated [1].

Climate-model experiments consistently indicate that sufficiently strong SRM could reduce global mean surface warming. However, reducing global mean temperature does not recreate the climate that would have existed under lower greenhouse-gas concentrations. Temperature, precipitation, atmospheric circulation, and hydrological responses may differ geographically and between intervention mechanisms [1,2].

This distinction motivates the **SRM Regional Impact Explorer**, which investigates how different SRM experiments affect climate at regional scales, initially focusing on the Southeast United States.

## 2. GeoMIP and the G6 experiments

The Geoengineering Model Intercomparison Project (GeoMIP) provides coordinated climate-model experiments designed to investigate the physical consequences and uncertainties associated with SRM.

Two particularly useful CMIP6-era experiments are **G6solar** and **G6sulfur**. Both begin from the high-forcing SSP5-8.5 scenario and apply an intervention intended to reduce global temperatures toward the trajectory associated with the more moderate SSP2-4.5 scenario.

The experiments achieve this through different mechanisms:

* **G6solar** represents an idealized reduction in incoming solar irradiance.
* **G6sulfur** represents the injection of sulfur into the stratosphere, producing reflective sulfate aerosols.

Because the experiments pursue broadly similar global-temperature objectives through physically different forcing mechanisms, they provide a useful framework for investigating whether similar global cooling produces similar regional climates.

G6solar should not be interpreted as an engineering simulation of a particular space-based sunshade or mirror system. It is an idealized reduced-solar-irradiance climate experiment.

## 3. Similar global cooling does not imply similar regional outcomes

Multi-model analysis of G6solar and G6sulfur demonstrates substantial differences between climate models and between intervention mechanisms.

Visioni et al. [2] evaluated sources of uncertainty across G6solar and G6sulfur simulations and found considerable inter-model spread in aerosol distributions, radiative forcing, stratospheric heating, precipitation, and regional surface climate. G6sulfur introduces processes that are absent from the idealized G6solar experiment, including aerosol transport and microphysics, stratospheric heating, and associated circulation responses.

These results establish an important principle for regional SRM research:

> Similar global-mean temperature targets do not guarantee similar regional climate outcomes.

Regional differences therefore should not be treated simply as small-scale noise around a globally uniform response. They can arise from physically meaningful differences in the way an intervention interacts with the atmosphere.

## 4. Atmospheric circulation can amplify regional differences

Jones et al. [3] directly compared G6solar and G6sulfur using two Earth system models and identified an important example of intervention-dependent atmospheric dynamics.

Both models produced a persistent positive Northern Hemisphere winter North Atlantic Oscillation anomaly under G6sulfur that was not reproduced under G6solar. This altered zonal circulation and North Atlantic storm-track behavior.

The study also found disagreement between the models over regional changes affecting the continental United States. The authors concluded that additional models were needed before robust conclusions could be drawn regarding continental-scale SRM impacts.

This is particularly relevant to the SRM Regional Impact Explorer. It suggests that regional differences between G6solar and G6sulfur may reflect genuine atmospheric mechanisms while simultaneously emphasizing the importance of multimodel analysis and explicit representation of uncertainty.

## 5. Hydroclimate is a major source of uncertainty

Hydrological responses represent one of the most consequential uncertainties in SRM research.

Ricke et al. [4] reviewed the hydrological consequences of solar geoengineering and concluded that most approaches are expected to weaken the global hydrological cycle, while regional outcomes vary considerably depending on intervention strategy, geography, and the particular hydrological quantity considered.

This makes precipitation particularly important for regional SRM assessment.

A climate intervention that successfully reduces temperature could still produce important changes in:

* mean precipitation,
* heavy precipitation,
* drought frequency,
* consecutive dry days,
* soil moisture,
* evaporation,
* storm behavior, and
* seasonal rainfall distributions.

For this reason, evaluating SRM primarily through temperature response provides an incomplete picture of regional climate consequences.

## 6. Increasing emphasis on regional extremes

Recent work has increasingly moved beyond global or annual averages toward regional climate impacts and extreme events.

Feng et al. [5] analyzed precipitation extremes across Southeast Asia using five GeoMIP6 models. Both G6solar and G6sulfur moderated some precipitation changes associated with SSP5-8.5, but the interventions did not produce identical regional responses. G6sulfur generally produced greater spatial variation, while G6solar produced more spatially consistent reductions in some precipitation-extreme metrics.

The study demonstrates the value of analyzing individual hazard indicators rather than assuming that an intervention's effect on mean temperature predicts its effect on extreme rainfall.

Earlier work by Dagon and Schrag [6] similarly showed that uniform solar geoengineering could reduce heat waves and consecutive dry days relative to a high-CO2 climate while still producing geographically heterogeneous responses. Soil-moisture feedbacks contributed substantially to regional differences.

Together, these studies support expanding regional SRM analysis from climatological means toward extremes and compound hazards.

## 7. Emerging U.S. research

Detailed SRM impact research over the United States remains less developed than global-scale analysis, but recent work indicates growing interest in weather-scale consequences.

Sun et al. [7] developed a convection-permitting Weather Research and Forecasting (WRF) framework at approximately 4-km resolution to investigate the effects of SAI on future weather across the contiguous United States.

Their simulations showed that greenhouse warming increased extreme precipitation and deep convective activity over parts of the eastern United States and that SAI could mitigate some of these changes. The study represents an important shift from global climate response toward mesoscale weather impacts.

This work also helps define a complementary role for the SRM Regional Impact Explorer.

High-resolution regional modeling can investigate individual atmospheric processes and weather systems in substantial detail. In contrast, the SRM Regional Impact Explorer is designed to systematically compare responses across multiple global climate models, scenarios, seasons, variables, and regions.

These approaches address different parts of the same scientific problem:

**High-resolution process modeling:**
How might SRM affect particular weather processes?

**Multimodel regional assessment:**
How consistently do climate models project particular regional consequences?

## 8. Research gap for the Southeast United States

Existing literature establishes that SRM effects can vary substantially by region, intervention mechanism, season, and climate model. Regional studies have examined parts of Asia, monsoon systems, hydrology, atmospheric circulation, and extreme events.

The Southeast United States presents a particularly useful case for regional assessment because it experiences multiple climate-sensitive hazards, including:

* extreme heat,
* high humidity and heat stress,
* convective precipitation,
* drought,
* tropical cyclones,
* inland flooding, and
* coastal hazards.

The region is also affected by atmospheric circulation originating well outside its boundaries. Consequently, regional SRM responses cannot necessarily be inferred from global mean cooling or local radiative forcing alone.

A systematic multimodel comparison of G6solar and G6sulfur over the Southeast United States can therefore contribute to understanding both the magnitude of projected regional changes and the degree to which climate models agree about those changes.

## 9. Current SRM Regional Impact Explorer results

The Phase 3 checkpoint evaluates monthly maximum near-surface air temperature (`tasmax`) from four matched GeoMIP models for 2071–2100: CNRM-ESM2-1, IPSL-CM6A-LR, MPI-ESM1-2-LR, and UKESM1-0-LL.

For the Southeast U.S. analysis region, the four-model JJA mean difference relative to SSP5-8.5 is approximately:

| Experiment | JJA `tasmax` difference | Model range | Sign agreement |
| ---------- | ----------------------: | ----------: | -------------: |
| G6solar    |                -2.14 °C | -2.67 to -1.71 °C | 100% |
| G6sulfur   |                -1.84 °C | -2.49 to -1.42 °C | 100% |

The four-model mean G6solar-minus-G6sulfur JJA difference is -0.30 °C, with individual-model values from -0.40 to -0.18 °C. All four models therefore give a more negative JJA response under G6solar in this regional calculation.

The agreement is season-dependent. MAM splits two models on each sign of the G6solar-minus-G6sulfur difference, and DJF G6sulfur includes one model with warming relative to SSP5-8.5. The result should therefore be interpreted narrowly rather than as a general ranking of intervention mechanisms. The Phase 3 checkpoint reports individual models, spread, counts, and sign agreement so disagreement remains visible.

## 10. Research direction

The literature suggests several priorities for developing the SRM Regional Impact Explorer.

### 10.1 Maintain a defensible model ensemble

Model disagreement is itself an important characteristic of SRM projections. Phase 3 expands the direct comparison to four models while excluding models that lack a usable matched `tasmax` triplet. Future additions should be made only when their exact variants, grids, parent branches, coverage, and provenance support a defensible direct comparison.

Results should continue to preserve individual model identity and report model spread, count, and sign agreement rather than presenting an ensemble mean alone.

### 10.2 Add precipitation

Hydrological responses are less predictable than temperature responses and may differ substantially between intervention mechanisms [2,4].

Mean precipitation provides a logical next variable before moving to daily extreme indices.

### 10.3 Analyze extremes

Daily climate-model output would allow calculation of decision-relevant indices such as:

* TXx or extreme maximum temperature,
* heatwave frequency and duration,
* Rx1day maximum one-day precipitation,
* heavy precipitation frequency,
* consecutive dry days, and
* compound heat and moisture metrics.

Such metrics may reveal important impacts that are obscured by seasonal means.

### 10.4 Map model agreement

Ensemble means alone can hide disagreement.

Future outputs should distinguish between:

* ensemble magnitude,
* inter-model spread,
* agreement on the sign of change, and
* regions where results remain inconclusive.

The spatial distribution of model confidence may itself be one of the most useful outputs of regional SRM assessment.

### 10.5 Move toward regional climate risk

The longer-term research opportunity is to connect climate-model responses with hazards relevant to particular places.

A regional climate-risk framework could examine questions such as:

* Where does SRM consistently reduce extreme heat?
* Where do G6solar and G6sulfur produce meaningfully different precipitation responses?
* Where is model uncertainty largest?
* Do intervention mechanisms alter drought and extreme-rainfall risks differently?
* Which regions experience residual climate change despite global temperature moderation?

This framing shifts the focus from whether SRM can alter global temperature toward the more decision-relevant question of how climate intervention could redistribute regional climate risk.

## 11. Project contribution

The SRM Regional Impact Explorer is intended to occupy the space between global GeoMIP analysis and highly specialized regional process modeling.

Its proposed contribution is an open and reproducible framework for:

1. acquiring traceable GeoMIP climate-model output,
2. comparing intervention scenarios using matched models,
3. calculating regional climate and hazard indicators,
4. preserving individual model responses,
5. quantifying multimodel agreement and uncertainty, and
6. communicating regional SRM consequences through reproducible datasets and interactive tools.

The project does not evaluate whether SRM should be deployed and does not treat GeoMIP experiments as engineering specifications for real-world deployment.

Instead, it addresses a scientific question that remains relevant regardless of future policy decisions:

> **How would different forms of solar radiation modification alter climate risk in particular regions, and where are those projected changes robust across climate models?**

## References

1. Parson, E. A., & Keith, D. W. (2024). Solar Geoengineering: History, Methods, Governance, Prospects. *Annual Review of Environment and Resources, 49*, 337–366. doi:10.1146/annurev-environ-112321-081911.

2. Visioni, D., MacMartin, D. G., Kravitz, B., Boucher, O., Jones, A., Lurton, T., Martine, M., Mills, M. J., Nabat, P., Niemeier, U., Séférian, R., & Tilmes, S. (2021). Identifying the sources of uncertainty in climate model simulations of solar radiation modification with the G6sulfur and G6solar Geoengineering Model Intercomparison Project (GeoMIP) simulations. *Atmospheric Chemistry and Physics, 21*, 10039–10063. doi:10.5194/acp-21-10039-2021.

3. Jones, A., Haywood, J. M., Jones, A. C., Tilmes, S., Kravitz, B., & Robock, A. (2021). North Atlantic Oscillation response in GeoMIP experiments G6solar and G6sulfur: why detailed modelling is needed for understanding regional implications of solar radiation management. *Atmospheric Chemistry and Physics, 21*, 1287–1304. doi:10.5194/acp-21-1287-2021.

4. Ricke, K., Wan, J. S., Saenger, M., & Lutsko, N. J. (2023). Hydrological Consequences of Solar Geoengineering. *Annual Review of Earth and Planetary Sciences, 51*, 447–470. doi:10.1146/annurev-earth-031920-083456.

5. Feng, Z.-Q., Tan, M. L., Juneng, L., Tye, M. R., Xia, L.-L., & Zhang, F. (2025). Effects of solar radiation modification on precipitation extremes in Southeast Asia: Insights from the GeoMIP G6 experiments. *Advances in Climate Change Research, 16*(3), 591–605. doi:10.1016/j.accre.2025.04.009.

6. Dagon, K., & Schrag, D. P. (2017). Regional climate variability under model simulations of solar geoengineering. *Journal of Geophysical Research: Atmospheres, 122*, 12106–12121. doi:10.1002/2017JD027110.

7. Sun, L., Hurrell, J. W., Rasmussen, K. L., Summers, B., Sherman, E. A., & Kravitz, B. (2026). Assessing the impact of solar climate intervention on future U.S. weather using a convection-permitting WRF model. *Geoscientific Model Development, 19*, 2239–2256. doi:10.5194/gmd-19-2239-2026.

## Suggested citation of this project

Lewis, A. (2026). *SRM Regional Impact Explorer: Regional climate-impact analysis for solar radiation modification*. GitHub repository. Version 0.3 Phase 3 release.

---

*This literature review accompanies an active research project. It will be updated as the model ensemble, analyzed variables, and relevant SRM literature expand.*
