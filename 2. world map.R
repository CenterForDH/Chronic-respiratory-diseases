#GBD : CRD_Covid19
library(tidyverse) 
library(patchwork) 
library(data.table)
library(dplyr)
library(scales)
library(ggplot2)
library(rworldmap)
library(rworldxtra)
library(countrycode)
library(RColorBrewer)

#load custom function
##don't change!
source("gbd_functions - GBD 2021.R")

#Text
theme(text = element_text(family = "sans"))
windowsFonts(Times_New_Roman = windowsFont("TT Times New Roman"))
par(family = "Times_New_Roman")

########################################################################################
# Data
## Combine multiple data to one dataframe
#columns: list of all eligible columns
columns <- c("measure_id", "measure_name", "location_id", "location_name", "sex_id", "sex_name", "age_id", "age_name", 
             "cause_id", "cause_name", "rei_id", "rei_name", "metric_id", "metric_name", "year", "year_start", "year_end", 
             "val", "upper", "lower")

#dir: directory of data. All data must be located in the directory, and no other file should be in the directory. 
dir <- "data/"

#diroutput: directory of the combined dataset. 
diroutput <- "GBD_result"

#projectName: id of the project
projectName <- "CRD"

df <- data.frame(matrix(ncol = length(columns), nrow = 0))
names(df) <- columns

#load data one by one and combine - combine all separate excel files in the designated directory into one --> result outcome is gbd_data.txt
#there should be no other files except for GBD excels in /data/
for (i in 1:length(list.files(dir))){
  # i <- 1
  file <- paste0(dir,list.files(dir)[i])
  a <- fread(file, header = T, stringsAsFactors = F)
  if(any(!names(a)%in%columns)){
    warning(paste(i,"if(!any(!names(a)%in%columns))"))
  }
  
  for (col in columns) {
    if (!col %in% names(a)) {
      a[[col]] <- NA
    }
    if (!col %in% names(df)) {
      df[[col]] <- NA
    }
  }
  
  df <- rbind(df,a)
  
  if (i %% 10 == 0) {
    cat("i:", i,"; ")
  }
  rm(a,col)
}

#check data
names(df)
str(df)
data_summary(df)
head(df)

#save data
fwrite(df,paste0(diroutput,projectName,"_data.csv"))

########################################################################################
## 1.2. Load data
df <- fread("GBD_CRD_data.csv") 

data_summary(SDI)
########################################################################################

### World map
measure1 <- 1 #measure_id: 1 Deaths, 2 DALYs, 3 YLDs, 4 YLLs, 5 Prevalence, 6 Incidence

metric1 <- 3 #metric_id: 1 Number, 2 Percent, 3 Rate
sex1 <- 3 #sex_id: 1 Male, 2 Female, 3 Both
age1 <- 27 #age_id: 22 All ages, 27 Age-standardized
cause1 <- 509 # cause_id: COPD = 509, Pneumoconiosis = 510, Asthma = 515, ILD = 516
#location1 <- all
#location_id: 102 United States of America, 523~573: 51 states
#year1 <- 2021

datf1 <- cr_df %>% 
  filter(measure_id %in% measure1) %>%
  filter(metric_id %in% metric1) %>%
  filter(sex_id %in% sex1) %>% 
  filter(age_id %in% age1) %>%
  filter(cause_id %in% cause1)
#filter(location_id %in% location1) %>%
#filter(year %in% year1) 

data_summary(datf1)

###########################################################################################
# iso3c
datf1$iso3 <- countrycode(datf1$location_name, "country.name", "iso3c")

# save
fwrite(datf1,paste0(diroutput,projectName,"_COPD_changerate_age_standrized_deaths.csv"))

# Extract country names where the value of the iso3 column is missing
missing_iso3_df <- datf1 %>%
  filter(is.na(iso3)) %>%
  select(location_name)

# Confirming the country that will be included in the final table
lolo_df <- fread("lolo.csv", header=TRUE, fill=TRUE)

# Use semi_join to find values that overlap with the countries that go into the final table
common_values <- semi_join(missing_iso3_df, lolo_df, by = c("location_name" = "Location"))

need_iso3 <- unique(common_values$location_name)
print(need_iso3)
###########################################################################################

# Map Resolution
mapResolution <- "high"
worldMap <- getMap(resolution = mapResolution)

