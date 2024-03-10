from requests_html import AsyncHTMLSession
from urllib.parse import urljoin

async def getNextFixture(teamName):
    teamName = teamName.lower()
    if teamName == "brighton & hove albion" or teamName == "brighton and hove albion":
        teamName = "brighton"
    elif teamName == "luton town":
        teamName = "luton"
    elif teamName == "manchester city":
        teamName = "man city"
    elif teamName == "manchester united" or teamName == "man united":
        teamName = "man utd"
    elif teamName == "newcastle united":
        teamName = "newcastle"
    elif teamName == "sheffield united" or teamName == "sheffield":
        teamName = "sheffield utd"
    elif teamName == "nottingham forest":
        teamName = "nott'm forest"
    elif teamName == "wolverhampton wanderers":
        teamName = "wolves"
    elif teamName == "tottenham hotspur" or teamName == "tottenham":
        teamName = "spurs"
    # Create an instance of the HTMLSession class to send HTTP requests
    session = AsyncHTMLSession()
    # The URL of the Premier League fixtures page
    url = "https://www.premierleague.com/fixtures"

    # Send a GET request to the URL and store the response
    page = await session.get(url)

    # Render any JavaScript code on the page to make sure the content is fully loaded
    # The sleep parameter specifies the number of seconds to wait before rendering the JavaScript code
    await page.html.arender(sleep=10)

    # Find all elements with the class "fixtures__matches-list"
    fixturesList = page.html.find(".fixtures__matches-list")
    datesList = []
    # Iterate through the elements and create a list of elements with the class "matchFixtureContainer"
    for i in fixturesList:
        if i.attrs.get("data-competition-matches-list") != "Date To Be Confirmed":
            datesList.append(i.find(".match-fixture"))
    fixtures = []
    # Flatten the list of lists of fixtures
    for sublist in datesList:
        fixtures.extend(sublist)
    # Iterate through the fixtures
    matchFound = False

    finalString = ""
    for fixture in fixtures:
        # Get the home team name and away team name
        homeTeam = fixture.attrs.get("data-home")
        awayTeam = fixture.attrs.get("data-away")
        # Get the time of the fixture
        time = fixture.xpath(".//*[@datetime]",first=True)


        # date = dateClass.attrs.get("data-ui-args")
        # Check if the home team or away team matches the input team name
        if homeTeam.lower() == teamName.lower() or awayTeam.lower() == teamName.lower():
            counter = 1
            for games in datesList:
                for matches in games:
                    if matches.attrs.get("data-home").lower() ==homeTeam.lower() and matches.attrs.get("data-away").lower() == awayTeam.lower():
                        finalDate = fixturesList[counter].attrs.get("data-competition-matches-list")
                        break
                counter+=1
            # If the team name matches, print the fixture information
            finalString += f'{homeTeam} vs {awayTeam} on {finalDate} at {time.attrs.get("datetime")}'
            matchFound = True
            break
    if matchFound == False:
        return "Team not found. Either the team entered was not found or the team's fixture may not be within 2 weeks"
    else:
        return finalString



async def getPlayerChoices(player):
    # create an HTML session
    session = AsyncHTMLSession()

    # create the URL based on the player's name
    url = f"https://www.premierleague.com/search?&term={player}"
    
    # get the page content using the HTML session
    page = await session.get(url)
    
    # render the page to allow JavaScript to execute
    await page.html.arender(sleep=3)

    # if the player name has only one word, get the first player link with class "statName"
    #if len(player.split()) == 1:
    playerLink = page.html.xpath(".//a[@class='stats-card__wrapper']")
    # if the player name has two words, get the player link that has the player's last name as a substring 
    #else:
    #    firstName = player.split()[0]
    #    lastName = player.split()[1]
    #    playerLink = page.html.xpath(".//a[@class='stats-card__wrapper']")

    playerChoiceList = []
    counter = 0
    for playerCard in playerLink:
        playerFirstName = playerCard.find(".stats-card__player-first")
        playerLastName = playerCard.find(".stats-card__player-last")[0]
        if not playerFirstName:
            playerName = f"{playerLastName.text}"
        else:
            playerFirstName = playerFirstName[0]
            playerName = f"{playerFirstName.text} {playerLastName.text}"  
        playerLink = page.html.xpath(".//a[@class='stats-card__wrapper']")[counter]
        playerShortURL = playerLink.attrs.get("href")
        playerChoice = f"{playerName},{playerShortURL}"
        playerChoiceList.append(playerChoice)
        counter += 1
    return playerChoiceList
    
