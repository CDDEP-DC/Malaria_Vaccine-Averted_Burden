library(rgdal)
library(ggplot2)
library(broom)
library(dplyr)
library(data.table)
library(viridis)

setwd("[File path]")

AvertData <- fread("Results/Malaria_ByCountry.csv") # Load Simulation Data
AfrPop <- fread("Data/CreateChoroplethPlotFiles/Pop1_byCountry.csv",header = T) # Load Population Data
AfrShape <- readOGR("Data/CreateChoroplethPlotFiles/afr_g2014_2013_0/afr_g2014_2013_0.shp")  # Load Shape File

AfrShape@data$id <- rownames(AfrShape@data) # Assign unique ID to merge
AfrShape@data <- AfrShape@data %>%                          
  left_join(AvertData) %>% 
  left_join(AfrPop, by = c("ISO3" = "Country Code")) # Combine Sim and Pop Data with Shapefile Data
AfrShape@data$Deaths_averted_pt <- AfrShape@data$D_avd_VE1 / AfrShape@data[,"Pop1"] * 1000 # Calculate density (per thousand persons)
AfrShape@data$Deaths_averted_pt_min <- AfrShape@data$D_avd_VE1_min / AfrShape@data[,"Pop1"] * 1000
AfrShape@data$Deaths_averted_pt_max <- AfrShape@data$D_avd_VE1_max / AfrShape@data[,"Pop1"] * 1000
AfrData <- fortify(AfrShape) %>% left_join(AfrShape@data) # Convert shape file object to data.frame for ggplot

Deaths_avertedplot <- ggplot() + 
  geom_polygon(data = AfrData, aes(long, y=lat, group=group, fill=Deaths_averted_pt), color="white") +
  coord_fixed() +
  # geom_text(data=AfrData, aes(x=long, y=lat, label=ISO3), color="white", size=3, alpha=0.6) +
  scale_fill_viridis(option="plasma", name = "Deaths Averted\nPer 1,000 Children") +
  ggtitle( "Deaths Averted per 1,000 Children At Risk by Country, WHO Africa Region (2021-2030)") +
  theme_void() +
  theme(plot.title = element_text(hjust = 0.5))

pdf(file="Results/Malaria_Map_Deaths.pdf", width = 10, height =8)
print(Deaths_avertedplot)
dev.off()

# Rank Averted per 1,000
countries <- as.data.frame(AfrShape@data$country)
averted_pt <- as.data.frame(AfrShape@data$Deaths_averted_pt)
averted_min <- as.data.frame(AfrShape@data$Deaths_averted_pt_min)
averted_max <- as.data.frame(AfrShape@data$Deaths_averted_pt_max)
Averted_per1000 <- cbind(countries, averted_pt, averted_min, averted_max)