# Get a map object excluding Antarctica
worldMap <- worldMap[worldMap$ISO_A3 != "ATA", ]
par(mai=c(0,0,0.2,0),xaxs="i",yaxs="i")
plot(worldMap, xlim = c(-180, 180), ylim = c(-90, 90), asp = 1, col = "#f2f2f2", border = "#ffffff", lwd = 0.5)
merged_map <- joinCountryData2Map(datf1, joinCode = "ISO3", nameJoinColumn = "iso3", mapResolution = "high") 

# Get a map object excluding Antarctica
merged_map <- merged_map[merged_map$ISO_A3 != "ATA", ]

# Plot global map
par(family = "Times_New_Roman")

# Replace null values with NA
worldMap[is.null(worldMap)] <- NA

# Replace NA values with white
na_color <- "white"
data <- ifelse(is.na(worldMap$prevalence), na_color, worldMap$prevalence)

# color fix
colourPalette<-c("light yellow","#C7E0B7","#84C6B8","#43B7C6","#2A81B9","#293990")

###########################################################################################

# Get a global map
# Automatically add a legend, “val” is the result value of the filtered data
mapCountryData(merged_map, nameColumnToPlot = "val", addLegend = TRUE, numCats =6, 
               colourPalette = colourPalette, borderCol = "black", missingCountryCol='Gray 90')
## Check legend section
map_result1 <- mapCountryData(merged_map, nameColumnToPlot = "val", addLegend = TRUE, numCats =6, 
                              colourPalette = colourPalette, borderCol = "black", missingCountryCol='Gray 90')
print(map_result1$cutVector)


## Data and section definition
cuts <- c(0, 1000, 1500, 2000, 2500, 3000, 3500) #for prevalence

mapCountryData(merged_map, nameColumnToPlot = "val", addLegend = TRUE, numCats =6, catMethod = cuts, 
               colourPalette = colourPalette, borderCol = "black", missingCountryCol='Gray 90')

## Final worldmap output version
mapCountryData(merged_map, nameColumnToPlot = "val", addLegend = FALSE, numCats =6, catMethod = cuts, 
               colourPalette = colourPalette, borderCol = "black", missingCountryCol='Gray 90', 
               mapTitle = "Age-standardized COPD deaths change rate (1990-2021)")

# Get a regional map
## Caribbean and Central America
mapCountryData(merged_map, nameColumnToPlot = "val", addLegend = FALSE,numCats =6,catMethod = cuts, colourPalette = colourPalette,borderCol = "black",missingCountryCol='Gray 90',xlim=c(-90,-60),ylim=c(5,30))
## Persian Gulf
mapCountryData(merged_map, nameColumnToPlot = "val", addLegend = FALSE,numCats =6,catMethod = cuts, colourPalette = colourPalette,borderCol = "black",missingCountryCol='Gray 90',xlim=c(45,65),ylim=c(22,30))
## Balkan Peninsula
mapCountryData(merged_map, nameColumnToPlot = "val", addLegend = FALSE,numCats =6,catMethod = cuts, colourPalette = colourPalette,borderCol = "black",missingCountryCol='Gray 90',xlim=c(18, 30),ylim=c(39,48))
## Southeast Asia
mapCountryData(merged_map, nameColumnToPlot = "val", addLegend = FALSE,numCats =6,catMethod = cuts, colourPalette = colourPalette,borderCol = "black",missingCountryCol='Gray 90',xlim=c(95,145),ylim=c(-10,25))
## West Africa
mapCountryData(merged_map, nameColumnToPlot = "val", addLegend = FALSE,numCats =6,catMethod = cuts, colourPalette = colourPalette,borderCol = "black",missingCountryCol='Gray 90',xlim=c(-20,20),ylim=c(-5,20))
## Eastern Mediterranean
mapCountryData(merged_map, nameColumnToPlot = "val", addLegend = FALSE,numCats =6,catMethod = cuts, colourPalette = colourPalette,borderCol = "black",missingCountryCol='Gray 90',xlim=c(25,40),ylim=c(30,45))
## Northern Europe
mapCountryData(merged_map, nameColumnToPlot = "val", addLegend = FALSE,numCats =6,catMethod = cuts, colourPalette = colourPalette,borderCol = "black",missingCountryCol='Gray 90',xlim=c(-10,30),ylim=c(50,70))

