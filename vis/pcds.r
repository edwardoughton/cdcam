###VISUALISE MODEL OUTPUTS###
#install.packages("tidyverse")
library(tidyverse)
# library(dplyr)
#install.packages("maptools")
library(maptools)
#install.packages("rgeos")
library(rgeos)
# install.packages("maps")
library(maps)
#install.packages("Cairo")
library(Cairo)
# install.packages('rgdal')
library(rgdal)
#install.packages("ggmap")
library(ggmap)
library(scales)
library(RColorBrewer)
#library(ineq)
#install.packages("ggpubr")
library(ggpubr)       
# install.packages("arules")
library(arules)
# install.packages("ggpolypath")
library(ggpolypath)

data_input_directory <- "D:\\Github\\cdcam\\data\\intermediate"
data_directory <- "D:\\Github\\cdcam\\results"
shapes_directory <- "D:\\Github\\cdcam\\data\\shapes\\"
output_directory <- "D:\\Github\\cdcam\\vis\\figures"

setwd(data_directory)

metric_files <- list.files(data_directory, pattern="*.csv")

#subset those metric files
metric_files <- metric_files[grep("^spend*", metric_files)]

#initialised empty dataframe
empty_df <- data.frame(year=numeric(),
                       area_id=character(), 
                       lad_id=character(),
                       population_density=numeric(),
                       item=character(),
                       cost=numeric())

import_function = lapply(metric_files, function(x) {
  DF <- read.csv(x, header = T, sep = ",")
  DF_Merge <- merge(empty_df, DF, all = T)
  DF_Merge$file <- as.factor(x)
  return(DF_Merge)})

all_scenarios <- do.call(rbind, import_function)

all_scenarios <- all_scenarios[which(
  all_scenarios$lad_id== 'E06000031' |
    all_scenarios$lad_id== 'E07000005' |
    all_scenarios$lad_id== 'E07000006' |
    all_scenarios$lad_id== 'E07000007' |
    all_scenarios$lad_id== 'E06000032' |
    all_scenarios$lad_id== 'E06000042' |
    all_scenarios$lad_id== 'E06000055' |
    all_scenarios$lad_id== 'E06000056' |
    all_scenarios$lad_id== 'E07000004' |
    all_scenarios$lad_id== 'E07000008' |
    all_scenarios$lad_id== 'E07000009' |
    all_scenarios$lad_id== 'E07000010' |
    all_scenarios$lad_id== 'E07000011' |
    all_scenarios$lad_id== 'E07000012' |
    all_scenarios$lad_id== 'E07000150' |
    all_scenarios$lad_id== 'E07000151' |
    all_scenarios$lad_id== 'E07000152' |
    all_scenarios$lad_id== 'E07000153' |
    all_scenarios$lad_id== 'E07000154' |
    all_scenarios$lad_id== 'E07000155' |
    all_scenarios$lad_id== 'E07000156' |
    all_scenarios$lad_id== 'E07000177' |
    all_scenarios$lad_id== 'E07000178' |
    all_scenarios$lad_id== 'E07000179' |
    all_scenarios$lad_id== 'E07000180' |
    all_scenarios$lad_id== 'E07000181' 
),]

all_scenarios <- all_scenarios %>% separate(file, c("file_type", "scenario", "data_scenario", "strategy"), "_", remove = FALSE)

all_scenarios$geotype[all_scenarios$population_density >= 7959] = 'Urban'
all_scenarios$geotype[all_scenarios$population_density >= 3119 & all_scenarios$population_density < 7959] = 'Suburban 1'
all_scenarios$geotype[all_scenarios$population_density >= 782 & all_scenarios$population_density < 3119] = 'Suburban 2'
all_scenarios$geotype[all_scenarios$population_density >= 112 & all_scenarios$population_density < 782] = 'Rural 1'
all_scenarios$geotype[all_scenarios$population_density >= 47 & all_scenarios$population_density < 112] = 'Rural 2'
all_scenarios$geotype[all_scenarios$population_density >= 25 & all_scenarios$population_density < 47] = 'Rural 3'
all_scenarios$geotype[all_scenarios$population_density < 25] = 'Rural 4'


all_scenarios$scenario = factor(all_scenarios$scenario, levels=c("base",
                                                                 "0-unplanned",
                                                                 "1-new-cities-from-dwellings",
                                                                 "2-expansion",
                                                                 "3-new-cities23-from-dwellings",
                                                                 "4-expansion23"),
                                                        labels=c("Baseline",
                                                                 "Unplanned",
                                                                 "New Cities",
                                                                 "Expansion",
                                                                 "New Cities 23k",
                                                                 "Expansion 23k"))

all_scenarios$data_scenario = factor(all_scenarios$data_scenario, levels=c("low",
                                                                           "base",
                                                                           "high"),
                                                                 labels=c("Low",
                                                                          "Baseline",
                                                                          "High"))

