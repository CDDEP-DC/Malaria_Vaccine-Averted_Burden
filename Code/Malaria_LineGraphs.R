# Line Graphs for HIV/Malaria vaccine averted health burden project
# Created by Alisa Hamilton; Updated 18 Feb 2022

library(readr)
library(dplyr)
library(stringr)
library(rqpd)
library(quantreg)
library(ggplot2)
library(scales)
library(reshape2)

# set directory
setwd("/Users/alisahamilton/Library/CloudStorage/OneDrive-CenterforDiseaseDynamics,Economics&Policy/HIV Malaria Vaccine/2. Code/")

# load data
Malaria <- read_csv("Results/Malaria_ByYear.csv")

# VE1 - VE 40% then step drop to 0% in year five
# VE2 - VE starts at 80%, dropping 20 percentage points per year
# VE3 - VE remains 40% for whole study period


# Cumulative cases averted
CasesAvt = Malaria %>% filter(outcome %in% c('I_avd_'))
CasesAvtPlot <- ggplot(CasesAvt) + 
  geom_line(aes(y=est, x=year, color=VE), size=.75) +
  geom_ribbon(aes(ymin=min, ymax=max, x=year, fill=VE), alpha = 0.1) +
  ggtitle("Cumulative Cases Averted per 1,000 Children\nby Vaccine Efficacy (VE) Scenario\nWHO Africa Region 2021-2030") + 
  labs(x = "Year", y = "Cases Averted per 1,000", color = 'Scenario', fill = 'Scenario') + 
  #scale_fill_discrete(name = "Scenario") +
  theme(plot.title = element_text(hjust = 0.5)) +
  theme(axis.text.x = element_text(angle = 45, vjust = 1, hjust=1)) + 
  scale_x_continuous(labels=CasesAvt$year,breaks=CasesAvt$year) + 
  scale_y_continuous(breaks = seq(0, 500, by = 100), labels=comma) 
tiff("Results/Malaria_CasesAvt_byYear.tiff", units="in", width=7, height=5, res=300)
print(CasesAvtPlot)
dev.off()

# Cumulative resistant cases averted
ResCasesAvt = Malaria %>% filter(outcome %in% c('Ires_avd_'))
ResCasesAvtPlot <- ggplot(ResCasesAvt) + 
  geom_line(aes(y=est, x=year, color=VE), size=.75) +
  geom_ribbon(aes(ymin=min, ymax=max, x=year, fill=VE), alpha = 0.1) +
  ggtitle("Cumulative Resistant Cases Averted per 1,000 Children\nby Vaccine Efficacy (VE) Scenario\nWHO Africa Region 2021-2030") + 
  theme(plot.title = element_text(hjust = 0.5)) +
  labs(x = "Year", y = " Resistant Cases Averted per 1,000", color = 'Scenario', fill = 'Scenario') + 
  theme(axis.text.x = element_text(angle = 45, vjust = 1, hjust=1)) + 
  scale_x_continuous(labels=ResCasesAvt$year,breaks=ResCasesAvt$year) + 
  scale_y_continuous(breaks = seq(0, 10, by = 0.5), labels=comma) 
tiff("Results/Malaria_ResCasesAvt_byYear.tiff", units="in", width=7, height=5, res=300)
print(ResCasesAvtPlot)
dev.off()

# Cumulative deaths averted
DeathsAvt = Malaria %>% filter(outcome %in% c('D_avd_'))
DeathsAvtPlot <- ggplot(DeathsAvt) + 
  geom_line(aes(y=est, x=year, color=VE), size=.75) +
  geom_ribbon(aes(ymin=min, ymax=max, x=year, fill=VE), alpha = 0.1) +
  ggtitle("Cumulative Deaths Averted per 1,000 Children\nby Vaccine Efficacy (VE) Scenario\nWHO Africa Region 2021-2030") + 
  labs(x = "Year", y = "Deaths Averted per 1,000", color = 'Scenario', fill = 'Scenario') + 
  theme(axis.text.x = element_text(angle = 45, vjust = 1, hjust=1)) + 
  theme(plot.title = element_text(hjust = 0.5)) +
  scale_x_continuous(labels=DeathsAvt$year,breaks=DeathsAvt$year) + 
  scale_y_continuous(breaks = seq(0, 2, by = .25), labels=comma) 
tiff("Results/Malaria_DeathsAvt_byYear.tiff", units="in", width=7, height=5, res=300)
print(DeathsAvtPlot)
dev.off()

