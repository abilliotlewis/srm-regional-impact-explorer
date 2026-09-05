# Daily-extremes placement decision

## Recommendation

Place the Phase 5 and Phase 6 daily-extreme analysis in the **supplementary information only**, with at most one short main-text Discussion sentence pointing to it.

## Rationale

The daily analysis has real scientific value because it tests whether monthly-mean temperature and precipitation differences translate into heat, heavy-rainfall, and dry-spell indices. It also retains year-level products and land-only spatial context. However, it uses only MPI-ESM1-2-LR `r2i1p1f1` on grid `gn`. Giving it a central Results subsection would blur the paper's strongest design feature: the matched four-model monthly ensemble.

The MPI case does not simply reproduce a uniform intervention ordering. Over Southeast land, the JJA G6solar-minus-G6sulfur climatological differences and independently resampled 95% intervals are:

| Index | Mean difference | 95% interval | Interpretation |
|---|---:|---:|---|
| TXx | -0.416 degrees Celsius | -0.800 to +0.028 | Interval includes zero |
| Heatwave days | -7.019 days | -12.887 to -1.384 | Interval excludes zero below |
| Rx5day | -2.126 mm | -4.760 to +0.435 | Interval includes zero |
| CDD | -0.874 days | -2.709 to +1.497 | Interval includes zero |

Annual heatwave days also differ (-35.970 days, interval -52.848 to -18.461), whereas annual TXx, Rx5day, and CDD intervals include zero. This is useful supporting evidence that a monthly-mean precipitation ordering does not guarantee a similarly clear extreme-rainfall or drought ordering. It does not establish a multi-model daily-extreme response.

## Suggested manuscript treatment

Main-text Discussion sentence:

> A supplementary MPI-ESM1-2-LR case study indicates that intervention differences in monthly means do not translate uniformly across daily indices, reinforcing the need for a multi-model daily analysis before drawing conclusions about extremes.

Supplementary content should include the full index definitions, threshold baseline and spell-boundary conventions, native-calendar handling, annual and seasonal sample rules, land-only maps, and year-to-year variability. Every table and caption should say “single model, single member.”

Do not describe these results as confirmation of the four-model ensemble. Their appropriate role is a process-relevant sensitivity case and a motivation for future work.