all_scenarios$geotype = factor(all_scenarios$geotype, levels=c("Urban",
                                                               "Suburban 1",
                                                               "Suburban 2",
                                                               "Rural 1",
                                                               "Rural 2",
                                                               "Rural 3",
                                                               "Rural 4"))

all_scenarios$strategy = factor(all_scenarios$strategy, levels=c("minimal.csv",
                                                                 "macrocell.csv",
                                                                 "small-cell.csv",
                                                                 "small-cell-and-spectrum.csv"),                                                                
                                                        labels=c("No Investment",
                                                                 "Spectrum Integration",
                                                                 "Small Cells",
                                                                 "Spectrum and Small Cells")
)

all_scenarios$item = factor(all_scenarios$item, levels=c("upgrade_to_lte",
                                                                 "carrier_700",
                                                                 "carrier_3500",
                                                                 "carrier_26000",
                                                                 "small_cells"),                                                                
                                                        labels=c("Upgrade to LTE",
                                                                 "Add 700 MHz",
                                                                 "Add 3.5 GHz",
                                                                 "Add 26 GHz",
                                                                 "Small Cell")
)

all_scenarios <- all_scenarios[which(all_scenarios$data_scenario== 'Baseline'), ]

costs <- ggplot(all_scenarios, aes(x = factor(year), y = (cost/1000000), fill=item)) + 
  scale_fill_brewer(palette="Spectral", name = expression('Cost Type'), direction=1) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
  geom_bar(stat="identity") +  labs(title = "Annual Investment Over The Study Period",
                                    subtitle = "Results reported by scenario, strategy and cost item",
                                    x = NULL, y = "Investment Cost (Millions of Pounds)") +
  facet_grid(scenario~strategy) 

### EXPORT TO FOLDER
setwd(output_directory)
tiff('costs.tiff', units="in", width=8.5, height=8.5, res=500)
print(costs)
dev.off()

costs_geotypes <- ggplot(all_scenarios, aes(x = factor(year), y = (cost/1000000), fill=geotype)) + 
  scale_fill_brewer(palette="Spectral", name = expression('Geotype')) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
  geom_bar(stat="identity") +  labs(title = "Annual Investment Over The Study Period",
                                    subtitle = "Results reported by scenario, strategy and geotype",
                                    x = NULL, y = "Investment Cost (Millions of Pounds)") +
  facet_grid(scenario~strategy) 


### EXPORT TO FOLDER
setwd(output_directory)
tiff('costs_geotypes.tiff', units="in", width=8.5, height=8.5, res=800)
print(costs_geotypes)
dev.off()
pdf('costs_geotypes.pdf', width=8.5, height=8.5)
print(costs_geotypes)
dev.off()

###################################################################################
#### PCD Geotypes
###################################################################################

data_input_directory <- "D:\\Github\\cdcam\\data\\intermediate\\_processed_postcode_sectors.csv"

postcode_sectors <- read.csv(data_input_directory)

postcode_sectors <- postcode_sectors[which(
  postcode_sectors$lad== 'E06000031' |
    postcode_sectors$lad== 'E07000005' |
    postcode_sectors$lad== 'E07000006' |
    postcode_sectors$lad== 'E07000007' |
    postcode_sectors$lad== 'E06000032' |
    postcode_sectors$lad== 'E06000042' |
    postcode_sectors$lad== 'E06000055' |
    postcode_sectors$lad== 'E06000056' |
    postcode_sectors$lad== 'E07000004' |
    postcode_sectors$lad== 'E07000008' |
    postcode_sectors$lad== 'E07000009' |
    postcode_sectors$lad== 'E07000010' |
    postcode_sectors$lad== 'E07000011' |
    postcode_sectors$lad== 'E07000012' |
    postcode_sectors$lad== 'E07000150' |
    postcode_sectors$lad== 'E07000151' |
    postcode_sectors$lad== 'E07000152' |
    postcode_sectors$lad== 'E07000153' |
    postcode_sectors$lad== 'E07000154' |
    postcode_sectors$lad== 'E07000155' |
    postcode_sectors$lad== 'E07000156' |
    postcode_sectors$lad== 'E07000177' |
    postcode_sectors$lad== 'E07000178' |
    postcode_sectors$lad== 'E07000179' |
    postcode_sectors$lad== 'E07000180' |
    postcode_sectors$lad== 'E07000181' 
),]

postcode_sectors$pop_density_km2 <- postcode_sectors$population / postcode_sectors$area_km2

postcode_sectors$geotype[postcode_sectors$pop_density_km2 >= 7959] = 'Urban'
postcode_sectors$geotype[postcode_sectors$pop_density_km2 >= 3119 & postcode_sectors$pop_density_km2 < 7959] = 'Suburban 1'
postcode_sectors$geotype[postcode_sectors$pop_density_km2 >= 782 & postcode_sectors$pop_density_km2 < 3119] = 'Suburban 2'
postcode_sectors$geotype[postcode_sectors$pop_density_km2 >= 112 & postcode_sectors$pop_density_km2 < 782] = 'Rural 1'
postcode_sectors$geotype[postcode_sectors$pop_density_km2 >= 47 & postcode_sectors$pop_density_km2 < 112] = 'Rural 2'
postcode_sectors$geotype[postcode_sectors$pop_density_km2 >= 25 & postcode_sectors$pop_density_km2 < 47] = 'Rural 3'
postcode_sectors$geotype[postcode_sectors$pop_density_km2 < 25] = 'Rural 4'

