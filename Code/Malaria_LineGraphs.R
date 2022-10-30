# Line Graphs for Malaria Vaccine-Averted Burden
# Created by Alisa Hamilton

library(readr)
library(dplyr)
library(stringr)
library(rqpd)
library(quantreg)
library(ggplot2)
library(scales)
library(reshape2)

# set directory
setwd("...")

# load data
Malaria <- read_csv("Results/Malaria_ByYear.csv")

# VE1 - VE 40% then step drop to 0% in year five
# VE2 - VE starts at 80%, dropping 20 percentage points per year
# VE3 - VE remains 40% for whole study period

# plot data
theme_update(plot.title = element_text(hjust = 0.5)) # center titles and resize text

# cases
CasesAvt = Malaria %>% filter(outcome %in% c('I'))
CasesAvtPlot <- ggplot(CasesAvt) + 
  geom_line(aes(y=est, x=year, color=VE), size=.75) +
  geom_ribbon(aes(ymin=min, ymax=max, x=year, fill=VE), alpha = 0.1) +
  ggtitle("Cumulative Cases Averted by Vaccine Efficacy (VE) Scenario\nWHO Africa Region 2021-2030") + 
  labs(x = "Year", y = "Cases Averted", color = 'Scenario', fill = 'Scenario') + 
  #scale_fill_discrete(name = "Scenario") +
  theme(axis.text.x = element_text(angle = 45, vjust = 1, hjust=1)) + 
  scale_x_continuous(labels=CasesAvt$year,breaks=CasesAvt$year) + 
  scale_y_continuous(breaks = seq(0, 200000000, by = 20000000), labels=comma) 
tiff("Results/Malaria_Cases_byYear.tiff", units="in", width=7, height=5, res=300)
print(CasesAvtPlot)
dev.off()

# resistant cases
ResCasesAvt = Malaria %>% filter(outcome %in% c('Ires'))
ResCasesAvtPlot <- ggplot(ResCasesAvt) + 
  geom_line(aes(y=est, x=year, color=VE), size=.75) +
  geom_ribbon(aes(ymin=min, ymax=max, x=year, fill=VE), alpha = 0.1) +
  ggtitle("Cumulative Resistant Cases Averted by Vaccine Efficacy (VE) Scenario\nWHO Africa Region 2021-2030") + 
  labs(x = "Year", y = " Resistant Cases Averted", color = 'Scenario', fill = 'Scenario') + 
  theme(axis.text.x = element_text(angle = 45, vjust = 1, hjust=1)) + 
  scale_x_continuous(labels=ResCasesAvt$year,breaks=ResCasesAvt$year) + 
  scale_y_continuous(breaks = seq(0, 2000000, by = 200000), labels=comma) 
tiff("Results/Malaria_ResCases_byYear.tiff", units="in", width=7, height=5, res=300)
print(ResCasesAvtPlot)
dev.off()

# deaths
DeathsAvt = Malaria %>% filter(outcome %in% c('D'))
DeathsAvtPlot <- ggplot(DeathsAvt) + 
  geom_line(aes(y=est, x=year, color=VE), size=.75) +
  geom_ribbon(aes(ymin=min, ymax=max, x=year, fill=VE), alpha = 0.1) +
  ggtitle("Cumulative Deaths Averted by Vaccine Efficacy (VE) Scenario\nWHO Africa Region 2021-2030") + 
  labs(x = "Year", y = "Deaths Averted", color = 'Scenario', fill = 'Scenario') + 
  theme(axis.text.x = element_text(angle = 45, vjust = 1, hjust=1)) + 
  scale_x_continuous(labels=DeathsAvt$year,breaks=DeathsAvt$year) + 
  scale_y_continuous(breaks = seq(0, 500000, by = 50000), labels=comma) 
tiff("Results/Malaria_Deaths_byYear.tiff", units="in", width=7, height=5, res=300)
print(DeathsAvtPlot)
dev.off()

# TFR scenarios
CasesAvt2 = Malaria %>% filter(outcome %in% c('Ires','Ires2'), VE %in% c('VE1'))
CasesAvt2$outcome[CasesAvt2$outcome %in% "Ires"] <- "Constant TFR"
CasesAvt2$outcome[CasesAvt2$outcome %in% "Ires2"] <- "TFR increases to 80%\nby 2030"
CasesAvt2Plot <- ggplot(CasesAvt2) + 
  geom_line(aes(y=est, x=year, color=outcome), size=.75) +
  geom_ribbon(aes(ymin=min, ymax=max, x=year, fill=outcome), alpha = 0.1) +
  ggtitle("Cumulative Resistant Cases Averted Under Two Resistance Scenarios\nWHO Africa Region 2021-2030") + 
  labs(x = "Year", y = "Resistant Cases Averted", color = 'Resistance Scenario', fill = 'Resistance Scenario') + 
  theme(axis.text.x = element_text(angle = 45, vjust = 1, hjust=1)) + 
  scale_x_continuous(labels=CasesAvt2$year,breaks=CasesAvt2$year) + 
  scale_y_continuous(breaks = seq(0, 10000000, by = 1000000), labels=comma) 
tiff("Results/Malaria_ResCases_byTFR.tiff", units="in", width=7, height=5, res=300)
print(CasesAvt2Plot)
dev.off()

