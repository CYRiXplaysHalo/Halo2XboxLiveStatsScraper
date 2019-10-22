from lxml import etree
from bs4 import BeautifulSoup
import json
import urllib.request
import time

def getGame(gameId, url):
    try:
        url = url + str(gameId)
        response = urllib.request.urlopen(url)
        data = response.read()      
        text = data.decode('utf-8')
        return text
    except urllib.error.URLError:
        print("URLError, trying again in 10 seconds")
        time.sleep(10)
        getGame(gameId, url)
    except http.client.RemoteDisconnected:
        print("RemoteDisconnected, trying again in 10 seconds")
        time.sleep(10)
        getGame(gameId, url)

for j in range(7067,10067):#14892):
    print(j)
    game_id = j
    
    h2_game_page = getGame(game_id, 'https://web.archive.org/web/1000/http://halo.bungie.net/Stats/GameStatsHalo2.aspx?gameid=')
    #with open(r'D:\HaloStats\GameStats\\' + str(game_id) + '.aspx', 'r') as myfile:
    #    h2_game_page=myfile.read().replace('\n', '')
    if h2_game_page == None:
        h2_game_page = getGame(game_id, 'http://halo.bungie.net/Stats/GameStatsHalo2.aspx?gameid=')
        
    game_info = h2_game_page[h2_game_page.find('<div class="stats_overview">'):]
    game_info = game_info[:game_info.find('<div class="clear"></div> ')]

    map_name = game_info[game_info.find('/images/Halo2Stats/Maps/')+24:]
    map_name = map_name[:map_name.find('.jpg')]

    game_name = game_info[game_info.find('<li class="first styled">')+25:]
    game_name = game_name[:game_name.find('</li>')]

    playlist = game_info[game_info.find('<li class="styled">Playlist - ')+30:]
    playlist = playlist[:playlist.find('&nbsp;')]

    datetime = game_info[game_info.find('<li>')+4:]
    datetime = datetime[:datetime.find('&nbsp;')]

    carnage_report = h2_game_page[h2_game_page.find('ctl00_mainContent_bnetpgd_pnlKills'):]
    carnage_report = carnage_report[:carnage_report.find("</table>")+8]
    carnage_report = carnage_report[carnage_report.find("<table"):]

    soup = BeautifulSoup(carnage_report, features="lxml")
    carnage_report_list = []
    carnage_report_team_list = []
    carnage_report_emblem_list = []
    carnage_report_color_list = []
    carnage_report_progress_list = []
    
    rows = soup .find_all('tr')
    for row in rows:
        #print([ele for ele in cols if ele])
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        if("Team" in str(row) or "Clan" in str(row)):
            team_list = [ele for ele in cols if ele]
            color = str(row)[str(row).find('background-color:')+17:]
            color = color[:color.find('"')]
            team_list.append(color.replace(';',''))
            carnage_report_team_list.append(team_list)
        else: 
            carnage_report_list.append([ele for ele in cols if ele])
        if("background-color" in str(row) and "Team" not in str(row) and "Clan" not in str(row)):
            #color = str(row)[str(row).find('play_matte'):]
            color = str(row)[str(row).find('ColorBG" style="background-color:')+33:]
            color = color[:color.find('"')]
            carnage_report_color_list.append(color)
        if("/Stats/emblem.ashx" in str(row)):
            emblem = str(row)[str(row).find('/Stats/emblem')+19:]
            emblem = emblem[:emblem.find('"')]
            carnage_report_emblem_list.append(emblem.replace('&amp;','&'))
        if("width:40px;height:15px;" in str(row)):
            progress = str(row)[str(row).find('width:40px;height:15px;')+44:]
            progress = progress[:progress.find('px')]
            progress_percentage = int(progress)/40
            carnage_report_progress_list.append(progress_percentage)
    carnage_report_json = []
    
    for i in range(1,len(carnage_report_list)):
        if(carnage_report_list[i][0].rfind('\n') != -1):
            last_space = carnage_report_list[i][0].rfind('\n')
        else:
            last_space = carnage_report_list[i][0].rfind(' ')
        player_rank = carnage_report_list[i][0][last_space+1:]
        player_name = carnage_report_list[i][0][:last_space].replace('\n','')
        if len(carnage_report_progress_list) == len(carnage_report_color_list) and len(carnage_report_color_list) == (len(carnage_report_list)-1):
            row = {'name':player_name,'team':carnage_report_color_list[i-1],'progress':carnage_report_progress_list[i-1],'emblem':carnage_report_emblem_list[i-1],'rank':player_rank,'kills':carnage_report_list[i][1],'assists':carnage_report_list[i][2],'deaths':carnage_report_list[i][3],'suicides':carnage_report_list[i][5],'betrayals':carnage_report_list[i][6],'score':carnage_report_list[i][7]}
        else:
            row = {'name':player_name,'emblem':carnage_report_emblem_list[i-1],'rank':player_rank,'kills':carnage_report_list[i][1],'assists':carnage_report_list[i][2],'deaths':carnage_report_list[i][3],'suicides':carnage_report_list[i][5],'betrayals':carnage_report_list[i][6],'score':carnage_report_list[i][7]}
        carnage_report_json.append(row)

    if len(carnage_report_team_list) > 0:
        team_stats = []
        for k in range(0,len(carnage_report_team_list)):
            team = carnage_report_team_list[k][0]
            kills = carnage_report_team_list[k][1]
            assists = carnage_report_team_list[k][2]
            deaths = carnage_report_team_list[k][3]
            suicides = carnage_report_team_list[k][5]
            betrayals = carnage_report_team_list[k][6]
            score = carnage_report_team_list[k][7]
            color = carnage_report_team_list[k][8].replace(';','')
            team_stats.append({'team':team,'kills':kills,'assists':assists,'deaths':deaths,'suicides':suicides,'betrayals':betrayals,'score':score,'color':color})
        game_json = {'gameId':game_id,'map':map_name,'game':game_name,'playlist':playlist,'dateTime':datetime,'teamReports':team_stats,'carnageReport':carnage_report_json}
    else:
        game_json = {'gameId':game_id,'map':map_name,'game':game_name,'playlist':playlist,'dateTime':datetime,'carnageReport':carnage_report_json}

    with open(r'D:\HaloStats\GameStats2\\' + str(game_id) + '.json', 'w') as fp:
        json.dump(game_json, fp)