subset <- postcode_sectors #unique(all_scenarios %>% select(area_id, lad_id, geotype, area))

names(subset)[names(subset) == "area_id"] <- "id"
subset$id <- as.character(subset$id)

setwd(shapes_directory)
all.shp <- readOGR(".", "arc_postcode_sectors")
all.shp <- fortify(all.shp, region = "StrSect")

all.shp$rank <- NA
all.shp$rank <- 1:nrow(all.shp)
all.shp <- merge(subset, all.shp, by = "id")
all.shp <- all.shp[order(all.shp$rank), ]

all.shp$geotype = ordered(
  all.shp$geotype,
  levels=c(           
          'Rural 4',
          'Rural 3',
          'Rural 2',
          'Rural 1',      
          'Suburban 2',
          'Suburban 1',
          'Urban'
  )
)

geotypes <- ggplot() +
  geom_polypath(
    data = all.shp,
    aes(
      x = long,
      y = lat,
      group = group,
      fill = geotype
    ),
    colour = "grey",
    size = 0.1
  ) +
  coord_equal() +
  scale_fill_brewer(
    palette = "Spectral",
    name = expression("Geotype"),
    direction = -1,
    drop = FALSE
  ) +
  theme(
    legend.text = element_text(size = 8),
    legend.position = "right",
    legend.title = element_text(size = 9),
    plot.title = element_text(size = 10),
    axis.text = element_blank(),
    axis.ticks = element_blank(),
    axis.title = element_blank(),
    axis.title.x = element_blank()
  ) +
  guides(fill = guide_legend(reverse = TRUE)) +
  labs(title = 'Postcode sector by geotype') 


### EXPORT TO FOLDER
setwd(output_directory)
tiff('geotypes.tiff', units="in", width=8, height=8.5, res=900)
print(geotypes)
dev.off()

data_input_directory <- "D:\\Github\\cdcam\\results\\pcd_metrics_base_base_minimal.csv"

pcds <- read.csv(data_input_directory)

subset <- pcds[which(pcds$year== '2020'), ]

names(subset)[names(subset) == "area_id"] <- "id"
subset$id <- as.character(subset$id)

setwd(shapes_directory)
all.shp <- readOGR(".", "arc_postcode_sectors")
all.shp <- fortify(all.shp, region = "StrSect")

all.shp$rank <- NA
all.shp$rank <- 1:nrow(all.shp)
all.shp <- merge(subset, all.shp, by = "id")
all.shp <- all.shp[order(all.shp$rank), ]

all.shp$capacity <- cut(all.shp$capacity, breaks=c(-Inf,10,20,30,40,50,60,70,80,Inf))  

all.shp$capacity = ordered(
  all.shp$capacity,
  levels=c(           
    '(-Inf,10]',
    '(10,20]',
    '(20,30]',
    '(30,40]',
    '(40,50]',
    '(50,60]',
    '(60,70]',
    '(70,80]',
    '(80, Inf]'
  ),
  labels=c(
    '0-10',
    '10-20',
    '20-30',
    '30-40',
    '40-50',
    '50-60',
    '60-70',
    '70-80',
    '80+'
  )
)

capacity <- ggplot() +
  geom_polypath(
    data = all.shp,
    aes(
      x = long,
      y = lat,
      group = group,
      fill = capacity
    ),
    colour = "grey",
    size = 0.1
  ) +
  coord_equal() +
  scale_fill_brewer(
    palette = "Spectral",
    name = expression("Mbps" ~ km ^ 2),
    direction = -1,
    drop = FALSE
  ) +
  theme(
    legend.text = element_text(size = 8),
    legend.position = "right",
    legend.title = element_text(size = 9),
    plot.title = element_text(size = 10),
    axis.text = element_blank(),
    axis.ticks = element_blank(),
    axis.title = element_blank(),
    axis.title.x = element_blank()
  ) +
  guides(fill = guide_legend(reverse = TRUE)) +
  labs(title = 'Postcode sector by mean cell edge capacity') 


### EXPORT TO FOLDER
setwd(output_directory)
tiff('capacity_4G.tiff', units="in", width=8, height=8.5, res=900)
print(capacity)
dev.off()


################################################################################
####### GGARRANGE #########
################################################################################

initial_graphic <- ggarrange(
                    geotypes, 
                    capacity,
                    labels = NULL,
                    ncol = 1,
                    nrow = 2,
                    align = "v")

### EXPORT TO FOLDER
setwd(output_directory)
tiff('initial_graphic.tiff', units="in", width=8, height=8.5, res=700)
print(initial_graphic)
dev.off()






