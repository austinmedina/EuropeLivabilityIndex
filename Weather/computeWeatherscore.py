import pandas as pd

def normalizeDifference(actual, preference, sIndex):
    difference = abs(actual - float(preference[sIndex]))
    min = difference.min()
    max = difference.max()
    differenceNormalized = (difference - min) / (max - min)
    return differenceNormalized

def computerWeatherScore(choices, unitChoices):

    weatherData = pd.read_csv("Data/Weather/weatherData.csv")
    springWeather = weatherData[weatherData['SEASON'] == 'Spring']
    summerWeather = weatherData[weatherData['SEASON'] == 'Summer']
    fallWeather = weatherData[weatherData['SEASON'] == 'Fall']
    winterWeather = weatherData[weatherData['SEASON'] == 'Winter']
    weatherDataSeasons = [springWeather, summerWeather, fallWeather, winterWeather]

    if (unitChoices[0] == 'Fahrenheit'):
        for index in range(len(choices[0])):
            choices[0][index] = (float(choices[0][index]) - 32.0) * (5/9)
    if (unitChoices[1] == 'Inches'):
        for index in range(len(choices[1])):
            choices[1][index] = (float(choices[1][index]) * 2.54)
        choices[1] = choices[1]
    if (unitChoices[2] == 'Inches'):
        for index in range(len(choices[2])):
            choices[2][index] = (float(choices[2][index]) * 2.54)

    scoreData = pd.DataFrame()
    sIndex = 0

    for season in weatherDataSeasons:
        season['SCORE'] = normalizeDifference(season['Average Temp (C)'], choices[0], sIndex) + normalizeDifference(season['Average Snow Depth (cm)'], choices[1], sIndex) + normalizeDifference(season['Average Rainfall (cm)'], choices[2], sIndex)  
        scoreData = pd.concat([scoreData, season])
        sIndex+=1
   
    return scoreData

def runLivabilityIndex(userChoices):
    choices = userChoices[:3]
    unitChoices = userChoices[3]
    scores = computerWeatherScore(choices, unitChoices)
    scoresDropped = scores.drop(columns=['SEASON', 'Average Temp (C)', 'Average Snow Depth (cm)', 'Average Rainfall (cm)'])
    scoresRegion = scoresDropped.groupby(['MUNICIPALITY', 'COUNTRY']).agg({'SCORE': 'mean'})
    scoresRegion = scoresRegion.sort_values(by=['SCORE'])
    scoresRegion = scoresRegion.drop(columns=['SCORE'])
    scoresRegion = scoresRegion.reset_index()
    return scoresRegion.iloc[:1]
    