async def getPlayerStats(shortUrl,season):
    session = AsyncHTMLSession()
    playerURL = urljoin("https://www.premierleague.com", shortUrl)
    
    # create the URL for the player's stats page
    if season == "Current Season":
        statsURL = playerURL.replace("overview", "stats?co=1&se=578")
    elif season == "All Time":
        statsURL = playerURL.replace("overview", "stats")


    # get the player's stats page content using the HTML session
    statsPage = await session.get(statsURL)

    # render the page to allow JavaScript to execute
    await statsPage.html.arender(sleep=3)

    finalString = ""

    
    # get the player's name from the playerDetails class and print it
    playerNameClass = statsPage.html.find(".playerDetails")
    for i in playerNameClass:
        playerFirstName = i.find(".player-header__name-first")
        playerLastName = i.find(".player-header__name-last")[0]
        if not playerFirstName:
            playerName = f"{playerLastName.text}"
        else:
            playerFirstName = playerFirstName[0]
            playerName = f"{playerFirstName.text} {playerLastName.text}"
        finalString += f"{playerName}\n\n"
        #print(playerName)
        #print()

    topStatWrapper = statsPage.html.find(".player-stats__top-stat")
    for topStat in topStatWrapper:
        topStatValue = topStat.find(".player-stats__top-stat-value")[0]
        finalString += f"{topStatValue.text}\n"
        #print(topStatValue.text)
    finalString += "\n"
    #print()

    # get all the stats from the player's stats page
    statWrapper = statsPage.html.find(".player-stats__stat-wrapper")
    # loop through the stats and print them out, skipping the Attack, Team, Discipline, and Defence headers
    for stat in statWrapper:
        statTitle = stat.find(".player-stats__stat-title")[0]
        statValues = stat.find(".player-stats__stat-value")
        finalString += f"{statTitle.text}\n\n"
        #print(statTitle.text)
        #print()
        for statValue in statValues:
            finalString += f"{statValue.text}\n"
            #print(statValue.text)
        finalString += "\n"
        #print()
    return finalString

async def getPlayerRankings(ranking):
    session = AsyncHTMLSession()
    match ranking:
        case "Goals":
            url = "https://www.premierleague.com/stats/top/players/goals"
        case "Assists":
            url = "https://www.premierleague.com/stats/top/players/goal_assist"
        case "Clean Sheets":
            url = "https://premierleague.com/stats/top/players/clean_sheet"
        case "Passes":
            url = "https://www.premierleague.com/stats/top/players/total_pass"

    rankingsPage = await session.get(url)

    await rankingsPage.html.arender(sleep=2)

    rankNumberList = rankingsPage.html.find(".stats-table__rank")
    rankNameList = rankingsPage.html.find(".stats-table__name")
    rankStatList = rankingsPage.html.find(".stats-table__main-stat")

    finalString = ""
    for i in range(10):
        finalString += f"{rankNumberList[i].text} {rankNameList[i].text} - {rankStatList[i].text}\n"

    return finalString



async def getTable():
    session = AsyncHTMLSession()

    url = "https://www.premierleague.com/tables"
    page = await session.get(url)
    await page.html.arender(sleep=3)

    #position = []
    #shortName = []
    #points = []
    #for i in range(0,20):
     #   position.append(page.html.find(".league-table__value")[i])
      #  shortName.append(page.html.find(".league-table__team-name--short")[i])
       # points.append(page.html.find(".league-table__points")[i])
    
    position = [elem.text for elem in page.html.find(".league-table__value")[:20]]
    shortName = [elem.text for elem in page.html.find(".league-table__team-name--short")[:20]]
    points = [elem.text for elem in page.html.find(".league-table__points")[:20]]
    gamesPlayed = [elem.text for elem in page.html.xpath(".//td")[2::14][:20]]

    max_len_pos = max(len(pos) for pos in position)
    max_len_name = max(len(name) for name in shortName)
    max_len_gp = max(len(gp) for gp in gamesPlayed)


    #gamesPlayed = []
    #for j in range (2,269,14):
    #    gamesPlayed.append(page.html.xpath(".//td")[j])

    finalString = "Pos  Club    GP    Pts\n"
    for pos, name, gp, pt in zip(position,shortName,gamesPlayed,points):
        finalString += f"{pos:<6} {name:<7} {gp:<6} {pt}\n"
    
    return finalString
    
    




