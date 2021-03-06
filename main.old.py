###################################################################################
### Summary


###################################################################################
### Libraries and Variables
## Import libraries
import logging
import os
import re
import datetime
import sys
from operator import itemgetter
from flask import Flask, request, redirect, url_for, send_from_directory, render_template
from werkzeug import secure_filename
#import fcntl

# Flask Initialization
UPLOAD_FOLDER = os.getcwd()+"/uploadedfile/"
ALLOWED_EXTENSIONS = set(['txt','csv'])
app = Flask(__name__)
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER    # Upload Folder
app.config['MAX_CONTENT_LENGTH']=1*1024*1024    # Upload File limit

# Server Initialization
# Dictionary for team
dic_team={}
dic_team_member={}
dic_team_file={}
TEAM_INFO_FILE = "TeamInfo.txt"
with open(TEAM_INFO_FILE) as teamInfoFile:
    team_i = 1
    for line in teamInfoFile:
        line_temp = line.strip("\n").strip("\r").split("|")
        team = re.sub(r'[^a-zA-Z0-9]','_',line_temp[0].lower())
        dic_team[team]=line_temp[0]
        dic_team_member[team] = line_temp[1]
        dic_team_file[team] = "%d_"%team_i+team+".txt"
        team_i += 1

list_team=[[dic_team[item],item] for item in dic_team]

# Data File
RANK_FILE = os.getcwd()+"/ranking.txt"
LOG_FILE = os.getcwd()+"/upload_log.txt"
TURE_FILE = os.getcwd()+"/test_log.txt"

# Create directory for team upload log
if not os.path.isdir("teamLog"):
    os.makedirs("teamLog")

# Create directory for temperary upload file folder
if not os.path.isdir("uploadedfile"):
    os.makedirs("uploadedfile")

# Create Ranking File
if not os.path.isfile(RANK_FILE):
    with open(RANK_FILE,"w") as rankFile:
        for item in dic_team_member:
            rankFile.write(item+"|"+dic_team_member[item]+"|0|No Uploads\n")

# Filter out file extension
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS

# Create Match Data
trueData = []
with open(TURE_FILE) as trueFile:
    for line in trueFile:
        trueData.append(line.strip("\n").strip("\r"))
###################################################################################
### Main pages

## Homepage, upload file
@app.route("/", methods=['GET','POST'])
def upload_file():
    correct_rate =  0
    try:
        if request.method == 'POST':
            file = request.files['file']
            if file and allowed_file(file.filename):
                upload_time = datetime.datetime.now()-datetime.timedelta(hours=5)
                team_name=request.form['team']
                time_string = upload_time.strftime("%Y%m%d%H%M%S")
                filename = secure_filename(time_string+team_name+file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
                return redirect(url_for('uploaded_file',filename=filename,teamName=team_name))
        return render_template("upload_file.html",teamList = list_team)
    except RequestEntityTooLarge:
        error = "File is too large!"
        return render_template("error.html",error = error)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

## Uploaded file and return correct rate
@app.route("/check/<filename>")
def uploaded_file(filename):
    testData = []

    teamName = request.args.get("teamName")
    upload_time = datetime.datetime.now()-datetime.timedelta(hours=5)
    #try:
    # Load uploaded test file
    with open(os.path.join(app.config['UPLOAD_FOLDER'],filename)) as testFile:
        for line in testFile:
            testData.append(line.strip("\n").strip("\r"))
    # Load True Result

    # Calculate correct rate
    if len(testData) == len(trueData):
        ans = [ 1 if i == j else 0 for i,j in zip(testData,trueData)]
        correct_rate = "%.4f"%(float(sum(ans))/float(len(ans)))
        with open(os.getcwd()+"/teamLog/"+dic_team_file[teamName],"a") as teamLogFile:
            with open(LOG_FILE,"a") as logFile:
                wString = upload_time.strftime("%Y-%m-%d %H:%M:%S")+"|From Team:"+teamName+"|Correct Rate: %.4f"%(float(sum(ans))/float(len(ans)))+"\n"
                #fcntl.flock(logFile, fcntl.LOCK_EX)
                logFile.write(wString)
                #fcntl.flock(logFile, fcntl.LOCK_UN)

                #fcntl.flock(teamLogFile, fcntl.LOCK_EX)
                teamLogFile.write(wString)
                #fcntl.flock(teamLogFile, fcntl.LOCK_UN)
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'],filename))

        # Update Leader board
        rank_list = []
        with open(RANK_FILE) as rankFile:
            for item in rankFile:
                temp_list = item.strip("\n").strip("\r").split("|")
                temp_list[2] = float(temp_list[2])
                rank_list.append(temp_list)

        update_bool = 0
        for line in rank_list:
            if line[0]==teamName:
                if float(correct_rate)>line[2]:
                    line[2] = float(correct_rate)
                    line[3] = upload_time.strftime("%Y-%m-%d %H:%M:%S")
                    update_bool = 1

        if update_bool:
            rank_list = sorted(rank_list, key=itemgetter(2), reverse=True)
            with open(RANK_FILE,"w") as rankFile:
                for line in rank_list:
                    #fcntl.flock(rankFile, fcntl.LOCK_EX)
                    rankFile.write("|".join(line[:2])+"|"+"%.4f"%line[2]+"|"+line[3]+"\n")
                    #fcntl.flock(rankFile, fcntl.LOCK_UN)
        return    render_template("uploaded_file.html",correct_rate="Correct Rate is " +
                                correct_rate, teamName=dic_team[teamName],
                                date=upload_time.strftime("%Y-%m-%d %H:%M:%S"))
    else:
        error = "Length doesn't match"
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'],filename))
        return render_template("error.html",error = error)

    #except FileNotFoundError:
    #    error = "File does not exist"
    #    return render_template("error.html",error = error)

# Leader Board
@app.route("/ranking")
def cur_ranking():
    rank_list = []
    i=1
    with open(RANK_FILE) as rankFile:
        for item in rankFile:
            temp=item.strip("\n").strip("\r").split("|")
            temp[0]=dic_team[temp[0]]
            rank_list.append([i]+temp)
            i=i+1
    return render_template("leader_board.html",rankList = rank_list)


if __name__=="__main__":
    #app.debug = True
    app.run(host='0.0.0.0',port=8080,debug=True)