# Cumulative cases - baseline and all VE scenarios
CasesAll = Malaria %>% filter(outcome %in% c('I_'))
CasesAllPlot <- ggplot(CasesAll) + 
  geom_line(aes(y=est, x=year, color=VE), size=.75) +
  geom_ribbon(aes(ymin=min, ymax=max, x=year, fill=VE), alpha = 0.1) +
  ggtitle("Cumulative Cases per 1,000 Children\nby Baseline and Vaccine Efficacy (VE) Scenario\nWHO Africa Region 2021-2030") + 
  labs(x = "Year", y = "Cases per 1,000", color = 'Scenario', fill = 'Scenario') + 
  #scale_fill_discrete(name = "Scenario") +
  theme(axis.text.x = element_text(angle = 45, vjust = 1, hjust=1)) + 
  theme(plot.title = element_text(hjust = 0.5)) +
  scale_x_continuous(labels=CasesAll$year,breaks=CasesAll$year) + 
  scale_y_continuous(breaks = seq(0, 2000, by = 200), labels=comma) 
tiff("Results/Malaria_CasesAll_byYear.tiff", units="in", width=7, height=5, res=300)
print(CasesAllPlot)
dev.off()

# Cumulative resistant cases - baseline and all VE scenarios
ResCasesAll = Malaria %>% filter(outcome %in% c('Ires_'))
ResCasesAllPlot <- ggplot(ResCasesAll) + 
  geom_line(aes(y=est, x=year, color=VE), size=.75) +
  geom_ribbon(aes(ymin=min, ymax=max, x=year, fill=VE), alpha = 0.1) +
  ggtitle("Cumulative Resistant Cases per 1,000 Children\nby Baseline and Vaccine Efficacy (VE) Scenario\nWHO Africa Region 2021-2030") + 
  theme(plot.title = element_text(hjust = 0.5)) +
  labs(x = "Year", y = " Resistant Cases per 1,000", color = 'Scenario', fill = 'Scenario') + 
  theme(axis.text.x = element_text(angle = 45, vjust = 1, hjust=1)) + 
  scale_x_continuous(labels=ResCasesAll$year,breaks=ResCasesAll$year) + 
  theme(plot.title = element_text(hjust = 0.5)) +
  scale_y_continuous(breaks = seq(0, 20, by = 1), labels=comma) 
tiff("Results/Malaria_ResCasesAll_byYear.tiff", units="in", width=7, height=5, res=300)
print(ResCasesAllPlot)
dev.off()

# Cumulative deaths - baseline and all VE scenarios
DeathsAll = Malaria %>% filter(outcome %in% c('D_'))
DeathsAllPlot <- ggplot(DeathsAll) + 
  geom_line(aes(y=est, x=year, color=VE), size=.75) +
  geom_ribbon(aes(ymin=min, ymax=max, x=year, fill=VE), alpha = 0.1) +
  ggtitle("Cumulative Deaths per 1,000 Children\nby Baseline and Vaccine Efficacy (VE) Scenario\nWHO Africa Region 2021-2030") + 
  labs(x = "Year", y = "Deaths Averted per 1,000", color = 'Scenario', fill = 'Scenario') + 
  theme(axis.text.x = element_text(angle = 45, vjust = 1, hjust=1)) + 
  scale_x_continuous(labels=DeathsAll$year,breaks=DeathsAll$year) + 
  theme(plot.title = element_text(hjust = 0.5)) +
  scale_y_continuous(breaks = seq(0, 5, by = 1), labels=comma) 
tiff("Results/Malaria_DeathsAll_byYear.tiff", units="in", width=7, height=5, res=300)
print(DeathsAllPlot)
dev.off()

# Cumulative resistant cases averted by delayed parasite clearance (DPC) scenario
CasesAvt2 = Malaria %>% filter(outcome %in% c('Ires_avd_','Ires2_avd_'), VE %in% c('VE1'))
CasesAvt2$outcome[CasesAvt2$outcome %in% "Ires_avd_"] <- "Constant DPC"
CasesAvt2$outcome[CasesAvt2$outcome %in% "Ires2_avd_"] <- "DPC increases to 80%\nby 2030"
CasesAvt2Plot <- ggplot(CasesAvt2) + 
  geom_line(aes(y=est, x=year, color=outcome), size=.75) +
  geom_ribbon(aes(ymin=min, ymax=max, x=year, fill=outcome), alpha = 0.1) +
  ggtitle("Cumulative Resistant Cases Averted per 1,000 Children\nby Drug Resistance Scenario\nWHO Africa Region 2021-2030") + 
  theme(plot.title = element_text(hjust = 0.5)) +
  labs(x = "Year", y = "Resistant Cases Averted per 1,000", color = 'Resistance Scenario', fill = 'Resistance Scenario') + 
  theme(axis.text.x = element_text(angle = 45, vjust = 1, hjust=1)) + 
  scale_x_continuous(labels=CasesAvt2$year,breaks=CasesAvt2$year) + 
  scale_y_continuous(breaks = seq(0, 20, by = 2), labels=comma) 
tiff("Results/Malaria_ResCases_byDPC.tiff", units="in", width=7, height=5, res=300)
print(CasesAvt2Plot)
dev.off()



