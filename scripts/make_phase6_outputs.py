"""Render the reproducible Phase 6 figures from compact result tables."""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from srm_explorer.geography import DOMAIN_LABELS,state_geometries

COLORS={"G6solar - SSP5-8.5":"#2166ac","G6sulfur - SSP5-8.5":"#b35806","G6solar - G6sulfur":"#542788"}
LABELS={"tasmax_mean":"JJA tasmax","pr_mean":"JJA precipitation"}

def boundaries(ax):
    for geometry in state_geometries().values():
      parts=getattr(geometry,"geoms",[geometry])
      for part in parts:
       x,y=part.exterior.xy; ax.plot(x,y,color="#333333",linewidth=.35,alpha=.8)
    ax.set_xlim(-100,-74); ax.set_ylim(24,38)

def native_figure(native,metric,path):
    data=native[(native.metric==metric)&(native.season=="JJA")&(native.comparison=="G6solar - G6sulfur")]
    models=sorted(data.model.unique()); bound=float(np.nanmax(abs(data.value)))
    fig,axes=plt.subplots(2,2,figsize=(12,7),constrained_layout=True,sharex=True,sharey=True)
    mesh=None
    for ax,model in zip(axes.flat,models,strict=True):
      s=data[data.model==model]; p=s.pivot(index="lat",columns="lon",values="value").sort_index()
      mesh=ax.pcolormesh(p.columns,p.index,p.values,cmap="RdBu_r",vmin=-bound,vmax=bound,shading="nearest"); boundaries(ax); ax.set_title(model)
    fig.colorbar(mesh,ax=axes,label=data.units.iloc[0],shrink=.85)
    fig.suptitle(f"{LABELS[metric]}: G6solar minus G6sulfur on each native grid")
    fig.savefig(path,dpi=300,bbox_inches="tight"); plt.close(fig)

def ensemble_figure(maps,metric,path):
    data=maps[(maps.metric==metric)&(maps.season=="JJA")]; comparisons=list(COLORS)
    means=data[data.comparison.isin(comparisons)]; bound=float(np.nanmax(abs(means["mean"])))
    fig,axes=plt.subplots(2,3,figsize=(14,7),constrained_layout=True,sharex=True,sharey=True)
    mesh=None
    for i,comparison in enumerate(comparisons):
      s=data[data.comparison==comparison]; p=s.pivot(index="lat",columns="lon",values="mean").sort_index(); mesh=axes[0,i].pcolormesh(p.columns,p.index,p.values,cmap="RdBu_r",vmin=-bound,vmax=bound,shading="nearest"); boundaries(axes[0,i]); axes[0,i].set_title(comparison)
      agreement=s.assign(signed=(s.positive_count-s.negative_count)/s.model_count).pivot(index="lat",columns="lon",values="signed").sort_index(); a=axes[1,i].pcolormesh(agreement.columns,agreement.index,agreement.values,cmap="PiYG",vmin=-1,vmax=1,shading="nearest"); boundaries(axes[1,i]); axes[1,i].set_title("Signed model agreement")
    fig.colorbar(mesh,ax=axes[0,:],label=means.units.iloc[0],shrink=.8); fig.colorbar(a,ax=axes[1,:],label="(positive - negative) / n",shrink=.8)
    fig.suptitle(f"Four-model common-grid {LABELS[metric]} responses and agreement")
    fig.savefig(path,dpi=300,bbox_inches="tight"); plt.close(fig)

def sensitivity_figure(results,path):
    domains=["original_box","southeast_land","gulf_coast","lower_mississippi","atlantic_southeast","appalachian_interior"]
    fig,axes=plt.subplots(1,2,figsize=(13,5.5),constrained_layout=True)
    for ax,metric in zip(axes,["tasmax_mean","pr_mean"],strict=True):
      data=results[(results.metric==metric)&(results.comparison=="G6solar - G6sulfur")]
      for season,marker in [("JJA","o"),("MAM","s"),("ANN","^")]:
       s=data[data.season==season].set_index("domain").loc[domains]; ax.errorbar(range(len(domains)),s["mean"],yerr=s["std"],marker=marker,capsize=3,label=season)
      ax.axhline(0,color="#333",linewidth=.8); ax.set_xticks(range(len(domains)),[DOMAIN_LABELS[d].replace(" states","") for d in domains],rotation=32,ha="right"); ax.set_title(metric); ax.set_ylabel(data.units.iloc[0]); ax.grid(axis="y",alpha=.2); ax.legend(frameon=False)
    fig.suptitle("Geographic sensitivity of G6solar minus G6sulfur")
    fig.savefig(path,dpi=300,bbox_inches="tight"); plt.close(fig)

def daily_figure(results,path):
    s=results[(results.comparison=="G6solar - G6sulfur")&(results.season=="JJA")].copy(); order=["txx","hwf_tx90_3d","rx5day","cdd"]; s=s.set_index("metric").loc[order]
    labels={"txx":"TXx","hwf_tx90_3d":"Heatwave days","rx5day":"Rx5day","cdd":"CDD"}
    fig,axes=plt.subplots(1,4,figsize=(13,4.5))
    for ax,(metric,row) in zip(axes,s.iterrows(),strict=True):
      ax.errorbar([0],[row.difference],yerr=[[row.difference-row.ci_lower],[row.ci_upper-row.difference]],fmt="o",color="#542788",capsize=5); ax.axhline(0,color="#333",linewidth=.8); ax.set_xticks([]); ax.set_title(labels[metric]); ax.set_ylabel(row.units); ax.text(.5,.03,f"Pooled yearly SD: {row.pooled_year_sd:.2f}",transform=ax.transAxes,ha="center",fontsize=8,bbox={"facecolor":"white","edgecolor":"none","alpha":.8}); ax.grid(axis="y",alpha=.2)
    fig.suptitle("MPI-ESM1-2-LR JJA land-only difference and block-bootstrap interval",y=.98)
    fig.tight_layout(rect=(0,0,1,.91))
    fig.savefig(path,dpi=300,bbox_inches="tight"); plt.close(fig)

def main():
    p=argparse.ArgumentParser(); p.add_argument("--docs",type=Path,default=ROOT/"docs"); a=p.parse_args(); d=a.docs
    native=pd.read_csv(d/"phase6_monthly_native_differences.csv.gz"); maps=pd.read_csv(d/"phase6_monthly_common_grid.csv.gz"); results=pd.read_csv(d/"phase6_domain_ensemble.csv"); daily=pd.read_csv(d/"phase6_daily_variability.csv")
    native_figure(native,"tasmax_mean",d/"phase6_tasmax_jja_native.png"); native_figure(native,"pr_mean",d/"phase6_pr_jja_native.png")
    ensemble_figure(maps,"tasmax_mean",d/"phase6_tasmax_jja_ensemble_maps.png"); ensemble_figure(maps,"pr_mean",d/"phase6_pr_jja_ensemble_maps.png")
    sensitivity_figure(results,d/"phase6_domain_sensitivity.png"); daily_figure(daily,d/"phase6_daily_land_variability.png")
    print("Wrote six Phase 6 figures")
if __name__=="__main__": main()
