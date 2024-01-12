import pandas as pd
import os
import requests
import API_KEYS

def readWeatherData(readDirectory, csvFile, dfCSVFile):
    
    directory = os.fsencode(readDirectory)
    columns = ''
    pdCol = []
    multiplier = 0

    filenameByte = os.path.join(directory, os.listdir(directory)[0])
    filename = filenameByte.decode('utf-8')

    with open(filename, "r", encoding='utf-8', errors='ignore') as t:
        lines = t.readlines()
        
        for line in lines:
            if 'TG,' in line:
                columns = 'STAID, SOUID,    DATE,   TG, Q_TG\n'
                pdCol = ['STAID','SOUID','DATE','TG','Q_TG']
                multiplier = 0.1
                break
            elif 'SD' in line:
                columns = 'STAID, SOUID,    DATE,   SD, Q_SD\n'
                pdCol = ['STAID','SOUID','DATE','SD','Q_SD']
                multiplier = 1
                break
            elif 'RR' in line:
                columns = 'STAID, SOUID,    DATE,   RR, Q_RR\n'
                pdCol = ['STAID','SOUID','DATE','RR','Q_RR']
                multiplier = .1
                break

    with open(csvFile, "w") as c:
        c.write(columns)

        for file in os.listdir(directory):
            filenameByte = os.path.join(directory, file)

            if os.path.isfile(filenameByte):
                filename = filenameByte.decode('utf-8')
                with open(filename, "r", encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    lineNumber = 0
                    
                    for line in lines:
                        if ',20' in line:
                            break
                        lineNumber = lineNumber + 1
                    
                    for line in lines[lineNumber:]:
                        c.write(line)

    weatherData = pd.read_csv(csvFile)
    weatherData.columns = pdCol
    weatherDataFilter = weatherData[weatherData[pdCol[4]] != 9]
    weatherDataFilter = weatherDataFilter[weatherDataFilter[pdCol[4]] != 1]
    weatherDataFilter['DATE'] = pd.to_datetime(weatherDataFilter['DATE'], format='%Y%m%d')
    weatherDataFilter = weatherDataFilter.drop(columns=['SOUID', pdCol[4]])
    weatherDataFilter[pdCol[3]] = weatherDataFilter[pdCol[3]] * multiplier

    weatherDataFilter.to_csv(dfCSVFile, index=False)

    return weatherDataFilter

def readStationData():
    with open("Data/Weather/AverageDailyTemp/sources.txt", "r") as f:
        lines = f.readlines()

    with open("Data/Weather/AverageDailyTemp/sources.txt", "w") as f:
        lineNumber = 0
        
        for line in lines:
            if 'STAID, SOUID' in line:
                break
            lineNumber = lineNumber + 1
        
        for line in lines[lineNumber:]:
            f.write(line)
    
    stationData = pd.read_csv("Data/Weather/AverageDailyTemp/sources.txt", on_bad_lines='warn')

    return stationData

#commented out to avoid accidental API calls that cost money
# def getLocation(lati, long):

#     lat = lati.split(':')
#     latitude = float(lat[0]) + (int(lat[1])/60) + (int(lat[2])/3600)
#     lng = long.split(':')
#     longitude = float(lng[0]) + (int(lng[1])/60) + (int(lng[2])/3600)

#     url = 'https://maps.googleapis.com/maps/api/geocode/json?latlng=' + str(latitude) + ',' + str(longitude) + '&result_type=administrative_area_level_1|country&key=' + API_KEY
#     googleResponse = requests.post(url)
#     gr = googleResponse.json()

#     city = ''
#     country = ''

#     if (gr['status'] == 'OK'):
#         for e in gr['results'][0]['address_components']:
#             for type in e['types']:
#                 if (type == 'administrative_area_level_1'):
#                     city = e['long_name']
#                     break
#                 elif (type == 'country'):
#                     country = e['long_name']
#                     break
                
#     return  city + ', ' + country

def createStationCSV():
    stationData = readStationData()
    stationData.columns = ['STAID','SOUID','SOUNAME','CN','LAT','LON','HGHT','ELEI','START','STOP','PARID','PARNAME']
    stationDataFiltered = stationData.drop(columns=['SOUNAME', 'HGHT', 'ELEI', 'PARID', 'PARNAME', 'START', 'STOP'])
    stationDataAPI = stationDataFiltered[stationDataFiltered['LAT'] != '         ']
    stationDataAPI['LOCATION'] = stationDataAPI.apply(lambda x: getLocation(x['LAT'], x['LON']), axis=1)
    stationDataResults = stationDataAPI
    stationDataResults[['MUNICIPALITY', 'COUNTRY', 'ToBeDropped']] = stationDataResults['LOCATION'].str.split(',', expand=True)
    stationDataResults = stationDataResults.drop(columns = ['SOUID', 'LAT', 'LON', 'LOCATION', 'ToBeDropped'])
    stationDataResultsTrimmed = stationDataResults[stationDataResults['MUNICIPALITY'] != '']
    stationDataResultsTrimmed = stationDataResultsTrimmed.drop_duplicates('STAID')
    stationDataResultsTrimmed.to_csv("Data/Weather/locations.csv", index=False)

def createWeatherData():
    temperaturePath = "Data/Weather/AverageDailyTemp/RawAvgTempData"
    temperatureCSV = "Data/Weather/AverageDailyTemp/AverageDailyTemp.csv"
    temperatureFilteredCSV = "Data/Weather/AverageDailyTemp/DailyTempFiltered.csv"
    snowPath = "Data/Weather/AverageDailySnowfall/RawSnowData"
    snowCSV = "Data/Weather/AverageDailySnowfall/AverageDailySnow.csv"
    snowFilteredCSV = "Data/Weather/AverageDailySnowfall/DailySnowFiltered.csv"
    rainPath = "Data/Weather/AverageDailyRain/RawRainData"
    rainCSV = "Data/Weather/AverageDailyRain/AverageDailyRain.csv"
    rainFilteredCSV = "Data/Weather/AverageDailyRain/DailyRainFiltered.csv"

    tempData = readWeatherData(temperaturePath, temperatureCSV, temperatureFilteredCSV)
    snowData = readWeatherData(snowPath, snowCSV, snowFilteredCSV)
    rainData = readWeatherData(rainPath, rainCSV, rainFilteredCSV)

    return tempData, snowData, rainData

def season(x):
    spring = range(60, 152)
    summer = range(152, 244)
    fall = range(244, 355)
    
    if x in spring:
        return 'Spring'
    if x in summer:
        return 'Summer'
    if x in fall:
        return 'Fall'
    else :
        return 'Winter'
    
def groupSeasons(data):    
    data['SEASON'] = data['DATE'].dt.dayofyear.apply(lambda x : season(x))
    data = data.drop(columns='DATE')
    if ('TG' in data.columns):
        locationAverageData = data.groupby(['SEASON', 'MUNICIPALITY', 'COUNTRY']).agg({'TG':['mean']})
        locationAverageData.columns = ['Average Temp (C)']
    elif ('SD' in data.columns):
        locationAverageData = data.groupby(['SEASON', 'MUNICIPALITY', 'COUNTRY']).agg({'SD':['mean']})
        locationAverageData.columns = ['Average Snow Depth (cm)']
    elif ('RR' in data.columns):
        locationAverageData = data.groupby(['SEASON', 'MUNICIPALITY', 'COUNTRY']).agg({'RR':['mean']})
        locationAverageData.columns = ['Average Rainfall (cm)']
    
    return locationAverageData

def mergeWeatherData(tempData, snowData, rainData, stationLocations):
    tempLocation = tempData.merge(stationLocations, left_on = 'STAID', right_on = 'STAID', how = 'left')
    snowLocation = snowData.merge(stationLocations, left_on = 'STAID', right_on = 'STAID', how = 'left')
    rainLocation = rainData.merge(stationLocations, left_on = 'STAID', right_on = 'STAID', how = 'left')

    tempLocation['DATE'] = pd.to_datetime(tempLocation['DATE'], format='%Y-%m-%d')
    snowLocation['DATE'] = pd.to_datetime(snowLocation['DATE'], format='%Y-%m-%d')
    rainLocation['DATE'] = pd.to_datetime(rainLocation['DATE'], format='%Y-%m-%d')

    tempByLocSeasons = groupSeasons(tempLocation)
    snowByLocSeasons = groupSeasons(snowLocation)
    rainByLocSeasons = groupSeasons(rainLocation)

    weatherData = tempByLocSeasons.merge(snowByLocSeasons, left_on = ['SEASON', 'MUNICIPALITY', 'COUNTRY'], right_on = ['SEASON', 'MUNICIPALITY', 'COUNTRY'], how = 'left')
    weatherData = weatherData.merge(rainByLocSeasons, left_on = ['SEASON', 'MUNICIPALITY', 'COUNTRY'], right_on = ['SEASON', 'MUNICIPALITY', 'COUNTRY'], how = 'left')
    weatherData = weatherData.dropna()

    return weatherData


def initializeWeatherData():
    #if first time running code and you dont have weather CSV's run:
    #createStationCSV()
    #tempData, snowData, rainData = createWeatherData()
    #Otherwise run:
    temperatureFilteredCSV = "Data/Weather/AverageDailyTemp/DailyTempFiltered.csv"
    snowFilteredCSV = "Data/Weather/AverageDailySnowfall/DailySnowFiltered.csv"
    rainFilteredCSV = "Data/Weather/AverageDailyRain/DailyRainFiltered.csv"

    stationLocations = pd.read_csv("Data/Weather/locations.csv")
    tempData = pd.read_csv(temperatureFilteredCSV)
    snowData = pd.read_csv(snowFilteredCSV)
    rainData = pd.read_csv(rainFilteredCSV)

    weatherData = mergeWeatherData(tempData, snowData, rainData, stationLocations)
    weatherData = weatherData.reset_index()

    weatherData.to_csv("../Data/Weather/weatherData.csv", index=False)

if __name__ == "__main__":
    initializeWeatherData()

